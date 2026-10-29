"""Published finite-difference penalized least-squares smoothing.

Guerrero (2007); Cortes-Toto, Guerrero & Reyes (2017).
The package estimates in-sample trends, not future forecasts.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import comb
import math
from typing import Literal

import numpy as np
from scipy.linalg import svd
from scipy.optimize import bisect, brentq
from scipy.special import binom

MeanMode = float | Literal["data"]


def difference_matrix(n: int, order: int) -> np.ndarray:
    """Build the order-d forward-difference matrix.

    Parameters
    ----------
    n : int
        Number of equally spaced observations; must be positive.
    order : int
        Nonnegative difference order strictly less than n.

    Returns
    -------
    numpy.ndarray
        Array with shape (n - order, n). The order-zero matrix is
        the n-by-n identity.

    Notes
    -----
    For order two, each row contains the stencil [1, -2, 1].
    """
    if int(n) != n or int(order) != order or not 0 <= order < n:
        raise ValueError("Require integer n >= 1 and 0 <= order < n.")
    n, order = int(n), int(order)
    if order == 0:
        return np.eye(n)
    matrix = np.zeros((n - order, n), dtype=float)
    rows = np.arange(n - order)
    for j in range(order + 1):
        matrix[rows, rows + j] = (-1.0) ** (order - j) * comb(order, j)
    return matrix


@dataclass(frozen=True)
class FitResult:
    """Output of a finite-difference penalized least-squares fit.

    Attributes
    ----------
    trend : numpy.ndarray
        Estimated in-sample trend.
    residual : numpy.ndarray
        Observed values minus the fitted trend.
    lambda_ : float
        Penalty parameter, possibly positive infinity.
    order : int
        Finite-difference order.
    mu : float
        Fixed or observed-difference plug-in reference mean.
    edf_conditional : float
        Trace of the smoothing operator, conditional on fixed mu.
    smoothness : float
        Normalized trace-based smoothness on [0, 1].
    guerrero_smoothness : float
        Original Guerrero trace-based smoothness index.
    """

    trend: np.ndarray
    residual: np.ndarray
    lambda_: float
    order: int
    mu: float
    edf_conditional: float
    smoothness: float
    guerrero_smoothness: float


class TrendSmoother:
    """Reusable spectral solver for penalized trend estimation.

    Parameters
    ----------
    n : int
        Number of equally spaced observations.
    order : int, default=2
        Nonnegative difference order strictly smaller than n.

    Notes
    -----
    Fits minimize the sum of squared residuals plus lambda times the
    sum of squared deviations of order-d differences from reference
    mu. The reusable full SVD costs O(n^3) time and O(n^2) memory;
    repeated spectral summaries take O(n) operations and full trend
    reconstruction takes O(n^2). A banded solver may be faster for
    a single fit or very long series.

    Examples
    --------
    >>> import numpy as np
    >>> from trendestimation import TrendSmoother
    >>> y = np.array([1., 1.5, 1.2, 2., 2.2, 2.5])
    >>> solver = TrendSmoother(len(y), order=2)
    >>> result = solver.fit(y, lambda_=10, mu=0.0)
    >>> result.trend.shape
    (6,)
    """

    def __init__(self, n: int, order: int = 2):
        self.D = difference_matrix(n, order)
        self.n, self.order = int(n), int(order)
        left, singular, vh = svd(self.D, full_matrices=True, check_finite=True)
        self._left_singular_vectors = left
        self._singular_values = singular
        self._mean_shift_coordinates = (left.T @ np.ones(self.n - self.order)) / singular
        self.eigenvectors = vh.T
        self.eigenvalues = np.r_[singular**2, np.zeros(self.order)]
        self._basis_squares = self.eigenvectors**2
        self._median_positive_eigenvalue = float(np.median(singular**2))
        with np.errstate(divide="ignore"):
            self._log_positive_eigenvalues = np.log(self.eigenvalues[: self.n - self.order])

    def _attenuation(self, lambda_: float) -> np.ndarray:
        lam = float(lambda_)
        if np.isnan(lam) or lam < 0:
            raise ValueError("lambda_ must lie in [0, infinity].")
        if np.isinf(lam):
            return np.r_[np.zeros(self.n - self.order), np.ones(self.order)]
        return 1.0 / (1.0 + lam * self.eigenvalues)

    def _reference(self, mu: float) -> np.ndarray:
        # D_d choose(t,d) = 1 for forward differences; D_0 = I.
        t = np.arange(self.n, dtype=float)
        if self.order == 0:
            return np.full(self.n, mu)
        return mu * binom(t, self.order)

    def _prepare(self, y, mu: MeanMode) -> tuple[np.ndarray, float, np.ndarray, np.ndarray]:
        y = np.asarray(y, dtype=float)
        if y.ndim != 1 or y.size != self.n or not np.all(np.isfinite(y)):
            raise ValueError(f"y must be a finite one-dimensional array of length {self.n}.")
        if mu == "data":
            value = float(np.mean(self.D @ y))
        else:
            value = float(mu)
        if not np.isfinite(value):
            raise ValueError("mu must be finite.")
        reference = self._reference(value)
        coordinates = self.eigenvectors.T @ (y - reference)
        # The positive spectral coordinates are formed without subtracting a
        # potentially enormous degree-d polynomial reference; see the
        # shift-free reconstruction in the CSDA working manuscript.
        r = self.n - self.order
        coordinates[:r] = (
            self.eigenvectors[:, :r].T @ y - value * self._mean_shift_coordinates
        )
        return y, value, reference, coordinates

    def degrees_of_freedom(self, lambda_: float) -> float:
        """Return conditional effective degrees of freedom.

        Parameters
        ----------
        lambda_ : float
            Nonnegative penalty, including positive infinity.

        Returns
        -------
        float
            Trace of the linear smoothing matrix for fixed mu.
        """
        return float(np.sum(self._attenuation(lambda_)))

    def _smoothness_log_value(self, log_lambda: float, *, complement: bool = False) -> float:
        """Stable positive-penalty spectral smoothness (or its complement).

        The logaddexp form remains accurate when expit underflows in the
        subnormal range. No n - tr(H) cancellation is involved.
        """
        z = log_lambda + self._log_positive_eigenvalues
        return float(np.mean(np.exp(-np.logaddexp(0.0, z if complement else -z))))

    def _smoothness_log_derivative(self, log_lambda: float) -> float:
        """Derivative of normalized smoothness with respect to log(lambda)."""
        z = log_lambda + self._log_positive_eigenvalues
        tail = np.exp(-np.logaddexp(0.0, np.abs(z)))
        return float(np.mean(tail * (1.0 - tail)))

    def smoothness(self, lambda_: float, *, normalized: bool = True) -> float:
        """Compute trace-based trend smoothness.

        Parameters
        ----------
        lambda_ : float
            Nonnegative penalty, including positive infinity.
        normalized : bool, default=True
            If True, scale the index to [0, 1]. If False, use
            Guerrero's original index with upper limit 1 - d/n.

        Returns
        -------
        float
            The requested smoothness index.
        """
        lam = float(lambda_)
        if np.isnan(lam) or lam < 0:
            raise ValueError("lambda_ must lie in [0, infinity].")
        maximum = (self.n - self.order) / (self.n - self.order if normalized else self.n)
        if lam == 0:
            return 0.0
        if np.isinf(lam):
            return float(maximum)
        return float(maximum * self._smoothness_log_value(math.log(lam)))

    def lambda_for_smoothness(
        self,
        smoothness: float,
        *,
        normalized: bool = True,
        method: str = "auto",
        tol: float = 1e-12,
        maxiter: int = 100,
    ) -> float:
        """Invert normalized or original Guerrero smoothness.

        Parameters
        ----------
        smoothness : float
            Target in [0, 1] (normalized) or [0, (n-d)/n] (original).
        normalized : bool, default=True
            Use the unit interval, or Guerrero's original n denominator.
        method : {"auto", "brentq", "newton", "secant", "bisect", "bisection"}
            The default chooses the robust Brent solver for general spectra,
            and uses an exact analytical inverse for scalar spectra.
            Newton and secant are bracket-safeguarded.
        tol : float, default=1e-12
            Positive relative tolerance in the smaller smoothness tail,
            with an absolute tolerance in log(lambda) for bracket methods.
        maxiter : int, default=100
            Maximum solver iterations; nonconvergence raises an exception.

        Returns
        -------
        float
            Nonnegative penalty, with infinity only at the exact endpoint.

        Notes
        -----
        Numerical methods solve in x=log(lambda). A final tail-based
        reconstruction check rejects inaccurate or unrepresentable roots.
        The last successful solve's private diagnostics support benchmarks.
        """
        target = float(smoothness)
        maximum = (self.n - self.order) / self.n if not normalized else 1.0
        if not np.isfinite(target) or not 0.0 <= target <= maximum:
            raise ValueError(f"smoothness must belong to [0, {maximum}].")
        methods = {"auto", "brentq", "newton", "secant", "bisect", "bisection"}
        if method not in methods:
            raise ValueError(f"method must be one of {sorted(methods)}.")
        if not np.isfinite(tol) or tol <= 0:
            raise ValueError("tol must be positive and finite.")
        if isinstance(maxiter, bool) or not isinstance(maxiter, (int, np.integer)) or maxiter < 1:
            raise ValueError("maxiter must be a positive integer.")
        if target == 0:
            return 0.0
        if target == maximum:
            return float("inf")
        if not np.all(np.isfinite(self._log_positive_eigenvalues)):
            raise ArithmeticError("Positive penalty eigenvalues are numerically rank deficient.")

        t = target / maximum
        q = (maximum - target) / maximum
        high = t > 0.5
        scale = q if high else t
        logit = math.log(t) - math.log(q)
        logs = self._log_positive_eigenvalues
        lower = logit - float(np.max(logs)) - 2.0
        upper = logit - float(np.min(logs)) + 2.0
        evaluations = 0
        derivative_evaluations = 0
        iterations = 0
        selected = (
            "analytic" if self.order == 0 or self.n - self.order == 1
            else "brentq" if method == "auto"
            else "bisect" if method == "bisection" else method
        )

        # D_0=I, while n-d=1 has exactly one positive penalty eigenvalue.
        if selected == "analytic":
            log_root = logit - float(logs[0])
        else:

            def residual(x: float) -> float:
                nonlocal evaluations
                evaluations += 1
                value = self._smoothness_log_value(x, complement=high)
                return (q - value) if high else (value - t)

            float_min_log = math.log(np.nextafter(0.0, 1.0))
            float_max_log = math.log(np.finfo(float).max)
            if lower < float_min_log and residual(float_min_log) > 0:
                raise OverflowError("Smoothness requires a penalty below finite float64 range.")
            if upper > float_max_log and residual(float_max_log) < 0:
                raise OverflowError("Smoothness requires a penalty above finite float64 range.")
            f_lower, f_upper = residual(lower), residual(upper)
            if f_lower >= 0 or f_upper <= 0:
                raise ArithmeticError("Unable to bracket smoothness in log-penalty space.")
            if selected == "brentq":
                log_root, result = brentq(
                    residual, lower, upper, xtol=tol,
                    rtol=4.0 * np.finfo(float).eps, maxiter=maxiter, full_output=True,
                )
                iterations = result.iterations
            elif selected == "bisect":
                log_root, result = bisect(
                    residual, lower, upper, xtol=tol,
                    rtol=4.0 * np.finfo(float).eps, maxiter=maxiter, full_output=True,
                )
                iterations = result.iterations
            elif selected == "newton":
                x = min(max(logit - float(np.median(logs)), lower), upper)
                log_root = None
                for iterations in range(1, maxiter + 1):
                    f_x = residual(x)
                    if abs(f_x) <= tol * scale:
                        log_root = x
                        break
                    if f_x < 0:
                        lower = x
                    else:
                        upper = x
                    derivative_evaluations += 1
                    derivative = self._smoothness_log_derivative(x)
                    candidate = x - f_x / derivative if derivative > 0 else math.nan
                    if not np.isfinite(candidate) or not lower < candidate < upper:
                        candidate = lower + (upper - lower) / 2
                    x = candidate
                if log_root is None:
                    raise RuntimeError(
                        f"Newton smoothness inversion did not converge in {maxiter} iterations."
                    )
            else:
                log_root = None
                for iterations in range(1, maxiter + 1):
                    candidate = lower - f_lower * (upper - lower) / (f_upper - f_lower)
                    width = upper - lower
                    if (
                        not np.isfinite(candidate)
                        or not lower + 0.1 * width < candidate < upper - 0.1 * width
                    ):
                        candidate = lower + width / 2
                    f_x = residual(candidate)
                    if abs(f_x) <= tol * scale:
                        log_root = candidate
                        break
                    if f_x < 0:
                        lower, f_lower = candidate, f_x
                    else:
                        upper, f_upper = candidate, f_x
                if log_root is None:
                    raise RuntimeError(
                        f"Secant smoothness inversion did not converge in {maxiter} iterations."
                    )

        log_min = math.log(np.nextafter(0.0, 1.0))
        log_max = math.log(np.finfo(float).max)
        if not log_min <= log_root <= log_max:
            raise OverflowError("Smoothness requires a penalty outside finite float64 range.")
        lam = float(math.exp(log_root))
        if not 0 < lam < float("inf"):
            raise OverflowError("Smoothness penalty is not representable as finite float64.")
        computed = self._smoothness_log_value(math.log(lam), complement=high)
        discrepancy = abs((q - computed) if high else (computed - t))
        if discrepancy > max(5.0 * tol, 1e-13) * scale:
            raise ArithmeticError("Numerical smoothness inversion failed reconstruction tolerance.")
        self._last_smoothness_root_diagnostics = {
            "method": selected,
            "iterations": iterations,
            "function_evaluations": evaluations + 1,
            "derivative_evaluations": derivative_evaluations,
        }
        return lam

    def fit(self, y, *, lambda_: float, mu: MeanMode = 0.0) -> FitResult:
        """Fit a finite-difference penalized least-squares trend.

        Parameters
        ----------
        y : array_like
            Finite one-dimensional sequence of n observations.
        lambda_ : float
            Nonnegative smoothing penalty; positive infinity selects
            the exact limiting nullspace projection.
        mu : float or {"data"}, default=0.0
            Target mean of order-d differences. Passing "data"
            uses the mean of D_d @ y (observed d-th differences).

        Returns
        -------
        FitResult
            Trend, residuals, effective degrees of freedom, and
            normalized/original smoothness indices.

        Notes
        -----
        Effective degrees of freedom are conditional on a fixed mu.
        When mu="data", they do not include the extra dependence
        introduced by estimating the reference from the observations.
        This method is an in-sample trend estimator, not a forecaster.
        """
        observed, value, reference, coords = self._prepare(y, mu)
        alpha = self._attenuation(lambda_)
        lam = float(lambda_)
        r = self.n - self.order
        if lam == 0.0:
            weights = np.zeros(r, dtype=float)
        elif math.isinf(lam):
            weights = np.ones(r, dtype=float)
        else:
            z = math.log(lam) + self._log_positive_eigenvalues
            weights = np.exp(-np.logaddexp(0.0, -z))
        # Algebraically identical PLS fit, but avoids reference + H(y-reference)
        # cancellation for high d and near-unit smoothness.
        trend = observed - self.eigenvectors[:, :r] @ (weights * coords[:r])
        return FitResult(
            trend=trend,
            residual=observed - trend,
            lambda_=float(lambda_),
            order=self.order,
            mu=value,
            edf_conditional=float(np.sum(alpha)),
            smoothness=self.smoothness(lambda_),
            guerrero_smoothness=self.smoothness(lambda_, normalized=False),
        )


def fit_trend(y, *, order: int = 2, lambda_: float = 1600.0, mu: MeanMode = 0.0) -> FitResult:
    """Fit one trend without explicitly constructing a reusable solver.

    Parameters
    ----------
    y : array_like
        One-dimensional series of observations.
    order : int, default=2
        Difference order.
    lambda_ : float, default=1600
        Nonnegative smoothing penalty, possibly positive infinity.
    mu : float or {"data"}, default=0.0
        Fixed reference-difference mean or observed-difference plug-in.

    Returns
    -------
    FitResult
        Fitted trend and diagnostics.

    Notes
    -----
    For repeated penalty values with fixed n and order, reuse a
    TrendSmoother instance to amortize the SVD preprocessing cost.
    """
    values = np.asarray(y)
    if values.ndim != 1:
        raise ValueError("y must be one-dimensional.")
    return TrendSmoother(len(values), order).fit(values, lambda_=lambda_, mu=mu)
