"""Experiment011: assemble a reproducible *sparse* tensor of measured times.

Inputs are immutable completed Experiment011 run folders. Each actual row
is kept with source/machine/repeat/status; the full 252000-cell PLAN is
separate. No missing or infeasible cell is assigned a fake runtime.
No RMSE is computed.

Usage (repository root):
    python paper/benchmarks/experiment011/analyze.py \
      --runs paper/benchmarks/experiment011/runs \
      --output paper/benchmarks/experiment011/analysis/PCAG103A08_001

Only compatible host/software/runner-hash blocks are aggregated.
Confidence intervals (when >=3 valid independent blocks) resample
block means, NOT dependent method/coordinate records.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

HERE = Path(__file__).resolve().parent
MEASURE_FIELDS = ("method_setup_s", "s_to_lambda_s",
                  "candidate_evaluation_s", "total_cold_s", "total_warm_s")
MEASURED_COLUMNS = (
    "run_tag", "case_id", "block", "block_seed", "repeat", "n", "d", "mu",
    "amplitude", "criterion", "grid_denominator", "coordinate", "workload",
    "method", "R", "M", "status", "selected_s", "selected_score",
    "method_setup_s", "s_to_lambda_s", "candidate_evaluation_s",
    "total_cold_s", "total_warm_s", "evaluations", "host",
    "environment_fingerprint", "blas_threads",
    "experiment006_source_sha256", "git_sha", "qa_classification"
)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf8",newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], columns) -> None:
    with path.open("w",encoding="utf8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=columns,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def machine_fingerprint(environment: dict) -> str:
    # Do not use Git commit here: result-only commits change HEAD without
    # altering the benchmark executable, NumPy or BLAS on the same host.
    keys=("host","python","numpy","scipy","blas_threads","threadpools")
    encoded=json.dumps({k:environment.get(k) for k in keys},
                       sort_keys=True).encode("utf8")
    return hashlib.sha256(encoded).hexdigest()


def load_block(path: Path) -> list[dict]:
    manifest=json.loads((path/"experiment011_case.json").read_text())
    environment=json.loads((path/"measurements"/"environment.json").read_text())
    qa=json.loads((path/"experiment011_qa.json").read_text())
    if manifest["experiment"]!="experiment011" or qa["experiment"]!="experiment011":
        raise ValueError(f"Not an Experiment011 archive: {path}")
    if (manifest["case"]["id"]!=qa["case_id"]
            or manifest["block"]!=qa["block"]):
        raise ValueError(f"QA/case mismatch: {path}")
    if qa["classification"] in ("needs_independent_numerical_review",
                                "insufficient_paired_comparisons"):
        # Preserve rows but prevent claims that these are validated pairs.
        pass
    raw=read_csv(path/"measurements"/"raw_times.csv")
    if len(raw)!=qa["raw_rows"]:
        raise ValueError(f"QA/raw row count mismatch: {path}")
    if environment["git_sha"]!=manifest["source_commit"]:
        raise ValueError(f"Source SHA mismatch: {path}")
    if environment["code_sha256"]!=manifest["source_file_sha256"]:
        raise ValueError(f"Source executable changed: {path}")
    finger=machine_fingerprint(environment)
    result=[]
    for row in raw:
        out=dict(row)
        out.update({
            "run_tag":path.parent.parent.name,
            "case_id":manifest["case"]["id"],
            "block":manifest["block"],
            "block_seed":manifest["seed"],
            "host":environment["host"],
            "environment_fingerprint":finger,
            "blas_threads":environment["blas_threads"],
            "experiment006_source_sha256":manifest["source_file_sha256"],
            "git_sha":manifest["source_commit"],
            "qa_classification":qa["classification"],
        })
        if row["status"]=="ok":
            for col in MEASURE_FIELDS:
                t=float(row[col])
                if not math.isfinite(t) or t<0:
                    raise ValueError(f"Invalid measured {col}: {path}")
        result.append(out)
    return result


def load_all(runs: Path, run_tag: str | None = None) -> list[dict]:
    if run_tag is not None and not (run_tag.replace("_","").replace("-","").isalnum()):
        raise ValueError("Invalid run tag")
    roots=sorted(runs.glob(f"{run_tag or '*'}/*/block*/experiment011_case.json"))
    if not roots:
        raise FileNotFoundError(f"No Experiment011 blocks under {runs}")
    results=[]
    seen=set()
    for src in roots:
        block=src.parent
        name=(block.parent.parent.name,block.parent.name,block.name)
        if name in seen:
            raise RuntimeError("Duplicate run/case/block "+str(name))
        seen.add(name)
        results.extend(load_block(block))
    return results


def status_and_measured(rows: list[dict]) -> dict:
    return {"actual_rows":len(rows),
            "success_rows":sum(x["status"]=="ok" for x in rows),
            "status_counts":dict(sorted(Counter(x["status"] for x in rows).items())),
            "case_count":len({x["case_id"] for x in rows}),
            "block_count":len({(x["run_tag"],x["case_id"],x["block"])
                               for x in rows}),
            "source_file_hashes":sorted({x["experiment006_source_sha256"]
                                         for x in rows}),
            "hosts":sorted({x["host"] for x in rows})}


def paired_naive(rows: list[dict]) -> list[dict]:
    matched=defaultdict(dict)
    for row in rows:
        key=(row["run_tag"],row["case_id"],int(row["block"]),
             int(row["block_seed"]),int(row["repeat"]),row["coordinate"],row["workload"],
             row["environment_fingerprint"],row["experiment006_source_sha256"])
        if row["method"] in matched[key]:
            raise ValueError("Duplicate method cell for "+str(key))
        matched[key][row["method"]]=row
    pairs=[]
    for key,methods in sorted(matched.items()):
        baseline=methods.get("naive_inverse")
        if baseline is None or baseline["status"]!="ok":
            # Baseline not feasible: no fabricated naive speedup.
            continue
        denominator=float(baseline["total_cold_s"])
        if denominator<=0:
            continue
        for method,measured in sorted(methods.items()):
            if method=="naive_inverse" or measured["status"]!="ok":
                continue
            if measured["qa_classification"] in (
                    "needs_independent_numerical_review",
                    "insufficient_paired_comparisons"):
                continue
            s_error=abs(float(measured["selected_s"])-
                        float(baseline["selected_s"]))
            # Marginal ML scores may differ by an additive normalizing
            # constant; report minimizer parity but not absolute score parity.
            score_error=(
                abs(float(measured["selected_score"])-
                    float(baseline["selected_score"]))/
                max(1.0,abs(float(baseline["selected_score"])))
                if measured["criterion"]!="mle" else 0.)
            if s_error>1e-10 or score_error>1e-7:
                continue
            t=float(measured["total_cold_s"])
            if t<=0:
                continue
            pairs.append({
                "run_tag":measured["run_tag"],"case_id":measured["case_id"],
                "block":measured["block"],"block_seed":measured["block_seed"],
                "repeat":measured["repeat"],
                "coordinate":measured["coordinate"],"workload":measured["workload"],
                "n":measured["n"],"d":measured["d"],"mu":measured["mu"],
                "criterion":measured["criterion"],"M":measured["M"],
                "R":measured["R"],"method":method,
                "naive_total_cold_s":denominator,
                "method_total_cold_s":t,
                "paired_naive_speedup":denominator/t,
                "source_sha256":measured["experiment006_source_sha256"],
                "environment_fingerprint":measured["environment_fingerprint"],
                "precision_note":"float64_parity_only_not_forward_error_certified",
            })
    return pairs


def block_mean_ci(block_means: list[float], seed=20261103):
    if len(block_means)<3:
        return None,None
    rng=random.Random(seed)
    n=len(block_means)
    boot=sorted(sum(rng.choices(block_means,k=n))/n
                for _ in range(2000))
    return boot[int(.025*len(boot))],boot[min(len(boot)-1,int(.975*len(boot)))]


def theory_family(method: str,criterion: str) -> str:
    if method=="naive_inverse":
        return "O(M*R*n^3) without reusable inverse"
    if method=="spectral_svd":
        if criterion=="cv":
            return "O(n*r^2 + R*n*r + M*I*r + M*R*n*r); r=n-d"
        return "O(n*r^2 + R*n*r + M*I*r + M*R*r); r=n-d"
    if method=="banded_cholesky":
        return "O(n*d^2 + M*I*n*d^2 + M*n*d^2 + M*R*n*d); full criteria"
    return "backend fit + separately charged O(M*n*d^2) banded diagnostics"


def summaries(rows: list[dict], required_blocks=3) -> list[dict]:
    bycell=defaultdict(list)
    for row in rows:
        key=(row["case_id"],row["method"],row["coordinate"],row["workload"],
             row["n"],row["d"],row["mu"],row["amplitude"],row["criterion"],
             row["M"],row["R"],row["host"],
             row["environment_fingerprint"],row["experiment006_source_sha256"])
        bycell[key].append(row)
    entries=[]
    for key,records in sorted(bycell.items()):
        blocks=defaultdict(list)
        for row in records:
            # Two run tags with the same deterministic block seed are
            # repeated inputs, NOT independent timing blocks.
            blocks[row["block_seed"]].append(row)
        complete=[]
        for block,subset in blocks.items():
            expected_repeats=2 if any(row["case_id"].startswith(
                ("pilot_","confirm_")) for row in subset) else 1
            indices={int(x["repeat"]) for x in subset if x["status"]=="ok"}
            if (len(subset)==expected_repeats and
                    indices==set(range(expected_repeats)) and
                    all(x["qa_classification"] not in
                        ("needs_independent_numerical_review",
                         "insufficient_paired_comparisons")
                        for x in subset) and
                    all(x["status"]=="ok" for x in subset)):
                complete.append(statistics.mean(
                    float(x["total_cold_s"]) for x in subset))
        low,high=block_mean_ci(complete)
        entry={k:v for k,v in zip(
            ("case_id","method","coordinate","workload",
             "n","d","mu","amplitude","criterion","M","R",
             "host","environment_fingerprint","experiment006_source_sha256"),key)}
        entry.update({
            "actual_rows":len(records),
            "status_counts":json.dumps(dict(Counter(x["status"] for x in records)),
                                       sort_keys=True),
            "complete_independent_blocks":len(complete),
            "required_blocks_for_interval":required_blocks,
            "block_mean_total_cold_s":(
                statistics.mean(complete) if complete else ""),
            "median_of_block_mean_total_cold_s":(
                statistics.median(complete) if complete else ""),
            "block_sd_total_cold_s":(
                statistics.stdev(complete) if len(complete)>=2 else ""),
            "block_bootstrap_ci95_low_s":low if low is not None else "",
            "block_bootstrap_ci95_high_s":high if high is not None else "",
            "ready_for_block_level_uncertainty":len(complete)>=required_blocks,
            "theory_big_o_work_not_seconds":theory_family(key[1],key[8]),
            "status":(
                "preliminary_block_mean" if len(complete)<required_blocks and complete
                else "validated_blocks_not_precision_certified"
                if len(complete)>=required_blocks else "incomplete_no_mean"),
        })
        entries.append(entry)
    return entries


def analyze(runs: Path, output: Path, run_tag: str | None = None) -> dict:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite prior analysis: {output}")
    rows=load_all(runs,run_tag=run_tag)
    pairs=paired_naive(rows)
    agg=summaries(rows)
    output.mkdir(parents=True,exist_ok=False)
    write_csv(output/"measured_timing_tensor.csv",rows,MEASURED_COLUMNS)
    pairfields=("run_tag","case_id","block","block_seed","repeat","coordinate","workload",
                "n","d","mu","criterion","M","R","method",
                "naive_total_cold_s","method_total_cold_s",
                "paired_naive_speedup","source_sha256",
                "environment_fingerprint","precision_note")
    write_csv(output/"paired_naive_speedups.csv",pairs,pairfields)
    if not agg:
        raise RuntimeError("Unexpected empty aggregate")
    write_csv(output/"block_aggregated_times.csv",agg,agg[0].keys())
    summary={
        "experiment":"experiment011",
        "kind":"measured_sparse_tensor_not_full_factorial",
        "source_run_directory":str(runs),
        "requested_run_tag":run_tag or "all_available_runs",
        **status_and_measured(rows),
        "matched_naive_pairs":len(pairs),
        "aggregated_cells":len(agg),
        "cells_with_3_or_more_complete_blocks":sum(
            x["complete_independent_blocks"]>=3 for x in agg),
        "note":("The 252000-cell factorial is an independent PLAN index. "
                "These rows are only genuinely measured cells. "
                "No RMSE is computed; theory Big-O entries are NOT seconds. "
                "One smoke block gives no block-bootstrap interval. "
                "A naive baseline speedup exists only when the naive "
                "pipeline completed on the same independent block."),
    }
    (output/"analysis_summary.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(summary,indent=2))
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--run-tag",type=str,default=None,
                        help="Select exactly one machine-run campaign; default is all")
    args=parser.parse_args()
    analyze(args.runs,args.output,run_tag=args.run_tag)


if __name__=="__main__":
    main()
