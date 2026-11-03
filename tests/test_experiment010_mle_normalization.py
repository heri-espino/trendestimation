"""Regression: all MLE benchmark pipelines must use the same score zero."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(
    Path(__file__).resolve().parents[1] / "paper" / "benchmarks" / "experiment006"))

from run import naive_score  # noqa: E402
from selected_inverse import BandedTrace, difference_gram_logdet  # noqa: E402
from trendestimation import TrendSmoother  # noqa: E402
from trendestimation.criteria import _score_from_coordinates  # noqa: E402
from trendestimation.core import difference_matrix  # noqa: E402


@pytest.mark.parametrize("n", [8, 12, 24])
@pytest.mark.parametrize("d", [1, 2, 3, 4, 5, 6])
def test_difference_gram_logdet_closed_product_against_dense_small(n, d):
    D = difference_matrix(n, d)
    sign, logdet = np.linalg.slogdet(D @ D.T)
    assert sign > 0
    assert np.isclose(difference_gram_logdet(n, d), logdet,
                      rtol=0., atol=1e-7)


def test_large_n_logdet_requires_no_dense_matrix():
    assert np.isfinite(difference_gram_logdet(131072, 6))
    assert difference_gram_logdet(64, 5) == pytest.approx(
        66.32448169, abs=1e-6)


@pytest.mark.parametrize("d", [1, 2, 3])
@pytest.mark.parametrize("mode", ["zero", "data", "fixed"])
@pytest.mark.parametrize("s", [0.25, 0.75, 1.0])
def test_mle_score_normalization_consistent_at_finite_and_infinite_S(
        d, mode, s):
    n = 32
    rng = np.random.default_rng(421 + d)
    y = 2.*np.sin(np.linspace(0, 3, n)) + rng.normal(0., .2, n)
    mu = (0.0 if mode == "zero" else
          float(np.mean(np.diff(y, n=d))) if mode == "data" else
          0.15)
    smoother = TrendSmoother(n, d)
    lam = smoother.lambda_for_smoothness(s)
    _, _, _, coord = smoother._prepare(y, mu)
    expected = _score_from_coordinates(
        smoother, coord, lambda_=lam, name="mle")
    actual = BandedTrace(n, d).fit_stats(y, lam, mu, "mle")["score"]
    assert np.isclose(actual, expected, rtol=1e-7, atol=1e-7)
    if np.isfinite(lam):
        inverse = naive_score(n, d, y, lam, mu, "mle")
        assert np.isclose(inverse, expected, rtol=1e-7, atol=1e-7)
