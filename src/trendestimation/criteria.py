"""Classical in-sample CV, GCV, AICc and BIC (Cortes-Toto et al., 2017)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.special import expit

from .core import TrendSmoother
from .likelihood import _score_profile_mle

Criterion = Literal["cv", "gcv", "aicc", "bic", "mle"]
Method = Literal["auto", "grid", "derivative"]
SearchSpace = Literal["lambda", "smoothness"]


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
    search_space : {"lambda", "smoothness"}
        Coordinate used for the candidate search.
    search_grid : numpy.ndarray
        Coordinates searched, aligned with grid and scores. The grid
        attribute always contains penalty values for compatibility.
    """

    criterion: str
    lambda_: float
    smoothness: float
    score: float
    grid: np.ndarray
    scores: np.ndarray
    search_space: str = "lambda"
    search_grid: np.ndarray | None = None



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


def _select_cv_smoothness(
    smoother: TrendSmoother, coordinates: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Refine classical fixed-mu CV directly in normalized smoothness.

    Sample a uniform S mesh together with logit-spaced values near both
    limits; refine stationary brackets via dCV/dS and local score valleys.
    Always compare exact endpoints. This is not certified global search.
    """
    sampled = np.unique(np.r_[
        np.linspace(0.0, 1.0, 97),
        expit(np.linspace(-28.0, 28.0, 97)),
    ])
    cache: dict[float, tuple[float, float, float]] = {}

    def evaluate(s: float) -> tuple[float, float, float]:
        s = float(s)
        if s not in cache:
            penalty = smoother.lambda_for_smoothness(s)
            score, derivative_log = _cv_score_and_log_derivative(
                smoother, coordinates, penalty,
            )
            derivative_s = float("nan")
            if 0.0 < s < 1.0 and np.isfinite(derivative_log):
                slope = smoother._smoothness_log_derivative(np.log(penalty))
                if slope > 0:
                    derivative_s = float(derivative_log / slope)
            cache[s] = float(penalty), float(score), derivative_s
        return cache[s]

    for s in sampled:
        evaluate(float(s))

    def derivative(s: float) -> float:
        value = evaluate(s)[2]
        if not np.isfinite(value):
            raise ValueError("Nonfinite derivative in smoothness search")
        return value

    def objective(s: float) -> float:
        return evaluate(s)[1]

    slopes = [evaluate(float(s))[2] for s in sampled]
    scores = [evaluate(float(s))[1] for s in sampled]
    finite_scores = [v for v in scores if np.isfinite(v)]
    threshold = 1e-13 * max(1.0, max(finite_scores, default=1.0))

    for i in range(1, len(sampled) - 2):
        left, right = slopes[i], slopes[i + 1]
        if not (np.isfinite(left) and np.isfinite(right)):
            continue
        if abs(left) <= threshold or abs(right) <= threshold:
            continue
        if np.signbit(left) == np.signbit(right):
            continue
        try:
            root = brentq(
                derivative, float(sampled[i]), float(sampled[i + 1]),
                xtol=1e-12, maxiter=100,
            )
            evaluate(float(root))
        except (ValueError, ArithmeticError, OverflowError, RuntimeError):
            continue

    # Refining sampled score valleys can catch a minimum with a nearly
    # flat or numerically unresolved derivative.
    for i in range(1, len(sampled) - 1):
        if not (scores[i] <= scores[i - 1] and scores[i] <= scores[i + 1]):
            continue
        if (
            np.isfinite(slopes[i - 1]) and np.isfinite(slopes[i + 1])
            and slopes[i - 1] < 0 < slopes[i + 1]
            and abs(slopes[i - 1]) > threshold
            and abs(slopes[i + 1]) > threshold
        ):
            continue
        try:
            result = minimize_scalar(
                objective,
                bounds=(float(sampled[i - 1]), float(sampled[i + 1])),
                method="bounded", options={"xatol": 1e-12},
            )
            if result.success:
                evaluate(float(result.x))
        except (ValueError, ArithmeticError, OverflowError, RuntimeError):
            continue

    search_grid = np.asarray(sorted(cache), dtype=float)
    penalties = np.asarray([cache[float(s)][0] for s in search_grid])
    scores = np.asarray([cache[float(s)][1] for s in search_grid])
    return penalties, scores, search_grid


def select_lambda(
    smoother: TrendSmoother, y, *, criterion: Criterion = "gcv",
    mu: float | Literal["data"] = 0.0, grid=None, method: Method = "auto",
    search_space: SearchSpace = "lambda",
) -> SelectionResult:
    """Select a smoothing penalty in lambda or normalized smoothness S.

    Parameters
    ----------
    smoother : TrendSmoother
        Reusable spectral smoother.
    y : array_like
        Observed finite one-dimensional data.
    criterion : {"cv", "gcv", "aicc", "bic", "mle"}
        The original statistical score; no criterion is redefined.
    mu : float or {"data"}, default=0.0
        Fixed numerical mean. Only conditional MLE permits the observed
        difference plug-in "data"; this is not joint mean estimation.
    grid : array_like, optional
        Candidate values in the selected search_space. For "lambda" these
        are nonnegative penalties, possibly infinity. For "smoothness"
        these are normalized S values in [0, 1]. Explicit grids retain
        their ordering and duplicates and override "auto" optimization.
    method : {"auto", "grid", "derivative"}, default="auto"
        Auto uses stationary-point refinement for CV and a grid for the
        other criteria. Explicit "derivative" requires CV, without grid.
    search_space : {"lambda", "smoothness"}, default="lambda"
        "lambda" preserves prior behavior and grids; "smoothness"
        optimizes the same score over s=S(lambda) in [0, 1].

    Returns
    -------
    SelectionResult
        The grid attribute always holds evaluated penalty values for
        backward compatibility. The search_grid attribute reports the
        searched coordinate, aligned with the scores, and the winner
        has both the selected penalty and normalized smoothness value.

    Notes
    -----
    S(lambda)=(n-tr(H_lambda))/(n-d), NOT Guerrero's n-denominator
    index. S(0)=0, S(infinity)=1. The inverse is unique for all
    interior values, but its numerical calculation can fail at
    unrepresentable float64 tails. A bounded parameterization neither
    guarantees faster optimization nor global optimality.

    For CV, the derivative search uses
    dCV/ds=(dCV/dloglambda)/(dS/dloglambda). Multiple stationary
    candidates and exact endpoints are compared. The MLE option
    remains conditional on fixed or observed-difference plug-in mu.
    """
    name = str(criterion).lower()
    if name not in {"cv", "gcv", "aicc", "bic", "mle"}:
        raise ValueError("criterion must be cv, gcv, aicc, bic, or mle.")
    if method not in {"auto", "grid", "derivative"}:
        raise ValueError("method must be auto, grid, or derivative.")
    if search_space not in {"lambda", "smoothness"}:
        raise ValueError("search_space must be lambda or smoothness.")
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
        if search_space == "lambda":
            penalties, scores = _select_cv_derivative(smoother, coord)
            searched = penalties.copy()
        else:
            penalties, scores, searched = _select_cv_smoothness(smoother, coord)
    else:
        if search_space == "lambda":
            if grid is None:
                scale = 1.0 / smoother._median_positive_eigenvalue
                grid = np.r_[scale * np.geomspace(1e-6, 1e6, 121), np.inf]
            penalties = np.asarray(grid, dtype=float)
            if (penalties.ndim != 1 or penalties.size == 0
                    or np.any(np.isnan(penalties)) or np.any(penalties < 0)):
                raise ValueError("grid must contain nonnegative lambda values.")
            searched = penalties.copy()
        else:
            if grid is None:
                grid = np.unique(np.r_[
                    np.linspace(0.0, 1.0, 121),
                    [1e-6, 1e-4, 1 - 1e-4, 1 - 1e-6],
                ])
            searched = np.asarray(grid, dtype=float)
            if (searched.ndim != 1 or searched.size == 0
                    or not np.all(np.isfinite(searched))
                    or np.any(searched < 0) or np.any(searched > 1)):
                raise ValueError("smoothness grid must contain values in [0, 1].")
            penalties = np.asarray([
                smoother.lambda_for_smoothness(float(s))
                for s in searched
            ], dtype=float)
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
        grid=penalties,
        scores=scores,
        search_space=search_space,
        search_grid=searched,
    )
