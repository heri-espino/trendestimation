"""Deterministic mathematical examples for the CSDA Weinert comparison.

These are algebraic checks, not timing benchmarks.
Run from repository root:
    python -m unittest discover -s paper/csda-unified-theory/tests -p "test_d3_weinert_comparison.py" -v
"""
import math
import unittest

import numpy as np


def difference_matrix(n: int, d: int) -> np.ndarray:
    dmat = np.zeros((n - d, n), dtype=float)
    for i in range(n - d):
        for k in range(d + 1):
            dmat[i, i + k] = (-1) ** (d - k) * math.comb(d, k)
    return dmat


EXPECTED_D3 = np.array(
    [
        [-1, 3, -3, 1, 0, 0],
        [0, -1, 3, -3, 1, 0],
        [0, 0, -1, 3, -3, 1],
    ],
    dtype=float,
)
EXPECTED_Q3 = np.array(
    [
        [1, -3, 3, -1, 0, 0],
        [-3, 10, -12, 6, -1, 0],
        [3, -12, 19, -15, 6, -1],
        [-1, 6, -15, 19, -12, 3],
        [0, -1, 6, -12, 10, -3],
        [0, 0, -1, 3, -3, 1],
    ],
    dtype=float,
)


class ThirdDifferenceAndWeinertTests(unittest.TestCase):
    def setUp(self):
        self.dmat = difference_matrix(6, 3)
        self.qmat = self.dmat.T @ self.dmat

    def test_manuscript_d_and_q_exact(self):
        np.testing.assert_array_equal(self.dmat, EXPECTED_D3)
        np.testing.assert_array_equal(self.qmat, EXPECTED_Q3)
        self.assertEqual(np.linalg.matrix_rank(self.dmat), 3)
        self.assertEqual(np.linalg.matrix_rank(self.qmat), 3)
        self.assertEqual(self.qmat[0, 5], 0.0)
        self.assertTrue(np.all(np.linalg.eigvalsh(self.qmat)[3:] > 0))

    def test_normal_matrix_spd_and_smoother_dense(self):
        a = np.eye(6) + self.qmat
        eigenvalues = np.linalg.eigvalsh(a)
        self.assertTrue(np.all(eigenvalues > 0))
        h = np.linalg.solve(a, np.eye(6))
        self.assertAlmostEqual(h[0, 5], 11.0 / 195.0, places=13)
        self.assertAlmostEqual(h[5, 0], 11.0 / 195.0, places=13)

    def test_weinert_alpha_matches_lambda_for_zero_reference(self):
        y = np.array([0.4, -0.7, 0.9, 1.2, 0.1, -1.4])
        for lam in (0.25, 1.0, 2.5, 12.0):
            alpha = 1.0 / lam
            weinert = np.linalg.solve(alpha * np.eye(6) + self.qmat, alpha * y)
            ours = np.linalg.solve(np.eye(6) + lam * self.qmat, y)
            np.testing.assert_allclose(weinert, ours, rtol=1e-12, atol=1e-12)

    def test_reusable_svd_for_multiple_lambda_and_nonzero_mu(self):
        y = np.array([2.0, -1.0, 0.0, 2.5, 2.0, 5.0])
        mu = 0.35
        u, sigma, vt = np.linalg.svd(self.dmat, full_matrices=False)
        v = vt.T
        uy = u.T @ np.ones(3)
        proj = vt @ y
        for lam in (0.1, 1.0, 8.0, 30.0):
            w = lam * sigma**2 / (1.0 + lam * sigma**2)
            svd_fit = y - v @ (w * proj - mu * w / sigma * uy)
            a = np.eye(6) + lam * self.qmat
            direct = np.linalg.solve(a, y + lam * mu * self.dmat.T @ np.ones(3))
            np.testing.assert_allclose(svd_fit, direct, rtol=1e-11, atol=1e-11)

    def test_cubic_constant_jerk_and_quadratic_zero_jerk(self):
        h = 0.5
        t = np.arange(6, dtype=float) * h
        jerk = 1.7
        cubic_position = 4.0 + 3.0 * t + 0.5 * 2.0 * t**2 + jerk * t**3 / 6.0
        quadratic_position = 4.0 + 3.0 * t + 0.5 * 2.0 * t**2
        np.testing.assert_allclose(
            self.dmat @ cubic_position, np.full(3, jerk * h**3), atol=1e-12
        )
        np.testing.assert_allclose(self.dmat @ quadratic_position, 0.0, atol=1e-12)


if __name__ == "__main__":
    unittest.main()
