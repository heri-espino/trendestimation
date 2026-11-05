"""Regression checks for the complete fixed-mean PLS leverage diagonal.

The thin SVD describes only penalized directions.  The smoother is
H = I - V diag(w) V.T, not V diag(1-w) V.T: the latter omits the
unpenalized polynomial nullspace and gives incorrect CV leverages.

This small deterministic identity check is independent of paper timings.
"""
from __future__ import annotations

import unittest
from math import comb

import numpy as np


def forward_difference(n: int, d: int) -> np.ndarray:
    """Return the unscaled order-d forward-difference matrix."""
    matrix = np.zeros((n - d, n), dtype=float)
    for row in range(n - d):
        for offset in range(d + 1):
            matrix[row, row + offset] = (-1) ** (d - offset) * comb(d, offset)
    return matrix


class TestFixedMeanSpectralLeverage(unittest.TestCase):
    def test_leverage_matches_direct_solve(self) -> None:
        for n, d, lam in [
            (8, 1, 0.7),
            (8, 2, 0.7),
            (12, 3, 1.2),
            (16, 4, 0.01),
        ]:
            with self.subTest(n=n, d=d, lam=lam):
                D = forward_difference(n, d)
                _, singular_values, Vt = np.linalg.svd(
                    D, full_matrices=False
                )
                V = Vt.T
                weights = (
                    lam * singular_values**2
                    / (1.0 + lam * singular_values**2)
                )
                spectral_leverage = 1.0 - (V**2) @ weights
                direct_leverage = np.diag(
                    np.linalg.solve(
                        np.eye(n) + lam * (D.T @ D), np.eye(n)
                    )
                )
                np.testing.assert_allclose(
                    spectral_leverage,
                    direct_leverage,
                    atol=1e-11,
                    rtol=1e-11,
                )
                self.assertAlmostEqual(
                    float(np.sum(spectral_leverage)),
                    float(n - np.sum(weights)),
                    places=10,
                )

    def test_endpoint_preserves_polynomial_nullspace(self) -> None:
        n, d = 8, 2
        D = forward_difference(n, d)
        _, _, Vt = np.linalg.svd(D, full_matrices=False)
        V = Vt.T
        nullspace_projector = np.eye(n) - V @ V.T
        self.assertAlmostEqual(
            float(np.trace(nullspace_projector)), float(d), places=10
        )
        # At maximal smoothing, nonzero leverage remains in the
        # polynomial nullspace; the penalized-only expression misses it.
        self.assertGreater(float(np.min(np.diag(nullspace_projector))), 0.0)


if __name__ == "__main__":
    unittest.main()
