"""Experiment006 mathematical reference checks (no runtime speed assertions)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from trendestimation import TrendSmoother, score_lambda, difference_matrix

HERE=Path(__file__).resolve().parents[1]/"paper"/"benchmarks"/"experiment006"
sys.path.insert(0,str(HERE))
from selected_inverse import BandedTrace, selected_inverse  # noqa: E402


@pytest.mark.parametrize("d",[1,2,3,4,5,6])
def test_selected_inverse_matches_independent_dense_inverse(d):
    n=24
    s=BandedTrace(n,d)
    for lam in (1e-3,.2,10.):
        factor=s.factor(lam)
        got=selected_inverse(factor)
        D=difference_matrix(n,d)
        truth=np.linalg.inv(np.eye(n)+lam*(D.T@D))
        for offset in range(d+1):
            np.testing.assert_allclose(
                got[offset,:n-offset],
                np.diag(truth,k=offset),atol=3e-7,rtol=3e-7)
        actual,_=s.statistics(lam,leverage=True)
        assert abs(actual-np.trace(truth))<2e-7


@pytest.mark.parametrize("d",[1,2,3,4,5,6])
def test_normalized_s_mapping_matches_public_svd(d):
    n=32
    spectral=TrendSmoother(n,d)
    trace=BandedTrace(n,d)
    for s in (.1,.5,.9):
        lam=trace.lambda_for_s(s)
        assert abs(spectral.smoothness(lam)-s)<3e-7


@pytest.mark.parametrize("d",[1,2,3,4])
@pytest.mark.parametrize("criterion",["cv","gcv","aicc","bic","mle"])
@pytest.mark.parametrize("mu",[0.,.15])
def test_selected_inverse_classical_scores_agree_with_spectral(d,criterion,mu):
    n=32
    y=np.random.default_rng(17+d).normal(size=n)
    structured=BandedTrace(n,d)
    spectral=TrendSmoother(n,d)
    for lam in (.02,3.):
        result=structured.fit_stats(y,lam,mu,criterion)
        expected=score_lambda(
            spectral,y,lambda_=lam,criterion=criterion,mu=mu)
        # All criteria, including finite-lambda MLE and exact S=1,
        # must use a single shared score normalization.
        np.testing.assert_allclose(
            result["score"],expected,rtol=3e-6,atol=3e-6)


@pytest.mark.parametrize("criterion",["cv","gcv","aicc","bic","mle"])
def test_exact_s_one_endpoint_is_not_a_huge_finite_lambda(criterion):
    n,d=32,2
    y=np.random.default_rng(83).normal(size=n)
    method=BandedTrace(n,d)
    lam=method.lambda_for_s(1.)
    assert np.isposinf(lam)
    result=method.fit_stats(y,lam,.15,criterion)
    expected=score_lambda(
        TrendSmoother(n,d),y,lambda_=float("inf"),
        criterion=criterion,mu=.15)
    np.testing.assert_allclose(
        result["score"],expected,rtol=1e-6,atol=1e-6)


def test_no_n_by_n_inverse_or_dense_eigendecomposition_in_large_plan():
    n,d=1000,6
    plan=BandedTrace(n,d)
    assert plan.bands.shape==(d+1,n)
    assert plan.D.shape==(n-d,n)
    lam=.5
    edf,_=plan.statistics(lam)
    assert d<edf<n
    assert 0<plan.smoothness(lam)<1


def test_invalid_inputs():
    with pytest.raises(ValueError):
        BandedTrace(10,0)
    with pytest.raises(ValueError):
        BandedTrace(6,6)
    plan=BandedTrace(24,2)
    with pytest.raises(ValueError):
        plan.lambda_for_s(1.1)
