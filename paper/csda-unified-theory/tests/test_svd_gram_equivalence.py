"""Deterministic SVD/Gram-eigen equivalence checks for the CSDA manuscript.

Run from repository root:
    python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_svd_gram_equivalence.py' -v

These are small algebra checks, not timing benchmarks or scientific experiments.
"""
import math
import unittest

import numpy as np


def difference_matrix(n, d):
    D = np.zeros((n - d, n), dtype=float)
    stencil = [(-1) ** (d - k) * math.comb(d, k) for k in range(d + 1)]
    for i in range(n - d):
        D[i, i:i + d + 1] = stencil
    return D


def smoothness(lam, delta):
    return float(np.mean(lam * delta / (1.0 + lam * delta)))


def invert_smoothness(target, delta):
    lo, hi = 0.0, 1.0
    while smoothness(hi, delta) < target:
        hi *= 2.0
    for _ in range(90):
        mid = (lo + hi) / 2.0
        if smoothness(mid, delta) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


class SvdGramEquivalenceTests(unittest.TestCase):
    def test_positive_spectrum_and_smoother(self):
        for d in (1, 2, 3):
            for n in range(d + 2, 10):
                with self.subTest(n=n, d=d):
                    D = difference_matrix(n, d)
                    _, singular, vh = np.linalg.svd(D, full_matrices=True)
                    Q = D.T @ D
                    eigenvalues, eigenvectors = np.linalg.eigh(Q)
                    r = n - d
                    np.testing.assert_allclose(
                        np.sort(singular ** 2), eigenvalues[-r:],
                        rtol=1e-8, atol=1e-10,
                    )
                    self.assertLess(np.max(np.abs(eigenvalues[:d])), 1e-10)
                    self.assertAlmostEqual(
                        (singular[0] / singular[-1]) ** 2,
                        eigenvalues[-1] / eigenvalues[d], places=6,
                    )
                    lam = 3.5
                    V = vh.T
                    H_svd = (
                        V * np.r_[1 / (1 + lam * singular ** 2), np.ones(d)]
                    ) @ V.T
                    H_eig = (
                        eigenvectors * (1 / (1 + lam * eigenvalues))
                    ) @ eigenvectors.T
                    H_direct = np.linalg.solve(np.eye(n) + lam * Q, np.eye(n))
                    np.testing.assert_allclose(H_svd, H_eig, rtol=1e-10, atol=1e-10)
                    np.testing.assert_allclose(H_svd, H_direct, rtol=1e-10, atol=1e-10)

    def test_inverse_smoothness_eigenvalue_sensitivity(self):
        singular = np.linalg.svd(difference_matrix(7, 2), compute_uv=False)
        delta = singular ** 2
        target = 0.75
        lam = invert_smoothness(target, delta)
        denominator = np.sum(delta / (1 + lam * delta) ** 2)
        j = 3
        predicted = -lam / (1 + lam * delta[j]) ** 2 / denominator
        step = 1e-5 * delta[j]
        plus, minus = delta.copy(), delta.copy()
        plus[j] += step
        minus[j] -= step
        observed = (
            invert_smoothness(target, plus) - invert_smoothness(target, minus)
        ) / (2 * step)
        self.assertAlmostEqual(predicted / observed, 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
