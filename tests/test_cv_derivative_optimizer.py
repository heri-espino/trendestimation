"""Analytical classical LOOCV differentiation and robust penalty search."""
from __future__ import annotations

import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.optimize import brentq

from trendestimation import TrendSmoother, cv_derivative, score_lambda, select_lambda


def _five_point_derivative(f, x, h):
    """Independent fourth-order centered finite-difference oracle (tests only)."""
    return (f(x - 2*h) - 8*f(x - h) + 8*f(x + h) - f(x + 2*h)) / (12*h)


@pytest.mark.parametrize("order", [0, 1, 2, 3, 5])
@pytest.mark.parametrize("lam", [0.002, 0.1, 5.0, 200.0])
@pytest.mark.parametrize("mu", [0.0, 0.27])
def test_derivative_against_independent_five_point_difference(order, lam, mu):
    n = 17
    y = np.random.default_rng(1050 + order).normal(size=n)
    smoother = TrendSmoother(n, order)
    f = lambda z: score_lambda(smoother, y, lambda_=z, criterion="cv", mu=mu)
    h = lam * 2e-4
    finite_difference = _five_point_derivative(f, lam, h)
    analytic = cv_derivative(smoother, y, lambda_=lam, mu=mu)
    assert np.isfinite(analytic)
    assert_allclose(analytic, finite_difference, rtol=6e-6, atol=2e-7)


@pytest.mark.parametrize("order", [0, 1, 2, 4, 8])
def test_small_penalty_continuation_and_infinite_boundary(order):
    n = 10
    smoother = TrendSmoother(n, order)
    y = np.random.default_rng(29 + order).normal(size=n)
    mu = 0.14
    for lam in [1e-24, 1e-14, 1e-8, 0.4, 1e10, np.inf]:
        score = score_lambda(smoother, y, lambda_=lam, criterion="cv", mu=mu)
        derivative = cv_derivative(smoother, y, lambda_=lam, mu=mu)
        assert np.isfinite(score)
        assert np.isfinite(derivative)
        assert score >= 0
    assert score_lambda(smoother, y, lambda_=0, criterion="cv", mu=mu) == np.inf
    assert cv_derivative(smoother, y, lambda_=np.inf, mu=mu) == 0.0
    with pytest.raises(ValueError):
        cv_derivative(smoother, y, lambda_=0, mu=mu)
    with pytest.raises(ValueError):
        cv_derivative(smoother, y, lambda_=-1, mu=mu)
    with pytest.raises(ValueError):
        cv_derivative(smoother, y, lambda_=1, mu="data")


@pytest.mark.parametrize("order", [1, 2, 3])
def test_against_high_resolution_grid(order):
    rng = np.random.default_rng(440 + order)
    n = 19
    y = 0.1 * np.arange(n) + np.sin(np.arange(n) / 2) + rng.normal(0, 0.3, n)
    smoother = TrendSmoother(n, order)
    selected = select_lambda(smoother, y, criterion="cv", mu=0.15)
    exhaustive = select_lambda(
        smoother, y, criterion="cv", mu=0.15, method="grid",
        grid=np.r_[np.geomspace(1e-12, 1e12, 6001), np.inf],
    )
    assert selected.score <= exhaustive.score + 1e-7
    assert selected.score == pytest.approx(
        score_lambda(smoother, y, criterion="cv", lambda_=selected.lambda_, mu=0.15),
        rel=1e-9, abs=1e-10,
    )
    assert selected.score == pytest.approx(float(np.min(selected.scores)))
    assert selected.smoothness == pytest.approx(smoother.smoothness(selected.lambda_))
    assert len(selected.grid) == len(selected.scores)
    assert np.array_equal(selected.grid, np.sort(selected.grid))
    assert len(selected.grid) >= 99


def test_multiple_local_minima_are_compared_not_just_first_root():
    # Reproducible signal with three derivative sign changes.
    n, order, mu = 13, 2, 0.25
    y = np.random.default_rng(31).normal(size=n)
    smoother = TrendSmoother(n, order)
    probe = np.geomspace(1e-4, 1e4, 401)
    d = np.array([cv_derivative(smoother, y, lambda_=float(l), mu=mu) for l in probe])
    brackets = np.where(d[:-1] * d[1:] < 0)[0]
    assert len(brackets) >= 3
    roots = [brentq(lambda l: cv_derivative(smoother, y, lambda_=l, mu=mu),
                    probe[i], probe[i + 1]) for i in brackets]
    candidate_scores = [
        score_lambda(smoother, y, lambda_=l, criterion="cv", mu=mu) for l in roots
    ]
    candidate_scores.append(
        score_lambda(smoother, y, lambda_=np.inf, criterion="cv", mu=mu)
    )
    selected = select_lambda(smoother, y, criterion="cv", mu=mu)
    assert selected.score <= min(candidate_scores) + 1e-8
    evaluated = selected.grid[np.isfinite(selected.grid) & (selected.grid > 0)]
    assert sum(np.min(abs(np.log(evaluated / root))) < 1e-5 for root in roots) >= 3


@pytest.mark.parametrize("order", [0, 1, 2, 3])
def test_constant_and_polynomial_signals_do_not_break_search(order):
    n = 22
    smoother = TrendSmoother(n, order)
    t = np.arange(n, dtype=float)
    signals = [np.full(n, 1.3)]
    if order > 0:
        signals.append(sum((0.1 + k / 10) * (t / n)**k for k in range(order)))
    if order == 2:
        mu = 0.04
        signals.append(mu * t * (t - 1) / 2)
    for y in signals:
        fixed_mu = 0.04 if order == 2 and np.array_equal(y, signals[-1]) else 0.0
        selected = select_lambda(smoother, y, criterion="cv", mu=fixed_mu)
        assert np.isfinite(selected.score)
        assert selected.score >= 0
        assert np.isfinite(selected.scores).any()
        assert selected.score == pytest.approx(
            np.min(selected.scores[np.isfinite(selected.scores)])
        )


def test_grid_semantics_and_other_criteria_unchanged():
    y = np.random.default_rng(42).normal(size=25)
    smoother = TrendSmoother(len(y), 2)
    original_grid = np.array([np.inf, 2.3, 0.0, 0.1, 2.3])
    for criterion in ["cv", "gcv", "aicc", "bic", "mle"]:
        automatic = select_lambda(smoother, y, criterion=criterion, grid=original_grid)
        direct = select_lambda(smoother, y, criterion=criterion, method="grid",
                               grid=original_grid)
        np.testing.assert_array_equal(automatic.grid, original_grid)
        np.testing.assert_array_equal(automatic.scores, direct.scores)
        assert automatic.lambda_ == direct.lambda_
        assert_allclose(automatic.scores, [
            score_lambda(smoother, y, lambda_=float(lam), criterion=criterion)
            for lam in original_grid
        ])
        if criterion != "cv":
            auto = select_lambda(smoother, y, criterion=criterion)
            legacy = select_lambda(smoother, y, criterion=criterion, method="grid")
            np.testing.assert_array_equal(auto.grid, legacy.grid)
            np.testing.assert_array_equal(auto.scores, legacy.scores)
    with pytest.raises(ValueError):
        select_lambda(smoother, y, criterion="gcv", method="derivative")
    with pytest.raises(ValueError):
        select_lambda(smoother, y, criterion="cv", method="oops")


def test_determinism_and_actual_evaluated_candidates():
    y = np.random.default_rng(778).normal(size=20)
    smoother = TrendSmoother(len(y), 2)
    a = select_lambda(smoother, y, criterion="cv", method="derivative", mu=0.1)
    b = select_lambda(smoother, y, criterion="cv", method="auto", mu=0.1)
    np.testing.assert_array_equal(a.grid, b.grid)
    np.testing.assert_array_equal(a.scores, b.scores)
    assert a.lambda_ == b.lambda_
    assert_allclose(a.scores, [
        score_lambda(smoother, y, lambda_=float(lam), mu=0.1, criterion="cv")
        for lam in a.grid
    ], atol=1e-12, rtol=1e-12)
