"""Independent numerical checks for Gaussian variance components."""

import numpy as np
import pytest
from scipy.special import binom

from trendestimation import (
    TrendSmoother, estimate_variance_components, score_lambda, select_lambda,
)


@pytest.mark.parametrize("order", [1, 2, 3])
@pytest.mark.parametrize("mu", [0.0, 0.27])
def test_variances_match_direct_eigendecomposition(order, mu):
    rng = np.random.default_rng(150 + order)
    n = 29
    y = np.linspace(-1, 2, n) + rng.normal(scale=0.45, size=n)
    lam = 8.25
    smoother = TrendSmoother(n, order=order)
    result = estimate_variance_components(smoother, y, lambda_=lam, mu=mu)

    # Independent eigendecomposition from the normal-equation penalty.
    eigenvalues, eigenvectors = np.linalg.eigh(smoother.D.T @ smoother.D)
    mask = eigenvalues > 1e-8
    assert mask.sum() == n - order
    reference = mu * binom(np.arange(n), order)
    residual_coordinates = eigenvectors[:, mask].T @ (y - reference)
    c = 1 + 1 / (lam * eigenvalues[mask])
    expected_noise = float(np.sum(residual_coordinates**2 / c) / (n - order))
    expected_differences = expected_noise / lam

    assert result.observation_variance == pytest.approx(expected_noise, rel=1e-9)
    assert result.difference_variance == pytest.approx(expected_differences, rel=1e-9)
    assert result.observation_sd**2 == pytest.approx(expected_noise, rel=1e-9)
    assert result.difference_sd**2 == pytest.approx(expected_differences, rel=1e-9)
    assert result.mu == pytest.approx(mu)
    assert result.lambda_ == pytest.approx(lam)
    assert result.n_penalized == n - order
    assert (
        result.observation_variance / result.difference_variance
        == pytest.approx(lam)
    )
    expected_score = (n - order) * np.log(expected_noise) + np.log(c).sum()
    assert score_lambda(
        smoother, y, lambda_=lam, mu=mu, criterion="mle"
    ) == pytest.approx(expected_score, rel=1e-9)


@pytest.mark.parametrize("mu", [0.0, "data"])
def test_variances_at_selected_mle_and_exact_infinity(mu):
    rng = np.random.default_rng(41)
    y = np.linspace(0, 1, 42) + rng.normal(0, 0.3, 42)
    smoother = TrendSmoother(len(y), 2)
    choice = select_lambda(smoother, y, criterion="mle", mu=mu)
    result = estimate_variance_components(
        smoother, y, lambda_=choice.lambda_, mu=mu
    )
    assert result.lambda_ == choice.lambda_
    assert np.isfinite(result.observation_variance)
    assert result.observation_variance > 0
    assert result.difference_variance >= 0
    if np.isfinite(choice.lambda_):
        assert result.difference_variance > 0
        assert result.observation_variance / result.difference_variance == pytest.approx(
            choice.lambda_
        )
    else:
        assert result.difference_variance == 0

    expected_mu = 0.0 if mu == 0.0 else float(np.mean(smoother.D @ y))
    assert result.mu == pytest.approx(expected_mu)

    boundary = estimate_variance_components(
        smoother, y, lambda_=np.inf, mu=mu
    )
    assert boundary.difference_variance == 0
    assert boundary.difference_sd == 0
    assert boundary.observation_variance == pytest.approx(
        np.sum((smoother.eigenvectors[:, : len(y) - 2].T
                @ (y - smoother._reference(expected_mu)))**2) / (len(y) - 2)
    )


def test_variance_components_invalid_and_degenerate_cases():
    smoother = TrendSmoother(25, order=2)
    y = np.linspace(0, 1, 25) + 0.1 * np.sin(np.arange(25))

    for value in [0, -1, np.nan, -np.inf]:
        with pytest.raises(ValueError):
            estimate_variance_components(smoother, y, lambda_=value)
    with pytest.raises(ValueError):
        estimate_variance_components(smoother, np.zeros(25), lambda_=10)
    with pytest.raises(ValueError):
        estimate_variance_components(TrendSmoother(25, order=0), y, lambda_=10)
    with pytest.raises(ValueError):
        estimate_variance_components(TrendSmoother(2, order=1), y[:2], lambda_=10)
    with pytest.raises(ValueError):
        estimate_variance_components(smoother, y, lambda_=10, mu="other")
    with pytest.raises(ValueError):
        estimate_variance_components(smoother, np.ones(24), lambda_=10)


def test_fixed_penalty_variance_is_not_residual_mse():
    rng = np.random.default_rng(2026)
    y = np.arange(40) * 0.02 + rng.normal(size=40)
    smoother = TrendSmoother(len(y), 2)
    estimate = estimate_variance_components(smoother, y, lambda_=10)
    fitted = smoother.fit(y, lambda_=10)
    residual_mse = float(np.mean(fitted.residual**2))
    assert not np.isclose(estimate.observation_variance, residual_mse)
