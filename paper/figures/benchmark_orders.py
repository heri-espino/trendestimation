"""Reproduce high-order finite-difference numerical diagnostics.

Run from repository root after source installation:
    python paper/figures/benchmark_orders.py

A compact deterministic diagnostic, not a universal accuracy or GPU benchmark.
Outputs data for a log-scale numerical-conditioning figure and records
host-specific optional timing information separately from mathematical claims.
"""
from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from time import perf_counter

import numpy as np
from trendestimation import TrendSmoother

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
N = 50
SEED = 24021
TARGET_S = 0.86
Y = np.random.default_rng(SEED).normal(size=N)


def run() -> None:
    results = []
    for d in range(1, 11):
        start = perf_counter()
        solver = TrendSmoother(N, d)
        setup_seconds = perf_counter() - start

        # Singular values are from an SVD of D_d, not a numerically
        # unstable eigenvalue decomposition of D_d.T @ D_d.
        delta = solver.eigenvalues[:N - d]
        positive_penalty_condition = float(np.max(delta) / np.min(delta))
        lam = solver.lambda_for_smoothness(TARGET_S)
        start = perf_counter()
        spectral = solver.fit(Y, lambda_=lam).trend
        fit_seconds = perf_counter() - start
        direct = np.linalg.solve(np.eye(N) + lam * (solver.D.T @ solver.D), Y)
        disagreement = float(np.max(np.abs(spectral - direct)))

        results.append({
            "d": d,
            "lambda": float(lam),
            "penalty_condition": positive_penalty_condition,
            "max_absolute_direct_disagreement": disagreement,
            "svd_setup_seconds_on_executing_host": setup_seconds,
            "one_spectral_fit_seconds_on_executing_host": fit_seconds,
        })
        if not np.isfinite(disagreement):
            raise RuntimeError("Nonfinite high-order diagnostic")
        print(
            f"d={d:2d}, cond(Q+)={positive_penalty_condition:.4g}, "
            f"lambda={lam:.4g}, direct disagreement={disagreement:.3g}"
        )

    with (HERE / "high_order_numerics.dat").open("w", encoding="utf-8") as handle:
        handle.write("d condition error lambda\n")
        for row in results:
            handle.write(
                f"{row['d']} {row['penalty_condition']:.12g} "
                f"{row['max_absolute_direct_disagreement']:.12g} "
                f"{row['lambda']:.12g}\n"
            )
    report = {
        "status": "bounded deterministic numerical diagnostic",
        "series_length": N,
        "seed": SEED,
        "normalized_smoothness_target": TARGET_S,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_logical": os.cpu_count(),
        "numpy_version": np.__version__,
        "results": results,
    }
    (PAPER / "high_order_summary.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    run()
