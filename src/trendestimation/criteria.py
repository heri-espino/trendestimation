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
    """Best smoothing criterion result on a specified grid.

    Attributes
    ----------
    criterion : str
        One of "cv", "gcv", "aicc", "bic", or "mle".
    lambda_ : float
        Selected penalty on the candidate grid.
    smoothness : float
        Normalized smoothness at the selected penalty.
    score : float
        Criterion value for the selected penalty.
    grid : numpy.ndarray
        Evaluated nonnegative penalty candidates.
    scores : numpy.ndarray
        Criterion scores, aligned to grid.
    """

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
    criterion: Criterion = "gcv", mu: float | Literal["data"] = 0.0,
) -> float:
    """Score a penalty by one classical in-sample selection criterion.

    Parameters
    ----------
    smoother : TrendSmoother
        Spectral smoother built for the series length and difference order.
    y : array_like
        Observed finite one-dimensional series.
    lambda_ : float
        Penalty to evaluate, including positive infinity.
    criterion : {"cv", "gcv", "aicc", "bic", "mle"}, default="gcv"
        Classical criterion or Gaussian profiled marginal MLE.
    mu : float or {"data"}, default=0.0
        Fixed numeric mean; MLE also permits observed-difference plug-in "data".

    Returns
    -------
    float
        Score (lower is preferred); infinity means the criterion
        is undefined at the chosen penalty.

    Notes
    -----
    Gaussian MLE profiles observation variance on the positive-penalty
    coordinates and eliminates unpenalized polynomial trend components.
    For MLE, mu="data" means mean(D_d @ y) and is used as a conditional
    plug-in, not joint maximum likelihood of mu and lambda. Classical
    CV/GCV/AICc/BIC require fixed numeric mu, and the MLE score is
    twice negative profiled marginal log-likelihood up to constants.
    lambda=0 has an improper prior and an infinite MLE score.

    Criteria are only provided for fixed numeric mu. Calling with
    mu="data" raises ValueError because a data-selected mean would
    have to be re-estimated in each deletion for exact leave-one-out CV.
    This is not rolling or forecast-horizon cross-validation.
    A standalone evaluation projects the observations on the spectral
    basis; select_lambda amortizes this step across a grid.
    """
    name = str(criterion).lower()
    if name not in {"cv", "gcv", "aicc", "bic", "mle"}:
        raise ValueError("criterion must be cv, gcv, aicc, bic, or mle.")
    if isinstance(mu, str) and (mu != "data" or name != "mle"):
        raise ValueError("Only mle supports mu='data'; classical criteria require fixed mu.")
    if name == "mle" and (smoother.order == 0 or smoother.n - smoother.order < 2):
        raise ValueError("mle requires order >= 1 and at least two penalized coordinates.")
    _, _, _, coord = smoother._prepare(y, mu if mu == "data" else float(mu))
    return _score_from_coordinates(smoother, coord, lambda_=lambda_, name=name)


def select_lambda(
    smoother: TrendSmoother, y, *, criterion: Criterion = "gcv",
    mu: float | Literal["data"] = 0.0, grid=None,
) -> SelectionResult:
    """Select smoothing strength on a grid using an in-sample criterion.

    Parameters
    ----------
    smoother : TrendSmoother
        Reusable spectral smoother with matching series length.
    y : array_like
        Finite observations to smooth.
    criterion : {"cv", "gcv", "aicc", "bic", "mle"}, default="gcv"
        Classical criterion or Gaussian profiled marginal MLE.
    mu : float or {"data"}, default=0.0
        Fixed numeric mean; MLE also permits observed-difference plug-in "data".
    grid : array_like, optional
        One-dimensional nonnegative lambda candidates; defaults to
        121 geometric candidates plus the exact infinite-penalty limit.

    Returns
    -------
    SelectionResult
        Best penalty, smoothness, and all evaluated grid scores.

    Raises
    ------
    ValueError
        If input candidates are invalid, all scores are undefined,
        or the input mu is unsupported for the selected criterion.

    Notes
    -----
    Gaussian MLE profiles observation variance on the positive-penalty
    coordinates and eliminates unpenalized polynomial trend components.
    For MLE, mu="data" means mean(D_d @ y) and is used as a conditional
    plug-in, not joint maximum likelihood of mu and lambda. Classical
    CV/GCV/AICc/BIC require fixed numeric mu, and the MLE score is
    twice negative profiled marginal log-likelihood up to constants.
    lambda=0 has an improper prior and an infinite MLE score.

    Selection is classical in-sample CV/GCV/AICc/BIC, not rolling
    time-series cross-validation or future-forecast tuning. The
    method evaluates a finite candidate grid and does not claim
    to find a globally optimal penalty outside that grid.

    Examples
    --------
    >>> import numpy as np
    >>> from trendestimation import TrendSmoother, select_lambda
    >>> y = np.linspace(0, 2, 30) + np.random.default_rng(3).normal(0, .2, 30)
    >>> result = select_lambda(TrendSmoother(len(y), 2), y, criterion="gcv")
    >>> 0 <= result.smoothness <= 1
    True
    """
    name = str(criterion).lower()
    if name not in {"cv", "gcv", "aicc", "bic", "mle"}:
        raise ValueError("criterion must be cv, gcv, aicc, bic, or mle.")
    if isinstance(mu, str) and (mu != "data" or name != "mle"):
        raise ValueError("Only mle supports mu='data'; classical criteria require fixed mu.")
    if name == "mle" and (smoother.order == 0 or smoother.n - smoother.order < 2):
        raise ValueError("mle requires order >= 1 and at least two penalized coordinates.")
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
