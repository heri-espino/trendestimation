"""Reproduce one two-panel Gaussian-contrast demonstration for the CSDA paper.

Synthetic observations only: true position is a cubic baseline plus a small
smooth perturbation; measurement noise is iid Gaussian. The nonzero reference
mu is FIXED from the known cubic baseline, never estimated from observations.
This is an illustrative fit, not an experiment or a model-comparison claim.

Run at repository root:
    python paper/csda-unified-theory/figures/render_gaussian_jerk.py

Requires the pinned AwesomeFigures in paper/requirements.txt.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import awesomefigures as af

from trendestimation import TrendSmoother, select_lambda

HERE = Path(__file__).resolve().parent
NAME = "gaussian_jerk_demo"
SEED = 20261122
N = 72
ORDER = 3
NOISE_SD = 0.08
SMOOTHNESS_GRID = np.linspace(0.02, 0.98, 91)


def example():
    """Compute a simple known-truth trajectory and one fixed-mu MLE fit."""
    t = np.linspace(0.0, 1.0, N)
    h = float(t[1] - t[0])
    # A cubic has baseline constant jerk 6(0.30) = 1.8 m/s^3.
    # The sinusoidal term gives a mildly varying true jerk.
    truth = (1.0 + t + 0.5 * t**2 + 0.30 * t**3
             + 0.12 * np.sin(3.0 * np.pi * t))
    y = truth + np.random.default_rng(SEED).normal(0.0, NOISE_SD, N)
    mu = 6.0 * 0.30 * h**3  # fixed third-difference reference, position units

    smoother = TrendSmoother(N, order=ORDER)
    choice = select_lambda(
        smoother, y, criterion="mle", mu=mu,
        search_space="smoothness", grid=SMOOTHNESS_GRID,
    )
    trend = smoother.fit(y, lambda_=choice.lambda_, mu=mu).trend
    scores = np.asarray(choice.scores, dtype=float)
    index = int(np.argmin(scores))
    if not (0 < index < len(SMOOTHNESS_GRID) - 1):
        raise RuntimeError("Demo MLE optimum fell on a search boundary.")
    if not np.all(np.isfinite(scores)):
        raise RuntimeError("Nonfinite Gaussian contrast value on the demo grid.")
    if not np.isclose(choice.smoothness, SMOOTHNESS_GRID[index], atol=5e-11):
        raise RuntimeError("Selected smoothness is inconsistent with the grid.")
    if not (np.mean((truth - trend)**2) < np.mean((truth - y)**2)):
        raise RuntimeError("Illustrative denoising diagnostic failed.")
    return t, truth, y, trend, mu, choice


def render():
    t, truth, observed, trend, mu, choice = example()
    af.set_style("elegante", palette="okabe-ito",
                 font="DejaVu Sans", use_tex=False, rasterize=True)
    colors = tuple(af.color_palette("okabe-ito", as_hex=True))
    if len(colors) < 3:
        raise RuntimeError("Pinned AwesomeFigures palette unavailable.")

    plt.rcParams.update({
        "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7,
        "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white",
    })

    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(3.48, 4.42),
        gridspec_kw={"height_ratios": (1.25, 1.0)},
    )
    fig.subplots_adjust(left=0.16, right=0.98, top=0.97,
                        bottom=0.11, hspace=0.39)

    top.scatter(t, observed, s=9, marker="o",
                color="#A3A9B3", edgecolors="none",
                alpha=0.80, label="Noisy observations", zorder=1)
    top.plot(t, truth, color="#202B38", lw=1.45, ls=(0, (4, 2)),
             label="True trend", zorder=2)
    top.plot(t, trend, color=colors[1], lw=1.8,
             label="PLS fit (Gaussian contrast)", zorder=3)
    top.set_ylabel("Position (m)")
    top.set_xlabel("Time (s)")
    top.legend(frameon=False, loc="upper left",
               handlelength=2.0, borderaxespad=0.1)
    top.grid(alpha=0.13, lw=0.4)

    relative = np.asarray(choice.scores, dtype=float) - float(choice.score)
    bottom.plot(SMOOTHNESS_GRID, relative, color=colors[1], lw=1.8)
    bottom.axvline(choice.smoothness, color="#202B38", lw=0.9,
                   linestyle=(0, (3, 2)), alpha=0.75)
    bottom.scatter([choice.smoothness], [0.0],
                   s=25, color=colors[1], zorder=5)
    bottom.annotate(
        rf"$\hat{{S}}={choice.smoothness:.3f}$",
        (choice.smoothness, 0.0), xytext=(-4, 16),
        textcoords="offset points", ha="right", va="bottom",
        fontsize=8, color="#202B38",
    )
    bottom.set_xlim(0.0, 1.0)
    bottom.set_ylim(bottom=-2.0)
    bottom.set_xlabel(r"Normalized smoothness $S$")
    bottom.set_ylabel(r"Gaussian contrast $-\min$")
    bottom.grid(alpha=0.13, lw=0.4)

    HERE.mkdir(parents=True, exist_ok=True)
    for extension in ("pdf", "png", "svg"):
        af.save_figure(
            fig, HERE / f"{NAME}.{extension}",
            dpi=210,
        )
    plt.close(fig)

    # Keep numerical provenance independently inspectable.
    np.savetxt(
        HERE / "gaussian_jerk_series.csv",
        np.column_stack([t, truth, observed, trend]),
        delimiter=",", header="time_s,true_position_m,observed_position_m,pls_fit_m",
        comments="", fmt="%.14g",
    )
    np.savetxt(
        HERE / "gaussian_jerk_profile.csv",
        np.column_stack([SMOOTHNESS_GRID, choice.grid, choice.scores]),
        delimiter=",", header="smoothness,lambda,profiled_minus_twice_loglik",
        comments="", fmt="%.14g",
    )
    files = [HERE / f"{NAME}.{ext}" for ext in ("pdf", "png", "svg")]
    files += [HERE / "gaussian_jerk_series.csv",
              HERE / "gaussian_jerk_profile.csv"]
    metadata = {
        "figure": NAME,
        "kind": "deterministic_synthetic_illustration",
        "n": N, "difference_order": ORDER, "seed": SEED,
        "noise_sd_m": NOISE_SD,
        "sampling_interval_s": float(t[1] - t[0]),
        "baseline_jerk_m_per_s3": 1.8,
        "fixed_mu_m": mu,
        "s_grid_points": len(SMOOTHNESS_GRID),
        "criterion": "mle",
        "criterion_interpretation": "profiled Gaussian contrast; fixed mu; in-sample",
        "selected_smoothness": float(choice.smoothness),
        "selected_lambda": float(choice.lambda_),
        "selected_score": float(choice.score),
        "truth_rmse_m": float(np.sqrt(np.mean((truth - trend)**2))),
        "observed_rmse_m": float(np.sqrt(np.mean((truth - observed)**2))),
        "awesomefigures_version": getattr(af, "__version__", "unknown"),
        "awesomefigures_apis": ["set_style", "color_palette", "save_figure"],
        "file_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in files},
    }
    (HERE / f"{NAME}.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps({
        "selected_S": metadata["selected_smoothness"],
        "selected_lambda": metadata["selected_lambda"],
        "true_trend_RMSE_m": metadata["truth_rmse_m"],
        "outputs": [p.name for p in files],
    }, indent=2))


if __name__ == "__main__":
    render()
