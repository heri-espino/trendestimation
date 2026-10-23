"""Search equivalence and robust boundaries for normalized smoothness coordinates."""
from __future__ import annotations

import numpy as np
import pytest
from numpy.testing import assert_allclose

from trendestimation import TrendSmoother, score_lambda, select_lambda
from trendestimation.criteria import cv_derivative


@pytest.mark.parametrize("order", [0, 1, 2, 4])
@pytest.mark.parametrize("criterion", ["cv", "gcv", "aicc", "bic"])
def test_same_explicit_candidates_have_same_original_scores(order, criterion):
    rng = np.random.default_rng(2320 + order)
    y = rng.normal(size=20) + 0.1 * np.arange(20)
    solver = TrendSmoother(len(y), order)
    mu = 0.17
    penalties = np.array([np.inf, 2.0, 0.0, 0.1, 2.0, 50.0])
    s = np.array([solver.smoothness(p) for p in penalties])
    by_lambda = select_lambda(
        solver, y, criterion=criterion, mu=mu, grid=penalties,
        search_space="lambda",
    )
    by_s = select_lambda(
        solver, y, criterion=criterion, mu=mu, grid=s,
        search_space="smoothness",
    )
    assert by_s.search_space == "smoothness"
    assert by_lambda.search_space == "lambda"
    assert_allclose(by_s.search_grid, s, rtol=0, atol=0)
    assert_allclose(by_lambda.search_grid, penalties, rtol=0, atol=0)
    assert_allclose(by_s.grid, penalties, rtol=2e-9, atol=1e-10)
    assert_allclose(by_s.scores, by_lambda.scores, rtol=1e-9, atol=1e-10)
    # For order zero, classical CV is flat over positive penalties:
    # equivalent finite search grids need not select the same tied value
    # after inverse-map roundoff, but their optimal scores must agree.
    if order == 0 and criterion == "cv":
        assert by_s.score == pytest.approx(by_lambda.score, abs=1e-10)
    else:
        assert by_s.lambda_ == pytest.approx(by_lambda.lambda_, rel=2e-9)
        assert by_s.smoothness == pytest.approx(by_lambda.smoothness, abs=1e-12)


def test_conditional_mle_preserves_data_mean_and_boundary():
    rng = np.random.default_rng(2345)
    y = rng.normal(size=32) + np.arange(32) * 0.05
    solver = TrendSmoother(len(y), 2)
    grid = np.array([0.0, 0.1, 1.0, 50.0, np.inf])
    s = np.array([solver.smoothness(lam) for lam in grid])
    raw = select_lambda(
        solver, y, criterion="mle", mu="data", grid=grid,
    )
    changed = select_lambda(
        solver, y, criterion="mle", mu="data", grid=s,
        search_space="smoothness",
    )
    assert np.isinf(changed.scores[0])
    assert_allclose(raw.scores, changed.scores, rtol=1e-9, atol=1e-9)
    assert changed.score == pytest.approx(raw.score)
    assert changed.lambda_ == pytest.approx(raw.lambda_, rel=1e-9)
    assert changed.smoothness == pytest.approx(s[np.argmin(raw.scores)])


def test_default_lambda_selection_still_uses_original_grid():
    rng = np.random.default_rng(913)
    y = rng.normal(size=28)
    solver = TrendSmoother(len(y), 2)
    default = select_lambda(solver, y, criterion="gcv")
    explicit = select_lambda(
        solver, y, criterion="gcv", search_space="lambda",
    )
    assert_allclose(default.grid, explicit.grid)
    assert_allclose(default.scores, explicit.scores)
    assert default.search_space == "lambda"
    assert_allclose(default.search_grid, default.grid)


def test_default_s_grid_hits_both_endpoints_and_is_not_lambda_grid():
    y = np.random.default_rng(130).normal(size=21)
    solver = TrendSmoother(len(y), 2)
    selected = select_lambda(
        solver, y, criterion="gcv", search_space="smoothness",
        method="grid",
    )
    assert selected.search_grid[0] == 0.0
    assert selected.search_grid[-1] == 1.0
    assert selected.grid[0] == 0.0
    assert np.isinf(selected.grid[-1])
    assert len(selected.search_grid) == len(selected.grid) == len(selected.scores)
    assert selected.smoothness == pytest.approx(
        solver.smoothness(selected.lambda_)
    )


@pytest.mark.parametrize("order", [0, 1, 2, 4])
def test_analytical_cv_s_search_against_dense_lambda_reference(order):
    rng = np.random.default_rng(102 + order)
    y = rng.normal(size=18) + 0.1 * np.arange(18)
    solver = TrendSmoother(len(y), order)
    mu = -0.15
    from_s = select_lambda(
        solver, y, criterion="cv", mu=mu,
        search_space="smoothness",
    )
    # Reference uses the existing log-lambda derivative method.
    from_lambda = select_lambda(
        solver, y, criterion="cv", mu=mu,
        search_space="lambda",
    )
    assert np.isfinite(from_s.score)
    assert from_s.score <= from_lambda.score + 1e-5
    assert_allclose(from_s.scores, [
        score_lambda(solver, y, criterion="cv", mu=mu, lambda_=lam)
        for lam in from_s.grid
    ], rtol=2e-12, atol=2e-12)
    assert_allclose(
        from_s.search_grid,
        [solver.smoothness(lam) for lam in from_s.grid],
        atol=2e-11, rtol=0,
    )
    assert np.array_equal(from_s.search_grid, np.sort(from_s.search_grid))
    assert len(from_s.search_grid) >= 180


def test_cv_derivative_chain_rule_matches_finite_difference_in_s():
    rng = np.random.default_rng(42)
    y = rng.normal(size=23)
    solver = TrendSmoother(len(y), 2)
    mu = 0.2
    for s in (0.12, 0.45, 0.8):
        lam = solver.lambda_for_smoothness(s)
        positive = solver.eigenvalues[: solver.n - solver.order]
        derivative_s = (
            cv_derivative(solver, y, lambda_=lam, mu=mu)
            / np.mean(positive / (1 + lam * positive)**2)
        )
        step = 1e-5

        def cv_at_s(value):
            inverse = solver.lambda_for_smoothness(value)
            return score_lambda(
                solver, y, lambda_=inverse, criterion="cv", mu=mu,
            )

        numerical = (cv_at_s(s + step) - cv_at_s(s - step)) / (2 * step)
        assert_allclose(derivative_s, numerical, rtol=1e-5, atol=2e-6)


@pytest.mark.parametrize("invalid", [-0.1, 1.0001, np.nan, np.inf, -np.inf])
def test_smoothness_grid_rejects_non_normalized_values(invalid):
    solver = TrendSmoother(15, 2)
    y = np.arange(15, dtype=float)
    with pytest.raises(ValueError, match="smoothness grid"):
        select_lambda(
            solver, y, criterion="gcv", search_space="smoothness",
            grid=[0.2, invalid],
        )


def test_invalid_space_derivative_and_mean_semantics():
    y = np.random.default_rng(10).normal(size=20)
    solver = TrendSmoother(len(y), 2)
    with pytest.raises(ValueError, match="search_space"):
        select_lambda(solver, y, search_space="unknown")
    with pytest.raises(ValueError, match="only supported"):
        select_lambda(
            solver, y, criterion="bic", method="derivative",
            search_space="smoothness",
        )
    with pytest.raises(ValueError, match="not both"):
        select_lambda(
            solver, y, criterion="cv", method="derivative",
            search_space="smoothness", grid=[0.5],
        )
    with pytest.raises(ValueError, match="fixed mu"):
        select_lambda(
            solver, y, criterion="cv", mu="data",
            search_space="smoothness",
        )
    with pytest.raises(ValueError, match="smoothness grid"):
        select_lambda(
            solver, y, criterion="gcv", search_space="smoothness", grid=[],
        )
    with pytest.raises(ValueError, match="smoothness grid"):
        select_lambda(
            solver, y, criterion="gcv", search_space="smoothness", grid=[0.5, 2],
        )


def test_unrepresentable_interior_s_not_silently_mapped_to_endpoint():
    solver = TrendSmoother(30, 2)
    y = np.random.default_rng(1).normal(size=30)
    with pytest.raises(OverflowError):
        select_lambda(
            solver, y, search_space="smoothness", criterion="gcv",
            grid=[np.nextafter(0.0, 1.0)],
        )
