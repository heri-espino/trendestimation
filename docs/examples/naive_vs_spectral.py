"""Reproducible dense-naive versus cached-spectral PLS benchmark.

Run from the repository root, after installing trendestimation:

    python docs/examples/naive_vs_spectral.py
    python docs/examples/naive_vs_spectral.py --repeats 5 --csv build/naive-vs-spectral.csv

This is a small, manual-only benchmark: literal leave-one-out dense
refitting has O(n^4) complexity. Deleting an observation removes its
data-fidelity weight; it never shortens the time grid or penalty.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import median
from time import perf_counter

import numpy as np

from trendestimation import TrendSmoother, difference_matrix, select_lambda


def explicit_loo_scores(y: np.ndarray, q: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Naive exact CV: n separate dense least-squares solves per penalty."""
    n = y.size
    scores = []
    for lam in grid:
        errors = np.empty(n)
        for i in range(n):
            weights = np.ones(n)
            weights[i] = 0.0
            # With fixed mu=0: (W_i + lambda Q) tau = W_i y.
            system = lam * q + np.diag(weights)
            fitted = np.linalg.solve(system, weights * y)
            errors[i] = y[i] - fitted[i]
        scores.append(float(np.mean(errors**2)))
    return np.asarray(scores)


def dense_hat_gcv_scores(y: np.ndarray, q: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Naive GCV: explicitly construct a full dense hat matrix per penalty."""
    n = y.size
    identity = np.eye(n)
    scores = []
    for lam in grid:
        hat = np.linalg.solve(identity + lam * q, identity)
        residual = y - hat @ y
        denom = 1.0 - np.trace(hat) / n
        scores.append(float(np.mean(residual**2) / denom**2))
    return np.asarray(scores)


def measured_seconds(call, repeats: int) -> float:
    """Warm up and report median elapsed wall time, excluding SVD setup."""
    call()
    samples = []
    for _ in range(repeats):
        start = perf_counter()
        call()
        samples.append(perf_counter() - start)
    return median(samples)


def run_case(n: int, grid: np.ndarray, repeats: int) -> list[dict[str, float | str | int]]:
    rng = np.random.default_rng(2026 + n)
    t = np.linspace(0.0, 1.0, n)
    y = 0.25 + 0.6 * t + np.sin(2 * np.pi * t) + rng.normal(0, 0.2, n)
    d = 2
    diff = difference_matrix(n, d)
    q = diff.T @ diff

    start = perf_counter()
    smoother = TrendSmoother(n, order=d)
    setup_ms = (perf_counter() - start) * 1000.0

    cases = (
        ("cv", explicit_loo_scores, "n full refits"),
        ("gcv", dense_hat_gcv_scores, "dense hat matrix"),
    )
    results = []
    for criterion, naive_score, baseline in cases:
        # An explicit grid forces the same candidates; no optimization
        # strategy differences. The selector reuses its spectral projection.
        def spectral():
            return select_lambda(
                smoother, y, criterion=criterion, mu=0.0,
                grid=grid, method="grid",
            ).scores

        def naive():
            return naive_score(y, q, grid)

        expected = naive()
        observed = spectral()
        if not np.allclose(expected, observed, rtol=2e-6, atol=1e-8):
            raise AssertionError(
                f"{criterion} n={n}: spectral and naive scores disagree: "
                f"max diff={np.max(np.abs(expected - observed))}"
            )
        spectral_s = measured_seconds(spectral, repeats)
        naive_s = measured_seconds(naive, repeats)
        results.append({
            "n": n,
            "criterion": criterion.upper(),
            "naive_baseline": baseline,
            "penalties": len(grid),
            "svd_setup_ms": setup_ms,
            "spectral_selection_ms": spectral_s * 1000.0,
            "naive_selection_ms": naive_s * 1000.0,
            "naive_over_spectral": naive_s / spectral_s,
            "max_abs_score_difference": float(np.max(np.abs(expected - observed))),
        })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[20, 32, 48])
    parser.add_argument("--penalties", nargs="+", type=float,
                        default=[0.5, 5.0, 50.0, 500.0])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--csv", type=Path, help="Optional machine-readable results")
    args = parser.parse_args()
    if any(n < 4 for n in args.sizes) or args.repeats < 1:
        parser.error("All series sizes must be >= 4; repeats must be positive.")
    grid = np.asarray(args.penalties, dtype=float)
    if grid.size == 0 or np.any(~np.isfinite(grid)) or np.any(grid <= 0):
        parser.error("Provide strictly positive, finite penalty candidates.")
    print("Synthetic data; d=2, fixed mu=0, identical penalty grids")
    print("SVD setup is reported separately, not included in selection timings.")
    print("| n | criterion | SVD setup (ms) | spectral grid (ms) | naive grid (ms) | naive / spectral | max score diff |")
    print("|---:|:---|---:|---:|---:|---:|---:|")
    rows = []
    for n in args.sizes:
        for row in run_case(n, grid, args.repeats):
            rows.append(row)
            print(
                f"| {n} | {row['criterion']} | {row['svd_setup_ms']:.3f} "
                f"| {row['spectral_selection_ms']:.3f} "
                f"| {row['naive_selection_ms']:.3f} "
                f"| {row['naive_over_spectral']:.2f}x "
                f"| {row['max_abs_score_difference']:.2e} |"
            )
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved: {args.csv}")


if __name__ == "__main__":
    main()
