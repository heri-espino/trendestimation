"""Experiment006 research implementation: unknown-mean Gaussian REML.

The public trendestimation API is not changed. The historical fixed-mu
likelihood in the library remains correct. This code estimates the mean
*inside* the restricted likelihood and then selects lambda continuously.

Numerical model: v = D_d y, B = D_d D_d.T, W = I + lambda B,
mu(lambda) = (1.T W^-1 v)/(1.T W^-1 1),
F_R = logdet(W) + log(1.T W^-1 1)
      + (m-1)*log((v-mu 1).T W^-1(v-mu 1)/(m-1)).
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import eigh
from scipy.optimize import minimize_scalar


@dataclass(frozen=True)
class Estimate:
    lambda_: float
    mu: float
    score: float
    selector: str
    smoothness: float
    position: str
    n_evaluations: int


class DifferenceLikelihood:
    """Cache the B eigensystem for fixed n and difference order.

    For d=3 and n=80 this is a 77x77 symmetric positive-definite
    matrix. No dense inverse or determinant is computed during scoring.
    """

    def __init__(self, smoother):
        self.smoother = smoother
        self.D = np.asarray(smoother.D, dtype=float)
        if self.D.ndim != 2 or self.D.shape[0] < 2:
            raise ValueError("Unknown-mean REML requires n-d >= 2")
        B = self.D @ self.D.T
        eigenvalues, eigenvectors = eigh(B, check_finite=True)
        if eigenvalues[0] <= 0:
            raise ValueError("Difference covariance is not positive definite")
        self.delta = eigenvalues
        self.one = eigenvectors.T @ np.ones(len(eigenvalues))
        self.U = eigenvectors
        self.m = len(eigenvalues)
        self._sum_log_delta = float(np.log(eigenvalues).sum())

    def transform(self, y):
        y = np.asarray(y, dtype=float)
        if y.shape != (self.D.shape[1],) or not np.isfinite(y).all():
            raise ValueError("y must be finite, 1-D and match the smoother length")
        return self.U.T @ (self.D @ y)

    def score(self, v, lam: float, *, fixed_mu: float | None = None):
        """Return (profile score, conditional GLS/fixed mean, derivative).

        lam=0 and infinity use the one-sided variance-ratio limits, not
        the existing library's improper-at-zero prior convention.
        """
        lam = float(lam)
        if np.isnan(lam) or lam < 0:
            raise ValueError("lambda must be nonnegative")
        v = np.asarray(v, dtype=float)
        if v.shape != (self.m,) or not np.isfinite(v).all():
            raise ValueError("Invalid difference coordinates")
        if fixed_mu is not None and not np.isfinite(fixed_mu):
            raise ValueError("fixed_mu must be finite")

        # For lambda=infinity work in covariance scaled by lambda.
        if np.isinf(lam):
            w = self.delta
            logdet = self._sum_log_delta
        else:
            w = 1.0 + lam * self.delta
            logdet = float(np.log1p(lam * self.delta).sum())
        invw = 1.0 / w
        a = float(np.dot(self.one * invw, self.one))
        if a <= 0 or not np.isfinite(a):
            return float("inf"), float("nan"), float("nan")
        mu = (float(np.dot(self.one * invw, v)) / a
              if fixed_mu is None else float(fixed_mu))
        residual = v - mu * self.one
        q = float(np.dot(residual * invw, residual))
        if not (q > 0) or not np.isfinite(q):
            return float("inf"), mu, float("nan")

        k = self.m - (1 if fixed_mu is None else 0)
        score = logdet + k * math.log(q / k)
        if fixed_mu is None:
            score += math.log(a)
        if np.isinf(lam):
            return float(score), mu, float("nan")
        trace = float(np.sum(self.delta * invw))
        d_quad = float(np.sum(self.delta * (residual * invw) ** 2))
        derivative = trace - k * d_quad / q
        if fixed_mu is None:
            d_a = float(np.sum(self.delta * (self.one * invw) ** 2))
            derivative -= d_a / a
        return float(score), float(mu), float(derivative)

    def limits(self):
        """A wide, finite lambda search based on the normalized smoothness index.

        Endpoints 0 and infinity are evaluated separately. The interior
        is a predetermined log-lambda lattice plus local refinements;
        it is not a mathematical proof of unimodality.
        """
        low = float(self.smoother.lambda_for_smoothness(0.0001))
        high = float(self.smoother.lambda_for_smoothness(0.9999))
        if not (0 < low < high < float("inf")):
            raise ValueError("Cannot construct finite positive lambda search")
        return low, high

    def optimize(
        self, y, *, fixed_mu: float | None = None,
        search: str = "continuous",
        grid: tuple[float, ...] | None = None,
    ) -> Estimate:
        v = self.transform(y)
        evaluations: dict[float, tuple[float, float, float]] = {}

        def evaluate(lam: float):
            lam = float(lam)
            if lam not in evaluations:
                evaluations[lam] = self.score(v, lam, fixed_mu=fixed_mu)
            return evaluations[lam]

        if search == "grid":
            if not grid or any(np.isnan(x) or x < 0 for x in grid):
                raise ValueError("Need a valid grid of nonnegative penalties")
            for lam in grid:
                evaluate(lam)
        elif search == "continuous":
            low, high = self.limits()
            logs = np.linspace(math.log(low), math.log(high), 61)
            f = np.empty(len(logs), dtype=float)
            for idx, ell in enumerate(logs):
                f[idx] = evaluate(math.exp(float(ell)))[0]
            # Refine ALL observed local minima, not a single arbitrary start.
            for i in range(1, len(logs)-1):
                if f[i] <= f[i-1] and f[i] <= f[i+1] and np.isfinite(f[i]):
                    result = minimize_scalar(
                        lambda x: evaluate(math.exp(float(x)))[0],
                        bounds=(float(logs[i-1]), float(logs[i+1])),
                        method="bounded", options={"xatol": 1e-8, "maxiter": 100},
                    )
                    evaluate(math.exp(float(result.x)))
        else:
            raise ValueError("search must be continuous or grid")

        if search == "continuous":
            # Explicitly include the limits only for the broad continuous
            # search. The baseline grid must remain EXACTLY the declared
            # values: S>=0.05, with infinity only because S=1 is listed.
            evaluate(0.0)
            evaluate(float("inf"))
        good = [(score, lam, mu) for lam, (score, mu, _) in evaluations.items()
                if np.isfinite(score) and np.isfinite(mu)]
        if not good:
            raise ValueError("All Gaussian restricted likelihood evaluations invalid")
        score, lam, mu = min(good, key=lambda x: (x[0], x[1]))
        if lam == 0:
            position = "zero_limit"
        elif np.isinf(lam):
            position = "infinity_limit"
        elif search == "grid":
            position = "finite_grid"
        else:
            position = "finite_continuous"
        return Estimate(
            lambda_=lam, mu=mu, score=score,
            selector="joint_reml" if fixed_mu is None else "fixed_mu_profile_mle",
            smoothness=float(self.smoother.smoothness(lam)),
            position=position, n_evaluations=len(evaluations),
        )
