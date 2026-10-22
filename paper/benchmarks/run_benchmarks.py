"""Paper-only reproducible comparison of naive dense, cached dense, spectral, banded PLS.

From repository root:
  python paper/benchmarks/run_benchmarks.py --preset quick --repeats 5
  python paper/benchmarks/run_benchmarks.py --preset full --repeats 7

Measurements are host-specific wall-clock seconds. We include factorization/setup,
repeat the complete workloads, verify numerical parity, and export machine metadata.
Heavy experiments are never run by ordinary CI or package imports.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
from contextlib import nullcontext
from datetime import datetime, timezone
from math import comb
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from scipy.linalg import solve_banded
from trendestimation import TrendSmoother

try:
    from threadpoolctl import threadpool_info, threadpool_limits
except ImportError:
    threadpool_info = lambda: []
    threadpool_limits = None

HERE = Path(__file__).resolve().parent
METHODS = ("dense_fresh", "dense_cached", "spectral", "banded")


def forward_differences(n: int, d: int) -> np.ndarray:
    """Independent finite difference stencil, including binomial coefficients."""
    if not 1 <= d < n:
        raise ValueError("Require 1 <= d < n.")
    D = np.zeros((n - d, n))
    for j in range(d + 1):
        t = np.arange(n - d)
        D[t, t + j] = (-1)**(d - j) * comb(d, j)
    return D


def directly_banded_penalty(n: int, d: int) -> np.ndarray:
    """Construct D.T @ D in banded storage WITHOUT materializing dense Q."""
    coeffs = [(-1)**(d - j) * comb(d, j) for j in range(d + 1)]
    bands = np.zeros((2*d + 1, n))
    for start in range(n-d):
        for a, ca in enumerate(coeffs):
            for b, cb in enumerate(coeffs):
                i, j = start + a, start + b
                bands[d + i - j, j] += ca*cb
    return bands


def dense_fit(y, Q, shift, lam):
    return np.linalg.solve(np.eye(y.size) + lam*Q, y + lam*shift)


def banded_fit(y, ab, shift, lam, d):
    system = lam*ab.copy()
    system[d] += 1.
    return solve_banded((d, d), system, y+lam*shift,
                        overwrite_ab=True, check_finite=False)


def make_fitter(method, y, d, mu):
    """Factory time is setup; closure execution time is a candidate fit."""
    n = len(y)
    if method == "dense_fresh":
        def solve(lam):
            D = forward_differences(n, d)
            shift = mu*(D.T @ np.ones(n-d))
            return dense_fit(y, D.T @ D, shift, lam)
        return solve
    if method == "dense_cached":
        D = forward_differences(n, d)
        Q = D.T @ D
        shift = mu*(D.T @ np.ones(n-d))
        return lambda lam: dense_fit(y, Q, shift, lam)
    if method == "spectral":
        model = TrendSmoother(n, order=d)
        return lambda lam: model.fit(y, lambda_=lam, mu=mu).trend
    if method == "banded":
        ab = directly_banded_penalty(n, d)
        # Accumulate D.T @ (mu * ones) without materializing a dense D.
        shift = np.zeros(n)
        for start in range(n-d):
            for k in range(d+1):
                shift[start+k] += mu * (-1)**(d-k) * comb(d,k)
        return lambda lam: banded_fit(y, ab, shift, lam, d)
    raise ValueError(f"Unknown method: {method}")


def measure(n, d, m, mu, seed, repeats):
    y = np.random.default_rng(seed).normal(size=n)
    lam_grid = np.geomspace(1e-3, 1e3, m)
    # Correctness checks are deliberately excluded from timed regions.
    ref = make_fitter("banded", y, d, mu)
    truths = [ref(float(lam)) for lam in lam_grid]
    errors = {}
    for method in METHODS:
        f = make_fitter(method, y, d, mu)
        errors[method] = float(max(
            np.max(np.abs(f(float(lam)) - target))
            for lam, target in zip(lam_grid, truths)
        ))
    if not np.isfinite(max(errors.values())) or max(errors.values()) > 3e-6:
        raise AssertionError(f"Numerical disagreement: n={n}, d={d}, m={m}, mu={mu}: {errors}")
    records = []
    for method in METHODS:
        samples = []
        for _ in range(repeats):
            start = perf_counter()
            f = make_fitter(method, y, d, mu)
            setup_s = perf_counter() - start
            start = perf_counter()
            for lam in lam_grid:
                f(float(lam))
            fit_s = perf_counter() - start
            samples.append((setup_s, fit_s))
        a = np.asarray(samples)
        total = a.sum(axis=1)
        records.append({
            "n": n, "d": d, "M": m, "mu": mu,
            "seed": seed, "method": method, "repeats": repeats,
            "setup_median_s": float(np.median(a[:, 0])),
            "fits_median_s": float(np.median(a[:, 1])),
            "total_median_s": float(np.median(total)),
            "total_min_s": float(np.min(total)),
            "total_max_s": float(np.max(total)),
            "total_MAD_s": float(np.median(np.abs(total-np.median(total)))),
            "max_error_banded": errors[method],
        })
    return records


def workloads(preset):
    if preset == "smoke":
        return [(30, 2, 1, 0.), (50, 2, 12, 0.), (50, 3, 12, .1)]
    if preset == "quick":
        return (
            [(n, 2, m, 0.) for n in (40, 100, 180) for m in (1, 16, 64)]
            + [(100, d, 24, 0.) for d in (1, 3, 5)]
            + [(100, 2, 24, .15)]
        )
    if preset == "full":
        return (
            [(n, 2, m, 0.) for n in (40, 100, 200, 400)
             for m in (1, 16, 64, 256)]
            + [(200, d, 64, 0.) for d in (1, 3, 5, 7)]
            + [(200, 2, 64, .15)]
        )
    raise ValueError(preset)


def save(folder, rows, settings):
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "full_fit_timings.csv").open("w", newline="", encoding="utf-8") as f:
        out = csv.DictWriter(f, fieldnames=list(rows[0]))
        out.writeheader()
        out.writerows(rows)
    groups = {}
    for r in rows:
        groups.setdefault((r["n"], r["d"], r["M"], r["mu"]), {})[r["method"]] = r
    with (folder / "full_fit_speedups.csv").open("w", newline="", encoding="utf-8") as f:
        out = csv.writer(f)
        out.writerow(["n", "d", "M", "mu", "dense_fresh_over_spectral",
                      "dense_cached_over_spectral", "banded_over_spectral"])
        for (n, d, m, mu), group in sorted(groups.items()):
            spectral = group["spectral"]["total_median_s"]
            out.writerow([n, d, m, mu] + [
                group[name]["total_median_s"]/spectral
                for name in ("dense_fresh", "dense_cached", "banded")
            ])
    (folder / "environment.json").write_text(
        json.dumps(settings, indent=2), encoding="utf-8"
    )
    # One file per observation for native PGFplots rendering.
    with (folder / "full_fit_at_M64.dat").open("w", encoding="utf-8") as f:
        f.write("n densefresh densecached spectral banded\n")
        for (n, d, m, mu), group in sorted(groups.items()):
            if d == 2 and mu == 0. and m == 64:
                f.write(f"{n} " + " ".join(
                    f"{group[name]['total_median_s']:.10g}" for name in METHODS
                ) + "\n")
    with (folder / "full_fit_plot.dat").open("w", encoding="utf-8") as f:
        f.write("n M densefresh densecached spectral banded\n")
        for (n, d, m, mu), group in sorted(groups.items()):
            if d == 2 and mu == 0. and m in (1, 16, 64):
                f.write(f"{n} {m} " + " ".join(
                    f"{group[name]['total_median_s']:.10g}"
                    for name in METHODS
                ) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("smoke", "quick", "full"), default="quick")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20261021)
    parser.add_argument("--blas-threads", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE / "results")
    args = parser.parse_args(argv)
    if args.repeats < 1 or args.blas_threads < 1:
        parser.error("repeats and blas-threads must be positive")
    ctx = threadpool_limits(limits=args.blas_threads) if threadpool_limits else nullcontext()
    metadata = {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "system": platform.platform(), "processor": platform.processor(),
        "logical_cpus": os.cpu_count(), "python": sys.version,
        "numpy": np.__version__, "scipy": scipy.__version__,
        "blas_threads": args.blas_threads,
        "git_revision": os.environ.get("GITHUB_SHA", "local-unrecorded"),
        "preset": args.preset, "repeats": args.repeats,
        "note": "Includes setup and M full trends, compared at identical lambdas. No energy/GPU measurements.",
        "models": {
            "dense_fresh": "rebuild D/Q and solve dense linear system per lambda; O(M n^3)",
            "dense_cached": "build dense Q once, solve dense linear system per lambda; O(M n^3)",
            "spectral": "full SVD O(n^3) once, O(n^2) memory, full fit O(M n^2)",
            "banded": "direct banded penalty assembly O(nd^2), banded solve O(Mnd^2) for fixed d",
        },
    }
    rows = []
    with ctx:
        metadata["threadpools"] = threadpool_info()
        configs = workloads(args.preset)
        for idx, (n, d, m, mu) in enumerate(configs, 1):
            print(f"[{idx}/{len(configs)}] n={n}, d={d}, M={m}, mu={mu}", flush=True)
            current = measure(n, d, m, mu, args.seed+idx, args.repeats)
            rows.extend(current)
            for item in current:
                print(f"  {item['method']:<14}: {item['total_median_s']:.6g}s", flush=True)
    save(args.output_dir, rows, metadata)
    print(f"All {len(configs)} workloads passed numerical parity. Output: {args.output_dir}")


if __name__ == "__main__":
    main()
