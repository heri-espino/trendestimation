"""Optional Matplotlib visualizations for historical trends and extrapolations.

Plots deliberately distinguish the future region from observations. There
are no unvalidated prediction intervals or claims of forecast performance.
"""
from __future__ import annotations

import numpy as np

from .core import TrendSmoother
from .forecasting import TrendForecast

INK = "#18344b"
BLUE = "#2764ac"
DEEP = "#173f72"
SKY = "#80b8d8"
PALE = "#ecf5fa"
POINT = "#97aabb"
OTHER = "#597c94"
TEAL = "#087f8c"


def _style(ax):
    """Use a clean low-chrome style without changing global rcParams."""
    ax.set_facecolor("white")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color("#c7d6e0")
    ax.tick_params(colors=OTHER, labelsize=9, length=3)
    ax.grid(axis="y", color="#e6eff5", lw=.7, zorder=0)
    ax.set_axisbelow(True)
    ax.title.set_color(INK)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)
    return ax


def _new_ax(ax, figsize=(10, 4.5)):
    if ax is None:
        import matplotlib.pyplot as plt
        _, ax = plt.subplots(figsize=figsize, layout="constrained")
    return _style(ax)


def plot_forecast(result: TrendForecast, *, ax=None, title=None, show_points=True):
    """Plot historical points, smoothed trend and future extrapolation.

    Future shading marks the horizon, NOT a confidence or prediction band.
    Returns the Matplotlib Axes for further customization.
    """
    ax = _new_ax(ax)
    n = len(result.observed)
    x = result.history_index
    if show_points:
        ax.scatter(x, result.observed, s=14, c=POINT, alpha=.8,
                   label="Observed points", zorder=3)
    else:
        ax.plot(x, result.observed, c=POINT, lw=.85, label="Observed series")
    ax.plot(x, result.fit.trend, lw=2.5, color=BLUE,
            label=f"PLS trend (smoothness {result.smoothness:.2f})")
    ax.axvspan(n - .5, result.future_index[-1] + .5, color=PALE, zorder=-1)
    fx = np.r_[n - 1, result.future_index]
    fy = np.r_[result.fit.trend[-1], result.forecast]
    ax.plot(fx, fy, lw=2.5, color=TEAL, ls="--",
            label=f"Trend extrapolation: {result.method}")
    ax.axvline(n - .5, color=OTHER, lw=1, ls=":")
    ax.scatter(result.future_index, result.forecast, color=TEAL, s=18, zorder=4)
    ax.set(xlabel="Time step", ylabel="Value",
           title=title or "Observed points, estimated trend and future extrapolation")
    ax.legend(frameon=False, fontsize=8)
    return ax


def plot_smoothness_comparison(
    y, *, order=2, mu=0.0, smoothness_levels=(.2, .5, .8, .95), ax=None,
):
    """Overlay several PLS smoothness targets on the same observations.

    A single SVD is reused across target levels. Returns the Axes.
    """
    observed = np.asarray(y, dtype=float)
    if observed.ndim != 1 or not np.all(np.isfinite(observed)):
        raise ValueError("y must be a finite one-dimensional series.")
    solver = TrendSmoother(len(observed), order)
    levels = tuple(float(s) for s in smoothness_levels)
    if not levels:
        raise ValueError("smoothness_levels must contain at least one value.")
    ax = _new_ax(ax)
    x = np.arange(len(observed))
    ax.scatter(x, observed, s=10, color=POINT, alpha=.5, label="Observed")
    colors = [SKY, OTHER, BLUE, DEEP, TEAL]
    for i, s in enumerate(levels):
        lam = solver.lambda_for_smoothness(s)
        fit = solver.fit(observed, lambda_=lam, mu=mu)
        ax.plot(x, fit.trend, lw=1.9, color=colors[i % len(colors)],
                label=f"Smoothness {fit.smoothness:.2f}")
    ax.set(xlabel="Time step", ylabel="Value",
           title="How fixed smoothness changes the estimated trend")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    return ax


def plot_forecast_methods(result: TrendForecast, *, ax=None, damping=.85):
    """Compare unvalidated last-value, linear and damped-linear extrapolations."""
    if not 0 < damping <= 1 or not np.isfinite(damping):
        raise ValueError("damping must belong to (0, 1].")
    ax = _new_ax(ax)
    n = len(result.observed)
    x = np.arange(n)
    ax.scatter(x, result.observed, color=POINT, s=10, alpha=.45, label="Observed")
    ax.plot(x, result.fit.trend, color=BLUE, lw=2.2, label="Estimated trend")
    steps = np.arange(1, result.horizon + 1)
    initial = result.fit.trend[-1]
    series = (
        ("Last value", np.full(result.horizon, initial), OTHER),
        ("Local linear", initial + result.slope * steps, TEAL),
        ("Damped linear", initial + result.slope * np.cumsum(damping ** steps), DEEP),
    )
    ax.axvspan(n - .5, result.future_index[-1] + .5, color=PALE, zorder=-1)
    for name, values, color in series:
        ax.plot(np.r_[n - 1, result.future_index], np.r_[initial, values],
                color=color, lw=2, ls="--", label=name)
    ax.set(xlabel="Time step", ylabel="Value",
           title="Alternative extrapolation assumptions (not forecast accuracy)")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    return ax


def plot_smoothness_path(result: TrendForecast, *, ax=None, points=100):
    """Plot normalized smoothness against penalty strength with chosen value."""
    if int(points) != points or points < 10:
        raise ValueError("points must be an integer >= 10.")
    solver = TrendSmoother(len(result.observed), result.fit.order)
    scale = 1 / solver._median_positive_eigenvalue
    penalties = scale * np.geomspace(1e-6, 1e6, int(points))
    values = [solver.smoothness(float(lam)) for lam in penalties]
    ax = _new_ax(ax)
    ax.semilogx(penalties, values, lw=2.4, color=BLUE, label="Normalized smoothness")
    if np.isfinite(result.lambda_) and result.lambda_ > 0:
        ax.scatter([result.lambda_], [result.smoothness],
                   s=65, color=TEAL, zorder=5, label="Selected penalty")
        ax.axhline(result.smoothness, color=SKY, lw=1, ls=":")
    else:
        ax.axhline(result.smoothness, color=TEAL, lw=1.3, ls="--",
                   label="Chosen endpoint")
    ax.set(xlabel="Penalty λ (log scale)", ylabel="Normalized smoothness",
           title="Smoothness controlled by the penalty", ylim=(-.02, 1.02))
    ax.legend(frameon=False, fontsize=8)
    return ax


def plot_residual_diagnostics(result: TrendForecast):
    """Return a 2x2 figure of historical *in-sample* residual diagnostics."""
    import matplotlib.pyplot as plt
    from scipy.stats import probplot

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout="constrained")
    r = result.fit.residual
    t = result.history_index
    ax = _style(axes[0, 0])
    ax.axhline(0, color=OTHER, lw=1)
    ax.scatter(t, r, c=BLUE, s=16, alpha=.7)
    ax.set(title="Historical fit residuals", xlabel="Time step", ylabel="Observed − trend")
    ax = _style(axes[0, 1])
    ax.hist(r, bins="auto", color=SKY, edgecolor="white")
    ax.set(title="Residual distribution", xlabel="Residual", ylabel="Count")
    ax = _style(axes[1, 0])
    if len(r) >= 3 and np.std(r) > 0:
        (theoretical, ordered), (slope, intercept, _) = probplot(r, dist="norm")
        ax.scatter(theoretical, ordered, c=BLUE, s=15)
        ax.plot(theoretical, slope * theoretical + intercept, c=TEAL, lw=1.3)
    else:
        ax.text(.5, .5, "Insufficient residual variation",
                transform=ax.transAxes, ha="center", va="center")
    ax.set(title="Normal Q–Q reference (descriptive)",
           xlabel="Normal quantile", ylabel="Ordered residual")
    ax = _style(axes[1, 1])
    max_lag = min(24, len(r) - 1)
    centered = r - np.mean(r)
    total = np.dot(centered, centered)
    if total > 0:
        lags = np.arange(1, max_lag + 1)
        acf = [np.dot(centered[:-k], centered[k:]) / total for k in lags]
        ax.vlines(lags, 0, acf, color=BLUE, lw=1.6)
        ax.scatter(lags, acf, color=BLUE, s=12)
    else:
        ax.text(.5, .5, "Zero residual variance",
                transform=ax.transAxes, ha="center", va="center")
    ax.axhline(0, color=OTHER, lw=1)
    ax.set(title="Residual autocorrelation (descriptive)",
           xlabel="Lag", ylabel="Sample ACF")
    fig.suptitle("Diagnostics of the in-sample trend fit — not forecast validation",
                 color=INK, fontsize=13)
    return fig


def plot_forecast_dashboard(result: TrendForecast):
    """Return one six-panel figure covering trends, residuals and assumptions."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 2, figsize=(14, 12), layout="constrained")
    plot_forecast(result, ax=axes[0, 0], title="Observations, trend and extrapolation")
    plot_forecast_methods(result, ax=axes[0, 1])
    ax = _style(axes[1, 0])
    ax.axhline(0, color=OTHER, lw=1)
    ax.scatter(result.history_index, result.fit.residual, c=BLUE, s=11)
    ax.set(title="In-sample residuals", xlabel="Time step", ylabel="Residual")
    ax = _style(axes[1, 1])
    ax.hist(result.fit.residual, bins="auto", color=SKY, edgecolor="white")
    ax.set(title="Residual distribution", xlabel="Residual", ylabel="Count")
    ax = _style(axes[2, 0])
    delta = np.diff(result.fit.trend)
    ax.plot(np.arange(1, len(result.observed)), delta, color=BLUE, lw=1.5)
    ax.axhline(result.slope, color=TEAL, ls="--",
               label=f"Local slope {result.slope:.3g}")
    ax.set(title="Changes in the estimated trend", xlabel="Time step",
           ylabel="First difference")
    ax.legend(frameon=False, fontsize=8)
    plot_smoothness_path(result, ax=axes[2, 1])
    fig.suptitle("Trend and extrapolation | illustrative assumptions, not prediction intervals",
                 color=INK, fontsize=14)
    return fig
