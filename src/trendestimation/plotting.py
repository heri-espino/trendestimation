"""Optional Matplotlib plots; importing the core does not load Matplotlib."""
from __future__ import annotations

import numpy as np


def plot_trend(y, fit, *, ax=None, title: str | None = None):
    """Plot observations and a fitted PLS trend; return Matplotlib axes."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots()
    x = np.arange(len(fit.trend))
    ax.plot(x, np.asarray(y), color="0.65", label="Observed", linewidth=1)
    ax.plot(x, fit.trend, label="Estimated trend", linewidth=2)
    ax.set(xlabel="Observation", ylabel="Value",
           title=title or "Penalized trend estimation")
    ax.legend()
    return ax


def plot_selection(selection, *, ax=None):
    """Plot a classical in-sample smoothing-parameter selection curve."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots()
    mask = np.isfinite(selection.grid) & (selection.grid > 0) & np.isfinite(selection.scores)
    ax.semilogx(selection.grid[mask], selection.scores[mask],
                label=selection.criterion.upper())
    if np.isfinite(selection.lambda_):
        ax.axvline(selection.lambda_, color="0.3", linestyle="--",
                   label="Selected lambda")
    ax.set(xlabel="Penalty parameter λ", ylabel="Criterion value",
           title="Smoothing selection")
    ax.legend()
    return ax
