"""Measured fixed-mu CV/GCV/AICc/BIC/conditional-MLE search in S and lambda.

This is a *different* timing experiment from the 6-backend GCV study:
it uses the public spectral select_lambda API and tests all five selection
CRITERIA over corresponding candidate penalty/S grids.

- matched_lambda: map a native 16-point S grid to penalties once, then
  reuse that grid for every criterion (inversion outside the selector).
- native_s: pass the same S targets to select_lambda, including 0 and 1,
  causing inversion within each criterion's selector.
- log_lambda: the same number of candidate points with a different,
  independently sampled log-penalty interior; not a parity comparison.

No objective values are compared *across criteria*. Exact S=0/S=1 are
included; CV and MLE at lambda=0 may have infinite (undefined) score.
Timings measure select_lambda with a prebuilt TrendSmoother, not its SVD
construction. Inversion-grid construction time is separately recorded.

Run from repository root:
 python paper/benchmarks/selection_coordinate_mle.py --preset quick
 python paper/benchmarks/selection_coordinate_mle.py --preset full --repeats 9
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from threadpoolctl import threadpool_limits, threadpool_info

from trendestimation import TrendSmoother, select_lambda

HERE = Path(__file__).resolve().parent
CRITERIA = ("cv", "gcv", "aicc", "bic", "mle")
POLICIES = ("matched_lambda", "native_s", "log_lambda")


def s_grid():
    return np.unique(np.r_[
        np.linspace(0, 1, 11),
        (0.95, 0.99, 0.999, 0.9999, 0.999999),
    ])


def simulated(n, seed):
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 1.0, n)
    latent = 0.65 * np.sin(2.8 * np.pi * t) + 0.2 * np.cos(
        5 * np.pi * t) + 0.15 * t
    return latent + rng.normal(0.0, 0.22, n)


def choose(model, y, criterion, mu, policy, penalties, targets, log_grid):
    if policy == "native_s":
        return select_lambda(model, y, criterion=criterion, mu=mu,
                             search_space="smoothness", grid=targets)
    grid = penalties if policy == "matched_lambda" else log_grid
    return select_lambda(model, y, criterion=criterion, mu=mu,
                         search_space="lambda", grid=grid)


def workloads(preset):
    if preset == "smoke":
        return ((26, 2),)
    if preset == "quick":
        return ((60, 2), (60, 4))
    if preset == "full":
        return ((60, 1), (60, 2), (60, 3), (60, 4),
                (100, 2), (100, 4))
    raise ValueError(preset)


def study(preset="quick", repeats=5, threads=1, seed=20261026,
          output_dir=HERE / "selection_coordinate_reference"):
    if repeats < 1 or threads < 1:
        raise ValueError("repeats/threads must be positive")
    results, scores, grid_rows, constructors = [], [], [], []
    with threadpool_limits(limits=threads):
        meta = {
            "recorded_utc": datetime.now(timezone.utc).isoformat(),
            "platform": platform.platform(), "cpu": platform.processor(),
            "python": sys.version, "numpy": np.__version__,
            "scipy": scipy.__version__, "blas_threads": threads,
            "threadpools": threadpool_info(), "seed": seed,
            "repeats": repeats, "preset": preset,
            "git_revision": os.environ.get("GITHUB_SHA", "local"),
            "criteria": list(CRITERIA), "policies": list(POLICIES),
            "note": "Public spectral selectors at the same native 16-point "
                    "S grid and mapped lambda penalties; SVD preparation "
                    "timed separately; GCV etc and MLE scores have "
                    "different units and are not numerically rankable.",
        }
        for n, d in workloads(preset):
            start = perf_counter()
            model = TrendSmoother(n, order=d)
            construction_s = perf_counter() - start
            y = simulated(n, seed + n + 17 * d)
            targets = s_grid()
            t0 = perf_counter()
            penalties = np.array([model.lambda_for_smoothness(float(s))
                                  for s in targets])
            mapping_s = perf_counter() - t0
            assert penalties[0] == 0 and np.isposinf(penalties[-1])
            recovered = np.array([model.smoothness(float(v)) for v in penalties])
            np.testing.assert_allclose(targets, recovered, rtol=0, atol=1e-9)
            scale = 1 / model._median_positive_eigenvalue
            log_grid = np.r_[0., scale * np.geomspace(1e-8, 1e8,
                                                      len(targets) - 2), np.inf]
            constructors.append({
                "n": n, "d": d, "svd_construction_s": construction_s,
                "mapped_grid_construction_s": mapping_s,
                "grid_size": len(targets),
            })
            for j, s in enumerate(targets):
                grid_rows.append({
                    "n": n, "d": d, "index": j, "S_target": float(s),
                    "lambda": float(penalties[j]),
                    "S_recovered": float(recovered[j]),
                    "lambda_log_policy": float(log_grid[j]),
                })
            for mu in (0.0, 0.15):
                for criterion in CRITERIA:
                    reference = choose(model, y, criterion, mu,
                                       "matched_lambda", penalties, targets, log_grid)
                    direct = choose(model, y, criterion, mu,
                                    "native_s", penalties, targets, log_grid)
                    np.testing.assert_allclose(
                        reference.grid, direct.grid, atol=1e-9, rtol=1e-9)
                    np.testing.assert_allclose(
                        reference.scores, direct.scores, atol=2e-8, rtol=2e-8)
                    for j, (lam, score) in enumerate(zip(reference.grid,
                                                          reference.scores)):
                        scores.append({
                            "n": n, "d": d, "mu": mu, "criterion": criterion,
                            "index": j, "lambda": float(lam),
                            "S": float(targets[j]), "score": float(score),
                            "finite": bool(np.isfinite(score)),
                        })
                    # Warm up every route before randomized timing blocks.
                    for policy in POLICIES:
                        choose(model, y, criterion, mu, policy,
                               penalties, targets, log_grid)
                    duration = {p: [] for p in POLICIES}
                    for repeat in range(repeats):
                        order = np.random.default_rng(
                            seed + repeat + n*100 + d*10 +
                            CRITERIA.index(criterion)).permutation(POLICIES)
                        for policy in order:
                            t0 = perf_counter()
                            choose(model, y, criterion, mu, policy,
                                   penalties, targets, log_grid)
                            duration[policy].append(perf_counter() - t0)
                    for policy in POLICIES:
                        selected = choose(model, y, criterion, mu, policy,
                                          penalties, targets, log_grid)
                        arr = np.array(duration[policy])
                        results.append({
                            "n": n, "d": d, "mu": mu, "criterion": criterion,
                            "policy": policy, "M": len(targets),
                            "repeats": repeats,
                            "selection_median_s": float(np.median(arr)),
                            "selection_MAD_s": float(np.median(
                                abs(arr-np.median(arr)))),
                            "lambda_selected": selected.lambda_,
                            "S_selected": selected.smoothness,
                            "score_selected": selected.score,
                            "candidate_count": len(selected.grid),
                            "finite_candidates": int(
                                np.isfinite(selected.scores).sum()),
                        })
            print(f"[selection] n={n} d={d}: {len(CRITERIA)} criteria, "
                  "two mu values, 3 candidate policies; parity verified",
                  flush=True)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    def write(name, records):
        with (out/name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    write("selector_timings.csv", results)
    write("criterion_score_paths.csv", scores)
    write("coordinate_grids.csv", grid_rows)
    write("setup_times.csv", constructors)
    (out/"environment.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Generated {len(results)} measured selector rows and "
          f"{len(scores)} criterion curve points in {out}")
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset",choices=("smoke","quick","full"),
                        default="quick")
    parser.add_argument("--repeats",type=int,default=5)
    parser.add_argument("--threads",type=int,default=1)
    parser.add_argument("--seed",type=int,default=20261026)
    parser.add_argument("--output-dir",type=Path,
                        default=HERE/"selection_coordinate_reference")
    args=parser.parse_args()
    study(args.preset,args.repeats,args.threads,args.seed,args.output_dir)


if __name__=="__main__":
    main()
