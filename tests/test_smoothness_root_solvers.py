"""Accuracy and stability tests for inverse Guerrero spectral smoothness."""

from decimal import Decimal, localcontext

import numpy as np
import pytest
from numpy.testing import assert_allclose

from trendestimation import TrendSmoother


METHODS = ("auto", "brentq", "newton", "secant", "bisect", "bisection")


def _decimal_inverse(smoother, target):
    """Independent 75-digit monotone bisection on the original lambda scale."""
    with localcontext() as ctx:
        ctx.prec = 75
        eig = [
            Decimal.from_float(float(x))
            for x in smoother.eigenvalues[: smoother.n - smoother.order]
        ]
        t = Decimal.from_float(float(target))
        odds = t / (1 - t)
        low = odds / max(eig)
        high = odds / min(eig)
        count = Decimal(len(eig))
        for _ in range(260):
            mid = (low + high) / 2
            value = sum((mid * e / (1 + mid * e) for e in eig), Decimal(0)) / count
            if value < t:
                low = mid
            else:
                high = mid
        return float((low + high) / 2)


@pytest.mark.parametrize("n,d", [(2, 0), (12, 1), (20, 2), (24, 3), (8, 7)])
@pytest.mark.parametrize("target", [1e-12, 0.03, 0.5, 0.92, 1 - 1e-12])
@pytest.mark.parametrize("method", METHODS)
def test_matches_independent_high_precision_reference(n, d, target, method):
    smoother = TrendSmoother(n, d)
    reference = _decimal_inverse(smoother, target)
    obtained = smoother.lambda_for_smoothness(target, method=method)
    assert_allclose(obtained, reference, rtol=3e-10, atol=0)
    assert smoother._last_smoothness_root_diagnostics["iterations"] >= 0
    complement = target > 0.5
    actual = smoother._smoothness_log_value(np.log(obtained), complement=complement)
    expected = 1 - target if complement else target
    assert abs(actual - expected) <= max(3e-11 * expected, 1e-320)


@pytest.mark.parametrize("d", [0, 1, 2, 4])
@pytest.mark.parametrize("method", METHODS)
def test_guerrero_original_scale_and_normalized_agree(d, method):
    smoother = TrendSmoother(19, d)
    max_original = (smoother.n - d) / smoother.n
    for s in (1e-9, 0.25, 0.8, 1 - 1e-6):
        a = smoother.lambda_for_smoothness(s, method=method)
        b = smoother.lambda_for_smoothness(
            s * max_original, normalized=False, method=method,
        )
        assert_allclose(a, b, rtol=1e-8, atol=0)
        assert smoother.smoothness(b, normalized=False) == pytest.approx(
            s * max_original, abs=1e-12,
        )


@pytest.mark.parametrize("method", METHODS)
def test_endpoints_are_exact(method):
    for d in (0, 1, 3, 9):
        smoother = TrendSmoother(10, d)
        maximum = (10 - d) / 10
        assert smoother.lambda_for_smoothness(0, method=method) == 0.0
        assert np.isinf(smoother.lambda_for_smoothness(1, method=method))
        assert np.isinf(smoother.lambda_for_smoothness(
            maximum, normalized=False, method=method,
        ))
        assert smoother.smoothness(np.inf, normalized=False) == maximum


@pytest.mark.parametrize("method", METHODS)
def test_scalar_spectrum_inversion_is_exact(method):
    for n, d in ((7, 0), (7, 6), (1, 0)):
        smoother = TrendSmoother(n, d)
        delta = smoother.eigenvalues[0]
        for target in (1e-14, 0.33, 1 - 1e-14):
            result = smoother.lambda_for_smoothness(target, method=method)
            assert_allclose(result, target / (1 - target) / delta, rtol=5e-15)
            assert smoother._last_smoothness_root_diagnostics["method"] == "analytic"


def test_low_smoothness_is_not_lost_to_trace_cancellation():
    smoother = TrendSmoother(18, 2)
    assert smoother.smoothness(1e-17) > 0
    assert smoother.smoothness(1e-17) < smoother.smoothness(1e-16)


def test_extreme_tails_and_conditioning():
    smoother = TrendSmoother(60, 4)
    for s in (1e-16, 1e-14, 1 - 1e-14, np.nextafter(1.0, 0.0)):
        for method in METHODS:
            lam = smoother.lambda_for_smoothness(s, method=method)
            assert np.isfinite(lam) and lam > 0
            tail = s if s < 0.5 else 1 - s
            recovered = smoother._smoothness_log_value(np.log(lam), complement=s > 0.5)
            assert abs(recovered - tail) / tail < 1e-10


@pytest.mark.parametrize("method", ("brentq", "newton", "secant", "bisect"))
def test_nonconvergence_is_reported(method):
    smoother = TrendSmoother(30, 2)
    with pytest.raises((RuntimeError, ArithmeticError)):
        smoother.lambda_for_smoothness(0.87654321, method=method, maxiter=1)


@pytest.mark.parametrize("value", [-0.1, 1.000001, np.nan, np.inf, -np.inf])
def test_invalid_normalized_targets_rejected(value):
    with pytest.raises(ValueError):
        TrendSmoother(8, 2).lambda_for_smoothness(value)


def test_invalid_original_target_and_solver_controls():
    smoother = TrendSmoother(10, 3)
    with pytest.raises(ValueError):
        smoother.lambda_for_smoothness(0.8, normalized=False)
    for kwargs in (
        {"method": "unknown"}, {"tol": 0}, {"tol": np.nan},
        {"maxiter": 0}, {"maxiter": 2.5}, {"maxiter": True},
    ):
        with pytest.raises(ValueError):
            smoother.lambda_for_smoothness(0.4, **kwargs)


def test_penalty_below_float64_range_raises_instead_of_returning_zero():
    smoother = TrendSmoother(30, 2)
    with pytest.raises(OverflowError):
        smoother.lambda_for_smoothness(np.nextafter(0.0, 1.0))


def test_log_parameter_analytic_derivative():
    smoother = TrendSmoother(37, 3)
    for x in (-25.0, -5.0, 0.0, 5.0, 25.0):
        eps = 1e-4
        high = x > 0
        sign = -1.0 if high else 1.0
        numerical = sign * (
            smoother._smoothness_log_value(x + eps, complement=high)
            - smoother._smoothness_log_value(x - eps, complement=high)
        ) / (2 * eps)
        analytic = smoother._smoothness_log_derivative(x)
        assert_allclose(analytic, numerical, rtol=5e-8)
