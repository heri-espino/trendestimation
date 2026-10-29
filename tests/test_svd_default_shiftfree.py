"""Regression tests for the SVD-by-default, shift-free fit policy."""
import numpy as np
import pytest
from scipy.linalg import lstsq

from trendestimation import TrendSmoother
from trendestimation.solvers import PreparedPLSSolver, fit_penalized


@pytest.mark.parametrize("order", [1, 2, 5, 6])
@pytest.mark.parametrize("mean_mode", [0.0, "data"])
def test_full_svd_default_matches_independent_scaled_qr(order, mean_mode):
    n = 48
    rng = np.random.default_rng(20261029 + order)
    y = np.sin(np.linspace(0.0, 8.0, n)) + rng.normal(0.0, .18, n)
    smoother = TrendSmoother(n, order=order)
    chosen_s = .999 if order >= 5 else .88
    lam = smoother.lambda_for_smoothness(chosen_s)
    mu = float(np.mean(smoother.D @ y)) if mean_mode == "data" else 0.0
    # Independent scaled, rectangular QR formulation of the same PLS.
    weight = np.sqrt(1.0 / lam)
    stacked = np.vstack((smoother.D, weight * np.eye(n)))
    rhs = np.r_[np.full(n-order, mu), weight*y]
    reference = lstsq(
        stacked, rhs, cond=1e-15, lapack_driver="gelsy",
    )[0]

    full = smoother.fit(y, lambda_=lam, mu=mean_mode).trend
    prepared = PreparedPLSSolver(n, order=order)
    assert prepared.method == "svd"
    from_default = prepared.fit(y, lambda_=lam, mu=mean_mode)
    single = fit_penalized(y, lambda_=lam, order=order, mu=mean_mode)
    many = prepared.fit_many(y, [lam], mu=mean_mode)[0]

    scale = max(1., float(np.linalg.norm(reference)))
    for candidate in (full, from_default, single, many):
        assert np.linalg.norm(candidate-reference)/scale < 1e-6


def test_full_svd_default_retains_exact_endpoints():
    y = np.array([.5, 1.2, -.5, 1.1, .2, .8, 1.5, -1.0])
    solver = PreparedPLSSolver(len(y), order=2)
    assert np.allclose(solver.fit(y,lambda_=0),y)
    finite = solver.fit(y,lambda_=np.inf,mu=0.)
    # The d=2 nullspace contains exactly linear trends.
    assert np.linalg.norm(np.diff(finite,n=2)) < 1e-9
