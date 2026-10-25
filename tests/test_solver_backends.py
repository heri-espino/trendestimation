"""Numerical correctness and API boundaries of alternative PLS fit backends."""
import numpy as np
import pytest
from numpy.testing import assert_allclose

from trendestimation import TrendSmoother, difference_matrix
from trendestimation.solvers import PreparedPLSSolver, fit_penalized


@pytest.mark.parametrize("d", [0, 1, 2, 3])
@pytest.mark.parametrize("mean_mode", [0.0, 0.15, "data"])
@pytest.mark.parametrize("lam", [0.0, 1e-5, 0.3, 20.0, 1e3, np.inf])
def test_full_trend_parity_all_backends(d, mean_mode, lam):
    n = 27
    rng = np.random.default_rng(39 + d)
    y = rng.normal(size=n) + 0.2 * np.arange(n) / n
    baseline = TrendSmoother(n, d).fit(
        y, lambda_=lam, mu=mean_mode,
    ).trend
    for method in ("svd", "eigh", "cholesky"):
        fitter = PreparedPLSSolver(n, d, method=method)
        actual = fitter.fit(y, lambda_=lam, mu=mean_mode)
        assert_allclose(
            actual, baseline, rtol=2e-7, atol=2e-7,
            err_msg=f"method={method}, d={d}, lambda={lam}",
        )


@pytest.mark.parametrize("d", [0, 1, 2, 4])
def test_against_independent_dense_normal_equations(d):
    rng = np.random.default_rng(402 + d)
    y = rng.normal(size=20)
    mu, lam = 0.08, 9.0
    D = difference_matrix(len(y), d)
    Q = D.T @ D
    truth = np.linalg.solve(
        np.eye(len(y)) + lam * Q,
        y + lam * mu * D.T @ np.ones(len(y) - d),
    )
    for method in ("svd", "eigh", "cholesky"):
        assert_allclose(
            fit_penalized(y, lambda_=lam, mu=mu, order=d, method=method),
            truth, rtol=1e-8, atol=1e-8,
        )


@pytest.mark.parametrize("method", ["svd", "eigh", "cholesky"])
def test_multiple_penalties_share_setup_and_match_single_fit(method):
    rng = np.random.default_rng(7)
    y = rng.standard_normal(31)
    penalties = [0.0, 1e-4, 0.9, 90.0, np.inf]
    fitter = PreparedPLSSolver(len(y), 2, method=method)
    batch = fitter.fit_many(y, penalties, mu="data")
    singles = np.stack([
        fitter.fit(y, lambda_=lam, mu="data") for lam in penalties
    ])
    assert batch.shape == (len(penalties), len(y))
    assert_allclose(batch, singles, atol=3e-9, rtol=3e-9)
    assert fitter.fit_many(y, [], mu=0.0).shape == (0, len(y))


@pytest.mark.parametrize("method", ["svd", "eigh", "cholesky"])
def test_infinite_penalty_enforces_target_differences(method):
    y = np.random.default_rng(65).normal(size=35)
    solver = PreparedPLSSolver(35, order=2, method=method)
    fitted = solver.fit(y, lambda_=np.inf, mu=0.125)
    D = difference_matrix(35, 2)
    assert_allclose(D @ fitted, 0.125, atol=1e-8)


def test_stored_memory_is_spectral_quadratic_banded_linear():
    n, d = 30, 2
    svd = PreparedPLSSolver(n, d, method="svd")
    eigh = PreparedPLSSolver(n, d, method="eigh")
    chol = PreparedPLSSolver(n, d, method="cholesky")
    assert chol.stored_bytes == 8 * (d + 1) * n
    assert svd.stored_bytes >= 8 * n * n
    assert eigh.stored_bytes >= 8 * n * n


@pytest.mark.parametrize("n,d,method", [
    (0, 0, "svd"),
    (12, 12, "eigh"),
    (10, -1, "cholesky"),
    (10, 1, "inverse"),
])
def test_invalid_constructor(n, d, method):
    with pytest.raises(ValueError):
        PreparedPLSSolver(n, d, method=method)


def test_invalid_penalties_and_data():
    solver = PreparedPLSSolver(12, order=2, method="cholesky")
    y = np.arange(12, dtype=float)
    with pytest.raises(ValueError):
        solver.fit(y, lambda_=-1)
    with pytest.raises(ValueError):
        solver.fit(y, lambda_=np.nan)
    with pytest.raises(ValueError):
        solver.fit(np.full(12, np.nan), lambda_=1)
    with pytest.raises(ValueError):
        solver.fit_many(y, [-2, 1.0])
    with pytest.raises(ValueError):
        solver.fit_many(y, [np.nan])


def test_existing_default_svd_trends_and_selection_unchanged():
    y = np.random.default_rng(18).normal(size=27)
    modern = PreparedPLSSolver(len(y), order=2)
    current = TrendSmoother(len(y), order=2)
    assert modern.method == "svd"
    assert_allclose(
        modern.fit(y, lambda_=8.0),
        current.fit(y, lambda_=8.0).trend,
        rtol=1e-11, atol=1e-11,
    )
