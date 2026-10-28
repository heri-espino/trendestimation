"""Paired accuracy and execution-time study for S^{-1} in float64.

Run from repository root:
  python benchmarks/inversion_study.py --repeats 35 --output-dir paper/computational-statistics-submission/research/final_vm/inversion

The four algorithms receive the same initialized TrendSmoother for a
given n,d,s. Methods are randomized within each timing block. The d=0
identity spectrum uses the analytical inverse for ALL methods and is
reported separately, not counted as a root-solver victory. Timing repeats
on the same host are technical repetitions, NOT independent data seeds.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from time import perf_counter_ns

import numpy as np
import scipy
from threadpoolctl import threadpool_info, threadpool_limits

from trendestimation import TrendSmoother

METHODS = ("brentq", "newton", "secant", "bisect")
TARGETS = (
    1e-14, 1e-10, 1e-6, .01, .1, .5, .9, .99,
    1-1e-6, 1-1e-10, 1-1e-14,
)
FIELDS = ("n","d","target","block","position","method","elapsed_us",
          "success","lambda","iterations","function_evaluations",
          "derivative_evaluations","relative_tail_error","failure_kind")


def _git_revision() -> str | None:
    try:
        return subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True,timeout=3,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError,subprocess.SubprocessError):
        return None


def _invert(model: TrendSmoother, target: float, method: str) -> dict:
    begun=perf_counter_ns()
    try:
        value=model.lambda_for_smoothness(target,method=method)
        duration=(perf_counter_ns()-begun)/1000.0
        diagnostic=model._last_smoothness_root_diagnostics
        upper=target>.5
        expected=1-target if upper else target
        actual=model._smoothness_log_value(np.log(value),complement=upper)
        relative=abs(expected-actual)/expected
        if not np.isfinite(relative) or relative>1e-9:
            raise ArithmeticError(f"Relative tail inversion error {relative:.6g}")
        return dict(
            elapsed_us=duration,success=1,lambda_=float(value),
            iterations=int(diagnostic["iterations"]),
            function_evaluations=int(diagnostic["function_evaluations"]),
            derivative_evaluations=int(diagnostic["derivative_evaluations"]),
            relative_tail_error=float(relative),failure_kind="",
        )
    except (ValueError,ArithmeticError,RuntimeError,OverflowError) as exc:
        return dict(
            elapsed_us=(perf_counter_ns()-begun)/1000.0,
            success=0,lambda_=float("nan"),iterations=-1,
            function_evaluations=-1,derivative_evaluations=-1,
            relative_tail_error=float("nan"),
            failure_kind=type(exc).__name__,
        )


def _write_csv(path: Path, rows: list[dict], fields: tuple[str,...]) -> None:
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(*, sizes=(30,60,120), orders=(0,1,2,3), repeats=35,
        threads=1, seed=20261027, output_dir:Path) -> dict:
    """Produce complete per-method raw observations and grouped summaries."""
    if min(repeats,threads)<1:
        raise ValueError("repeats and threads must be positive")
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    raw=[]
    rng=np.random.default_rng(seed)
    with threadpool_limits(limits=threads):
        for n in sizes:
            for d in orders:
                if not 0<=d<n:
                    continue
                model=TrendSmoother(n,order=d)
                print(f"[inversion] n={n} d={d} targets={len(TARGETS)}",flush=True)
                for target in TARGETS:
                    # Warm the exact target/method without billing time,
                    # then measure in randomized complete matched blocks.
                    for method in METHODS:
                        _invert(model,target,method)
                    for block in range(repeats):
                        for position,method in enumerate(rng.permutation(METHODS)):
                            result=_invert(model,target,str(method))
                            row={
                                "n":n,"d":d,"target":format(target,".17g"),
                                "block":block,"position":position,
                                "method":str(method),
                                "elapsed_us":result["elapsed_us"],
                                "success":result["success"],
                                "lambda":result["lambda_"],
                                "iterations":result["iterations"],
                                "function_evaluations":result["function_evaluations"],
                                "derivative_evaluations":result["derivative_evaluations"],
                                "relative_tail_error":result["relative_tail_error"],
                                "failure_kind":result["failure_kind"],
                            }
                            raw.append(row)
        blas=threadpool_info()
    _write_csv(output_dir/"raw_inversions.csv",raw,FIELDS)
    summary=[]
    for n in sizes:
        for d in orders:
            if not 0<=d<n:
                continue
            for target in TARGETS:
                key=format(target,".17g")
                for method in METHODS:
                    rows=[x for x in raw if x["n"]==n and x["d"]==d
                          and x["target"]==key and x["method"]==method]
                    successes=[x for x in rows if x["success"]]
                    durations=np.array([x["elapsed_us"] for x in successes])
                    errors=[x["relative_tail_error"] for x in successes]
                    summary.append({
                        "n":n,"d":d,"target":key,"method":method,
                        "trials":len(rows),"failures":len(rows)-len(successes),
                        "median_us":float(np.median(durations)) if len(durations) else None,
                        "p10_us":float(np.quantile(durations,.1)) if len(durations) else None,
                        "p90_us":float(np.quantile(durations,.9)) if len(durations) else None,
                        "median_iterations":float(median(x["iterations"] for x in successes))
                        if successes else None,
                        "median_function_evaluations":float(
                            median(x["function_evaluations"] for x in successes))
                        if successes else None,
                        "max_relative_tail_error":float(max(errors)) if errors else None,
                        "analytic_case":bool(d==0),
                    })
    fields=tuple(summary[0])
    _write_csv(output_dir/"summary.csv",summary,fields)
    metadata={
        "protocol":"randomized_paired_float64_inverse_v1",
        "recorded_utc":datetime.now(timezone.utc).isoformat(),
        "git_revision":_git_revision(),"sizes":list(sizes),"orders":list(orders),
        "targets":[format(s,".17g") for s in TARGETS],"methods":list(METHODS),
        "repeats":repeats,"randomization_seed":seed,"blas_threads_requested":threads,
        "environment":{
            "python":sys.version,"numpy":np.__version__,"scipy":scipy.__version__,
            "platform":platform.platform(),"processor":platform.processor(),
            "cpu_count":os.cpu_count(),"threadpools":blas,
        },
        "scientific_limits":(
            "Only float64 arithmetic. Tail error computed with complementary "
            "smoothness for s>0.5 to reduce cancellation. No timing hypothesis "
            "tests: repeats on one machine are technical, not independent units. "
            "Accuracy and failure status take priority over raw speed. "
            "d=0 is analytical for all algorithms; do not rank these cases."
        ),
    }
    (output_dir/"environment.json").write_text(
        json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    return {"raw":raw,"summary":summary,"metadata":metadata}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes",default="30,60,120")
    parser.add_argument("--orders",default="0,1,2,3")
    parser.add_argument("--repeats",type=int,default=35)
    parser.add_argument("--threads",type=int,default=1)
    parser.add_argument("--seed",type=int,default=20261027)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    report=run(
        sizes=tuple(map(int,args.sizes.split(","))),
        orders=tuple(map(int,args.orders.split(","))),
        repeats=args.repeats,threads=args.threads,seed=args.seed,
        output_dir=args.output_dir,
    )
    failed=sum(x["failures"] for x in report["summary"])
    print(f"[inversion] {len(report['raw'])} timed observations; "
          f"{failed} failures; outputs: {args.output_dir}",flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
