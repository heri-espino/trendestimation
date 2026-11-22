"""Algebraic checks for cross-manuscript PLS precision identities.

Source mathematics: Guerrero (2007), Eq. (21)--(23);
Cortes-Toto, Guerrero and Reyes (2017), Eq. (13)--(16).
No experiments, measurements, or external datasets are used.
"""

import math
import unittest

import numpy as np


def difference_matrix(n: int, d: int) -> np.ndarray:
    """Order-d forward differences, exactly matching the manuscripts."""
    result = np.zeros((n - d, n), dtype=float)
    for i in range(n - d):
        for k in range(d + 1):
            result[i, i + k] = (-1) ** (d - k) * math.comb(d, k)
    return result


class PrecisionMatrixIdentityTests(unittest.TestCase):
    def test_posterior_precision_trace_and_spectral_weights(self):
        for n, d in ((7, 1), (9, 2), (10, 3)):
            D = difference_matrix(n, d)
            Q = D.T @ D
            r = n - d
            eigenvalues = np.linalg.eigvalsh(Q)
            delta = eigenvalues[d:]
            self.assertEqual(np.linalg.matrix_rank(D), r)
            self.assertTrue(np.all(delta > 0))

            for lam in (0.01, 1.0, 40.0):
                sigma_u2 = 0.07
                sigma_e2 = lam * sigma_u2
                A = np.eye(n) + lam * Q
                J = np.eye(n) / sigma_e2 + Q / sigma_u2
                P = Q / sigma_u2
                # Explicit inversion appears only in this small deterministic test.
                H = np.linalg.solve(A, np.eye(n))
                posterior_cov = np.linalg.solve(J, np.eye(n))
                np.testing.assert_allclose(posterior_cov, sigma_e2 * H,
                                           rtol=2e-11, atol=2e-11)
                self.assertTrue(np.linalg.eigvalsh(J).min() > 0)

                s = np.sum(lam * delta / (1 + lam * delta)) / r
                s_trace = np.trace(P @ posterior_cov) / r
                s_df = (n - np.trace(H)) / r
                np.testing.assert_allclose([s_trace, s_df], [s, s],
                                           rtol=1e-11, atol=1e-11)
                np.testing.assert_allclose(
                    np.trace(posterior_cov) / sigma_e2
                    + np.trace(P @ posterior_cov),
                    n, rtol=1e-11, atol=1e-11,
                )
                # Guerrero's original n-normalized index differs by r/n.
                np.testing.assert_allclose(
                    np.trace(P @ posterior_cov) / n, (r / n) * s,
                    rtol=1e-11, atol=1e-11,
                )

    def test_mean_and_physical_jerk_covariance(self):
        n, d, mu = 10, 3, 0.004
        D = difference_matrix(n, d)
        Q = D.T @ D
        y = np.linspace(-0.5, 0.8, n) ** 3
        sigma_e2, sigma_u2 = 0.04, 0.08
        lam = sigma_e2 / sigma_u2
        J = np.eye(n) / sigma_e2 + Q / sigma_u2
        rhs = y / sigma_e2 + D.T @ (mu * np.ones(n - d)) / sigma_u2
        mean = np.linalg.solve(J, rhs)
        expected = np.linalg.solve(
            np.eye(n) + lam * Q, y + lam * mu * D.T @ np.ones(n - d)
        )
        np.testing.assert_allclose(mean, expected, rtol=1e-12, atol=1e-12)
        covariance = np.linalg.solve(J, np.eye(n))
        dt = 0.1
        jerk_cov = D @ covariance @ D.T / dt**6
        np.testing.assert_allclose(jerk_cov, jerk_cov.T, atol=1e-7)
        self.assertGreater(np.linalg.eigvalsh(jerk_cov).min(), 0)

    def test_common_scale_changes_absolute_precision_not_smoothness(self):
        n, d, lam = 9, 3, 2.0
        D = difference_matrix(n, d)
        Q = D.T @ D
        sigma_e2, sigma_u2 = 0.2, 0.1
        baseline_J = np.eye(n) / sigma_e2 + Q / sigma_u2
        factor = 4.0
        scaled_J = np.eye(n) / (factor**2 * sigma_e2) + Q / (
            factor**2 * sigma_u2
        )
        np.testing.assert_allclose(scaled_J, baseline_J / factor**2)
        baseline_S = np.trace((Q / sigma_u2)
                              @ np.linalg.solve(baseline_J, np.eye(n))) / (n - d)
        scaled_S = np.trace((Q / (factor**2 * sigma_u2))
                            @ np.linalg.solve(scaled_J, np.eye(n))) / (n - d)
        self.assertAlmostEqual(baseline_S, scaled_S, places=12)


if __name__ == "__main__":
    unittest.main()
