"""Published finite-difference penalized least-squares smoothing.

Guerrero (2007); Cortes-Toto, Guerrero & Reyes (2017).
The package estimates in-sample trends, not future forecasts.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Literal

import numpy as np
from scipy.linalg import svd
from scipy.optimize import brentq
from scipy.special import binom

MeanMode = float | Literal["data"]


def difference_matrix(n: int, order: int) -> np.ndarray:
    """Forward-difference matrix, including the order-zero identity."""
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
    trend: np.ndarray
    residual: np.ndarray
    lambda_: float
    order: int
    mu: float
    edf_conditional: float
    smoothness: float
    guerrero_smoothness: float


class TrendSmoother:
    """Reusable full SVD of the finite-difference operator.

    Full SVD costs O(n^3) preprocessing and O(n^2) memory. For
    repeated lambda evaluation, spectral summaries cost O(n);
    a reconstructed fitted curve costs O(n^2). Banded solvers can
    be faster for a single fit on a very long time series.
    """

    def __init__(self, n: int, order: int = 2):
        self.D = difference_matrix(n, order)
        self.n, self.order = int(n), int(order)
        _, singular, vh = svd(self.D, full_matrices=True, check_finite=True)
        self.eigenvectors = vh.T
        self.eigenvalues = np.r_[singular**2, np.zeros(self.order)]
        self._basis_squares = self.eigenvectors**2
        self._median_positive_eigenvalue = float(np.median(singular**2))

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
        return y, value, reference, coordinates

    def degrees_of_freedom(self, lambda_: float) -> float:
        """Trace of H_lambda conditional on a fixed mean mu."""
        return float(np.sum(self._attenuation(lambda_)))

    def smoothness(self, lambda_: float, *, normalized: bool = True) -> float:
        """Compute either normalized or original Guerrero smoothness.

        The default uses (n-tr(H))/(n-d), with range [0,1].
        normalized=False uses Guerrero's original (n-tr(H))/n,
        whose maximum is (n-d)/n. Here EDF = tr(H) conditions on
        the supplied difference-reference mean mu.
        """
        numerator = self.n - self.degrees_of_freedom(lambda_)
        return float(numerator / (self.n - self.order if normalized else self.n))

    def lambda_for_smoothness(
        self, smoothness: float, *, normalized: bool = True,
    ) -> float:
        """Invert either smoothness convention, including exact endpoints.

        Parameters
        ----------
        smoothness : float
            Desired smoothness in [0, 1] if normalized=True, or
            [0, (n-d)/n] for Guerrero's original n-denominator index.
        normalized : bool, default True
            True: (n - tr(H))/(n-d). False: (n - tr(H))/n.

        Returns
        -------
        float
            Nonnegative penalty parameter, possibly infinity at the
            smoothest limiting value.
        """
        target = float(smoothness)
        maximum = 1.0 if normalized else (self.n - self.order) / self.n
        if not np.isfinite(target) or not 0 <= target <= maximum:
            raise ValueError(f"smoothness must belong to [0, {maximum}].")
        if target == 0:
            return 0.0
        if target == maximum:
            return float("inf")
        upper = 1.0 / self._median_positive_eigenvalue
        while self.smoothness(upper, normalized=normalized) < target:
            upper *= 2.0
            if not np.isfinite(upper):
                raise ArithmeticError("Could not bracket the requested smoothness.")
        return float(brentq(
            lambda lam: self.smoothness(lam, normalized=normalized) - target,
            0.0, upper,
        ))

    def fit(self, y, *, lambda_: float, mu: MeanMode = 0.0) -> FitResult:
        """Fit ||y-tau||^2 + lambda ||D_d tau - mu 1||^2.

        mu='data' sets mu to the arithmetic mean of D_d @ y
        (the observed order-d differences), not the raw-series mean
        except when d=0. mu=0.0 is the zero-reference convention.
        EDF conditions on mu; it does not count estimating the plug-in.
        """
        observed, value, reference, coords = self._prepare(y, mu)
        alpha = self._attenuation(lambda_)
        trend = reference + self.eigenvectors @ (alpha * coords)
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
    """One-shot fit. Reuse TrendSmoother across lambda sweeps."""
    values = np.asarray(y)
    if values.ndim != 1:
        raise ValueError("y must be one-dimensional.")
    return TrendSmoother(len(values), order).fit(values, lambda_=lambda_, mu=mu)
