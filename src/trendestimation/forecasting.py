"""Conditional extrapolation of a fitted penalized-least-squares trend.

This is a deterministic forecast baseline, not a statistically calibrated
forecasting model or a forecast-optimal smoothing procedure.
"""
from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral
from typing import Literal

import numpy as np

from .core import FitResult, MeanMode, TrendSmoother

ForecastMethod = Literal["local_linear", "damped_linear", "last_value"]


@dataclass(frozen=True)
class TrendForecast:
    """Historical observations, fitted trend, and conditional future extrapolation.

    forecast contains future values indexed by future_index. fit contains the
    original in-sample PLS estimate; smoothness is not predictive confidence.
    """

    observed: np.ndarray
    fit: FitResult
    forecast: np.ndarray
    future_index: np.ndarray
    method: ForecastMethod
    window: int
    slope: float
    damping: float

    @property
    def history_index(self) -> np.ndarray:
        """Observation positions on a regular integer timeline."""
        return np.arange(len(self.observed))

    @property
    def horizon(self) -> int:
        """Number of future sample steps."""
        return int(len(self.forecast))

    @property
    def lambda_(self) -> float:
        """Smoothing penalty used in the historical fit."""
        return self.fit.lambda_

    @property
    def smoothness(self) -> float:
        """Achieved normalized in-sample PLS smoothness."""
        return self.fit.smoothness


def forecast_trend(
    y,
    *,
    horizon: int = 12,
    smoothness: float | None = None,
    lambda_: float | None = None,
    order: int = 2,
    mu: MeanMode = 0.0,
    method: ForecastMethod = "local_linear",
    window: int | None = None,
    damping: float = 0.85,
) -> TrendForecast:
    """Fit a historical PLS trend and extrapolate its endpoint into future steps.

    Parameters
    ----------
    y : array_like
        Finite, one-dimensional, equally spaced historical observations only.
    horizon : int, default 12
        Positive number of future sample steps.
    smoothness : float, optional
        Normalized PLS smoothness target in [0, 1]. Default 0.8 if no penalty
        is supplied. This is neither accuracy nor a confidence probability.
    lambda_ : float, optional
        Explicit nonnegative penalty, including infinity. Cannot be combined
        with smoothness.
    order : int, default 2
        Differencing order, 0 <= order < len(y).
    mu : float or "data", default 0
        Fixed reference difference mean or Guerrero's fitted plug-in mean.
    method : {"local_linear", "damped_linear", "last_value"}
        local_linear estimates a slope by ordinary least squares on the final
        window of fitted trend values, and anchors the next step to the final
        fitted trend. damped_linear uses incremental slopes times damping**k.
        last_value projects the final fitted trend as a constant.
    window : int, optional
        Historical fitted trend points used for local slope. The default is
        min(n, 24, max(3, ceil(0.2*n))), or n for very short sequences.
    damping : float, default 0.85
        Increment decay in (0, 1], used for damped_linear.

    Returns
    -------
    TrendForecast
        In-sample fit, conditional extrapolations, horizon positions and
        slope metadata.

    Notes
    -----
    Future indices use the same integer-step spacing as observations.
    Extrapolation cannot be interpreted as an estimated conditional mean or
    statistically validated forecast without independent rolling evaluation.
    No prediction intervals or forecast-accuracy guarantees are supplied.
    Fitted end points can be revised when further observations arrive.

    Examples
    --------
    >>> import numpy as np
    >>> y = .1*np.arange(40) + np.random.default_rng(4).normal(0, .2, 40)
    >>> forecast_trend(y, horizon=6, smoothness=.8).forecast.shape
    (6,)
    """
    observed = np.asarray(y, dtype=float)
    if observed.ndim != 1 or observed.size < 2 or not np.all(np.isfinite(observed)):
        raise ValueError("y must be a finite one-dimensional series with at least two points.")
    if isinstance(horizon, (bool, np.bool_)) or not isinstance(horizon, Integral) or horizon < 1:
        raise ValueError("horizon must be a positive integer.")
    if smoothness is not None and lambda_ is not None:
        raise ValueError("Specify only one of smoothness or lambda_.")
    if method not in ("local_linear", "damped_linear", "last_value"):
        raise ValueError("method must be local_linear, damped_linear, or last_value.")
    if not np.isfinite(damping) or not 0 < damping <= 1:
        raise ValueError("damping must belong to (0, 1].")

    n = len(observed)
    if window is None:
        window = min(n, 24, max(3, int(np.ceil(.2 * n))))
    if (isinstance(window, (bool, np.bool_))
            or not isinstance(window, Integral)
            or not 1 <= window <= n):
        raise ValueError("window must be an integer from 1 through len(y).")
    if method != "last_value" and window < 2:
        raise ValueError("local-linear methods need window >= 2.")

    solver = TrendSmoother(n, order=order)
    if lambda_ is None:
        target = .8 if smoothness is None else float(smoothness)
        selected = solver.lambda_for_smoothness(target)
    else:
        selected = float(lambda_)
    fit = solver.fit(observed, lambda_=selected, mu=mu)

    slope = 0.0
    if method != "last_value":
        recent = fit.trend[-window:]
        x = np.arange(window, dtype=float)
        centered = x - np.mean(x)
        slope = float(
            np.dot(centered, recent - np.mean(recent)) / np.dot(centered, centered)
        )
    steps = np.arange(1, int(horizon) + 1, dtype=float)
    if method == "last_value":
        increments = np.zeros(int(horizon))
    elif method == "damped_linear":
        increments = slope * np.cumsum(damping ** steps)
    else:
        increments = slope * steps
    future = fit.trend[-1] + increments
    if not np.all(np.isfinite(future)):
        raise ArithmeticError("Extrapolation overflowed; rescale data or reduce horizon.")
    return TrendForecast(
        observed=observed.copy(),
        fit=fit,
        forecast=future,
        future_index=np.arange(n, n + int(horizon)),
        method=method,
        window=int(window),
        slope=slope,
        damping=float(damping),
    )
