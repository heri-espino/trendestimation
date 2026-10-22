"""Paper-only benchmark for the effective-degrees-of-freedom (trace) profile.

Unlike run_benchmarks.py, this measures tr[(I + lambda D.T D)^(-1)]
for M penalty values. Dense methods solve n RHS vectors at each lambda,
the spectral method sums scalar attenuation factors, and the banded
method solves n RHS vectors using structured factorization. Setup is
included and numerical equivalence is checked outside timed blocks.

Run from the repository root:
    python paper/benchmarks/trace_benchmarks.py --preset quick --repeats 5
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.linalg import solve_banded
from trendestimation import TrendSmoother

try:
    from threadpoolctl import threadpool_limits
except ImportError:
    from contextlib import nullcontext
    threadpool_limits = lambda limits: nullcontext()

from run_benchmarks import forward_differences, directly_banded_penalty

HERE = Path(__file__).resolve().parent
METHODS = ("dense_fresh_trace", "dense_cached_trace", "spectral_trace", "banded_trace")


def make_trace(method, n, d):
    identity = np.eye(n)
    if method == "dense_fresh_trace":
        def evaluate(lam):
            D = forward_differences(n, d)
            return float(np.trace(np.linalg.solve(identity + lam*(D.T@D), identity)))
        return evaluate
    if method == "dense_cached_trace":
        D = forward_differences(n, d)
        Q = D.T@D
        return lambda lam: float(np.trace(np.linalg.solve(identity + lam*Q, identity)))
    if method == "spectral_trace":
        model = TrendSmoother(n, order=d)
        return lambda lam: model.degrees_of_freedom(lam)
    if method == "banded_trace":
        bands = directly_banded_penalty(n, d)
        def evaluate(lam):
            ab = lam*bands.copy()
            ab[d] += 1.
            return float(np.trace(solve_banded((d, d), ab, identity, check_finite=False)))
        return evaluate
    raise ValueError(method)


def benchmark_trace(n, d, m, repeats):
    grid = np.geomspace(1e-3, 1e3, m)
    reference = make_trace("spectral_trace", n, d)
    exact = [reference(float(lam)) for lam in grid]
    records = []
    for method in METHODS:
        fn = make_trace(method, n, d)
        difference = float(max(
            abs(fn(float(lam)) - ans) for lam, ans in zip(grid, exact)
        ))
        if not np.isfinite(difference) or difference > 1e-6:
            raise AssertionError(f"Trace mismatch: {n}, {d}, {m}, {method}, {difference}")
        samples = []
        for _ in range(repeats):
            start = perf_counter()
            f = make_trace(method, n, d)
            setup = perf_counter() - start
            start = perf_counter()
            for lam in grid:
                f(float(lam))
            duration = perf_counter()-start
            samples.append((setup,duration))
        times = np.asarray(samples)
        records.append({
            "n":n, "d":d, "M":m, "method":method, "repeats":repeats,
            "setup_median_s":float(np.median(times[:,0])),
            "trace_evaluation_median_s":float(np.median(times[:,1])),
            "total_median_s":float(np.median(times.sum(axis=1))),
            "max_abs_trace_error":difference,
        })
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("smoke","quick","full"), default="quick")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--blas-threads", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE/"results")
    args = parser.parse_args()
    if args.repeats < 1 or args.blas_threads < 1:
        parser.error("Require positive repeats and threads")
    scenarios = {
        "smoke": [(35,2,8)],
        "quick": [(40,2,8),(100,2,8),(100,2,32),(180,2,32)],
        "full": [(40,2,8),(100,2,8),(100,2,32),(180,2,32),(250,2,64)],
    }[args.preset]
    rows = []
    with threadpool_limits(limits=args.blas_threads):
        for n,d,m in scenarios:
            current = benchmark_trace(n,d,m,args.repeats)
            rows.extend(current)
            print(f"n={n}, d={d}, M={m}: " + ", ".join(
                f"{r['method']}={r['total_median_s']:.5g}s" for r in current
            ), flush=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir/"trace_timings.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (args.output_dir/"trace_plot.dat").open("w",encoding="utf-8") as f:
        f.write("n M densefresh densecached spectral banded\n")
        grouped={}
        for row in rows:
            grouped.setdefault((row["n"],row["M"]),{})[row["method"]]=row
        for (n,m), group in sorted(grouped.items()):
            f.write(f"{n} {m} " + " ".join(
                f"{group[method]['total_median_s']:.10g}" for method in METHODS
            ) + "\n")
    print("Trace profiles agree. Output:",args.output_dir)


if __name__ == "__main__":
    main()
