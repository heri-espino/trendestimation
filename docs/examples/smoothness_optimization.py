"""Reproduce the classical LOOCV-versus-smoothness documentation figure.

Run from the repository root:
    python -m pip install -e ".[plot,docs]"
    python docs/examples/smoothness_optimization.py

This is in-sample leave-one-out validation, NOT chronological forecasting.
The script does not download data or alter source files.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from trendestimation import TrendSmoother, score_lambda, select_lambda


def main() -> None:
    """Calculate seeded CV values and save the documentation SVG."""
    rng = np.random.default_rng(2026)
    t = np.arange(60, dtype=float)
    y = (
        0.035 * t
        + 0.7 * np.sin(t / 8.0)
        + 0.35 * np.cos(t / 17.0)
        + rng.normal(0.0, 0.33, t.size)
    )
    smoother = TrendSmoother(t.size, order=2)
    mu = 0.0  # Fixed numeric reference: required by classical CV.

    # The current default is a finite penalty grid, not analytic CV minimization.
    cv_choice = select_lambda(smoother, y, criterion="cv", mu=mu)
    gcv_choice = select_lambda(smoother, y, criterion="gcv", mu=mu)
    legacy_grid = np.r_[np.geomspace(1e-4, 1e5, 180), np.inf]
    grid_choice = select_lambda(
        smoother, y, criterion="cv", mu=mu, grid=legacy_grid
    )
    print("selector        lambda         normalized S       MSE or score")
    for label, choice in (
        ("default CV", cv_choice),
        ("explicit grid", grid_choice),
        ("GCV", gcv_choice),
    ):
        print(
            f"{label:13s} {choice.lambda_:12.5g}"
            f" {choice.smoothness:16.6f} {choice.score:16.7f}"
        )

    # Each S target is converted to its unique penalty, including no
    # data-dependent or hidden calibration of the reference mean.
    smoothness_values = np.linspace(0.02, 0.98, 49)
    penalties = np.array([
        smoother.lambda_for_smoothness(float(s))
        for s in smoothness_values
    ])
    cv_mse = np.array([
        score_lambda(smoother, y, lambda_=float(lam),
                     criterion="cv", mu=mu)
        for lam in penalties
    ])

    candidates = (0.15, 0.35, 0.55, 0.75, 0.90)
    print("\nCandidate smoothness   penalty lambda    classical CV MSE")
    candidate_mse = []
    for s in candidates:
        lam = smoother.lambda_for_smoothness(s)
        score = score_lambda(
            smoother, y, lambda_=lam, criterion="cv", mu=mu
        )
        candidate_mse.append(score)
        print(f"{s:18.2f} {lam:16.7g} {score:19.7f}")

    fig, ax = plt.subplots(figsize=(8.8, 5.2), layout="constrained")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.plot(
        smoothness_values, cv_mse, color="#1465A2",
        linewidth=2.7, label="Classical LOO MSE", zorder=2
    )
    ax.scatter(
        candidates, candidate_mse, color="#08436F",
        edgecolor="white", linewidth=1.3, s=65,
        label="Candidate smoothness levels", zorder=4
    )
    for s, score in zip(candidates, candidate_mse):
        ax.annotate(
            f"{s:.2f}", (s, score), xytext=(0, 11),
            textcoords="offset points", ha="center",
            fontsize=9, color="#08436F"
        )
    ax.set(
        title="Classical LOOCV score by normalized smoothness",
        xlabel="Normalized smoothness, S",
        ylabel="Classical leave-one-out MSE",
        xlim=(0, 1),
    )
    ax.grid(True, color="#D6E4F0", linewidth=0.8, alpha=0.9)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors="#253B4D")
    ax.title.set_color("#163D5B")
    ax.xaxis.label.set_color("#253B4D")
    ax.yaxis.label.set_color("#253B4D")

    output = (
        Path(__file__).resolve().parents[1]
        / "_static" / "figures" / "smoothness-cv.svg"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format="svg", metadata={"Date": None})
    plt.close(fig)
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
