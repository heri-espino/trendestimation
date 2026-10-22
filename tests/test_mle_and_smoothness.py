"""Regression checks for Gaussian MLE and Guerrero smoothness conventions."""

import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.special import binom

from trendestimation import (
    TrendSmoother, difference_matrix, fit_trend, score_lambda, select_lambda,
)


@pytest.mark.parametrize("order", [0, 1, 2, 3])
def test_both_smoothness_scales_and_inverse(order):
    n = 22
    solver = TrendSmoother(n, order=order)
    original_max = (n - order) / n

    assert solver.smoothness(0, normalized=False) == pytest.approx(0)
    assert solver.smoothness(np.inf, normalized=False) == pytest.approx(original_max)
    assert solver.smoothness(np.inf, normalized=True) == pytest.approx(1.0)
    assert np.isinf(
        solver.lambda_for_smoothness(original_max, normalized=False)
    )

    for lam in [0.1, 1.0, 100.0]:
        original = solver.smoothness(lam, normalized=False)
        normalized = solver.smoothness(lam)
        assert original == pytest.approx(normalized * original_max)
        assert solver.lambda_for_smoothness(
            original, normalized=False,
        ) == pytest.approx(lam, rel=1e-7)
        assert solver.lambda_for_smoothness(normalized) == pytest.approx(
            lam, rel=1e-7
        )

    with pytest.raises(ValueError):
        solver.lambda_for_smoothness(original_max + 1e-3, normalized=False)


@pytest.mark.parametrize("order", [0, 1, 2, 3])
def test_data_mean_is_mean_of_order_d_observed_differences(order):
    y = np.linspace(3.0, 8.0, 23) + np.sin(np.arange(23) / 3)
    solver = TrendSmoother(y.size, order=order)
    for lam in [0, 1.5, np.inf]:
        fit = solver.fit(y, lambda_=lam, mu="data")
        assert fit.mu == pytest.approx(np.mean(difference_matrix(y.size, order) @ y))
        assert fit.guerrero_smoothness == pytest.approx(
            solver.smoothness(lam, normalized=False)
        )
    if order == 0:
        assert solver.fit(y, lambda_=1, mu="data").mu == pytest.approx(y.mean())


@pytest.mark.parametrize("order", [1, 2, 3])
def test_profile_mle_matches_independent_spectral_covariance(order):
    rng = np.random.default_rng(2026)
    y = rng.normal(size=14) + np.linspace(0, 2, 14)
    mu = 0.17
    lam = 4.5
    n = y.size
    solver = TrendSmoother(n, order)
    p = np.full(n, mu) if order == 0 else mu * binom(np.arange(n), order)

    # Independently construct the covariance on the positive-penalty space.
    values, basis = np.linalg.eigh(solver.D.T @ solver.D)
    positive = values > 1e-8
    assert positive.sum() == n - order
    z = basis[:, positive].T @ (y - p)
    covariance = np.diag(1 + 1 / (lam * values[positive]))
    quad = float(z @ np.linalg.solve(covariance, z))
    sign, logdet = np.linalg.slogdet(covariance)
    assert sign > 0
    r = n - order
    expected = r * np.log(quad / r) + logdet
    actual = score_lambda(solver, y, lambda_=lam, mu=mu, criterion="mle")
    assert actual == pytest.approx(expected, rel=1e-9, abs=1e-9)


@pytest.mark.parametrize("mu", [0.0, "data"])
def test_mle_scores_and_selects_for_numeric_or_observed_difference_mean(mu):
    rng = np.random.default_rng(105)
    y = np.linspace(0, 4, 37) + rng.normal(scale=0.5, size=37)
    solver = TrendSmoother(len(y), order=2)
    grid = np.r_[0.0, np.geomspace(1e-3, 1e3, 25), np.inf]
    chosen = select_lambda(solver, y, criterion="mle", mu=mu, grid=grid)

    assert chosen.criterion == "mle"
    assert chosen.lambda_ > 0
    assert np.isfinite(chosen.score)
    assert chosen.score == pytest.approx(np.min(chosen.scores))
    assert np.isinf(chosen.scores[0])
    assert_allclose(chosen.scores[1:], [
        score_lambda(solver, y, lambda_=lam, mu=mu, criterion="mle")
        for lam in grid[1:]
    ], rtol=1e-11)
    assert chosen.smoothness == pytest.approx(solver.smoothness(chosen.lambda_))
    fitted = solver.fit(y, lambda_=chosen.lambda_, mu=mu)
    assert fitted.trend.shape == y.shape


def test_mle_boundary_and_validation():
    y = np.linspace(0, 3, 27) + np.sin(np.arange(27))
    solver = TrendSmoother(len(y), order=2)

    assert np.isinf(score_lambda(solver, y, lambda_=0, criterion="mle"))
    assert np.isfinite(score_lambda(solver, y, lambda_=np.inf, criterion="mle"))
    assert np.isfinite(score_lambda(solver, y, lambda_=1e-200, criterion="mle"))
    for lam in [-1, np.nan]:
        with pytest.raises(ValueError):
            score_lambda(solver, y, lambda_=lam, criterion="mle")

    with pytest.raises(ValueError):
        select_lambda(solver, y, criterion="cv", mu="data")
    with pytest.raises(ValueError):
        select_lambda(solver, y, criterion="gcv", mu="data")
    with pytest.raises(ValueError):
        score_lambda(solver, y, lambda_=1, criterion="aicc", mu="data")
    with pytest.raises(ValueError):
        select_lambda(TrendSmoother(len(y), order=0), y, criterion="mle")
    with pytest.raises(ValueError):
        select_lambda(solver, y, criterion="mle", mu="incorrect")
    with pytest.raises(ValueError):
        select_lambda(solver, np.zeros(len(y)), criterion="mle")


def test_data_mu_fit_and_guerrero_original_via_one_shot_api():
    y = np.array([1.0, 1.3, 2.1, 2.5, 3.3, 3.0])
    fit = fit_trend(y, order=1, lambda_=15, mu="data")
    assert fit.mu == pytest.approx(np.mean(np.diff(y)))
    assert fit.guerrero_smoothness == pytest.approx(
        fit.smoothness * (len(y) - 1) / len(y)
    )
