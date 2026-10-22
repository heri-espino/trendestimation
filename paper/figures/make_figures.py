"""Regenerate the deterministic SMCCA simulation and numerical checks.

Run from repository root:
    python paper/figures/make_figures.py

Requires: numpy, scipy and an editable installation of trendestimation.
No future/held-out forecasting evaluation or large simulation is performed.
"""
from pathlib import Path
import json

import numpy as np

from trendestimation import TrendSmoother, simulate_cortes_toto, select_lambda

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

case = simulate_cortes_toto(
    n=50, shape="nonlinear", seasonal=False, noise_sd=0.5, seed=19
)
smoother = TrendSmoother(50, order=2)
methods = ("cv", "gcv", "aicc", "bic")
choices = {
    method: select_lambda(smoother, case.observed, criterion=method, mu=0.0)
    for method in methods
}
trends = {
    method: smoother.fit(case.observed, lambda_=choice.lambda_).trend
    for method, choice in choices.items()
}

with (OUT / "cortes_toto_synthetic.dat").open("w", encoding="utf-8") as handle:
    handle.write("t observed true cv gcv aicc bic\n")
    for i in range(50):
        values = [i + 1, case.observed[i], case.trend[i]]
        values.extend(trends[method][i] for method in methods)
        handle.write(" ".join(f"{float(v):.10g}" for v in values) + "\n")

rng = np.random.default_rng(20261021)
y = rng.normal(size=50)
checks = []
for d in (1, 2, 3):
    sm = TrendSmoother(50, order=d)
    for mu in (0.0, 0.15):
        lam = 30.0
        D = sm.D
        direct = np.linalg.solve(
            np.eye(50) + lam * (D.T @ D),
            y + lam * mu * D.T @ np.ones(50 - d),
        )
        spectral = sm.fit(y, lambda_=lam, mu=mu).trend
        limit = sm.fit(y, lambda_=np.inf, mu=mu).trend
        checks.append({
            "d": d, "mu": mu,
            "solver_inf_error": float(np.linalg.norm(spectral - direct, ord=np.inf)),
            "limit_penalty_error": float(np.max(np.abs(D @ limit - mu))),
        })

with (ROOT / "results_summary.json").open("w", encoding="utf-8") as handle:
    json.dump({
        "scenario": {"n": 50, "shape": "nonlinear", "noise_sd": 0.5,
                     "seed": 19, "d": 2, "mu": 0},
        "selected": {
            k: {
                "lambda": v.lambda_,
                "smoothness": v.smoothness,
                "recovery_rmse": float(
                    np.sqrt(np.mean((trends[k] - case.trend) ** 2))
                ),
            }
            for k, v in choices.items()
        },
        "checks": checks,
        "environment": {"numpy": np.__version__},
    }, handle, indent=2)

rows = []
for name, choice in choices.items():
    rmse = np.sqrt(np.mean((trends[name] - case.trend) ** 2))
    rows.append(
        f"{name.upper()} & {choice.lambda_:.3g} & "
        f"{choice.smoothness:.3f} & {rmse:.3f} " + r"\\"
    )
table = (
    "\\begin{tabular}{lrrr}\n\\hline\n"
    "Criterion & $\\widehat\\lambda$ & $S$ & Trend RMSE \\\\\n"
    "\\hline\n" + "\n".join(rows) + "\n\\hline\n\\end{tabular}\n"
)
(ROOT / "criteria_table.tex").write_text(table, encoding="utf-8")

print("Generated paper synthetic illustration and numerical checks.")
print("Maximum solver difference:", max(row["solver_inf_error"] for row in checks))
print("Maximum infinity-limit residual:",
      max(row["limit_penalty_error"] for row in checks))
