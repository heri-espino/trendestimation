"""Experiment005: parity, numerical integrity and API tests for structured fits."""
from __future__ import annotations

import importlib.util

import numpy as np
import pytest
from numpy.testing import assert_allclose

from trendestimation import PreparedPLSSolver, TrendSmoother, difference_matrix
from trendestimation.solvers import fit_penalized


@pytest.mark.parametrize("d", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("mu", [0.0, 0.15, "data"])
@pytest.mark.parametrize("lam", [1e-4, 0.1, 20.0])
def test_structured_direct_against_dense_and_svd(d, mu, lam):
    n = 34
    y = np.random.default_rng(20 + d).normal(size=n)
    mean = np.mean(np.diff(y, n=d)) if mu == "data" else mu
    D = difference_matrix(n, d)
    matrix = np.eye(n) + lam * (D.T @ D)
    rhs = y + lam * mean * (D.T @ np.ones(n-d))
    truth = np.linalg.solve(matrix, rhs)
    for method in ("banded_lu", "sparse_lu"):
        actual = PreparedPLSSolver(n, d, method=method).fit(
            y, lambda_=lam, mu=mu
        )
        assert_allclose(actual, truth, rtol=5e-8, atol=5e-8)
        assert_allclose(actual, TrendSmoother(n, d).fit(
            y, lambda_=lam, mu=mu
        ).trend, rtol=5e-8, atol=5e-8)


@pytest.mark.parametrize("preconditioner", ["fft", "dst", "jacobi", "none"])
@pytest.mark.parametrize("d", [0, 1, 2, 3])
@pytest.mark.parametrize("mu", [0.0, 0.12, "data"])
def test_pcg_against_banded_cholesky(preconditioner, d, mu):
    n = 42
    y = np.random.default_rng(170+d).normal(size=n)
    lam = 1.5
    solver = PreparedPLSSolver(
        n, d, method="pcg", preconditioner=preconditioner,
        cg_rtol=1e-10, cg_maxiter=2000,
    )
    fitted = solver.fit(y, lambda_=lam, mu=mu)
    expected = PreparedPLSSolver(n, d, method="cholesky").fit(
        y, lambda_=lam, mu=mu,
    )
    assert_allclose(fitted, expected, rtol=3e-8, atol=3e-8)
    assert solver.cg_iterations is not None
    assert solver.cg_relative_residual < 5e-9


@pytest.mark.parametrize("method", ["banded_lu", "sparse_lu", "pcg"])
def test_endpoints_and_batches(method):
    n = 37
    y = np.random.default_rng(33).normal(size=n)
    params = dict(method=method)
    if method == "pcg":
        params["preconditioner"] = "jacobi"
    solver = PreparedPLSSolver(n, order=2, **params)
    penalties = [0.0, 0.001, 0.8, np.inf]
    for mean in (0.0, 0.15, "data"):
        batch = solver.fit_many(y, penalties, mu=mean)
        singles = np.vstack([solver.fit(y, lambda_=lam, mu=mean)
                             for lam in penalties])
        assert_allclose(batch, singles, atol=1e-8)
        assert_allclose(batch[0], y)
        assert solver.fit_many(y, [], mu=mean).shape == (0,n)
        D = difference_matrix(n,2)
        expected = float(np.mean(D@y)) if mean=="data" else mean
        assert_allclose(D @ batch[-1], expected, atol=1e-8)


def test_sparse_lu_factor_cache_reuse():
    y = np.random.default_rng(101).normal(size=55)
    solver = PreparedPLSSolver(55, 2, method="sparse_lu", factor_cache=True)
    assert solver.cached_factor_count == 0
    a = solver.fit(y, lambda_=3., mu=0.)
    assert solver.cached_factor_count == 1
    b = solver.fit(y, lambda_=3., mu=0.15)
    assert solver.cached_factor_count == 1
    solver.fit(y, lambda_=5., mu=0.0)
    assert solver.cached_factor_count == 2
    assert np.max(abs(a-b))>1e-5


def test_non_convergence_must_raise():
    y = np.random.default_rng(103).normal(size=70)
    solver = PreparedPLSSolver(
        70, 2, method="pcg", preconditioner="none",
        cg_rtol=1e-13, cg_maxiter=1,
    )
    with pytest.raises(ArithmeticError, match="did not converge"):
        solver.fit(y, lambda_=200.0)
    assert solver.cg_iterations == 1
    assert solver.cg_relative_residual is not None


def test_optional_sparse_cholesky_is_not_silent_lu():
    y = np.random.default_rng(12).normal(size=28)
    if importlib.util.find_spec("sksparse") is None:
        with pytest.raises(ImportError, match="CHOLMOD"):
            PreparedPLSSolver(28, 2, method="sparse_cholesky")
    else:
        pytest.importorskip("sksparse.cholmod")
        s = PreparedPLSSolver(28, 2, method="sparse_cholesky", factor_cache=True)
        actual = s.fit(y, lambda_=2., mu=.1)
        expected = PreparedPLSSolver(28, 2, method="cholesky").fit(
            y, lambda_=2., mu=.1
        )
        assert_allclose(actual, expected, atol=1e-8)
        assert s.cached_factor_count == 1


def test_no_dense_n_by_n_structure_and_validation():
    for method in ("sparse_lu", "banded_lu", "pcg"):
        s = PreparedPLSSolver(400, 3, method=method)
        assert s.eigenvectors is None
        assert s.stored_bytes < 400*400*8//4
    with pytest.raises(ValueError, match="preconditioner"):
        PreparedPLSSolver(30,2,method="pcg",preconditioner="magic")
    with pytest.raises(ValueError, match="factor_cache"):
        PreparedPLSSolver(30,2,method="pcg",factor_cache=True)
    with pytest.raises(ValueError, match="cg_rtol"):
        PreparedPLSSolver(30,2,method="pcg",cg_rtol=-1)
    with pytest.raises(ValueError):
        fit_penalized(np.ones(30),method="sparse_lu",lambda_=-2)


def test_banded_cholesky_factor_cache_same_lambda_different_mean():
    n=51
    rng=np.random.default_rng(117)
    y=rng.normal(size=n)
    fitter=PreparedPLSSolver(n,2,method="cholesky",factor_cache=True)
    assert fitter.cached_factor_count==0
    a=fitter.fit(y,lambda_=11.,mu=0.0)
    assert fitter.cached_factor_count==1
    b=fitter.fit(y,lambda_=11.,mu=0.2)
    assert fitter.cached_factor_count==1
    assert np.linalg.norm(a-b)>1e-4
    truth=PreparedPLSSolver(n,2,method="cholesky").fit(
        y,lambda_=11.,mu=0.2)
    assert_allclose(b,truth,atol=1e-9)
    fitter.fit(y,lambda_=9.,mu=0.0)
    assert fitter.cached_factor_count==2
    assert fitter.stored_bytes>8*(2+1)*n


def test_scikit_sparse_05_adapter_uses_csc_array_and_solve(monkeypatch):
    """Mock 0.5 public API so CI can test compatibility without CHOLMOD."""
    import sys
    from types import ModuleType
    from scipy.sparse import csc_array, issparse

    root = ModuleType("sksparse")
    child = ModuleType("sksparse.cholmod")
    matrices = []

    def cho_factor(A):
        assert isinstance(A, csc_array), (
            "scikit-sparse 0.5 requires a CSC sparse array")
        matrices.append(A.copy())
        class Factor:
            def solve(self, b):
                return np.linalg.solve(A.toarray(), b)
        return Factor()

    child.cho_factor = cho_factor
    root.cholmod = child
    monkeypatch.setitem(sys.modules, "sksparse", root)
    monkeypatch.setitem(sys.modules, "sksparse.cholmod", child)
    n, d = 28, 2
    y = np.random.default_rng(911).normal(size=n)
    solver = PreparedPLSSolver(n, d, method="sparse_cholesky",
                               factor_cache=True)
    fitted = solver.fit(y, lambda_=2.0, mu=0.15)
    expected = PreparedPLSSolver(n, d, method="cholesky").fit(
        y, lambda_=2.0, mu=0.15)
    assert_allclose(fitted, expected, rtol=2e-9, atol=2e-9)
    assert len(matrices) == 1
    assert issparse(matrices[0])


def test_scikit_sparse_04_adapter_retains_legacy_solve_A(monkeypatch):
    """The explicit modern conversion must not break older 0.4 installs."""
    import sys
    from types import ModuleType
    from scipy.sparse import csc_matrix

    root = ModuleType("sksparse")
    child = ModuleType("sksparse.cholmod")
    matrices = []
    def cholesky(A):
        assert isinstance(A, csc_matrix)
        matrices.append(A.copy())
        class Factor:
            def solve_A(self, b):
                return np.linalg.solve(A.toarray(), b)
        return Factor()
    child.cholesky = cholesky
    root.cholmod = child
    monkeypatch.setitem(sys.modules, "sksparse", root)
    monkeypatch.setitem(sys.modules, "sksparse.cholmod", child)
    n, d = 20, 1
    y = np.random.default_rng(912).normal(size=n)
    fit = PreparedPLSSolver(n, d, method="sparse_cholesky").fit(
        y, lambda_=1.4, mu=0.)
    reference = PreparedPLSSolver(n, d, method="cholesky").fit(
        y, lambda_=1.4, mu=0.)
    assert_allclose(fit, reference, rtol=1e-9, atol=1e-9)
    assert len(matrices) == 1
