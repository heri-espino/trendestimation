"""Direct dense-B regression checks for the Gaussian REML identity.

The existing API remains unchanged. This test proves that the repo's
positive-penalty spectral score is the same Gaussian fixed-mu REML as
the author's direct Dy-mu1 covariance objective, up to -logdet(DD.T).
"""
from __future__ import annotations

from math import comb

import numpy as np
import pytest

from trendestimation import TrendSmoother, score_lambda


def _example(n: int, d: int, mu: float) -> tuple[np.ndarray, np.ndarray]:
    t = np.arange(n, dtype=float)
    rng = np.random.default_rng(8431 + n + d)
    # A shifted d-th degree binomial polynomial has D_d p_mu = mu * 1.
    p = mu * np.array([comb(int(i), d) for i in t], dtype=float)
    y = 2.0 + 0.6 * t + 0.004 * t*t + p + rng.normal(0.0, 0.15, n)
    return y, p


def _dense_fixed_mu(smoother: TrendSmoother, y: np.ndarray,
                    lam: float, mu: float) -> tuple[float, float]:
    D = smoother.D
    B = D @ D.T
    z = D @ y - mu
    W = np.eye(len(z)) + lam * B
    logdet_sign, logdet = np.linalg.slogdet(W)
    if logdet_sign != 1:
        raise ValueError("Covariance must be positive definite")
    q = float(z @ np.linalg.solve(W, z))
    objective = logdet + len(z) * np.log(q / len(z))
    return float(objective), float(np.linalg.slogdet(B)[1])


@pytest.mark.parametrize("order", [1, 2, 3, 4])
@pytest.mark.parametrize("mu", [0.0, 0.013, -0.026])
@pytest.mark.parametrize("lam", [0.002, 0.4, 5.0, 100.0])
def test_existing_mle_matches_guerrero_fixed_mean_reml(
    order: int, mu: float, lam: float,
):
    y, _ = _example(25, order, mu)
    smoother = TrendSmoother(len(y), order=order)
    direct, logdet_b = _dense_fixed_mu(smoother, y, lam, mu)
    existing = score_lambda(
        smoother, y, lambda_=lam, mu=mu, criterion="mle"
    )
    # Equality up to constant -(sum log positive eigenvalues) = -logdet B.
    np.testing.assert_allclose(
        existing, direct - logdet_b, rtol=5e-10, atol=3e-8,
    )


@pytest.mark.parametrize("lam", [0.01, 0.7, 3.0, 55.0])
def test_direct_covariance_derivative_and_spectral_score_have_same_gradient(lam):
    smoother = TrendSmoother(32, order=3)
    y, _ = _example(32, 3, 0.015)
    mu = 0.015
    D = smoother.D
    B = D @ D.T
    z = D @ y - mu
    W = np.eye(len(z)) + lam * B
    invz = np.linalg.solve(W, z)
    invb = np.linalg.solve(W, B)
    q = float(z @ invz)
    analytic = float(np.trace(invb) - len(z) * (invz @ B @ invz) / q)
    step = lam * 1e-5
    up = score_lambda(smoother, y, lambda_=lam+step, mu=mu, criterion="mle")
    down = score_lambda(smoother, y, lambda_=lam-step, mu=mu, criterion="mle")
    numerical = (up-down) / (2*step)
    np.testing.assert_allclose(numerical, analytic, rtol=1e-5, atol=1e-6)


def _reml_unknown_mu(smoother: TrendSmoother, y: np.ndarray,
                     lam: float) -> tuple[float, float, float]:
    """Independent dense formula for *future* implementation, not current API."""
    D = smoother.D
    v = D @ y
    m = len(v)
    if m < 2:
        raise ValueError("Unknown reference requires m >= 2")
    W = np.eye(m) + lam * (D @ D.T)
    one = np.ones(m)
    invone = np.linalg.solve(W, one)
    invv = np.linalg.solve(W, v)
    info = float(one @ invone)
    mu_hat = float(one @ invv / info)
    residual = v - mu_hat*one
    q = float(residual @ np.linalg.solve(W, residual))
    score = (
        np.linalg.slogdet(W)[1]
        + np.log(info)
        + (m-1) * np.log(q/(m-1))
    )
    return float(score), mu_hat, float(one @ np.linalg.solve(W, residual))


def test_unknown_mean_reml_differs_from_sample_plug_in_and_gls_is_orthogonal():
    smoother = TrendSmoother(38, order=3)
    y, _ = _example(38, 3, 0.03)
    lam = 8.0
    proper, mu_hat, orthogonality = _reml_unknown_mu(smoother, y, lam)
    sample = float(np.mean(smoother.D @ y))
    plug_in = score_lambda(
        smoother, y, lambda_=lam, mu=sample, criterion="mle"
    )
    assert np.isfinite(proper) and np.isfinite(mu_hat)
    assert abs(orthogonality) < 1e-9
    # The models use different nuisance-parameter elimination terms,
    # not just the fixed covariance determinant constant.
    assert abs(mu_hat - sample) > 1e-6
    assert np.isfinite(plug_in)


def test_unknown_mean_reml_is_invariant_to_added_degree_d_reference():
    smoother = TrendSmoother(35, order=3)
    y, _ = _example(35, 3, 0.01)
    n = len(y)
    shift = 0.02 * np.array([comb(i, 3) for i in range(n)])
    D = smoother.D
    np.testing.assert_allclose(D @ shift, 0.02, atol=1e-11)
    for lam in (0.1, 2.0, 40.0):
        a, ma, _ = _reml_unknown_mu(smoother, y, lam)
        b, mb, _ = _reml_unknown_mu(smoother, y+shift, lam)
        np.testing.assert_allclose(a, b, atol=1e-7, rtol=0)
        np.testing.assert_allclose(mb-ma, 0.02, atol=1e-10, rtol=0)
