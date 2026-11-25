"""Independent numerical regression for the six-point SVD manuscript example.

No benchmarks or external observations.  The regression checks direct
matrix solves against full reduced-SVD reconstruction, including a
nonzero reference level.  Singular vector signs are not fixed.
"""
from __future__ import annotations

import unittest
import numpy as np


D = np.array(
    [[-1, 3, -3, 1, 0, 0],
     [0, -1, 3, -3, 1, 0],
     [0, 0, -1, 3, -3, 1]],
    dtype=float,
)

H_NUMERATOR = np.array(
    [[171, 47, -8, -18, -8, 11],
     [47, 84, 59, 19, -6, -8],
     [-8, 59, 84, 59, 19, -18],
     [-18, 19, 59, 84, 59, -8],
     [-8, -6, 19, 59, 84, 47],
     [11, -8, -18, -8, 47, 171]],
    dtype=float,
)


class D3NumericSvdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.u, cls.s, cls.vt = np.linalg.svd(D, full_matrices=False)
        cls.q = D.T @ D
        cls.y = np.array([0, 2, 0, 1, 3, 2], dtype=float)

    def test_singular_values_and_full_reconstruction(self) -> None:
        np.testing.assert_allclose(
            self.s,
            [6.66515456, 3.74165739, 1.25527476],
            atol=6e-9, rtol=0,
        )
        np.testing.assert_allclose(
            self.u @ np.diag(self.s) @ self.vt,
            D, rtol=0, atol=3e-14,
        )
        np.testing.assert_allclose(
            np.linalg.eigvalsh(D @ D.T),
            self.s[::-1] ** 2, atol=2e-13, rtol=0,
        )

    def test_exact_smoother_and_far_off_diagonal(self) -> None:
        direct = np.linalg.solve(np.eye(6) + self.q, np.eye(6))
        weights = self.s**2 / (1 + self.s**2)
        spectral = np.eye(6) - self.vt.T @ np.diag(weights) @ self.vt
        np.testing.assert_allclose(
            direct, H_NUMERATOR / 195, atol=2e-14, rtol=0,
        )
        np.testing.assert_allclose(
            direct, spectral, atol=2e-14, rtol=0,
        )
        self.assertAlmostEqual(direct[0, -1], 11 / 195, places=13)
        self.assertEqual(np.linalg.matrix_rank(self.q, tol=1e-9), 3)

    def test_affine_nonzero_reference_agrees_across_penalties(self) -> None:
        for lam in (0, 0.01, 1, 20, 100):
            for mu in (-1.5, 0, 1):
                with self.subTest(lam=lam, mu=mu):
                    direct = np.linalg.solve(
                        np.eye(6) + lam * self.q,
                        self.y + lam * mu * D.T @ np.ones(3),
                    )
                    w = lam * self.s**2 / (1 + lam * self.s**2)
                    spectral = self.y - self.vt.T @ (
                        w * (self.vt @ self.y)
                        - mu * (w / self.s) * (self.u.T @ np.ones(3))
                    )
                    np.testing.assert_allclose(
                        direct, spectral, atol=4e-12, rtol=0,
                    )
                    if lam == mu == 1:
                        np.testing.assert_allclose(
                            direct, np.array([14, 238, 243, 238, 308, 519]) / 195,
                            atol=2e-12, rtol=0,
                        )

    def test_all_printed_svd_entries_match_source_to_four_places(self) -> None:
        # The text uses a specific Lapack sign convention; validate the
        # decomposition numerically rather than requiring vector signs.
        np.testing.assert_allclose(
            abs(self.u),
            abs(np.array([[-.5339, -.7071, .4637],
                          [.6557, 0, .7550],
                          [-.5339, .7071, .4637]])),
            atol=6e-5, rtol=0,
        )
        np.testing.assert_allclose(
            abs(self.vt),
            abs(np.array([[.0801, -.3387, .6155, -.6155, .3387, -.0801],
                          [.1890, -.5669, .3780, .3780, -.5669, .1890],
                          [-.3694, .5067, .3268, -.3268, -.5067, .3694]])),
            atol=6e-5, rtol=0,
        )


if __name__ == "__main__":
    unittest.main()
