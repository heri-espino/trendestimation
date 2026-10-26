#!/usr/bin/env python3
"""Time the *released public* select_lambda implementation in both coordinates.

This measures the actual default method='auto' behavior, rather than the
controlled 36-cell fixed-grid factorial search. In particular, CV runs
different multistart derivative searches in the two coordinate spaces;
the candidate counts are NOT necessarily matched. Interpret runtime
together with attained criterion value and score evaluation count.

Examples:
  python benchmarks/public_coordinate_optimizer_benchmark.py --preset smoke
  python benchmarks/public_coordinate_optimizer_benchmark.py --preset quick --seeds 3 --repeats 4
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

import numpy as np
import scipy
from threadpoolctl import threadpool_info, threadpool_limits
from trendestimation import TrendSmoother, select_lambda

from criterion_coordinate_matrix import CRITERIA, git_head, sample_data, workload

OUTPUT = Path("build/criterion-coordinate-study")
FIELDS = ("n", "d", "mu", "case", "seed", "block", "criterion",
          "search_space", "setup_ns", "select_ns", "total_ns",
          "evaluated_candidates", "lambda_selected", "s_selected",
          "score_selected")


def measure(n: int, d: int, mu: float, y: np.ndarray, *,
            case: int, seed: int, block: int, criterion: str,
            coordinate: str) -> dict:
    t0 = perf_counter_ns()
    model = TrendSmoother(n, order=d)
    t1 = perf_counter_ns()
    selection = select_lambda(model, y, criterion=criterion,
                              mu=mu, search_space=coordinate, method="auto")
    t2 = perf_counter_ns()
    return dict(n=n, d=d, mu=mu, case=case, seed=seed,
                block=block, criterion=criterion,
                search_space=coordinate, setup_ns=t1-t0,
                select_ns=t2-t1, total_ns=t2-t0,
                evaluated_candidates=int(len(selection.grid)),
                lambda_selected=float(selection.lambda_),
                s_selected=float(selection.smoothness),
                score_selected=float(selection.score))


def run(args):
    cases, _ = workload(args.preset)
    out = []
    for index, (n, d, mu) in enumerate(cases):
        for k in range(args.seeds):
            seed = args.seed+k
            y = sample_data(n, d, seed)
            for block in range(args.repeats):
                rng = np.random.default_rng(
                    np.random.SeedSequence([args.seed, index, k, block, 991]))
                jobs = [(crit, coord) for crit in CRITERIA
                        for coord in ("lambda", "smoothness")]
                for pos in rng.permutation(len(jobs)):
                    crit, coord = jobs[int(pos)]
                    out.append(measure(n, d, mu, y, case=index,
                                       seed=seed, block=block,
                                       criterion=crit, coordinate=coord))
        print(f"[public-selector] case {index+1}/{len(cases)} n={n} d={d}",
              flush=True)
    return out


def summary_for(rows):
    groups = defaultdict(list)
    reference = {(r["case"], r["seed"], r["block"], r["criterion"]):
                 r["score_selected"] for r in rows
                 if r["search_space"] == "lambda"}
    for r in rows:
        groups[(r["n"], r["d"], r["mu"], r["criterion"],
                r["search_space"])].append(r)
    out = []
    for key, items in sorted(groups.items()):
        times = np.asarray([r["total_ns"]/1e6 for r in items])
        chosen = np.asarray([r["score_selected"]-reference[(
            r["case"], r["seed"], r["block"], r["criterion"])]
            for r in items])
        counts = np.asarray([r["evaluated_candidates"] for r in items])
        out.append(dict(zip(("n", "d", "mu", "criterion", "search_space"), key),
                        trials=len(items), median_ms=float(np.median(times)),
                        mad_ms=float(np.median(np.abs(times-np.median(times)))),
                        median_candidates=float(np.median(counts)),
                        median_score_delta_vs_lambda=float(np.median(chosen))))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("smoke", "quick", "full"),
                        default="smoke")
    parser.add_argument("--seeds", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20261025)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if min(args.seeds, args.repeats, args.threads) < 1:
        parser.error("seeds, repeats and threads must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with threadpool_limits(limits=args.threads):
        rows = run(args)
        env = dict(python=sys.version, numpy=np.__version__,
                   scipy=scipy.__version__, platform=platform.platform(),
                   timestamp_utc=datetime.now(timezone.utc).isoformat(),
                   git_revision=git_head(), thread_limit=args.threads,
                   threadpool_info=threadpool_info(), preset=args.preset,
                   repeats=args.repeats, seeds=args.seeds, seed=args.seed,
                   note="Actual public auto selectors; do not treat native"
                   " CV searches as equal evaluation budgets.")
    for filename, data, fields in (
        ("public_raw.csv", rows, FIELDS),
        ("public_summary.csv", summary_for(rows), None),
    ):
        with (args.output_dir/filename).open("w", newline="",
                                             encoding="utf-8") as f:
            writer = csv.DictWriter(f, fields or list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    (args.output_dir/"public_environment.json").write_text(
        json.dumps(env, indent=2, default=str)+"\n", encoding="utf-8")
    print(f"Saved {len(rows)} public auto-selector trials to {args.output_dir}")


if __name__ == "__main__":
    main()
