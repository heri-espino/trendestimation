"""Reproducible, SVD-amortized benchmark of spectral smoothness inversion.

Run manually: python benchmarks/smoothness_root_solvers.py --repeats 30
Optional: --output build/root_solvers.csv. This script never runs in CI.
Function evaluations include bracketing and final verification. Measured
iteration counts are solver iterations (0 for analytical inverses).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean
from time import perf_counter_ns

import numpy as np

from trendestimation import TrendSmoother

METHODS = ("auto", "brentq", "newton", "secant", "bisect")
TARGETS = (
    1e-14, 1e-10, 1e-6, 0.01, 0.1, 0.5, 0.9, 0.99,
    1 - 1e-6, 1 - 1e-10, 1 - 1e-14,
)


def measure(smoother: TrendSmoother, target: float, method: str, repeats: int) -> dict:
    """Time inversion only; one already-constructed smoother is reused."""
    elapsed = []
    iterations = []
    evaluations = []
    derivatives = []
    absolute_errors = []
    relative_errors = []
    failures = 0
    for _ in range(repeats):
        start = perf_counter_ns()
        try:
            lam = smoother.lambda_for_smoothness(target, method=method)
            elapsed.append((perf_counter_ns() - start) / 1000)
            stat = smoother._last_smoothness_root_diagnostics
            iterations.append(stat["iterations"])
            evaluations.append(stat["function_evaluations"])
            derivatives.append(stat["derivative_evaluations"])
            # Complementary evaluation avoids 1-S cancellation near the upper end.
            high = target > 0.5
            tail = 1 - target if high else target
            recovered = smoother._smoothness_log_value(np.log(lam), complement=high)
            absolute_errors.append(abs(tail - recovered))
            relative_errors.append(abs(tail - recovered) / tail)
        except (ArithmeticError, RuntimeError, ValueError, OverflowError):
            failures += 1
    return {
        "method": method,
        "target": format(target, ".17g"),
        "repeats": repeats,
        "failures": failures,
        "mean_microseconds": mean(elapsed) if elapsed else float("nan"),
        "mean_iterations": mean(iterations) if iterations else float("nan"),
        "mean_function_evaluations": mean(evaluations) if evaluations else float("nan"),
        "mean_derivative_evaluations": mean(derivatives) if derivatives else float("nan"),
        "max_absolute_tail_error": max(absolute_errors, default=float("nan")),
        "max_relative_tail_error": max(relative_errors, default=float("nan")),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", default="30,60,120")
    parser.add_argument("--orders", default="0,1,2,3")
    parser.add_argument("--repeats", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repeats <= 0:
        parser.error("--repeats must be positive")
    rows = []
    for n in map(int, args.sizes.split(",")):
        for d in map(int, args.orders.split(",")):
            if not 0 <= d < n:
                continue
            beginning = perf_counter_ns()
            smoother = TrendSmoother(n, order=d)
            setup_ms = (perf_counter_ns() - beginning) / 1e6
            print(f"n={n:3d} d={d}: one-time SVD setup {setup_ms:.2f} ms")
            for target in TARGETS:
                for method in METHODS:
                    record = measure(smoother, target, method, args.repeats)
                    record.update(n=n, d=d, svd_setup_ms=setup_ms)
                    rows.append(record)
    print("\nMethod        Calls   Failures   Mean us   Mean iterations   Max relative tail error")
    for method in METHODS:
        group = [r for r in rows if r["method"] == method]
        print(
            f"{method:10} {sum(r['repeats'] for r in group):6d} "
            f"{sum(r['failures'] for r in group):10d} "
            f"{mean(r['mean_microseconds'] for r in group):9.2f} "
            f"{mean(r['mean_iterations'] for r in group):17.2f} "
            f"{max(r['max_relative_tail_error'] for r in group):23.3g}"
        )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nWrote detailed benchmark: {args.output}")


if __name__ == "__main__":
    main()
