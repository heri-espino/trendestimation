"""Six-way paper companion benchmark: dense/banded Cholesky and nonzero mu.

Compares identical fixed-mu PLS trends for one grid of finite penalties,
including all four original paper methods without changing their tables.
The two new algorithms are dense Cholesky (cho_factor/cho_solve) and
positive-definite banded Cholesky (cholesky_banded/cho_solve_banded).

For fixed numeric mu, the normal equations are
  (I + lambda D.T D) tau = y + lambda * mu * D.T @ 1 .
Thus mu changes the right hand side, NOT the coefficient matrix,
effective degrees of freedom, or the cost of its factorizations.

From root:
  python paper/benchmarks/cholesky_comparison.py --preset smoke --repeats 2
  python paper/benchmarks/cholesky_comparison.py --preset quick --repeats 5
  python paper/benchmarks/cholesky_comparison.py --preset full --repeats 7
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
from scipy.linalg import cho_factor, cho_solve, cholesky_banded, cho_solve_banded
from threadpoolctl import threadpool_info, threadpool_limits

from run_benchmarks import forward_differences, make_fitter
from trace_benchmarks import make_trace
from trendestimation.solvers import _penalty_lower_bands


HERE = Path(__file__).resolve().parent
METHODS = ("dense_fresh", "dense_cached", "spectral", "banded",
           "dense_cholesky", "banded_cholesky")
TRACE_METHODS = ("dense_fresh_trace", "dense_cached_trace", "spectral_trace",
                 "banded_trace", "dense_cholesky_trace", "banded_cholesky_trace")


def _mu_shift(n: int, d: int, mu: float) -> np.ndarray:
    # Use the EXACT original paper right-hand side for meaningful comparison.
    # No reference-mean estimation or per-fold refitting occurs here.
    D = forward_differences(n, d)
    return float(mu) * (D.T @ np.ones(n - d))


def make_six_fitter(method: str, y: np.ndarray, d: int, mu: float):
    """Prepare a reusable fit function; factorization stays inside each fit."""
    if method in METHODS[:4]:
        return make_fitter(method, y, d, mu)
    n = len(y)
    shift = _mu_shift(n, d, mu)
    if method == "dense_cholesky":
        D = forward_differences(n, d)
        Q = D.T @ D
        identity = np.eye(n)

        def fit(lam):
            matrix = identity + lam * Q
            factor = cho_factor(matrix, lower=True, check_finite=False)
            return cho_solve(factor, y + lam * shift, check_finite=False)

        return fit
    if method == "banded_cholesky":
        bands = _penalty_lower_bands(n, d)

        def fit(lam):
            system = lam * bands.copy()
            system[0] += 1.0
            factor = cholesky_banded(system, lower=True, check_finite=False)
            return cho_solve_banded((factor, True), y + lam * shift,
                                    check_finite=False)

        return fit
    raise ValueError("Unknown method: " + str(method))


def make_six_trace(method: str, n: int, d: int):
    """EDF computation: mu does not appear in tr((I+lambda Q)^-1)."""
    if method in TRACE_METHODS[:4]:
        return make_trace(method, n, d)
    identity = np.eye(n)
    if method == "dense_cholesky_trace":
        D = forward_differences(n, d)
        Q = D.T @ D

        def trace(lam):
            factor = cho_factor(identity + lam * Q, lower=True, check_finite=False)
            return float(np.trace(cho_solve(factor, identity, check_finite=False)))

        return trace
    if method == "banded_cholesky_trace":
        bands = _penalty_lower_bands(n, d)

        def trace(lam):
            system = lam * bands.copy()
            system[0] += 1.0
            factor = cholesky_banded(system, lower=True, check_finite=False)
            return float(np.trace(cho_solve_banded(
                (factor, True), identity, check_finite=False)))

        return trace
    raise ValueError("Unknown trace method: " + str(method))


def fit_workloads(preset):
    if preset == "smoke":
        return [(28, 2, 4, m) for m in (0.0, 0.15)]
    if preset == "quick":
        # Every structural workload is repeated at exactly the same n,d,M
        # for mu=0 and mu=0.15, using the same data seed and penalty grid.
        bases = ((40, 2, 1), (40, 2, 32), (100, 2, 1),
                 (100, 2, 32), (100, 2, 64), (140, 2, 32),
                 (100, 1, 32), (100, 3, 32))
    else:
        bases = ((40, 2, 1), (40, 2, 32), (100, 2, 1),
                 (100, 2, 32), (100, 2, 64), (140, 2, 32),
                 (100, 1, 32), (100, 3, 32),
                 (200, 2, 64), (200, 2, 128),
                 (300, 2, 64), (200, 4, 64))
    return [(n, d, m, mu) for n, d, m in bases for mu in (0.0, 0.15)]


def trace_workloads(preset):
    if preset == "smoke":
        return [(28, 2, 4)]
    if preset == "quick":
        return [(40, 2, 8), (100, 2, 16), (140, 2, 32)]
    return [(40, 2, 8), (100, 2, 16), (140, 2, 32),
            (200, 2, 64), (200, 3, 32)]


def _timed_trials(factory, grid, repeats):
    trials = []
    for _ in range(repeats):
        started = perf_counter()
        solve = factory()
        prepared = perf_counter()
        for lam in grid:
            solve(float(lam))
        finished = perf_counter()
        trials.append((prepared-started, finished-prepared))
    a = np.asarray(trials, dtype=float)
    total = a.sum(axis=1)
    return {
        "setup_median_s": float(np.median(a[:, 0])),
        "evaluation_median_s": float(np.median(a[:, 1])),
        "total_median_s": float(np.median(total)),
        "total_MAD_s": float(np.median(abs(total - np.median(total)))),
    }


def measure_fits(n, d, M, mu, seed, repeats):
    data = np.random.default_rng(seed).normal(size=n)
    grid = np.geomspace(1e-3, 1e3, M)
    baseline = make_fitter("banded", data, d, mu)
    truth = [baseline(float(lam)) for lam in grid]
    results = []
    for method in METHODS:
        f = make_six_fitter(method, data, d, mu)
        error = max(float(np.max(np.abs(f(float(lam))-reference)))
                    for lam, reference in zip(grid, truth))
        if not np.isfinite(error) or error > 3e-6:
            raise AssertionError(f"Fit disagreement at n={n} d={d} M={M} "
                                 f"mu={mu} method={method}: {error}")
        stats = _timed_trials(lambda: make_six_fitter(method, data, d, mu),
                              grid, repeats)
        results.append(dict(
            n=n, d=d, M=M, mu=mu, seed=seed, method=method,
            repeats=repeats, **stats, max_error_banded=error))
    return results


def measure_traces(n, d, M, repeats):
    grid = np.geomspace(1e-3, 1e3, M)
    spectral = make_six_trace("spectral_trace", n, d)
    truth = [spectral(float(lam)) for lam in grid]
    results = []
    for method in TRACE_METHODS:
        f = make_six_trace(method, n, d)
        error = max(abs(f(float(lam)) - target)
                    for lam, target in zip(grid, truth))
        if not np.isfinite(error) or error > 1e-6:
            raise AssertionError(f"Trace disagreement n={n} d={d} M={M} "
                                 f"method={method}: {error}")
        stats = _timed_trials(lambda: make_six_trace(method, n, d),
                              grid, repeats)
        results.append(dict(n=n, d=d, M=M, method=method, repeats=repeats,
                            **stats, max_abs_trace_error=error))
    return results


def _write_csv(path, rows):
    if not rows:
        raise ValueError("No benchmark observations")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(preset="quick", repeats=5, blas_threads=1, seed=20261026,
        output_dir=HERE / "results" / "six_solver"):
    if preset not in ("smoke", "quick", "full"):
        raise ValueError("Unknown preset")
    if repeats < 1 or blas_threads < 1:
        raise ValueError("repeats and BLAS threads must be positive")
    output_dir = Path(output_dir)
    rows = []
    trace_rows = []
    with threadpool_limits(limits=blas_threads):
        metadata = {
            "date_utc": datetime.now(timezone.utc).isoformat(),
            "system": platform.platform(),
            "processor": platform.processor(),
            "logical_cpus": os.cpu_count(),
            "python": sys.version,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "blas_threads": blas_threads,
            "threadpools": threadpool_info(),
            "preset": preset, "repeats": repeats, "seed": seed,
            "git_revision": os.environ.get("GITHUB_SHA", "local-unrecorded"),
            "fit_methods": list(METHODS), "trace_methods": list(TRACE_METHODS),
            "note": ("Measured on this host. Same signal and penalties for paired "
                     "mu=0/0.15 fits; mu does not alter the smoothing matrix. "
                     "The original four-method paper CSVs are untouched."),
        }
        for idx, (n,d,M,mu) in enumerate(fit_workloads(preset), 1):
            # Seed independent of mu, making the contrast paired by design.
            local_seed = seed + 97*n + 13*d + M
            batch = measure_fits(n,d,M,mu,local_seed,repeats)
            rows.extend(batch)
            winner = min(batch, key=lambda r:r["total_median_s"])
            print(f"[fit {idx}/{len(fit_workloads(preset))}] "
                  f"n={n} d={d} M={M} mu={mu:g} "
                  f"winner={winner['method']} "
                  f"{winner['total_median_s']*1e3:.4g}ms", flush=True)
        for idx, (n,d,M) in enumerate(trace_workloads(preset), 1):
            batch = measure_traces(n,d,M,repeats)
            trace_rows.extend(batch)
            winner = min(batch, key=lambda r:r["total_median_s"])
            print(f"[trace {idx}/{len(trace_workloads(preset))}] "
                  f"n={n} d={d} M={M} winner={winner['method']}", flush=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "full_fit_timings.csv", rows)
    _write_csv(output_dir / "trace_timings.csv", trace_rows)
    (output_dir / "environment.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8")
    print("Recorded six-method timing and parity data:", output_dir)
    return rows, trace_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("smoke","quick","full"), default="quick")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--blas-threads", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20261026)
    parser.add_argument("--output-dir", type=Path,
                        default=HERE / "results" / "six_solver")
    args = parser.parse_args()
    run(args.preset, args.repeats, args.blas_threads, args.seed, args.output_dir)


if __name__ == "__main__":
    main()
