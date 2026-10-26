"""Full-range S-grids and mapped-penalty selection must agree exactly."""
from __future__ import annotations

import numpy as np

from trendestimation import TrendSmoother, select_lambda
from trendestimation._docs_coordinates import notebook_s_grid


def test_default_doc_grid_covers_exact_limits_and_high_smoothness_tail():
    s = notebook_s_grid()
    np.testing.assert_allclose(s[:1], [0])
    assert len(s) == 16
    assert s[-1] == 1.0
    assert np.all(np.diff(s) > 0)
    for target in np.linspace(0, 1, 11):
        assert np.any(np.isclose(s, target, rtol=0, atol=1e-15))
    for near_one in (0.95, 0.99, 0.999, 0.9999, 0.999999):
        assert near_one in s


def test_s_grid_inversion_roundtrips_and_scores_are_mapped_penalty_scores():
    y = np.random.default_rng(10).normal(size=36)
    smoother = TrendSmoother(len(y), order=2)
    s_grid = notebook_s_grid()
    penalty_grid = np.asarray([
        smoother.lambda_for_smoothness(float(s)) for s in s_grid])
    recovered_s = np.asarray([smoother.smoothness(float(lam))
                              for lam in penalty_grid])
    assert penalty_grid[0] == 0.0
    assert np.isposinf(penalty_grid[-1])
    assert np.all(np.diff(penalty_grid) > 0)
    np.testing.assert_allclose(recovered_s, s_grid, atol=1e-10, rtol=0)
    for criterion in ("cv", "gcv", "aicc", "bic"):
        direct = select_lambda(smoother, y, criterion=criterion,
                               mu=0.0, search_space="smoothness",
                               grid=s_grid)
        mapped = select_lambda(smoother, y, criterion=criterion,
                               mu=0.0, search_space="lambda",
                               grid=penalty_grid)
        np.testing.assert_allclose(mapped.grid, direct.grid,
                                   rtol=1e-10, atol=1e-10)
        np.testing.assert_allclose(mapped.scores, direct.scores,
                                   rtol=1e-8, atol=1e-8)
        assert mapped.lambda_ == direct.lambda_
        assert mapped.smoothness == direct.smoothness


def test_representative_classical_cv_endpoint_undefined():
    y = np.random.default_rng(11).normal(size=24)
    smoother = TrendSmoother(len(y), order=2)
    result = select_lambda(smoother, y, criterion="cv", grid=[0, 1, np.inf])
    assert np.isposinf(result.scores[0])
    assert np.any(np.isfinite(result.scores[1:]))
