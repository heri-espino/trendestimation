"""Regression tests for Paper C's third-difference PLS forecast attribution.

These are deterministic algebraic checks on synthetic vectors, NOT a
statistical experiment and NOT an evaluation on NGSIM trajectories.
They deliberately call the real run_case.continuation() implementation
while leaving all frozen Paper C artifacts untouched.

Run from repository root:
    python -m unittest discover -s paper/ngsim-jerk-case-study/tests -v
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys
import unittest

import numpy as np


_CASE_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = _CASE_DIR.parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))
_SPEC = importlib.util.spec_from_file_location(
    "ngsim_case_for_test", _CASE_DIR / "run_case.py"
)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
continuation = _MODULE.continuation


def third_difference(n: int) -> np.ndarray:
    """Identical standard forward-difference convention to np.diff."""
    return np.diff(np.eye(n), n=3, axis=0)


def cubic_particular(t: np.ndarray) -> np.ndarray:
    """q_t = binomial(t,3), so D3 q = 1."""
    return np.array(
        [math.comb(int(i), 3) if i >= 3 else 0 for i in t],
        dtype=float,
    )


class TestJerkReferenceForecastAttribution(unittest.TestCase):
    def test_endpoint_mean_telescopes(self) -> None:
        rng = np.random.default_rng(57331)
        for n in (6, 12, 80):
            with self.subTest(n=n):
                y = rng.normal(size=n)
                direct = float(np.mean(np.diff(y, n=3)))
                second = np.diff(y, n=2)
                boundary = float((second[-1] - second[0]) / (n - 3))
                self.assertAlmostEqual(direct, boundary, places=12)

    def test_particular_solution_and_fit_identity(self) -> None:
        n = 80
        D = third_difference(n)
        q = cubic_particular(np.arange(n))
        np.testing.assert_allclose(D @ q, np.ones(n - 3), atol=1e-11)

        lam = 0.23
        mu = 0.00015
        y = 0.2 * np.sin(np.arange(n) / 7) + 0.005 * np.arange(n)
        Q = D.T @ D
        H = np.linalg.solve(np.eye(n) + lam * Q, np.eye(n))
        fit_affine = H @ y + mu * (np.eye(n) - H) @ q
        fit_normal = np.linalg.solve(
            np.eye(n) + lam * Q, y + lam * mu * D.T @ np.ones(n - 3)
        )
        np.testing.assert_allclose(fit_affine, fit_normal, rtol=1e-9, atol=1e-9)

    def test_crossed_forecast_exact_decomposition(self) -> None:
        n, h = 80, 20
        y = 0.02 * np.arange(n) + 0.4 * np.sin(np.arange(n) / 8)
        D = third_difference(n)
        q = cubic_particular(np.arange(n))
        q_future = cubic_particular(np.arange(n, n + h))
        mu = 0.00012

        # L is the actual continuation's degree-2, last-25-point operator.
        L = lambda z: continuation(z, order=3, mu=0.0, horizon=h)
        for lam in (0.0, 0.1, 1.0):
            with self.subTest(lam=lam):
                H = np.linalg.solve(
                    np.eye(n) + lam * (D.T @ D), np.eye(n)
                )
                base = H @ y
                fit_effect = (np.eye(n) - H) @ q

                def forecast(mu_fit: float, mu_future: float) -> np.ndarray:
                    fit = base + mu_fit * fit_effect
                    return continuation(
                        fit, order=3, mu=mu_future, horizon=h
                    )

                for mf, mc in ((0.0, 0.0), (mu, 0.0), (0.0, mu), (mu, mu)):
                    direct = forecast(mf, mc)
                    analytic = (
                        L(base)
                        + mf * L(fit_effect)
                        + mc * (q_future - L(q))
                    )
                    np.testing.assert_allclose(
                        direct, analytic, rtol=1e-9, atol=5e-9
                    )

                interaction = (
                    forecast(mu, mu)
                    - forecast(mu, 0.0)
                    - forecast(0.0, mu)
                    + forecast(0.0, 0.0)
                )
                np.testing.assert_allclose(
                    interaction, np.zeros(h), atol=5e-9
                )

                if lam == 0.0:
                    # With no regularization, fitted positions do not
                    # depend on mu, but the separately appended cubic can.
                    np.testing.assert_allclose(
                        forecast(mu, 0.0), forecast(0.0, 0.0),
                        atol=5e-9,
                    )
                    self.assertGreater(
                        np.linalg.norm(forecast(0.0, mu) - forecast(0.0, 0.0)),
                        1e-8,
                    )


if __name__ == "__main__":
    unittest.main()
