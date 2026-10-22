"""Synthetic linear/nonlinear examples from Cortes-Toto et al. (2017, Section 3)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.stats import beta


@dataclass(frozen=True)
class SimulatedSeries:
    """Reproducible synthetic time series and its components.

    Attributes
    ----------
    observed : numpy.ndarray
        Sum of trend, seasonality, and noise.
    trend : numpy.ndarray
        Known simulation trend.
    seasonality : numpy.ndarray
        Deterministic seasonal contribution, possibly zero.
    noise : numpy.ndarray
        Generated Gaussian innovations.
    """

    observed: np.ndarray
    trend: np.ndarray
    seasonality: np.ndarray
    noise: np.ndarray


def simulate_cortes_toto(
    n: int = 50, *, shape: Literal["linear", "nonlinear"] = "linear",
    seasonal: bool = False, noise_sd: float = 0.5, seed: int = 0,
) -> SimulatedSeries:
    """Generate synthetic trend scenarios from Cortés-Toto et al. (2017).

    Parameters
    ----------
    n : int, default=50
        Number of observations.
    shape : {"linear", "nonlinear"}, default="linear"
        Linear 4t/n or a 0.6/0.4 mixture of Beta densities.
    seasonal : bool, default=False
        Include periodic quarterly offsets (1, -0.5, -2.5, 2).
    noise_sd : float, default=0.5
        Standard deviation of Gaussian observation noise.
    seed : int, default=0
        Random seed for deterministic reproduction.

    Returns
    -------
    SimulatedSeries
        Observed series and each known simulation component.

    Notes
    -----
    This recreates selected simulation settings from the published
    study; it is not a newly collected empirical dataset.
    """
    if n < 2 or int(n) != n or not np.isfinite(noise_sd) or noise_sd < 0:
        raise ValueError("Require integer n>=2 and nonnegative finite noise_sd.")
    t = np.arange(1, n + 1, dtype=float) / n
    if shape == "linear":
        trend = 4.0 * t
    elif shape == "nonlinear":
        trend = 0.6 * beta.pdf(t, 30, 17) + 0.4 * beta.pdf(t, 3, 11)
    else:
        raise ValueError("shape must be linear or nonlinear.")
    seasonality = (np.array([1.0, -0.5, -2.5, 2.0])[np.arange(n) % 4]
                   if seasonal else np.zeros(n))
    noise = np.random.default_rng(seed).normal(scale=noise_sd, size=n)
    return SimulatedSeries(
        observed=trend + seasonality + noise,
        trend=trend, seasonality=seasonality, noise=noise,
    )
