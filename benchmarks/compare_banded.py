"""MANUAL benchmark: repeated spectral PLS fits versus banded linear solves.

Use: python packages/trendestimation/benchmarks/compare_banded.py
No simulation campaign is run, and no results are stored automatically.
Measure total/setup and per-candidate times; do not treat numbers from
one machine as universal speed superiority.
"""
from __future__ import annotations

from time import perf_counter
import numpy as np
from scipy.linalg import solve_banded
from trendestimation import TrendSmoother, difference_matrix


def make_banded_system(n: int, d: int) -> np.ndarray:
    """Construct banded storage of D.T @ D once per (n, d)."""
    D = difference_matrix(n, d)
    Q = D.T @ D
    ab = np.zeros((2 * d + 1, n))
    for j in range(n):
        for i in range(max(0, j - d), min(n, j + d + 1)):
            ab[d + i - j, j] = Q[i, j]
    return ab


def banded_fit(y: np.ndarray, penalty_bands: np.ndarray, lam: float) -> np.ndarray:
    d = (penalty_bands.shape[0] - 1) // 2
    ab = lam * penalty_bands
    ab[d, :] += 1.0
    return solve_banded((d, d), ab, y, overwrite_ab=True,
                        check_finite=False)


def run(n: int = 160, order: int = 2, evaluations: int = 100) -> None:
    if order < 1 or order >= n:
        raise ValueError("This banded benchmark assumes 1 <= order < n.")
    y = np.random.default_rng(120).normal(size=n)
    lambdas = np.geomspace(1e-5, 1e4, evaluations)
    t0 = perf_counter()
    smoother = TrendSmoother(n, order)
    spectral_setup = perf_counter() - t0
    t1 = perf_counter()
    bands = make_banded_system(n, order)
    banded_setup = perf_counter() - t1

    t2 = perf_counter()
    spectral = [smoother.fit(y, lambda_=lam).trend for lam in lambdas]
    spectral_time = perf_counter() - t2
    t3 = perf_counter()
    banded = [banded_fit(y, bands, lam) for lam in lambdas]
    banded_time = perf_counter() - t3
    maximum_disagreement = max(
        float(np.max(np.abs(a - b))) for a, b in zip(spectral, banded)
    )
    print(f"n={n} d={order} lambda_evaluations={evaluations}")
    print(f"spectral setup={spectral_setup:.6f}s; fits={spectral_time:.6f}s")
    print(f"banded setup={banded_setup:.6f}s; fits={banded_time:.6f}s")
    print(f"maximum absolute trend difference={maximum_disagreement:.3g}")
    print("Interpret per-candidate time together with one-time setup costs.")


if __name__ == "__main__":
    run()
