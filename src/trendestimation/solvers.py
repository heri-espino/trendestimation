"""Alternative backends for *full trend reconstruction* in PLS smoothing.

This module deliberately does not replace TrendSmoother's SVD-based
selection-criterion implementation. It compares equivalent, reusable
full-trend fitters without silently claiming Cholesky can supply exact
spectral EDF, CV leverages or smoothness indices at the same cost.

Methods
-------
svd: full SVD of the finite-difference matrix (existing baseline).
eigh: symmetric eigen-decomposition of the formed D.T @ D.
cholesky: positive-definite Cholesky factorization in lower band storage
          of I + lambda * D.T @ D, newly computed for each lambda.

Full SVD and eigh reuse dense spectral bases across penalties; Cholesky
builds the penalty directly in banded form without a dense n-by-n Q.
"""
from __future__ import annotations

from math import comb
from typing import Literal

import numpy as np
from scipy.linalg import (
    cho_solve_banded, cholesky_banded, eigh, svd,
)
from scipy.special import binom

from .core import difference_matrix

FitBackend = Literal["svd", "eigh", "cholesky"]


def _penalty_lower_bands(n: int, d: int) -> np.ndarray:
    """Return the lower-band representation of D_d.T @ D_d.

    bands[k, i] stores Q[i+k, i]; only d+1 diagonals are allocated.
    """
    bands = np.zeros((d + 1, n), dtype=float)
    coeff = [(-1) ** (d - j) * comb(d, j) for j in range(d + 1)]
    for first in range(n - d):
        for a, ca in enumerate(coeff):
            for b in range(a, d + 1):
                bands[b - a, first + a] += ca * coeff[b]
    return bands


class PreparedPLSSolver:
    """Fit the *same* PLS trends with one of three linear-algebra backends.

    Parameters
    ----------
    n : int
        Series length, at least one.
    order : int, default=2
        Forward difference order with 0 <= order < n.
    method : {"svd", "eigh", "cholesky"}, default="svd"
        Solver used for the fitted trend. The default intentionally matches
        the current library rather than asserting an unverified fastest method.

    Notes
    -----
    Unlike TrendSmoother.fit, fit returns only the reconstructed 1-D trend;
    EDF, normalized smoothness, CV, GCV, AICc, BIC and MLE are handled by
    the existing spectral API. This prevents hiding expensive spectral work
    inside a supposedly fast Cholesky fit.
    """

    def __init__(
        self, n: int, order: int = 2, *, method: FitBackend = "svd",
    ) -> None:
        if (isinstance(n, (bool, np.bool_)) or
                not isinstance(n, (int, np.integer)) or n < 1):
            raise ValueError("n must be a positive integer.")
        if (isinstance(order, (bool, np.bool_)) or
                not isinstance(order, (int, np.integer)) or not 0 <= order < n):
            raise ValueError("order must be an integer in [0, n).")
        if method not in ("svd", "eigh", "cholesky"):
            raise ValueError("method must be svd, eigh, or cholesky.")

        self.n = int(n)
        self.order = int(order)
        self.method = method
        self.eigenvectors: np.ndarray | None = None
        self.eigenvalues: np.ndarray | None = None
        self.penalty_bands: np.ndarray | None = None

        if method == "cholesky":
            self.penalty_bands = _penalty_lower_bands(self.n, self.order)
        else:
            D = difference_matrix(self.n, self.order)
            if method == "svd":
                _, singular, vh = svd(D, full_matrices=True, check_finite=True)
                self.eigenvectors = vh.T
                self.eigenvalues = np.r_[
                    singular * singular, np.zeros(self.order),
                ]
            else:
                values, vectors = eigh(D.T @ D, check_finite=True)
                # The d exactly unpenalized modes are the first d sorted
                # eigenpairs. Floating-point roundoff may perturb zero.
                values[:self.order] = 0.0
                if np.any(values[self.order:] <= 0):
                    raise ArithmeticError(
                        "eigh could not resolve the positive penalty spectrum; "
                        "use method='svd' for this ill-conditioned case."
                    )
                self.eigenvectors = vectors
                self.eigenvalues = values

    def _prepare(
        self, y, mu: float | Literal["data"],
    ) -> tuple[np.ndarray, np.ndarray]:
        observed = np.asarray(y, dtype=float)
        if (observed.ndim != 1 or observed.size != self.n
                or not np.all(np.isfinite(observed))):
            raise ValueError("y must be a finite one-dimensional array of length n.")
        if mu == "data":
            # np.diff avoids allocating an n-by-n difference matrix.
            reference_mean = float(np.mean(np.diff(observed, n=self.order)))
        else:
            reference_mean = float(mu)
        if not np.isfinite(reference_mean):
            raise ValueError("mu must be finite.")
        if self.order == 0:
            reference = np.full(self.n, reference_mean)
        else:
            reference = reference_mean * binom(
                np.arange(self.n, dtype=float), self.order,
            )
        if not np.all(np.isfinite(reference)):
            raise OverflowError("The polynomial reference is not representable.")
        return observed, reference

    def _fit_prepared(
        self,
        observed: np.ndarray,
        reference: np.ndarray,
        lam: float,
        coordinates: np.ndarray | None,
    ) -> np.ndarray:
        if np.isnan(lam) or lam < 0:
            raise ValueError("lambda_ must be nonnegative, possibly infinity.")
        if lam == 0:
            return observed.copy()

        centered = observed - reference
        if self.method == "cholesky":
            if np.isinf(lam):
                if self.order == 0:
                    return reference.copy()
                # Orthonormal polynomial space, independent of lambda.
                # Legendre basis avoids a poorly scaled raw Vandermonde.
                grid = np.linspace(-1.0, 1.0, self.n)
                basis = np.polynomial.legendre.legvander(
                    grid, self.order - 1,
                )
                projected = basis @ np.linalg.lstsq(
                    basis, centered, rcond=None,
                )[0]
                return reference + projected
            assert self.penalty_bands is not None
            ab = lam * self.penalty_bands.copy()
            ab[0, :] += 1.0
            if not np.all(np.isfinite(ab)):
                raise OverflowError("The banded system overflows float64.")
            factor = cholesky_banded(
                ab, lower=True, overwrite_ab=True, check_finite=False,
            )
            solution = cho_solve_banded(
                (factor, True), centered, check_finite=False,
            )
            return reference + solution

        assert self.eigenvalues is not None
        assert self.eigenvectors is not None
        alpha = (
            (self.eigenvalues == 0).astype(float)
            if np.isinf(lam)
            else 1.0 / (1.0 + lam * self.eigenvalues)
        )
        if coordinates is None:
            coordinates = self.eigenvectors.T @ centered
        return reference + self.eigenvectors @ (alpha * coordinates)

    def fit(
        self, y, *, lambda_: float,
        mu: float | Literal["data"] = 0.0,
    ) -> np.ndarray:
        """Compute one full fitted trend, without spectral diagnostics."""
        observed, reference = self._prepare(y, mu)
        return self._fit_prepared(
            observed, reference, float(lambda_), None,
        )

    def fit_many(
        self, y, lambdas, *, mu: float | Literal["data"] = 0.0,
    ) -> np.ndarray:
        """Compute fitted trends for multiple penalties, reusing projections.

        Returns an array with one fitted trend per row. For dense spectral
        methods the projection of y-p_mu is shared. Cholesky refactorizes
        the banded system for each distinct finite positive penalty.
        """
        penalties = np.asarray(lambdas, dtype=float)
        if penalties.ndim != 1 or not np.all(~np.isnan(penalties)):
            raise ValueError("lambdas must be a one-dimensional non-NaN array.")
        if np.any(penalties < 0):
            raise ValueError("lambdas must be nonnegative.")
        observed, reference = self._prepare(y, mu)
        coords = None
        if self.eigenvectors is not None:
            coords = self.eigenvectors.T @ (observed - reference)
        return np.asarray([
            self._fit_prepared(observed, reference, float(lam), coords)
            for lam in penalties
        ]).reshape(penalties.size, self.n)

    @property
    def stored_bytes(self) -> int:
        """Direct bytes of long-lived ndarray state (not process RSS)."""
        return sum(
            a.nbytes for a in (
                self.eigenvectors, self.eigenvalues, self.penalty_bands,
            ) if a is not None
        )


def fit_penalized(
    y, *, lambda_: float, order: int = 2,
    mu: float | Literal["data"] = 0.0,
    method: FitBackend = "svd",
) -> np.ndarray:
    """Fit one trend with a chosen backend, returning its 1-D values.

    Construct PreparedPLSSolver explicitly for repeated penalty fits so
    the cost of spectral preparation is paid only once.
    """
    values = np.asarray(y, dtype=float)
    if values.ndim != 1:
        raise ValueError("y must be one-dimensional.")
    return PreparedPLSSolver(
        len(values), order=order, method=method,
    ).fit(values, lambda_=lambda_, mu=mu)
