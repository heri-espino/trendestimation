"""Regression tests for an S-only public PLS interface."""
import numpy as np
import pytest

from trendestimation import TrendSmoother, fit_smoothness


@pytest.mark.parametrize("n,order,target,mu", [
    (19, 1, 0.35, 0.0),
    (28, 2, 0.86, 0.15),
    (36, 3, 0.63, 0.0),
    (29, 4, 0.95, 0.05),
    (20, 2, 0.0, 0.15),
    (20, 2, 1.0, 0.15),
])
def test_smoothness_only_fit_has_exact_existing_estimator(n, order, target, mu):
    data=np.linspace(-1, 2, n) + 0.31*np.sin(np.arange(n)*1.4)
    smoother=TrendSmoother(n, order=order)
    penalty=smoother.lambda_for_smoothness(target)
    old=smoother.fit(data, lambda_=penalty, mu=mu)
    new=smoother.fit_smoothness(data, smoothness=target, mu=mu)
    simple=fit_smoothness(data, smoothness=target, order=order, mu=mu)
    np.testing.assert_allclose(new.trend,old.trend,rtol=5e-13,atol=1e-12)
    np.testing.assert_allclose(simple.trend,old.trend,rtol=5e-13,atol=1e-12)
    assert new.lambda_==old.lambda_
    assert np.isclose(new.smoothness,target,atol=5e-12)
    assert np.isclose(simple.smoothness,target,atol=5e-12)


def test_smoothness_only_fit_supports_mu_data_without_claiming_joint_edf():
    n=25
    y=2+np.linspace(0, 4, n)**2 + np.sin(np.linspace(0, 7, n))
    model=TrendSmoother(n,order=2)
    reference=model.fit_smoothness(y,smoothness=.72,mu="data")
    actual=fit_smoothness(y,smoothness=.72,order=2,mu="data")
    np.testing.assert_allclose(actual.trend,reference.trend,atol=1e-12)
    assert np.isfinite(actual.edf_conditional)


@pytest.mark.parametrize("target",[-0.1, 1.1, float("nan"), float("inf")])
def test_smoothness_only_rejects_invalid_targets(target):
    with pytest.raises(ValueError,match="smoothness"):
        fit_smoothness(np.arange(12.0),smoothness=target)


def test_smoothness_only_rejects_non_vector():
    with pytest.raises(ValueError,match="one-dimensional"):
        fit_smoothness(np.ones((3,4)),smoothness=0.5)


def test_smoothness_only_solver_choice_is_explicit():
    model=TrendSmoother(22,order=2)
    y=np.sin(np.linspace(0,3,22))
    a=model.fit_smoothness(y,smoothness=0.61,method="brentq")
    b=model.fit_smoothness(y,smoothness=0.61,method="newton")
    np.testing.assert_allclose(a.trend,b.trend,rtol=1e-11,atol=1e-11)
