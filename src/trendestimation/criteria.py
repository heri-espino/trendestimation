"""Classical in-sample CV, GCV, AICc and BIC (Cortes-Toto et al., 2017)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .core import TrendSmoother
from .likelihood import _score_profile_mle

Criterion = Literal["cv", "gcv", "aicc", "bic", "mle"]


@dataclass(frozen=True)
class SelectionResult:
    criterion: str
    lambda_: float
    smoothness: float
    score: float
    grid: np.ndarray
    scores: np.ndarray


def _score_from_coordinates(
    smoother: TrendSmoother, coord: np.ndarray, *,
    lambda_: float, name: Criterion,
) -> float:
    if name == "mle":
        return _score_profile_mle(smoother, coord, lambda_=lambda_)
    alpha = smoother._attenuation(lambda_)
    edf = float(np.sum(alpha))
    residual_coordinates = (1.0 - alpha) * coord
    rss = float(residual_coordinates @ residual_coordinates)
    n = smoother.n
    eps = np.finfo(float).eps * max(1.0, float(coord @ coord))
    if name == "cv":
        residual = smoother.eigenvectors @ residual_coordinates
        leverage = smoother._basis_squares @ alpha
        denom = 1.0 - leverage
        if np.any(denom <= 1e-10):
            return float("inf")
        return float(np.mean((residual / denom) ** 2))
    if name == "gcv":
        denom = 1.0 - edf / n
        return float((rss / n) / denom**2) if denom > 1e-10 else float("inf")
    if rss <= eps:
        return float("inf")
    log_mean_rss = np.log(rss / n)
    if name == "bic":
        return float(log_mean_rss + edf * np.log(n) / n)
    denom = n - edf - 2.0
    return float(log_mean_rss + (2.0 * edf + 1.0) / denom) if denom > 0 else float("inf")


def score_lambda(
    smoother: TrendSmoother, y, *, lambda_: float,
    criterion: Criterion = "gcv", mu: float = 0.0,
) -> float:
    """Evaluate an in-sample score or profiled Gaussian likelihood.

    Supported criteria are cv, gcv, aicc, bic, and mle. The mle score
    is twice negative profiled Gaussian marginal log-likelihood, up
    to an additive constant (smaller is better). For mle only,
    mu='data' uses the mean of the observed d-th differences as a
    conditional plug-in; this is not joint estimation of mu.
    All classical criteria require fixed numeric mu, because their
    usual degrees-of-freedom and CV formulas do not refit the mean.
    """
    name = str(criterion).lower()
    if name not in {"cv", "gcv", "aicc", "bic", "mle"}:
        raise ValueError("criterion must be cv, gcv, aicc, bic, or mle.")
    if isinstance(mu, str) and (mu != "data" or name != "mle"):
        raise ValueError("Only mle supports mu='data'; classical criteria require fixed mu.")
    _, _, _, coord = smoother._prepare(y, mu if mu == "data" else float(mu))
    return _score_from_coordinates(smoother, coord, lambda_=lambda_, name=name)


def select_lambda(
    smoother: TrendSmoother, y, *, criterion: Criterion = "gcv",
    mu: float = 0.0, grid=None,
) -> SelectionResult:
    """Choose lambda on a grid using CV/GCV/AICc/BIC or Gaussian MLE.

    mle maximizes profiled Gaussian marginal likelihood, removing
    the d-dimensional unpenalized difference nullspace and profiling
    observation variance. Its mu='data' option uses a conditional
    observed-difference plug-in, not joint estimation of the mean.
    Only mle accepts mu='data'; classic criteria need numeric mu.
    lambda=0 has no proper Gaussian latent prior and receives
    infinite MLE score; lambda=infinity is evaluated exactly.
    Default grid: 121 geometric lambdas and the infinite endpoint.
    This is not forecast-horizon TSCV or a forecasting estimator.
    """
    name = str(criterion).lower()
    if name not in {"cv", "gcv", "aicc", "bic", "mle"}:
        raise ValueError("criterion must be cv, gcv, aicc, bic, or mle.")
    if isinstance(mu, str) and (mu != "data" or name != "mle"):
        raise ValueError("Only mle supports mu='data'; classical criteria require fixed mu.")
    if grid is None:
        scale = 1.0 / smoother._median_positive_eigenvalue
        grid = np.r_[scale * np.geomspace(1e-6, 1e6, 121), np.inf]
    grid = np.asarray(grid, dtype=float)
    if grid.ndim != 1 or grid.size == 0 or np.any(np.isnan(grid)) or np.any(grid < 0):
        raise ValueError("grid must contain nonnegative lambda values.")
    _, _, _, coord = smoother._prepare(y, mu if mu == "data" else float(mu))
    scores = np.asarray([
        _score_from_coordinates(smoother, coord, lambda_=lam, name=name)
        for lam in grid
    ])
    valid = np.isfinite(scores)
    if not np.any(valid):
        raise ValueError("No finite criterion score on the grid.")
    best = int(np.argmin(np.where(valid, scores, np.inf)))
    return SelectionResult(
        criterion=name,
        lambda_=float(grid[best]),
        smoothness=smoother.smoothness(grid[best]),
        score=float(scores[best]),
        grid=grid, scores=scores,
    )
