"""Experiment007: join paired timings to independent per-fit numerical QA.

Never rank fast fits that failed accuracy (including a single failed S).
A successful comparison to the SVD baseline is tagged PROVISIONAL unless
every fitted candidate is independently certified against Decimal 85.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
from statistics import median,mean

def read(path):
    with path.open(encoding="utf-8",newline="") as stream:
        return list(csv.DictReader(stream))

def save(path,records,columns):
    with path.open("w",encoding="utf-8",newline="") as stream:
        w=csv.DictWriter(stream,fieldnames=columns)
        w.writeheader();w.writerows(records)

def s_id(s):
    return round(float(s),12)

def analyze(directory:Path):
    directory=Path(directory)
    raw=read(directory/"raw_times.csv")
    qc=read(directory/"forward_accuracy.csv")
    meta=json.loads((directory/"metadata.json").read_text(encoding="utf-8"))
    if not raw or not qc: raise ValueError("No raw results to analyze")
    if (directory/"provisional_winners.csv").exists():
        raise FileExistsError("Refusing to replace existing analysis")
    qlook={}
    for q in qc:
        key=(q["n"],q["d"],q["scale"],q["policy"],q["seed"],
             q["method"],s_id(q["s"]),int(q["series_id"]))
        if key in qlook:raise ValueError("Duplicate QA key")
        qlook[key]=q
    workload_qa=[]
    for t in raw:
        targets=([.9] if t["workload"].startswith("one_s")
                 else meta["smoothness"])
        expect=len(targets)*int(t["R"])
        evidence=[]
        for s in targets:
            for series in range(int(t["R"])):
                key=(t["n"],t["d"],t["scale"],t["mu_policy"],
                     t["seed"],t["method"],s_id(s),series)
                evidence.append(qlook.get(key))
        complete=all(x is not None for x in evidence) and len(evidence)==expect
        accurate=(complete and all(x["status"]=="agreement" for x in evidence))
        decimal=sum(x["reference"]=="decimal85" for x in evidence if x)
        if int(t["M"])!=len(targets):
            raise ValueError("Timed M does not match QA targets")
        workload_qa.append(dict(
            **t,qa_complete=complete,qa_valid=accurate,
            reference_level=("all_decimal85" if decimal==expect else
                             "mixed_decimal_and_svd" if decimal>0 else
                             "svd_proxy_only"),
            decimal85_evaluations=decimal,required_fits=expect,
            max_checked_relative_error=(
                max(float(x["relative_fit_error"]) for x in evidence
                    if x is not None and x["relative_fit_error"].lower()!="nan")
                if evidence and any(x is not None and x["relative_fit_error"].lower()!="nan"
                                    for x in evidence)
                else float("nan")
            ),
            eligible=(t["status"]=="ok" and accurate),
        ))
    status=[]
    groups=defaultdict(list)
    for q in qc:
        groups[(q["policy"],q["n"],q["d"],q["scale"],q["method"])].append(q)
    for key,records in sorted(groups.items()):
        counts=Counter(q["status"] for q in records)
        ind=[q for q in records if q["reference"]=="decimal85"]
        status.append(dict(
            mu_policy=key[0],n=int(key[1]),d=int(key[2]),
            scale=key[3],method=key[4],
            total=len(records),agreement=counts["agreement"],
            inaccurate=counts["inaccurate"],solver_failed=counts["solver_failed"],
            independent_decimal85=len(ind),
            independent_decimal85_agreement=sum(q["status"]=="agreement" for q in ind),
            independent_decimal85_inaccurate=sum(q["status"]=="inaccurate" for q in ind),
            independent_decimal85_rejected=sum(q["status"]=="solver_failed" for q in ind),
        ))
    groups=defaultdict(list)
    for row in workload_qa:
        key=(row["n"],row["d"],row["scale"],row["mu_policy"],
             row["workload"],row["method"])
        groups[key].append(row)
    timing=[]
    for key,observations in sorted(groups.items()):
        eligible=(len(observations)==len(meta["seeds"]) and
                  all(r["eligible"] for r in observations))
        vals=[float(x["cold_total_s"]) for x in observations if x["eligible"]]
        refcount=sum(int(x["decimal85_evaluations"]) for x in observations)
        timing.append(dict(
            n=int(key[0]),d=int(key[1]),scale=key[2],
            mu_policy=key[3],workload=key[4],method=key[5],
            repetitions=len(observations),
            complete_accuracy=bool(eligible),
            numerical_certification=("mixed_reference" if refcount else "svd_proxy_only"),
            decimal85_evaluations=refcount,
            mean_cold_s=mean(vals) if eligible else float("nan"),
            median_cold_s=median(vals) if eligible else float("nan"),
            max_forward_error_checked=(
                max(r["max_checked_relative_error"] for r in observations
                    if r["eligible"]) if eligible else float("nan"))
        ))
    percell=defaultdict(list)
    for row in timing:
        percell[(row["n"],row["d"],row["scale"],
                 row["mu_policy"],row["workload"])].append(row)
    winners=[]
    for key,choices in sorted(percell.items()):
        possible=[x for x in choices if x["complete_accuracy"]]
        chosen=min(possible,key=lambda x:x["median_cold_s"]) if possible else None
        svd=next((x for x in possible if x["method"]=="svd"),None)
        winners.append(dict(
            n=key[0],d=key[1],scale=key[2],mu_policy=key[3],
            workload=key[4],winning_method=(chosen["method"] if chosen else ""),
            winning_median_cold_s=(chosen["median_cold_s"] if chosen else float("nan")),
            svd_median_cold_s=(svd["median_cold_s"] if svd else float("nan")),
            provisional_speedup_vs_svd=(
                svd["median_cold_s"]/chosen["median_cold_s"]
                if chosen and svd and chosen["median_cold_s"]>0 else float("nan")),
            eligible_methods=len(possible),
            independent_certification_all=False,
            interpretation="DESCRIPTIVE ONLY: two seeds; mostly SVD proxy QA",
        ))
    save(directory/"accuracy_by_nd.csv",status,list(status[0]))
    save(directory/"timing_by_workload.csv",timing,list(timing[0]))
    save(directory/"provisional_winners.csv",winners,list(winners[0]))
    count=Counter((w["workload"],w["winning_method"])
                  for w in winners if w["mu_policy"]=="data")
    lines=[
        "# Experiment007 — Observed-difference mean solver study",
        "",
        "This report is generated exclusively from the archived actual timing",
        "and numerical validation files. This is a **fit-only** pilot with",
        f"**{len(meta['seeds'])} independent seeded blocks** and "
        f"**{meta.get('timing_repeats',1)} cold timing repetitions per block**; "
        "not a complete statistical-criterion benchmark.",
        "",
        "Primary mean: mu='data'=mean(np.diff(y,n=d)) computed independently",
        "for each observed series. Fixed mu=0 is a control, not the default.",
        "",
        f"- Timed workloads: {len(raw)}",
        f"- Individual method/fit QA records: {len(qc)}",
        f"- Timing rows passing ALL required fit-accuracy checks: {sum(x['eligible'] for x in workload_qa)} / {len(workload_qa)}",
        f"- Independent Decimal-85 accuracy checks: {sum(x['reference']=='decimal85' for x in qc)} / {len(qc)}",
        "",
        "## Descriptive winners among complete numerically agreeing methods",
        "",
        "| Workload | SVD | Cholesky | Sparse LU | FFT-PCG | No eligible method |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for workload in ("one_s_one_series","grid_one_series",
                     "one_s_three_series","grid_three_series"):
        vals=[count[workload,m] for m in ("svd","cholesky","sparse_lu","pcg_fft","")]
        lines.append("| "+workload+" | "+" | ".join(map(str,vals))+" |")
    lines.extend([
        "",
        "These are **not** universal optimal dimension switches: they combine",
        f"only n=64/128/256, {len(meta['seeds'])} seed blocks and limited S-grid sizes. The sampled",
        "fixed mu=0 and data-derived mean policies must not be conflated.",
        "Speed rankings exclude an entire method×workload×seed block if",
        "even one candidate failed numerical agreement, rather than counting",
        "incomplete grids as fast winners.",
        "",
        "Most correctness checks use spectral SVD as a provisional comparator.",
        "An 85-decimal-digit independent reference is available for selected",
        "n<=128, high-d, high-S cases only. A forward-error threshold of 1e-6",
        "is used for QA. Dataset generation knows the latent trend only to",
        "report mu_true as a diagnostic; the solver receives mu='data', never",
        "that oracle. No complete cell is independently certified at all S.",
        "",
        "Do not replace the package default with a rule inferred from this",
        "pilot; collect additional independent precision references, more",
        "seeds and larger series, and time full criterion computations first.",
    ])
    (directory/"RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    hashes={}
    for name in ("raw_times.csv","forward_accuracy.csv","metadata.json"):
        hashes[name]=hashlib.sha256((directory/name).read_bytes()).hexdigest()
    (directory/"analysis_provenance.json").write_text(
        json.dumps(dict(input_sha256=hashes,timed_rows=len(raw),qa_rows=len(qc),
                        note="All raw observations retained; no invalid results ranked"),
                   indent=2)+"\n",encoding="utf-8")
    print("\n".join(lines),flush=True)
    return status,timing,winners

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-dir",required=True,type=Path)
    args=p.parse_args()
    analyze(args.run_dir)
