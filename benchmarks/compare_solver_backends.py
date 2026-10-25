"""Repeatable full-trend PLS benchmark: SVD vs eigh(Q) vs banded Cholesky.

From repo root:
    python benchmarks/compare_solver_backends.py --preset smoke --repeats 3
    python benchmarks/compare_solver_backends.py --preset quick --output results.json
    python benchmarks/compare_solver_backends.py --preset full --repeats 7 --threads 1

No benchmark is executed on import, in normal CI, or in a docs build.
The report intentionally distinguishes setup, one fit, repeated full fits,
reused observation projections and long-lived stored-array bytes.
It does not benchmark EDF, CV or profile likelihood as though they were
identical tasks to fitting one full trend.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from time import perf_counter

import numpy as np
import scipy

from trendestimation.solvers import PreparedPLSSolver

try:
    from threadpoolctl import threadpool_info, threadpool_limits
except ImportError:
    threadpool_info = lambda: []  # noqa: E731
    threadpool_limits = None

METHODS = ("svd", "eigh", "cholesky")


def cases_for(preset: str) -> list[tuple[int, int, int, float]]:
    if preset == "smoke":
        return [(24, 1, 1, 0.), (32, 2, 8, 0.1), (36, 3, 16, 0.)]
    if preset == "quick":
        return ([
            (n, 2, m, mu)
            for n in (32, 96, 192)
            for m in (1, 16, 64)
            for mu in (0., 0.15)
        ] + [(96, d, 16, 0.) for d in (1, 3, 5)])
    if preset == "full":
        return ([
            (n, 2, m, mu)
            for n in (32, 64, 128, 256, 512)
            for m in (1, 16, 64, 256)
            for mu in (0., 0.15)
        ] + [(256, d, 64, 0.) for d in (1, 3, 5)])
    raise ValueError(f"Unknown benchmark preset: {preset}")


def _time(callable_):
    started = perf_counter()
    result = callable_()
    return perf_counter() - started, result


def measure_case(
    n: int, order: int, count: int, mu: float, seed: int, repeats: int,
) -> list[dict]:
    """One matched workload, independent correctness checks outside timers."""
    rng = np.random.default_rng(seed + n * 17 + order)
    t = np.linspace(0., 1., n)
    y = np.sin(7 * t) + .3 * t + rng.normal(0., .1, n)
    lambdas = np.geomspace(1e-4, 1e4, count)
    baseline = PreparedPLSSolver(n, order, method="svd")
    reference = baseline.fit_many(y, lambdas, mu=mu)
    # The differences are measured against a fresh reference, not the
    # timings, and every candidate is checked, not just the first one.
    measurements: dict[str, list[dict]] = {name: [] for name in METHODS}
    errors: dict[str, float] = {}
    try:
        for method in METHODS:
            fitter = PreparedPLSSolver(n, order, method=method)
            compared = fitter.fit_many(y, lambdas, mu=mu)
            error = float(np.max(np.abs(compared - reference)))
            errors[method] = error
            tolerance = 1e-6 + 1e-7 * float(np.max(np.abs(reference)))
            if not np.isfinite(error) or error > tolerance:
                raise AssertionError(
                    f"Numerical disagreement n={n}, d={order}, M={count}, "
                    f"mu={mu}: {method} error={error}, tolerance={tolerance}"
                )

        for rep in range(repeats):
            # Rotate run order to mitigate systematic warm-cache bias.
            order_for_repetition = METHODS[rep % 3:] + METHODS[:rep % 3]
            for method in order_for_repetition:
                setup, fitter = _time(
                    lambda method=method: PreparedPLSSolver(
                        n, order, method=method,
                    )
                )
                single, _ = _time(
                    lambda: fitter.fit(y, lambda_=float(lambdas[0]), mu=mu)
                )
                repeated, _ = _time(
                    lambda: [
                        fitter.fit(y, lambda_=float(lam), mu=mu)
                        for lam in lambdas
                    ]
                )
                batched, _ = _time(
                    lambda: fitter.fit_many(y, lambdas, mu=mu)
                )
                measurements[method].append({
                    "setup_seconds": setup,
                    "single_fit_seconds": single,
                    "repeated_fit_seconds": repeated,
                    "batched_fit_seconds": batched,
                    "setup_plus_batched_seconds": setup + batched,
                    "stored_bytes": fitter.stored_bytes,
                })
    except (FloatingPointError, np.linalg.LinAlgError) as exc:
        raise RuntimeError(
            f"Numerical backend failed n={n} d={order} M={count}: {exc}"
        ) from exc

    rows = []
    for method in METHODS:
        times = measurements[method]
        rows.append({
            "n": n, "order": order, "evaluations": count,
            "mu": mu, "seed": seed, "repetitions": repeats,
            "method": method, "max_abs_error_vs_svd": errors[method],
            **{
                key + "_median": float(median(row[key] for row in times))
                for key in (
                    "setup_seconds", "single_fit_seconds",
                    "repeated_fit_seconds", "batched_fit_seconds",
                    "setup_plus_batched_seconds", "stored_bytes",
                )
            },
        })
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("smoke", "quick", "full"), default="smoke")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20261025)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    if args.repeats < 1 or args.threads < 1:
        parser.error("repeats and threads must be >= 1")
    context = (
        threadpool_limits(limits=args.threads)
        if threadpool_limits is not None else nullcontext()
    )
    with context:
        rows = []
        for n, d, count, mu in cases_for(args.preset):
            rows.extend(measure_case(
                n, d, count, mu, args.seed, args.repeats,
            ))
        blas = threadpool_info()
    result = {
        "kind": "matched_full_trend_reconstruction",
        "preset": args.preset,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": sys.version.split()[0], "numpy": np.__version__,
            "scipy": scipy.__version__, "platform": platform.platform(),
            "processor": platform.processor(), "blas_threads_requested": args.threads,
            "blas_threadpool_info": blas, "threadpool_control_available": (
                threadpool_limits is not None
            ),
        },
        "methodology": (
            "Identical y, d, mu and penalties across methods. One-time setup, "
            "single fit, repeated individual fits and batched/reused-projection "
            "fits measured separately; medians across repeated runs. "
            "Stored bytes omit temporary BLAS/LAPACK allocations and RSS. "
            "Comparisons do not include tuning CV/GCV/MLE and cannot justify "
            "a universal fastest default. No GPU or energy measurements."
        ),
        "rows": rows,
    }
    encoded = json.dumps(result, indent=2)
    print(encoded)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
