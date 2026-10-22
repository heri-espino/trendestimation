"""MANUAL benchmark: separate spectral setup, full fits and criterion evaluation.

Usage:
    python benchmarks/profile_solver_costs.py --n 32 64 128 --order 2
    python benchmarks/profile_solver_costs.py --n 32 64 --order 3 --output results.json

This script never runs in automatic CI and never writes a file unless --output
is explicitly supplied. Its dense SVD and banded implementations have different
one-time and repeated-work cost profiles. Timings are machine-specific.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from math import comb
from pathlib import Path
from statistics import median
from time import perf_counter

import numpy as np
import scipy
from scipy.linalg import solve_banded

from trendestimation import TrendSmoother, select_lambda


def penalty_bands(n: int, d: int) -> np.ndarray:
    """Directly assemble D.T @ D in banded storage, avoiding dense Q."""
    if not (0 <= d < n):
        raise ValueError("Require 0 <= order < n.")
    weights = [(-1) ** (d - i) * comb(d, i) for i in range(d + 1)]
    bands = np.zeros((2 * d + 1, n))
    for row in range(n - d):
        for a, wa in enumerate(weights):
            i = row + a
            for b, wb in enumerate(weights):
                j = row + b
                bands[d + i - j, j] += wa * wb
    return bands


def banded_fit(y: np.ndarray, bands: np.ndarray, lam: float) -> np.ndarray:
    """Solve SPD normal equations in general-band storage for mu=0."""
    d = (bands.shape[0] - 1) // 2
    system = lam * bands
    system[d, :] += 1.0
    return solve_banded((d, d), system, y, check_finite=False)


def elapsed_median(action, repeats: int) -> float:
    """Median elapsed seconds over independent, sequential invocations."""
    values = []
    for _ in range(repeats):
        tic = perf_counter()
        action()
        values.append(perf_counter() - tic)
    return float(median(values))


def profile(n: int, d: int, candidates: int, repeats: int, seed: int) -> dict:
    if n <= d or candidates < 1 or repeats < 1:
        raise ValueError("Require n > order, candidates >= 1, repeats >= 1.")
    y = np.random.default_rng(seed + n + d).standard_normal(n)
    lambdas = np.geomspace(1e-5, 1e3, candidates)
    spectral_setup = elapsed_median(lambda: TrendSmoother(n, d), repeats)
    banded_setup = elapsed_median(lambda: penalty_bands(n, d), repeats)
    spectral = TrendSmoother(n, d)
    bands = penalty_bands(n, d)

    # Compare equivalent tasks: full reconstructed trend for each candidate.
    spectral_fits = elapsed_median(
        lambda: [spectral.fit(y, lambda_=float(lam)).trend for lam in lambdas],
        repeats,
    )
    banded_fits = elapsed_median(
        lambda: [banded_fit(y, bands, float(lam)) for lam in lambdas],
        repeats,
    )

    # Distinct tasks, reported separately: O(n) spectral EDF (after SVD)
    # and gridwise GCV with one reusable projection.
    traces = elapsed_median(
        lambda: [spectral.degrees_of_freedom(float(lam)) for lam in lambdas],
        repeats,
    )
    gcv = elapsed_median(
        lambda: select_lambda(spectral, y, criterion="gcv", mu=0.0, grid=lambdas),
        repeats,
    )
    max_abs = max(
        float(np.max(np.abs(
            spectral.fit(y, lambda_=float(lam)).trend
            - banded_fit(y, bands, float(lam))
        )))
        for lam in lambdas
    )
    return {
        "n": n,
        "order": d,
        "evaluations": candidates,
        "repetitions": repeats,
        "seed": seed,
        "spectral_setup_seconds_median": spectral_setup,
        "banded_setup_seconds_median": banded_setup,
        "spectral_full_fits_seconds_median": spectral_fits,
        "banded_full_fits_seconds_median": banded_fits,
        "spectral_setup_plus_fits_seconds": spectral_setup + spectral_fits,
        "banded_setup_plus_fits_seconds": banded_setup + banded_fits,
        "spectral_edf_grid_seconds_median": traces,
        "spectral_gcv_grid_seconds_median": gcv,
        "maximum_absolute_spectral_banded_disagreement": max_abs,
        "agreement_within_1e-6": max_abs <= 1e-6,
        "stored_spectral_arrays_bytes": sum(
            arr.nbytes for arr in (
                spectral.D, spectral.eigenvectors, spectral.eigenvalues,
                spectral._basis_squares,
            )
        ),
        "stored_banded_penalty_bytes": bands.nbytes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", nargs="+", type=int, default=[32, 64, 128])
    parser.add_argument("--order", type=int, default=2)
    parser.add_argument("--evaluations", type=int, default=20)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    results = {
        "description": "Full trend reconstruction comparisons and separate EDF/GCV operations",
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
        },
        "cases": [
            profile(n, args.order, args.evaluations, args.repetitions, args.seed)
            for n in args.n
        ],
        "interpretation": (
            "Timings are medians, not complexity proofs. Full fit comparisons "
            "include reused solver state but not one-time construction. "
            "Setup-plus-fits adds them. EDF/GCV are different operations and "
            "must not be compared to full reconstruction as equivalent work. "
            "Reported byte counts cover explicitly stored arrays, not total "
            "process RSS or temporary LAPACK memory. "
            "Run with controlled BLAS threads for repeatability."
        ),
    }
    encoded = json.dumps(results, indent=2)
    print(encoded)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    return 0 if all(c["agreement_within_1e-6"] for c in results["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
