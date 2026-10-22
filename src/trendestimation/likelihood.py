"""Gaussian marginal-likelihood selection for penalized differences.

Implements profiled Gaussian marginal likelihood (REML-style) on the
positive-penalty spectral subspace. The difference-operator nullspace
is treated as an unpenalized nuisance trend. The observation variance
is unknown and profiled out. This extends the Gaussian marginal-
likelihood framework discussed by Biessy (2026, Section 5.3), which
treats the observation variance as known.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .core import MeanMode, TrendSmoother


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


@dataclass(frozen=True)
class VarianceComponents:
    """Profiled Gaussian variance-component estimates for a chosen penalty.

    Attributes
    ----------
    observation_variance : float
        Estimated variance of independent observation errors,
        sigma_epsilon squared.
    difference_variance : float
        Estimated variance of centered latent d-th differences,
        sigma_eta squared. This is not the variance of the entire
        latent trend tau, which depends on time and the nullspace.
    observation_sd : float
        Square root of observation_variance.
    difference_sd : float
        Square root of difference_variance.
    lambda_ : float
        Ratio observation_variance / difference_variance for finite
        positive penalties, or infinity at zero difference variance.
    mu : float
        Fixed or observed-difference plug-in mean used for fitting.
    n_penalized : int
        Number of positive-penalty spectral coordinates (n - d).
    """

    observation_variance: float
    difference_variance: float
    observation_sd: float
    difference_sd: float
    lambda_: float
    mu: float
    n_penalized: int


def estimate_variance_components(
    smoother: TrendSmoother, y, *, lambda_: float,
    mu: MeanMode = 0.0,
) -> VarianceComponents:
    """Estimate the two Gaussian PLS variance components for a chosen lambda.

    Parameters
    ----------
    smoother : TrendSmoother
        SVD-based smoother for the observed series and difference order.
    y : array_like
        Observed one-dimensional finite series, with matching length.
    lambda_ : float
        Selected positive penalty (e.g., from criterion="mle");
        positive infinity is allowed and sets the difference variance
        to zero. lambda=0 cannot define a finite Gaussian latent prior.
    mu : float or {"data"}, default=0.0
        Mean of the latent d-th differences. With "data", plug in the
        arithmetic mean of the observed d-th differences D_d @ y.

    Returns
    -------
    VarianceComponents
        Profiled observation and latent-difference variances, their
        standard deviations, selected lambda, reference mean, and
        number of penalized spectral coordinates.

    Notes
    -----
    In this Gaussian variance-components interpretation,

        y = tau + epsilon,
        epsilon ~ N(0, sigma_epsilon**2 * I),
        D_d tau - mu * 1 ~ N(0, sigma_eta**2 * I),
        lambda = sigma_epsilon**2 / sigma_eta**2.

    Integrating the penalized trend and eliminating its unpenalized
    polynomial nullspace yields independent positive spectral
    coordinates z_j with marginal covariance

        sigma_epsilon**2 * (1 + 1/(lambda * delta_j)).

    The observation variance is estimated by the same profile-likelihood
    calculation used by criterion="mle":

        sigma_epsilon**2_hat =
            sum_j z_j**2 / (1 + 1/(lambda * delta_j)) / (n - d).

    The latent-difference variance then equals
    sigma_epsilon**2_hat / lambda; at lambda=infinity it is zero.
    Both are conditional plug-in estimates at the *provided* lambda;
    they are MLE component estimates when lambda was selected by the
    matching profiled Gaussian marginal-likelihood criterion.

    mu="data" is an empirical plug-in, not a joint ML estimate of mu.
    No standard errors or confidence intervals are claimed. Neither
    variance represents the empirical variance of the fitted trend
    or the raw residual MSE. The method is not forecast validation.

    Examples
    --------
    >>> import numpy as np
    >>> from trendestimation import (
    ...     TrendSmoother, select_lambda, estimate_variance_components,
    ... )
    >>> y = np.linspace(0, 2, 30) + np.random.default_rng(42).normal(0, .3, 30)
    >>> smoother = TrendSmoother(len(y), order=2)
    >>> selection = select_lambda(smoother, y, criterion="mle", mu=0.0)
    >>> components = estimate_variance_components(
    ...     smoother, y, lambda_=selection.lambda_, mu=0.0,
    ... )
    >>> components.observation_variance >= 0
    True
    """
    rank = smoother.n - smoother.order
    if smoother.order == 0 or rank < 2:
        raise ValueError(
            "Gaussian profile MLE requires order >= 1 "
            "and at least two positive-penalty coordinates."
        )

    lam = float(lambda_)
    if np.isnan(lam) or lam <= 0:
        raise ValueError("lambda_ must be strictly positive or infinity.")

    _, mean_value, _, coordinates = smoother._prepare(y, mu)
    values = smoother.eigenvalues[:rank]
    if np.isinf(lam):
        log_variance_factor = np.zeros(rank, dtype=float)
    else:
        log_variance_factor = np.logaddexp(0.0, -np.log(lam) - np.log(values))

    whitened = coordinates[:rank] * np.exp(-0.5 * log_variance_factor)
    variance_observation = float((whitened @ whitened) / rank)
    if not np.isfinite(variance_observation) or variance_observation <= 0:
        raise ValueError(
            "Gaussian variance components are not identifiable: "
            "the penalized spectral energy is zero or nonfinite."
        )

    variance_difference = (
        0.0 if np.isinf(lam) else float(variance_observation / lam)
    )
    if not np.isfinite(variance_difference):
        raise OverflowError("Latent-difference variance overflowed at lambda_.")
    return VarianceComponents(
        observation_variance=variance_observation,
        difference_variance=variance_difference,
        observation_sd=float(np.sqrt(variance_observation)),
        difference_sd=float(np.sqrt(variance_difference)),
        lambda_=lam,
        mu=mean_value,
        n_penalized=rank,
    )
