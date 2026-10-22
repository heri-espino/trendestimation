"""Classical in-sample CV, GCV, AICc and BIC (Cortes-Toto et al., 2017)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.optimize import brentq, minimize_scalar

from .core import TrendSmoother
from .likelihood import _score_profile_mle

Criterion = Literal["cv", "gcv", "aicc", "bic", "mle"]
Method = Literal["auto", "grid", "derivative"]


@dataclass(frozen=True)
class SelectionResult:
    """Best smoothing criterion result and actually evaluated candidates.

    Attributes
    ----------
    criterion : str
        One of "cv", "gcv", "aicc", "bic", or "mle".
    lambda_ : float
        Selected penalty among evaluated candidates.
    smoothness : float
        Normalized smoothness at the selected penalty.
    score : float
        Criterion value for the selected penalty.
    grid : numpy.ndarray
        All evaluated nonnegative candidates, including derivative refinements.
    scores : numpy.ndarray
        Criterion scores, aligned with the evaluated candidates.
    """

    criterion: str
    lambda_: float
    smoothness: float
    score: float
    grid: np.ndarray
    scores: np.ndarray



def _cv_score_and_log_derivative(
    smoother: TrendSmoother, coord: np.ndarray, lam: float,
) -> tuple[float, float]:
    """Exact classical LOOCV score and its log-penalty derivative.

    Let Q=D_d.T D_d=U diag(delta) U.T, with positive spectral part U_+
    and c=U.T(y-p_mu), where D_d p_mu=mu*1. Put
    w_j=lambda*delta_j/(1+lambda*delta_j). Then

        r_i = (U_+(w*c))_i,
        1-h_ii = (U_+**2 @ w)_i,
        CV = mean((r/(1-h_ii))**2).

    Writing a=r, b=1-h_ii and dots for d/d(log lambda),
    dCV/d(log lambda) = 2*mean((a/b)*(dot(a)-a*dot(b)/b)/b).

    The ordinary derivative uses w'_j=delta_j/(1+lambda*delta_j)^2.
    Close to lambda=0+, cancel lambda from a and b using instead
    v_j=delta_j/(1+lambda*delta_j), v'_j=-v_j**2. This preserves
    the leave-one-out ratio without subtractive cancellation.

    At lambda=0 the actual unregularized LOOCV refits are undefined,
    so the score is +inf. The right-sided score is approached using
    strictly positive penalties. At infinity use the exact limit.
    """
    if np.isnan(lam) or lam < 0:
        raise ValueError("lambda_ must lie in [0, infinity].")
    if lam == 0:
        return float("inf"), float("nan")
    rank = smoother.n - smoother.order
    delta = smoother.eigenvalues[:rank]
    U = smoother.eigenvectors[:, :rank]
    U2 = smoother._basis_squares[:, :rank]
    z = coord[:rank]

    if np.isinf(lam):
        weights = np.ones(rank)
        dweights = np.zeros(rank)
        logarithmic = True
    elif lam <= 1.0 / float(np.max(delta)):
        weights = delta / (1.0 + lam * delta)
        dweights = -(weights * weights)
        logarithmic = False
    else:
        alpha = 1.0 / (1.0 + lam * delta)
        weights = 1.0 - alpha
        dweights = weights * alpha
        logarithmic = True

    a = U @ (weights * z)
    b = U2 @ weights
    if np.any(b <= 0) or not np.all(np.isfinite(b)):
        return float("inf"), float("nan")
    e = a / b
    score = float(np.mean(e * e))
    if not np.isfinite(score):
        return float("inf"), float("nan")
    da = U @ (dweights * z)
    db = U2 @ dweights
    de = (da - e * db) / b
    derivative = float(2.0 * np.mean(e * de))
    if not logarithmic:
        derivative *= lam
    if not np.isfinite(derivative):
        derivative = float("nan")
    return score, derivative


def cv_derivative(
    smoother: TrendSmoother, y, *, lambda_: float, mu: float = 0.0,
) -> float:
    """Analytical d(CV)/d(lambda) for exact fixed-mu classical LOOCV.

    For H=(I+lambda*Q)^-1 and r=y-tau, let b_i=1-h_ii.
    Then r'=H Q H(y-p_mu), h'_ii=-(H Q H)_ii, and
    CV'=2*mean((r/b)*(r'*b+r*h'_ii)/b**2).
    The implementation uses the cached eigensystem and an equivalent
    spectral quotient stable for small positive lambda. It does not
    use finite differences or recompute a dense matrix inverse.

    The mean mu must be fixed and numeric; mu='data' is not exact
    LOOCV without re-estimating the mean on each deletion.
    lambda=0 is undefined; the derivative tends to 0 at infinity.
    This is in-sample, not chronological forecast cross-validation.
    """
    lam = float(lambda_)
    if np.isnan(lam) or lam <= 0:
        raise ValueError("cv_derivative requires positive lambda_ (or infinity).")
    if isinstance(mu, str):
        raise ValueError("cv_derivative requires fixed numeric mu.")
    _, _, _, coordinates = smoother._prepare(y, float(mu))
    _, derivative_log = _cv_score_and_log_derivative(smoother, coordinates, lam)
    return 0.0 if np.isinf(lam) else float(derivative_log / lam)


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
        return _cv_score_and_log_derivative(smoother, coord, float(lambda_))[0]
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



def _select_cv_derivative(
    smoother: TrendSmoother, coordinates: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Explore a broad log scale and refine all sampled stationary brackets.

    This is a deterministic multi-start search, NOT certified global
    optimization: sufficiently narrow features may evade a finite mesh.
    """
    delta = smoother.eigenvalues[:smoother.n - smoother.order]
    low = 1e-12 / float(np.max(delta))
    high = 1e12 / float(np.min(delta))
    low = max(low, np.nextafter(0.0, 1.0))
    high = min(high, np.finfo(float).max / 100.0)
    if not np.isfinite(low) or not np.isfinite(high) or high <= low:
        scale = 1.0 / smoother._median_positive_eigenvalue
        low, high = scale * 1e-12, scale * 1e12

    cache: dict[float, tuple[float, float]] = {}

    def evaluate(lam: float) -> tuple[float, float]:
        lam = float(lam)
        if lam not in cache:
            cache[lam] = _cv_score_and_log_derivative(smoother, coordinates, lam)
        return cache[lam]

    log_points = np.linspace(np.log(low), np.log(high), 97)
    points = np.exp(log_points)
    for lam in points:
        evaluate(lam)
    evaluate(0.0)
    evaluate(float("inf"))

    def df_dt(loglam: float) -> float:
        value = evaluate(float(np.exp(loglam)))[1]
        if not np.isfinite(value):
            raise ValueError("Nonfinite CV derivative during refinement")
        return value

    def objective(loglam: float) -> float:
        return evaluate(float(np.exp(loglam)))[0]

    values = [evaluate(lam)[1] for lam in points]
    scores = [evaluate(lam)[0] for lam in points]
    score_scale = max(1.0, max(s for s in scores if np.isfinite(s)))
    threshold = 1e-13 * score_scale
    for i in range(len(points) - 1):
        left, right = values[i], values[i + 1]
        if not (np.isfinite(left) and np.isfinite(right)):
            continue
        if abs(left) <= threshold or abs(right) <= threshold:
            continue
        if np.signbit(left) == np.signbit(right):
            continue
        try:
            root = brentq(df_dt, log_points[i], log_points[i + 1],
                          xtol=1e-11, maxiter=100)
            evaluate(float(np.exp(root)))
        except (ValueError, RuntimeError, OverflowError):
            continue

    # Fallback for sampled score valleys missed by the derivative scan.
    for i in range(1, len(points) - 1):
        if not (scores[i] <= scores[i - 1] and scores[i] <= scores[i + 1]):
            continue
        if (abs(values[i - 1]) > threshold and abs(values[i + 1]) > threshold
                and values[i - 1] < 0 < values[i + 1]):
            continue
        try:
            result = minimize_scalar(
                objective, bounds=(log_points[i - 1], log_points[i + 1]),
                method="bounded", options={"xatol": 1e-10},
            )
            if result.success:
                evaluate(float(np.exp(result.x)))
        except (ValueError, RuntimeError, OverflowError):
            continue

    penalties = np.array(sorted(cache), dtype=float)
    criterion_scores = np.asarray([cache[float(lam)][0] for lam in penalties])
    return penalties, criterion_scores


def select_lambda(
    smoother: TrendSmoother, y, *, criterion: Criterion = "gcv",
    mu: float | Literal["data"] = 0.0, grid=None, method: Method = "auto",
) -> SelectionResult:
    """Select smoothing strength with grid or analytical CV refinement.

    For criterion='cv', method='auto' (default) finds all sampled
    derivative sign-change brackets on a broad log-penalty interval,
    refines them with Brent's root solver, verifies their original
    CV scores, and also compares boundary and limiting candidates.
    A finite search cannot certify the global minimum.

    method='grid' preserves the 121-point default grid plus infinity.
    An explicitly provided grid overrides method='auto' and scores
    only those values, preserving their order and any duplicates.
    Non-CV criteria always use the legacy grid strategy; explicit
    method='derivative' is only supported for classical CV.

    SelectionResult.grid and .scores record every scored candidate,
    including root evaluations for derivative-based search.
    The reported smoothness is the existing normalized trace index.
    Fixed numeric mu is mandatory for classical criteria. MLE alone
    supports the empirical plug-in mu='data' as before.
    """
    name = str(criterion).lower()
    if name not in {"cv", "gcv", "aicc", "bic", "mle"}:
        raise ValueError("criterion must be cv, gcv, aicc, bic, or mle.")
    if method not in {"auto", "grid", "derivative"}:
        raise ValueError("method must be auto, grid, or derivative.")
    if isinstance(mu, str) and (mu != "data" or name != "mle"):
        raise ValueError("Only mle supports mu='data'; classical criteria require fixed mu.")
    if name == "mle" and (smoother.order == 0 or smoother.n - smoother.order < 2):
        raise ValueError("mle requires order >= 1 and at least two penalized coordinates.")
    if name != "cv" and method == "derivative":
        raise ValueError("method='derivative' is only supported for criterion='cv'.")
    if grid is not None and method == "derivative":
        raise ValueError("Provide a grid or use method='derivative', not both.")
    _, _, _, coord = smoother._prepare(y, mu if mu == "data" else float(mu))
    if name == "cv" and grid is None and method != "grid":
        penalties, scores = _select_cv_derivative(smoother, coord)
    else:
        if grid is None:
            scale = 1.0 / smoother._median_positive_eigenvalue
            grid = np.r_[scale * np.geomspace(1e-6, 1e6, 121), np.inf]
        penalties = np.asarray(grid, dtype=float)
        if (penalties.ndim != 1 or penalties.size == 0
                or np.any(np.isnan(penalties)) or np.any(penalties < 0)):
            raise ValueError("grid must contain nonnegative lambda values.")
        scores = np.asarray([
            _score_from_coordinates(smoother, coord, lambda_=lam, name=name)
            for lam in penalties
        ])
    valid = np.isfinite(scores)
    if not np.any(valid):
        raise ValueError("No finite criterion score on the grid.")
    best = int(np.argmin(np.where(valid, scores, np.inf)))
    return SelectionResult(
        criterion=name,
        lambda_=float(penalties[best]),
        smoothness=smoother.smoothness(penalties[best]),
        score=float(scores[best]),
        grid=penalties, scores=scores,
    )
