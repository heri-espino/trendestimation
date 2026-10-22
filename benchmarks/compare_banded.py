"""Manual benchmark: reusable full SVD versus direct banded construction/solve.

Run from repository root:
    python benchmarks/compare_banded.py

This is illustrative; compare end-to-end setup and repeated-fit time,
check numerical parity, and repeat on the reported host. No heavy
benchmark is triggered automatically in CI or documentation updates.
"""
from __future__ import annotations

from math import comb
from time import perf_counter

import numpy as np
from scipy.linalg import solve_banded

from trendestimation import TrendSmoother


def make_banded_system(n: int, d: int) -> np.ndarray:
    """Build D.T @ D directly in banded representation, no dense n×n matrix."""
    if not 1 <= d < n:
        raise ValueError("Require 1 <= d < n")
    coefficients = [(-1) ** (d - j) * comb(d, j) for j in range(d + 1)]
    ab = np.zeros((2 * d + 1, n))
    for r in range(n - d):
        for a, ca in enumerate(coefficients):
            i = r + a
            for b, cb in enumerate(coefficients):
                j = r + b
                ab[d + i - j, j] += ca * cb
    return ab


def banded_fit(y: np.ndarray, penalty_bands: np.ndarray, lam: float) -> np.ndarray:
    d = (penalty_bands.shape[0] - 1) // 2
    ab = lam * penalty_bands.copy()
    ab[d] += 1.
    return solve_banded((d, d), ab, y, overwrite_ab=True, check_finite=False)


def run(n: int = 160, order: int = 2, evaluations: int = 100) -> None:
    if order < 1 or order >= n or evaluations < 1:
        raise ValueError("Require 1 <= order < n and evaluations >= 1")
    y = np.random.default_rng(120).normal(size=n)
    lambdas = np.geomspace(1e-5, 1e4, evaluations)
    t0 = perf_counter()
    spectral = TrendSmoother(n, order)
    spectral_setup = perf_counter() - t0
    t1 = perf_counter()
    bands = make_banded_system(n, order)
    banded_setup = perf_counter() - t1

    t2 = perf_counter()
    spectral_fits = [spectral.fit(y, lambda_=float(lam)).trend for lam in lambdas]
    spectral_time = perf_counter() - t2
    t3 = perf_counter()
    banded_fits = [banded_fit(y, bands, float(lam)) for lam in lambdas]
    banded_time = perf_counter() - t3
    error = max(float(np.max(np.abs(a - b)))
                for a, b in zip(spectral_fits, banded_fits))

    print(f"n={n}; d={order}; number of lambdas={evaluations}")
    print(f"spectral setup: {spectral_setup:.6f}s; fitting: {spectral_time:.6f}s")
    print(f"banded setup:   {banded_setup:.6f}s; fitting: {banded_time:.6f}s")
    print(f"spectral end-to-end: {spectral_setup+spectral_time:.6f}s")
    print(f"banded end-to-end:   {banded_setup+banded_time:.6f}s")
    print(f"maximum absolute trend disagreement: {error:.4g}")
    print("Host-dependent times; do not infer universal spectral superiority.")
    if not np.isfinite(error) or error > 1e-6:
        raise AssertionError("Spectral and banded solutions disagree.")


if __name__ == "__main__":
    run()
