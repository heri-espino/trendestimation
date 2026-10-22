"""Create a locally saved gallery of trend-extrapolation figures.

Usage from repository root:
    python examples/forecast_gallery.py --output-dir build/forecast-gallery

This is explicitly manual and uses seeded SYNTHETIC observations.
No financial data, claims of forecast skill, or statistical intervals.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from trendestimation import (
    forecast_trend,
    plot_forecast,
    plot_forecast_dashboard,
    plot_forecast_methods,
    plot_residual_diagnostics,
    plot_smoothness_comparison,
    plot_smoothness_path,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--smoothness", type=float, default=0.8)
    parser.add_argument("--horizon", type=int, default=18)
    parser.add_argument("--dpi", type=int, default=160)
    args = parser.parse_args()

    t = np.arange(110, dtype=float)
    true_signal = 1.2 + 0.028 * t + 0.6 * np.sin(t / 21) + 0.002 * np.maximum(t - 70, 0)
    y = true_signal + np.random.default_rng(2026).normal(0, 0.27, len(t))
    result = forecast_trend(
        y, horizon=args.horizon, smoothness=args.smoothness, order=2,
        method="damped_linear", window=18, damping=.9,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    axes_plots = (
        ("01-observations-trend-and-forecast.png", lambda: plot_forecast(result)),
        ("02-smoothness-comparison.png", lambda: plot_smoothness_comparison(y)),
        ("03-extrapolation-methods.png", lambda: plot_forecast_methods(result)),
        ("04-smoothness-path.png", lambda: plot_smoothness_path(result)),
    )
    for filename, build in axes_plots:
        ax = build()
        ax.figure.savefig(args.output_dir / filename, dpi=args.dpi, facecolor="white")
        plt.close(ax.figure)
        print(args.output_dir / filename)
    figures = (
        ("05-residual-diagnostics.png", plot_residual_diagnostics),
        ("06-six-panel-dashboard.png", plot_forecast_dashboard),
    )
    for filename, build in figures:
        fig = build(result)
        fig.savefig(args.output_dir / filename, dpi=args.dpi, facecolor="white")
        plt.close(fig)
        print(args.output_dir / filename)

    print("All values were generated from a seeded synthetic series.")
    print(f"Achieved normalized smoothness: {result.smoothness:.6f}")
    print(f"Smoothing penalty: {result.lambda_:.6g}")
    print("Extrapolations are conditional illustrations, not validated forecasts.")


if __name__ == "__main__":
    main()
