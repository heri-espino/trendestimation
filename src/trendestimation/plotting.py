"""Optional Matplotlib plots; importing the core does not load Matplotlib."""
from __future__ import annotations

import numpy as np


def plot_trend(y, fit, *, ax=None, title: str | None = None):
    """Visualize observations alongside an estimated in-sample trend.

    Parameters
    ----------
    y : array_like
        Original observation vector.
    fit : FitResult
        Result of a finite-difference PLS fit.
    ax : matplotlib.axes.Axes, optional
        Existing axes; if omitted, create a Matplotlib figure.
    title : str, optional
        Custom plot title.

    Returns
    -------
    matplotlib.axes.Axes
        Axes with observations and the fitted trend.

    Notes
    -----
    Matplotlib is an optional dependency, imported on demand.
    """
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots()
    x = np.arange(len(fit.trend))
    ax.plot(x, np.asarray(y), color="0.65", label="Observed", linewidth=1)
    ax.plot(x, fit.trend, label="Estimated trend", linewidth=2)
    ax.set(xlabel="Observation", ylabel="Value",
           title=title or "Penalized trend estimation")
    ax.grid(True, axis="both", color="#CFDCE7", alpha=0.6, linewidth=0.65)
    ax.set_axisbelow(True)
    ax.legend()
    return ax


def plot_selection(selection, *, ax=None):
    """Plot candidate penalties and their classical selection scores.

    Parameters
    ----------
    selection : SelectionResult
        Result of select_lambda on a candidate grid.
    ax : matplotlib.axes.Axes, optional
        Axes to reuse, or None to create a Matplotlib figure.

    Returns
    -------
    matplotlib.axes.Axes
        Semi-log penalty plot with the selected lambda indicated.

    Notes
    -----
    This figure depicts an **in-sample smoothing criterion**,
    not out-of-sample forecast error. Infinite and nonpositive
    penalty candidates are excluded from the log-x plot.
    """
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
    ax.grid(True, axis="both", color="#CFDCE7", alpha=0.6, linewidth=0.65)
    ax.set_axisbelow(True)
    ax.legend()
    return ax
