"""Experiment006: independent dense likelihood, derivative and boundary tests."""
from __future__ import annotations

from math import comb
from pathlib import Path
import sys

import numpy as np
import pytest

from trendestimation import TrendSmoother

HERE = Path(__file__).resolve().parents[1] / "paper" / "ngsim-jerk-case-study"
sys.path.insert(0, str(HERE / "experiments" / "experiment006"))
from reml import DifferenceLikelihood  # noqa: E402


def dense_unknown(smoother, y, lam):
    D = smoother.D
    v = D @ y
    m = len(v)
    W = np.eye(m) + lam*(D @ D.T)
    invone = np.linalg.solve(W, np.ones(m))
    invv = np.linalg.solve(W, v)
    a = float(invone.sum())
    mu = float(invv.sum()/a)
    r = v - mu
    q = float(r @ np.linalg.solve(W, r))
    score = float(np.linalg.slogdet(W)[1] + np.log(a)
                  + (m-1)*np.log(q/(m-1)))
    return score, mu


@pytest.mark.parametrize("d", [1, 2, 3, 4])
@pytest.mark.parametrize("lam", [0.001, 0.1, 3.0, 200.0])
def test_profile_gls_and_remllikelihood_match_dense_matrix(d, lam):
    rng = np.random.default_rng(994 + d)
    y = 2 + 0.2*np.arange(30) + rng.normal(0, .15, size=30)
    s = TrendSmoother(30, order=d)
    solver = DifferenceLikelihood(s)
    score, mu, grad = solver.score(solver.transform(y), lam)
    direct_score, direct_mu = dense_unknown(s, y, lam)
    np.testing.assert_allclose(score, direct_score, rtol=1e-8, atol=2e-7)
    np.testing.assert_allclose(mu, direct_mu, rtol=1e-8, atol=2e-7)
    step = lam*1e-5
    a = solver.score(solver.transform(y), lam+step)[0]
    b = solver.score(solver.transform(y), lam-step)[0]
    np.testing.assert_allclose(grad, (a-b)/(2*step), rtol=3e-5, atol=1e-5)


def test_unknown_mu_interpolates_between_raw_difference_mean_and_cubic_ols():
    s = TrendSmoother(80, order=3)
    rng = np.random.default_rng(123)
    t = np.arange(80, dtype=float)
    y = 15 + 0.4*t + 0.03*t*t + 0.0001*t**3 + rng.normal(0, .5, 80)
    solver = DifferenceLikelihood(s)
    v = solver.transform(y)
    raw = float(np.mean(s.D @ y))
    ols = float(6*np.polynomial.Polynomial.fit(t, y, 3).convert().coef[3])
    mu_at_zero = solver.score(v, 0.0)[1]
    mu_at_inf = solver.score(v, float("inf"))[1]
    np.testing.assert_allclose(mu_at_zero, raw, atol=1e-9)
    np.testing.assert_allclose(mu_at_inf, ols, atol=1e-5, rtol=0)


def test_cubic_shift_changes_mean_but_not_joint_profile_score():
    s = TrendSmoother(45, order=3)
    rng = np.random.default_rng(245)
    y = 4+0.9*np.arange(45)+rng.normal(0,.3,45)
    cubic = np.array([comb(i,3) for i in range(45)],dtype=float) * 0.01
    solver = DifferenceLikelihood(s)
    for lam in (0.0,0.5,10.0,float("inf")):
        score, mu, _ = solver.score(solver.transform(y),lam)
        score2, mu2, _ = solver.score(solver.transform(y+cubic),lam)
        np.testing.assert_allclose(score,score2,rtol=0,atol=1e-5)
        np.testing.assert_allclose(mu2-mu,0.01,rtol=0,atol=1e-8)


def test_continuous_optimum_is_not_worse_than_initial_grid():
    rng = np.random.default_rng(312)
    n = 80
    t = np.arange(n)*0.1
    y = 18*t + .2*t**3/6 + rng.normal(0,0.1,n)
    s = TrendSmoother(n, order=3)
    solver = DifferenceLikelihood(s)
    grid = tuple(s.lambda_for_smoothness(v) for v in (.05,.1,.2,.4,.6,.8,.95,.99))
    continuous = solver.optimize(y,search="continuous")
    discrete = solver.optimize(y,search="grid",grid=grid)
    assert np.isfinite(continuous.score) and np.isfinite(discrete.score)
    # The log mesh is much denser than the coarse candidate grid;
    # minor differences due to finite numerical refinement are allowed.
    assert continuous.score <= discrete.score + .03
    assert 0 <= continuous.smoothness <= 1
    assert continuous.n_evaluations >= 63


def test_invalid_parameters_are_rejected():
    s = TrendSmoother(30,order=3)
    model = DifferenceLikelihood(s)
    v = model.transform(np.linspace(0,10,30)+.01*np.sin(np.arange(30)))
    with pytest.raises(ValueError):
        model.score(v, -1)
    with pytest.raises(ValueError):
        model.score(v,np.nan)
    with pytest.raises(ValueError):
        model.score(v,1,fixed_mu=np.nan)
    with pytest.raises(ValueError):
        model.optimize(np.zeros(30),search="grid",grid=())


def test_guerrero_existing_plug_in_not_same_as_unknown_mean_reml():
    s=TrendSmoother(45,order=3)
    rng=np.random.default_rng(55)
    y=rng.normal(0,.15,45)+.1*np.arange(45)
    model=DifferenceLikelihood(s)
    v=model.transform(y)
    ml=model.score(v,5,fixed_mu=float(np.mean(s.D@y)))[0]
    proper=model.score(v,5)[0]
    assert np.isfinite(ml) and np.isfinite(proper)
    assert not np.isclose(ml,proper,rtol=1e-8,atol=1e-8)
