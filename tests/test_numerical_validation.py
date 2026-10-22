"""Independent numerical oracles for the finite-difference PLS implementation.

The reference implementation here deliberately avoids TrendSmoother's SVD,
eigenvectors, eigenvalues, and reconstruction code.
"""
from __future__ import annotations

from math import comb

import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.linalg import null_space, solve_banded

from trendestimation import TrendSmoother, difference_matrix, score_lambda


def reference_difference(n: int, d: int) -> np.ndarray:
    """Independent difference stencil via repeated finite differences of I."""
    return np.diff(np.eye(n), n=d, axis=0)


def reference_penalty_bands(n: int, d: int) -> np.ndarray:
    """Assemble D.T @ D directly into general-band storage, without dense D/Q."""
    stencil = [(-1) ** (d - j) * comb(d, j) for j in range(d + 1)]
    bands = np.zeros((2 * d + 1, n), dtype=float)
    for r in range(n - d):
        for a, va in enumerate(stencil):
            i = r + a
            for b, vb in enumerate(stencil):
                j = r + b
                bands[d + i - j, j] += va * vb
    return bands


def reference_banded_fit(y: np.ndarray, d: int, lam: float, mu: float) -> np.ndarray:
    """Normal equations solved with a directly constructed banded matrix."""
    n = len(y)
    bands = lam * reference_penalty_bands(n, d)
    bands[d] += 1.0
    D = reference_difference(n, d)
    rhs = y + lam * mu * (D.T @ np.ones(n - d))
    return solve_banded((d, d), bands, rhs, check_finite=True)


def reference_constrained_projection(y: np.ndarray, d: int, mu: float) -> np.ndarray:
    """Closest vector to y satisfying D tau = mu 1, using QR/SVD null space."""
    D = reference_difference(len(y), d)
    particular = np.linalg.lstsq(D, np.full(len(y) - d, mu), rcond=None)[0]
    null = null_space(D)
    return particular + null @ (null.T @ (y - particular))


@pytest.mark.parametrize("n", [8, 21, 48])
@pytest.mark.parametrize("order", [0, 1, 2, 3, 5])
def test_finite_difference_stencils_rank_and_nullity(n: int, order: int) -> None:
    if order >= n:
        pytest.skip("Difference order must be less than sample length")
    D = difference_matrix(n, order)
    ref = reference_difference(n, order)
    assert_allclose(D, ref, rtol=0, atol=0)
    assert np.linalg.matrix_rank(D) == n - order
    if order:
        x = np.linspace(-1, 1, n)
        for degree in range(order):
            assert_allclose(D @ x**degree, 0.0, atol=5e-10)


@pytest.mark.parametrize("n", [8, 21, 48])
@pytest.mark.parametrize("order", [0, 1, 2, 3, 5])
@pytest.mark.parametrize("mu", [0.0, 0.37])
def test_spectral_matches_independent_banded_solve(
    n: int, order: int, mu: float,
) -> None:
    rng = np.random.default_rng(9000 + n * 11 + order)
    y = rng.normal(size=n)
    smoother = TrendSmoother(n, order)
    for lam in (0.0, 0.002, 1.0, 200.0):
        actual = smoother.fit(y, lambda_=lam, mu=mu).trend
        reference = reference_banded_fit(y, order, lam, mu)
        assert_allclose(actual, reference, rtol=1e-8, atol=1e-8)
        # The first-order (KKT) residual is a separate equation-based check.
        D = reference_difference(n, order)
        gradient = (actual - y) + lam * D.T @ (
            D @ actual - mu * np.ones(n - order)
        )
        scale = max(1.0, np.linalg.norm(y), np.linalg.norm(lam * D.T @ (D @ actual)))
        assert np.linalg.norm(gradient) <= 2e-7 * scale


@pytest.mark.parametrize("order", [0, 1, 2, 3, 5])
@pytest.mark.parametrize("mu", [0.0, 0.3])
def test_infinite_penalty_is_independent_constrained_projection(
    order: int, mu: float,
) -> None:
    n = 18
    y = np.random.default_rng(2026 + order).normal(size=n)
    solver = TrendSmoother(n, order)
    exact = solver.fit(y, lambda_=np.inf, mu=mu).trend
    reference = reference_constrained_projection(y, order, mu)
    assert_allclose(exact, reference, rtol=2e-8, atol=2e-8)
    assert_allclose(reference_difference(n, order) @ exact, mu, atol=2e-8)
    assert solver.degrees_of_freedom(np.inf) == pytest.approx(float(order))


@pytest.mark.parametrize("order", [0, 1, 2, 3])
def test_both_lambda_limits_are_numerically_approached(order: int) -> None:
    n = 14
    rng = np.random.default_rng(72 + order)
    y = rng.normal(size=n)
    smoother = TrendSmoother(n, order)
    mu = -0.23
    assert_allclose(smoother.fit(y, lambda_=0, mu=mu).trend, y, atol=1e-12)
    assert_allclose(smoother.fit(y, lambda_=1e-12, mu=mu).trend, y, atol=5e-10)
    large = smoother.fit(y, lambda_=1e13, mu=mu).trend
    limit = reference_constrained_projection(y, order, mu)
    assert_allclose(large, limit, rtol=3e-6, atol=3e-6)


@pytest.mark.parametrize("order", [0, 1, 2, 3, 5])
def test_residual_increases_while_penalty_decreases(order: int) -> None:
    n = 30
    y = np.random.default_rng(830 + order).normal(size=n)
    D = reference_difference(n, order)
    solver = TrendSmoother(n, order)
    mu = 0.12
    previous_fidelity = -1.0
    previous_penalty = np.inf
    previous_edf = float(n) + 1
    for lam in (0.0, 0.001, 0.1, 1.0, 10.0, 1000.0, np.inf):
        fit = solver.fit(y, lambda_=lam, mu=mu)
        fidelity = np.linalg.norm(y - fit.trend) ** 2
        penalty = np.linalg.norm(D @ fit.trend - mu) ** 2
        assert fidelity >= previous_fidelity - 1e-8
        assert penalty <= previous_penalty + 1e-8
        assert 0 <= fit.edf_conditional <= previous_edf + 1e-10
        assert order - 1e-10 <= fit.edf_conditional <= n + 1e-10
        previous_fidelity, previous_penalty = fidelity, penalty
        previous_edf = fit.edf_conditional


@pytest.mark.parametrize("lam", [0.0, 0.0001, 1.0, 1e3, np.inf])
def test_order_zero_has_exact_scalar_shrinkage(lam: float) -> None:
    y = np.random.default_rng(18).normal(size=17)
    mu = 0.27
    got = TrendSmoother(len(y), 0).fit(y, lambda_=lam, mu=mu).trend
    expected = (
        np.full_like(y, mu)
        if np.isinf(lam)
        else (y + lam * mu) / (1.0 + lam)
    )
    assert_allclose(got, expected, atol=1e-12)


@pytest.mark.parametrize("order", [1, 2, 3, 4])
def test_polynomial_nullspace_signals_are_preserved(order: int) -> None:
    n = 29
    x = np.linspace(-1, 1, n)
    y = sum((0.1 + k / 10) * x**k for k in range(order))
    for lam in (0.0, 0.1, 100.0, 1e8, np.inf):
        got = TrendSmoother(n, order).fit(y, lambda_=lam, mu=0.0).trend
        assert_allclose(got, y, rtol=1e-8, atol=1e-8)


@pytest.mark.parametrize("order", [0, 1, 2, 3])
def test_edf_matches_direct_trace(order: int) -> None:
    n = 22
    solver = TrendSmoother(n, order)
    D = reference_difference(n, order)
    Q = D.T @ D
    for lam in (0.0, 0.1, 10.0, 1000.0):
        expected = np.trace(np.linalg.solve(np.eye(n) + lam * Q, np.eye(n)))
        assert solver.degrees_of_freedom(lam) == pytest.approx(
            expected, rel=2e-8, abs=2e-8
        )


@pytest.mark.parametrize("order", [1, 2, 3])
def test_cv_matches_repeated_refits_with_held_out_data(order: int) -> None:
    n, lam, mu = 12, 2.75, -0.13
    y = np.random.default_rng(100 + order).normal(size=n)
    D = reference_difference(n, order)
    Q = D.T @ D
    score = score_lambda(TrendSmoother(n, order), y, lambda_=lam, criterion="cv", mu=mu)
    squared_errors = []
    for withheld in range(n):
        w = np.ones(n)
        w[withheld] = 0.0
        A = np.diag(w) + lam * Q
        rhs = w * y + lam * mu * D.T @ np.ones(n - order)
        prediction = np.linalg.solve(A, rhs)[withheld]
        squared_errors.append((y[withheld] - prediction) ** 2)
    assert score == pytest.approx(float(np.mean(squared_errors)), rel=1e-8)


@pytest.mark.parametrize("order", [1, 2, 3])
def test_moderate_conditioning_on_longer_sequences(order: int) -> None:
    n = 70
    y = np.random.default_rng(420 + order).normal(size=n)
    solver = TrendSmoother(n, order)
    for lam in (1e-8, 1e-3, 1.0, 1e3):
        actual = solver.fit(y, lambda_=lam, mu=0.0).trend
        expected = reference_banded_fit(y, order, lam, 0.0)
        assert_allclose(actual, expected, rtol=1e-7, atol=1e-7)
        assert np.all(np.isfinite(actual))
