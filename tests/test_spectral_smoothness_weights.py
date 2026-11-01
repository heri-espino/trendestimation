"""Direct-S spectral-weight fitting equals the existing normalized PLS path."""
import numpy as np
import pytest

from trendestimation import TrendSmoother
from trendestimation.smoothness_weights import fit_spectral_smoothness


@pytest.mark.parametrize("d", [1, 2, 3, 4, 5, 6])
@pytest.mark.parametrize("smoothness", [0.0, 0.1, 0.5, 0.87, 0.99, 1 - 1e-10, 1.0])
@pytest.mark.parametrize("mu", [0.0, 0.007, "data"])
def test_direct_weights_equal_existing_pls(d, smoothness, mu):
    n=36
    rng=np.random.default_rng(125+d)
    x=np.linspace(0,1,n)
    y=.5*x+.4*x*x+.35*np.sin(5*x)+rng.normal(0,.08,n)
    solver=TrendSmoother(n,order=d)
    direct=fit_spectral_smoothness(solver,y,smoothness=smoothness,mu=mu)
    penalty=solver.lambda_for_smoothness(smoothness)
    expected=solver.fit(y,lambda_=penalty,mu=mu)
    np.testing.assert_allclose(direct.trend,expected.trend,rtol=2e-8,atol=3e-8)
    np.testing.assert_allclose(direct.residual,expected.residual,rtol=2e-8,atol=3e-8)
    assert abs(direct.smoothness-expected.smoothness)<2e-11
    assert direct.edf_conditional==pytest.approx(expected.edf_conditional,abs=2e-9)
    assert direct.mu==pytest.approx(expected.mu)
    assert direct.root_function_evaluations==0 if smoothness in (0.,1.) else direct.root_function_evaluations>0


@pytest.mark.parametrize("d", [1,3,6])
def test_direct_fit_handles_extreme_near_one_smoothness(d):
    n=50
    y=np.sin(np.linspace(0,5,n))+.01*np.arange(n)
    solver=TrendSmoother(n,order=d)
    for s in (1e-14, 1-1e-14):
        direct=fit_spectral_smoothness(solver,y,smoothness=s,mu=0.)
        lam=solver.lambda_for_smoothness(s)
        baseline=solver.fit(y,lambda_=lam,mu=0.)
        np.testing.assert_allclose(direct.trend,baseline.trend,rtol=1e-9,atol=1e-9)


def test_scalar_spectrum_weight_has_analytic_solution():
    n,d=10,9
    solver=TrendSmoother(n,order=d)
    y=np.arange(n,dtype=float)
    direct=fit_spectral_smoothness(solver,y,smoothness=0.67,mu=0.)
    old=solver.fit(y,lambda_=solver.lambda_for_smoothness(.67),mu=0.)
    np.testing.assert_allclose(direct.trend,old.trend,atol=1e-11)


@pytest.mark.parametrize("invalid", [-0.1, 1.00001, np.nan, np.inf])
def test_reject_invalid_smoothness(invalid):
    model=TrendSmoother(12,order=3)
    with pytest.raises(ValueError,match="smoothness"):
        fit_spectral_smoothness(model,np.arange(12.),smoothness=invalid)


def test_input_validation_and_no_svd_refactor():
    solver=TrendSmoother(18,order=3)
    y=np.linspace(1.,2.,18)
    with pytest.raises(ValueError,match="1-D"):
        fit_spectral_smoothness(solver,np.ones((18,1)),smoothness=.5)
    with pytest.raises(ValueError,match="mu"):
        fit_spectral_smoothness(solver,y,smoothness=.5,mu="unknown")
    with pytest.raises(ValueError,match="tol"):
        fit_spectral_smoothness(solver,y,smoothness=.5,tol=0)
    with pytest.raises(ValueError,match="maxiter"):
        fit_spectral_smoothness(solver,y,smoothness=.5,maxiter=0)
    direct=fit_spectral_smoothness(solver,y,smoothness=.5)
    assert direct.root_function_evaluations>0
    assert direct.trend.shape==(18,)
