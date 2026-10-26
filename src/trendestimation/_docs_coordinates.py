"""Notebook-only lambda and normalized smoothness comparisons.

Plots use actual fixed-mu PLS criteria and do not claim that a one-off
wall-clock observation establishes algorithmic superiority.
"""
from __future__ import annotations

from time import perf_counter
import numpy as np
from .core import TrendSmoother
from .criteria import score_lambda, select_lambda


def show_dual_coordinate_gallery(series=None, *, order=2, mu=0.0, max_points=60):
    """Display S(lambda), paired CV/GCV/AICc/BIC plots and selection timings."""
    import matplotlib.pyplot as plt

    x = np.linspace(0, 1, max_points)
    fallback = (0.65*np.sin(9*x) + 0.4*x +
                np.random.default_rng(2026).normal(0, 0.24, max_points))
    context = "independent seeded synthetic series"
    if series is None:
        y = fallback
    else:
        try:
            raw = np.asarray(series, dtype=float).reshape(-1)
            if raw.size < 12 or not np.all(np.isfinite(raw)):
                raise ValueError("invalid data for plotting")
            y = raw[-max_points:]
            context = ("same series" if raw.size <= max_points else
                       "last 60 points of the notebook series")
        except (ValueError, TypeError):
            y = fallback
            context = "seeded fallback for nonnumeric notebook input"

    d = min(int(order), len(y)-2)
    if d < 1:
        raise ValueError("difference order must be positive")
    model = TrendSmoother(len(y), order=d)
    print(f"Paired penalty and smoothness: {context}; n={len(y)}, d={d}, mu={mu:g}")

    penalties = np.geomspace(1e-3, 2e3, 85)
    sm = np.asarray([model.smoothness(float(v)) for v in penalties])
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 3.8), layout="constrained")
    axs[0].semilogx(penalties, sm, color="#205fd4", lw=2.6)
    axs[0].set(xlabel="Penalty lambda (log scale)", ylabel="Normalized S",
               title="S(lambda), with exact limits 0 and 1")
    axs[1].plot(sm, penalties, color="#138b94", lw=2.6)
    axs[1].set(xlabel="Normalized smoothness S", ylabel="Penalty lambda",
               title="Inverse transformation lambda(S)")
    axs[1].set_yscale("log")
    for ax in axs:
        ax.grid(alpha=.25)
    plt.show()

    fig, axes = plt.subplots(4, 2, figsize=(11.7, 14.0),
                            layout="constrained")
    for row, criterion in enumerate(("cv", "gcv", "aicc", "bic")):
        scores = np.asarray([
            score_lambda(model, y, lambda_=float(lam),
                         criterion=criterion, mu=mu)
            for lam in penalties])
        valid = np.isfinite(scores)
        if not np.any(valid):
            continue
        best = int(np.argmin(np.where(valid, scores, np.inf)))
        for ax, xx, color in (
            (axes[row, 0], penalties, "#205fd4"),
            (axes[row, 1], sm, "#138b94"),
        ):
            ax.plot(xx[valid], scores[valid], color=color, lw=2.5)
            ax.scatter([xx[best]], [scores[best]],
                       color="#c4546d", zorder=5, s=40)
            ax.set(title=f"{criterion.upper()}: identical candidate penalties",
                   ylabel="Criterion score (smaller preferred)")
            ax.grid(alpha=.25)
        axes[row, 0].set(xlabel="Penalty lambda (log scale)")
        axes[row, 0].set_xscale("log")
        axes[row, 1].set(xlabel="Normalized smoothness S")
        axes[row, 1].set_xlim(0, 1)
        print(f"{criterion.upper()}: selected lambda={penalties[best]:.5g}, "
              f"S={sm[best]:.5f}, score={scores[best]:.6g}")
    plt.show()

    times = {}
    for coordinate in ("lambda", "smoothness"):
        start = perf_counter()
        result = select_lambda(model, y, criterion="gcv", mu=mu,
                               search_space=coordinate)
        times[coordinate] = (perf_counter()-start)*1e3
        print(f"GCV {coordinate} auto-search: {times[coordinate]:.3f} ms, "
              f"lambda={result.lambda_:.5g}, S={result.smoothness:.5f}, "
              f"score={result.score:.6g}, candidates={len(result.grid)}")
    fig, ax = plt.subplots(figsize=(8.2, 3.6), layout="constrained")
    ax.bar(["lambda", "smoothness"],
           [times["lambda"], times["smoothness"]],
           color=["#205fd4", "#138b94"])
    ax.set(ylabel="Milliseconds (single illustrative run)",
           title="GCV auto-selection: different default candidate grids")
    ax.grid(axis="y", alpha=.25)
    plt.show()
    print("Timing is descriptive, not a controlled speed ranking. See the "
          "factorial and public API benchmarks for paired repetitions.")
