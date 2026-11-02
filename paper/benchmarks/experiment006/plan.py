"""Experiment006 full factorial manifest and deterministic resource guard.

The manifest is a *plan*, not generated benchmark data. Enumerates every
requested axis, one/multiple S and one/multiple series, direct-S versus
mapped-lambda, and explicit method feasibility. Rows for new fit-only
backends remain not_implemented_full_criterion rather than fake times.

Run:
 python paper/benchmarks/experiment006/plan.py --output .../plan.csv
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from run import (
    N_LEVELS,D_LEVELS,GRID_DENOMINATORS,CRITERIA,POLICIES,
    SCENARIOS,METHODS,memory_budget_status,
)

FIT_ONLY=("banded_lu","sparse_lu","sparse_cholesky",
          "pcg_fft","pcg_dst","pcg_jacobi")
MU_LEVELS=("0.0","0.15","data")
AMPLITUDES=("low","high")


def manifest(repeats=7,R=8,max_work=5e7,max_dense_bytes=2*1024**3):
    if repeats<1 or R<2:raise ValueError("repeats>=1, R>=2 required")
    for n in N_LEVELS:
        for d in D_LEVELS:
            for mu in MU_LEVELS:
                for amplitude in AMPLITUDES:
                    for criterion in CRITERIA:
                        for method in METHODS+FIT_ONLY:
                            for scenario in SCENARIOS:
                                # The one-S task is not parameterized by
                                # a grid: do not duplicate it four times.
                                grid_sizes=(
                                    (0,) if scenario.startswith("one_s")
                                    else GRID_DENOMINATORS
                                )
                                for denom in grid_sizes:
                                    for policy in POLICIES:
                                        ns=(1 if "one_series" in scenario else R)
                                        m=(1 if denom==0 else denom)
                                        if mu=="data" and criterion!="mle":
                                            status="statistical_not_applicable"
                                        elif method in FIT_ONLY:
                                            status="fit_only_not_complete_criterion"
                                        else:
                                            status=memory_budget_status(
                                                n,d,method,denom,
                                                max_dense_bytes,max_work,
                                                scenario,ns,repeats)
                                        yield dict(
                                            n=n,d=d,mu=mu,amplitude=amplitude,
                                            criterion=criterion,method=method,
                                            scenario=scenario,coordinate=policy,
                                            grid_denominator=denom,
                                            series_count=ns,candidates_per_series=m,
                                            repeats=repeats,
                                            planned_candidate_evaluations=ns*m*repeats,
                                            estimated_arithmetic_work=(
                                                float(n)*max(1,d*d)*ns*m*repeats
                                                if method not in ("naive_inverse",
                                                                  "spectral_svd")
                                                else (float(n**3)*ns*m*repeats
                                                      if method=="naive_inverse"
                                                      else float(n*n)*ns*m*repeats)
                                            ),
                                            status=status,
                                        )


def write_manifest(path:Path,*,repeats=7,R=8,max_work=5e7,max_dense_bytes=2*1024**3):
    path=Path(path)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing plan: {path}")
    counts=Counter()
    records=0
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=None
        for row in manifest(repeats,R,max_work,max_dense_bytes):
            if writer is None:
                writer=csv.DictWriter(f,fieldnames=list(row))
                writer.writeheader()
            writer.writerow(row)
            counts[row["status"]]+=1
            records+=1
    print(f"Planned {records} factorial cells in {path}")
    for status,count in sorted(counts.items()):
        print(f"  {status}: {count}")
    return counts


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repeats",type=int,default=7)
    p.add_argument("--series-count",type=int,default=8)
    p.add_argument("--max-work",type=float,default=5e7)
    p.add_argument("--max-dense-bytes",type=int,default=2*1024**3)
    p.add_argument("--output",type=Path,
                   default=Path("paper/benchmarks/experiment006/manifest.csv"))
    a=p.parse_args()
    write_manifest(a.output,repeats=a.repeats,R=a.series_count,
                   max_work=a.max_work,max_dense_bytes=a.max_dense_bytes)


if __name__=="__main__":
    main()
