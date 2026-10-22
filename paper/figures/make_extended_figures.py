"""Reproduce the observed-data figure and independent joint-mu checks.

Run from the root of trendestimation:
    python -m pip install -e .
    python -m pip install statsmodels pandas
    python paper/figures/make_extended_figures.py

The bundled statsmodels historical CO2 dataset is used offline.
This does not implement a public joint-MLE API or a forecasting model.
"""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import binom
from trendestimation import TrendSmoother

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent


def mu_profile(sm: TrendSmoother, y: np.ndarray, lam: float) -> float:
    """GLS mu given lambda, after eliminating unpenalized coordinates."""
    if sm.order < 1 or lam <= 0:
        raise ValueError("Require d >= 1 and lambda > 0.")
    r = sm.n - sm.order
    V = sm.eigenvectors[:, :r]
    b = V.T @ binom(np.arange(sm.n, dtype=float), sm.order)
    z = V.T @ y
    delta = sm.eigenvalues[:r]
    w = (np.ones(r) if np.isinf(lam)
         else (lam * delta) / (1.0 + lam * delta))
    return float(np.dot(w * b, z) / np.dot(w * b, b))


def joint_profile_score(sm: TrendSmoother, y: np.ndarray, lam: float) -> float:
    """Concentrated marginal Gaussian likelihood score, smaller is better."""
    if lam <= 0:
        return float("inf")
    r = sm.n - sm.order
    V = sm.eigenvectors[:, :r]
    z = V.T @ y
    b = V.T @ binom(np.arange(sm.n, dtype=float), sm.order)
    delta = sm.eigenvalues[:r]
    log_c = (np.zeros(r) if np.isinf(lam)
             else np.logaddexp(0.0, -np.log(lam) - np.log(delta)))
    w = np.exp(-log_c)
    mu = float(np.dot(w * b, z) / np.dot(w * b, b))
    rss = float(np.sum(w * (z - b * mu)**2))
    return float(r * np.log(rss / r) + np.sum(log_c)) if rss > 0 else float("inf")


def main() -> None:
    import statsmodels.api as statsmodels

    # Historical physical measurement data bundled with statsmodels.
    weekly = statsmodels.datasets.co2.load_pandas().data["co2"]
    monthly = weekly.loc["1990":"1999"].resample("MS").mean()
    missing = int(monthly.isna().sum())
    if missing:
        monthly = monthly.interpolate(limit_direction="both")
    y = monthly.to_numpy(float)
    n = len(y)
    assert n == 120 and np.all(np.isfinite(y))
    year = monthly.index.year.to_numpy() + (monthly.index.month.to_numpy() - 1) / 12

    profiles = {}
    penalties = {}
    for d in (2, 3, 4, 5):
        model = TrendSmoother(n, d)
        lam = model.lambda_for_smoothness(0.86)
        profiles[d] = model.fit(y, lambda_=lam, mu=0.).trend
        penalties[d] = float(lam)
    with (HERE / "mauna_loa_1990_1999.dat").open("w") as handle:
        handle.write("year observed d2 d3 d4 d5\n")
        for i in range(n):
            values = [year[i], y[i]] + [profiles[d][i] for d in (2, 3, 4, 5)]
            handle.write(" ".join(f"{float(v):.10g}" for v in values) + "\n")

    model = TrendSmoother(n, 2)
    plug_in = float(np.mean(model.D @ y))
    profiled = mu_profile(model, y, penalties[2])
    optimum = minimize_scalar(
        lambda t: joint_profile_score(model, y, float(np.exp(t))),
        bounds=(-12, 18),
        method="bounded",
        options={"xatol": 1e-7},
    )

    checks = []
    for d in (1, 2, 3, 5):
        rng = np.random.default_rng(400 + d)
        observed = rng.normal(size=50)
        reference = TrendSmoother(50, d)
        D = reference.D
        m, lam = 50 - d, 27.
        mu = mu_profile(reference, observed, lam)
        # Solve the joint normal equations in (tau, mu), independently.
        system = np.zeros((51, 51))
        system[:50, :50] = np.eye(50) + lam * (D.T @ D)
        system[:50, 50] = -lam * D.T @ np.ones(m)
        system[50, :50] = -lam * np.ones(m) @ D
        system[50, 50] = lam * m
        direct = np.linalg.solve(system, np.r_[observed, 0.])
        spectral = reference.fit(observed, lambda_=lam, mu=mu).trend
        checks.append({
            "d": d, "mean_error": float(abs(direct[-1] - mu)),
            "trend_error_max": float(np.max(np.abs(direct[:50] - spectral))),
        })
    if max(r["trend_error_max"] for r in checks) > 1e-7:
        raise AssertionError("Joint profile and normal equations disagree")

    report = {
        "dataset": "statsmodels.datasets.co2; Mauna Loa historical weekly CO2",
        "period": "1990-01 to 1999-12", "n_months": n,
        "missing_months_interpolated": missing,
        "normalized_target_smoothness": 0.86,
        "lambda_by_d": penalties, "mu_data_d2": plug_in,
        "mu_profile_d2_at_controlled_lambda": profiled,
        "joint_mle_lambda_interval": [float(np.exp(-12)), float(np.exp(18))],
        "joint_mle_candidate_lambda": float(np.exp(optimum.x)),
        "joint_mle_candidate_mu": mu_profile(model, y, float(np.exp(optimum.x))),
        "joint_mle_local_optimization_success": bool(optimum.success),
        "independent_normal_equation_checks": checks,
        "limits": "in-sample historical illustration; no forecast evaluation",
    }
    (PAPER / "real_data_summary.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
