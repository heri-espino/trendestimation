"""Experiment011 full factorial MANIFEST ONLY; never evaluates a criterion.

The comprehensive 252,000-cell design is the user's requested tensor
index, not a completed timing table. Reuse Experiment008's already
established (and audited) complete-factorial generator. This avoids
inventing a competing grid or losing previous experimental results.

Run from the repository root:
    python paper/benchmarks/experiment011/full_plan.py

The output contains planned statuses, not seconds. Existing archived
Experiment008 and Experiment010 measurements remain separate and
must be reconciled by exact case/host/source keys before comparison.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP008 = ROOT / "paper" / "benchmarks" / "experiment008" / "run_batches.py"
EXP006 = ROOT / "paper" / "benchmarks" / "experiment006" / "run.py"
OUT = HERE / "plans" / "full_factorial_plan.csv.gz"
EXPECTED_CELLS = 252_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def full_axes() -> dict:
    sys.path.insert(0, str(EXP006.parent))
    sys.path.insert(0, str(EXP008.parent))
    from run import (
        N_LEVELS, D_LEVELS, CRITERIA, METHODS, SCENARIOS,
        POLICIES, GRID_DENOMINATORS
    )
    axes = dict(
        n=list(N_LEVELS), d=list(D_LEVELS),
        mu=["0", "data", "0.15"], amplitude=["low", "high"],
        criterion=list(CRITERIA), method=list(METHODS),
        grid_denominator=list(GRID_DENOMINATORS),
        workload=list(SCENARIOS), coordinate=list(POLICIES),
    )
    expected={
        "n":[64,128,256,512,1024,16384,131072],
        "d":[1,2,3,4,5,6],
        "mu":["0","data","0.15"],
        "amplitude":["low","high"],
        "criterion":["cv","gcv","bic","aicc","mle"],
        "grid_denominator":[100,1000,10000,100000],
        "workload":["one_s_one_series","grid_one_series",
                    "one_s_multiple_series","grid_multiple_series"],
        "coordinate":["direct_s","mapped_lambda"],
    }
    for key,values in expected.items():
        if axes[key]!=values:
            raise AssertionError(f"Existing Experiment006 factor drift: {key}={axes[key]}")
    if len(axes["method"])!=10 or len(set(axes["method"]))!=10:
        raise AssertionError("Full plan must contain exactly ten complete-criterion methods")
    # The one-S workloads are counted ONCE per factor configuration,
    # not once for each of the four multi-S grid densities.
    nbase=(len(axes["n"])*len(axes["d"])*len(axes["mu"])*
           len(axes["amplitude"])*len(axes["criterion"])*
           len(axes["method"])*len(axes["coordinate"]))
    total=nbase*(2+2*len(axes["grid_denominator"]))
    assert total==EXPECTED_CELLS, total
    return axes


def verify_manifest(path: Path, axes: dict) -> dict:
    statuses={}
    count=0
    sample=[]
    with gzip.open(path,"rt",encoding="utf-8",newline="") as stream:
        reader=csv.DictReader(stream)
        required={"n","d","mu","amplitude","criterion",
                  "method","grid_denominator","workload","coordinate",
                  "R","M","planned_fits","score_semantics","plan_status"}
        if set(reader.fieldnames or []) != required:
            raise ValueError("Source manifest columns changed; review earlier study")
        for row in reader:
            count+=1
            status=row["plan_status"]
            statuses[status]=statuses.get(status,0)+1
            if count in (1, 2, 5, EXPECTED_CELLS):
                sample.append({k:row[k] for k in
                               ("n","d","mu","criterion","method",
                                "M","workload","coordinate","plan_status")})
            if row["method"] not in axes["method"]:
                raise ValueError("Unknown solver")
            if row["plan_status"] not in (
                "eligible","budget_exceeded",
                "infeasible_dense_memory","infeasible_naive_runtime",
                "infeasible_svd_runtime"
            ):
                raise ValueError("Unknown planned feasibility status")
            if row["workload"].startswith("one_s"):
                if (row["grid_denominator"],row["M"]) != ("0","1"):
                    raise ValueError("Single-S workload is redundantly enumerated")
            else:
                if int(row["M"]) not in axes["grid_denominator"]:
                    raise ValueError("Invalid multi-S grid")
    if count!=EXPECTED_CELLS:
        raise ValueError(f"Expected {EXPECTED_CELLS} planned rows; got {count}")
    return {"planned_cells":count,
            "resource_status_counts":dict(sorted(statuses.items())),
            "sample_only":sample}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=OUT)
    parser.add_argument("--repeats",type=int,default=6,
                        help="Planned times per cell; no measurements launched")
    parser.add_argument("--series-count",type=int,default=3)
    parser.add_argument("--max-work",type=float,default=5e8)
    parser.add_argument("--max-dense-bytes",type=int,default=2*1024**3)
    args=parser.parse_args()
    if args.repeats<1 or args.series_count<2:
        parser.error("positive repeats and at least two series required")
    axes=full_axes()
    # Import existing Experiment008 generator only after verifying its axes.
    from run_batches import planned_cells
    dest=args.output.resolve()
    meta=dest.with_suffix(".metadata.json")
    inputs={
        "generator_sha256":sha256(EXP008),
        "resource_guard_sha256":sha256(EXP006),
        "axes":axes,"requested_repeats":args.repeats,
        "series_count_for_multiple_series":args.series_count,
        "max_work":args.max_work,
        "max_dense_bytes":args.max_dense_bytes,
        "coordinate_note":("direct_s and mapped_lambda evaluate the exact "
                           "same candidate S grid; neither is an independent "
                           "log-lambda optimization search"),
        "not_a_timing_dataset":True,
        "amplitude_note":"low=1e-3, high=1e6 in the inherited sample generator",
        "mean_note":("0 and 0.15 fixed, data=mean(D_d y); non-MLE "
                     "plug-in scores are conditional, not refitted LOOCV"),
        "resource_note":("eligibility is model-based. Dense n=131072 matrix "
                         "is 128 GiB before factorization workspaces."),
        "statistic_note":("Repeated runtime outcomes need real independent "
                          "blocks, status masks, and paired naive speedups; "
                          "no RMSE is part of this study."),
    }
    if dest.exists() or meta.exists():
        if not dest.exists() or not meta.exists():
            raise FileExistsError("Incomplete existing plan; preserve and investigate")
        saved=json.loads(meta.read_text(encoding="utf-8"))
        if {k:saved[k] for k in inputs}!=inputs:
            raise FileExistsError("Previous plan has different settings/source; choose a new output")
        summary=verify_manifest(dest, axes)
        if summary["resource_status_counts"]!=saved["resource_status_counts"]:
            raise RuntimeError("Archived plan metadata does not match actual rows")
        print(json.dumps({"status":"existing_full_plan_verified",
                          "path":str(dest),**summary},indent=2))
        return
    dest.parent.mkdir(parents=True,exist_ok=True)
    count,statuses=planned_cells(
        dest,repeats=args.repeats,R=args.series_count,
        max_work=args.max_work,max_dense_bytes=args.max_dense_bytes
    )
    if count!=EXPECTED_CELLS:
        raise RuntimeError(f"Experiment008 manifest has {count}, expected {EXPECTED_CELLS}")
    summary=verify_manifest(dest,axes)
    if summary["resource_status_counts"]!=dict(sorted(statuses.items())):
        raise RuntimeError("Generator and file disagree; do not publish the plan")
    meta.write_text(json.dumps({
        "study":"experiment011_full_factorial_index",
        "data_type":"planned_method_workload_eligibility_only",
        **inputs, **summary,
        "manifest_sha256":sha256(dest),
        "method":"Reuse Experiment008 planned_cells without running any solver",
    },indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"full_plan_generated_not_measured",
                      "path":str(dest),**summary},indent=2))


if __name__=="__main__":
    main()
