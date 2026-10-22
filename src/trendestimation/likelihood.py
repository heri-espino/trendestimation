"""Gaussian marginal-likelihood selection for penalized differences.

Implements profiled Gaussian marginal likelihood (REML-style) on the
positive-penalty spectral subspace. The difference-operator nullspace
is treated as an unpenalized nuisance trend. The observation variance
is unknown and profiled out. This extends the Gaussian marginal-
likelihood framework discussed by Biessy (2026, Section 5.3), which
treats the observation variance as known.
"""

from __future__ import annotations

import numpy as np

from .core import TrendSmoother


def _score_profile_mle(
    smoother: TrendSmoother, coordinates: np.ndarray, *, lambda_: float,
) -> float:
    """Return twice negative profiled log-likelihood, up to a constant.

    On the r = n-d positive-penalty coordinates with eigenvalues delta_j,
    assume independent Gaussian observation noise of variance sigma^2
    and latent trend variance sigma^2/(lambda*delta_j). The marginal
    variance is sigma^2 * c_j, c_j = 1 + 1/(lambda*delta_j).
    Profiling sigma^2 yields

        r * log(sum_j z_j^2 / c_j / r) + sum_j log(c_j).

    Smaller values are better; unpenalized nullspace coordinates and
    additive constants have been eliminated. lambda=0 has an improper
    infinite latent variance and receives an infinite score, as do
    observations with degenerate zero residual energy.

    An upstream mu='data' is an empirical plug-in mean. This is a
    *conditional plug-in likelihood*, not joint MLE of mu and lambda.
    """
    lam = float(lambda_)
    if np.isnan(lam) or lam < 0:
        raise ValueError("lambda_ must lie in [0, infinity].")
    if lam == 0:
        return float("inf")

    rank = smoother.n - smoother.order
    eigenvalues = smoother.eigenvalues[:rank]
    z = coordinates[:rank]

    # Log-variance form avoids overflow when lambda is very small.
    if np.isinf(lam):
        log_variance = np.zeros(rank, dtype=float)
    else:
        log_variance = np.logaddexp(0.0, -np.log(lam) - np.log(eigenvalues))
    standardized = z * np.exp(-0.5 * log_variance)
    weighted_ss = float(standardized @ standardized)
    if not np.isfinite(weighted_ss) or weighted_ss <= 0:
        return float("inf")
    return float(rank * np.log(weighted_ss / rank) + np.sum(log_variance))
