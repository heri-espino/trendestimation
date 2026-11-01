"""Experimental PLS fitting directly from prescribed spectral smoothness weights.

This module intentionally does NOT replace the existing, independently tested
lambda-based API and does not modify concurrent PR #79 (S-only convenience
wrapper). It demonstrates a different way to execute the *same* estimator:

    w_j = r_j*u / (1-u+r_j*u), r_j=delta_j/delta_*
    mean(w_j) = requested normalized smoothness S.

The scalar implicit ridge-family coupling remains necessary. Internally we
solve its logit(u) for stability, but fitting does not calculate a lambda
or a dense matrix inverse. This does NOT imply a runtime advantage.

Future integration should first rebase PR #79 on the current shift-free core.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal

import numpy as np
from scipy.optimize import brentq
from scipy.special import expit

from .core import TrendSmoother


@dataclass(frozen=True)
class SpectralSmoothnessFit:
    """Result of direct spectral-weight reconstruction.

    The logit of a representative shrinkage weight is an *implicit*
    one-dimensional penalty coordinate; it is NOT the same as S and
    should not be interpreted as another statistical hyperparameter.
    """

    trend: np.ndarray
    residual: np.ndarray
    smoothness: float
    mu: float
    order: int
    edf_conditional: float
    root_function_evaluations: int


def fit_spectral_smoothness(
    smoother: TrendSmoother,
    y,
    *,
    smoothness: float,
    mu: float | Literal["data"] = 0.0,
    tol: float = 1e-12,
    maxiter: int = 150,
) -> SpectralSmoothnessFit:
    """Fit the SAME PLS estimator using S-constrained spectral weights.

    No lambda is passed in or explicitly computed. One monotonically
    increasing scalar root in the log-odds of a representative weight
    remains necessary except at S=0 or S=1. The root is solved in
    normalized spectral coordinates, unlike a naive dense inversion.

    The accepted smoothness is the normalized Guerrero-derived
    S=(n-tr H)/(n-d). EDF is conditional on a *fixed* reference mu;
    when mu="data", the reported EDF does not include the dependence
    introduced by estimating mu from y.

    This research prototype requires an existing TrendSmoother whose
    full SVD was prepared once. No fresh factorization occurs per fit.
    """
    if not isinstance(smoother, TrendSmoother):
        raise TypeError("smoother must be an existing TrendSmoother")
    s = float(smoothness)
    if not np.isfinite(s) or not 0.0 <= s <= 1.0:
        raise ValueError("smoothness must be a finite value in [0, 1]")
    if not np.isfinite(tol) or tol <= 0:
        raise ValueError("tol must be positive and finite")
    if isinstance(maxiter, bool) or not isinstance(maxiter, int) or maxiter < 1:
        raise ValueError("maxiter must be a positive integer")
    observed = np.asarray(y, dtype=float)
    if observed.ndim != 1 or len(observed) != smoother.n or not np.all(np.isfinite(observed)):
        raise ValueError(f"y must be a finite 1-D sequence of length {smoother.n}")
    if isinstance(mu, str):
        if mu != "data":
            raise ValueError("mu must be finite numeric or 'data'")
        value = float(np.mean(smoother.D @ observed))
    else:
        value = float(mu)
    if not np.isfinite(value):
        raise ValueError("mu must be finite")

    n, d = smoother.n, smoother.order
    r = n-d
    V = smoother.eigenvectors[:, :r]
    if s == 0.0:
        trend = observed.copy()
        edf = float(n)
        evaluations = 0
    else:
        if s == 1.0:
            weights = np.ones(r, dtype=float)
            evaluations = 0
        else:
            logs = np.asarray(smoother._log_positive_eigenvalues, dtype=float)
            if logs.shape != (r,) or not np.all(np.isfinite(logs)):
                raise ArithmeticError("Cannot resolve a positive penalty spectrum")
            anchor = float(np.median(logs))
            log_ratios = logs-anchor
            # Let u be the shrinkage weight at the reference eigenvalue.
            # x = logit(u), so w_j=expit(x+log(delta_j/delta_*)).
            # x is an implicit scalar dual variable, NOT S.
            log_odds_s = math.log(s)-math.log1p(-s)
            lower = log_odds_s-float(np.max(log_ratios))-2.0
            upper = log_odds_s-float(np.min(log_ratios))+2.0
            high = s > .5
            tail = (1.0-s) if high else s
            evaluations = 0

            def residual(x: float) -> float:
                nonlocal evaluations
                evaluations += 1
                z = x+log_ratios
                # Complementary tail avoids subtracting nearly equal
                # numbers when S is extremely close to one.
                target = np.mean(expit(-z) if high else expit(z))
                return float(target-tail)

            x = brentq(
                residual,lower,upper,
                xtol=tol,rtol=4*np.finfo(float).eps,
                maxiter=maxiter,
            )
            z=x+log_ratios
            mismatch = abs(float(np.mean(expit(-z) if high else expit(z)))-tail)
            if mismatch > max(5*tol,1e-13)*tail:
                raise ArithmeticError("Spectral smoothness root failed validation")
            weights = expit(z)
        # Cached spectral projections for D_d p_mu = mu*1:
        # V.T(y-p_mu)=V.T y - mu* U.T 1 / sigma
        coordinates = V.T @ observed - value*smoother._mean_shift_coordinates
        trend = observed - V @ (weights*coordinates)
        edf = float(d + np.sum(1.0-weights))
    return SpectralSmoothnessFit(
        trend=trend,
        residual=observed-trend,
        smoothness=s,
        mu=value,
        order=d,
        edf_conditional=edf,
        root_function_evaluations=evaluations,
    )
