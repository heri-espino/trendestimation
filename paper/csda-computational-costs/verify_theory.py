"""Deterministic algebraic checks for the standalone CSDA complexity paper.

No timing results, synthetic performance claims or optimizer benchmarks
are generated. Test only equalities stated in the manuscript.
"""
from __future__ import annotations

from math import isclose

import numpy as np
from scipy.linalg import cho_solve_banded, cholesky_banded


def selected_inverse_from_band_factor(lower: np.ndarray) -> np.ndarray:
    """Takahashi selected inverse using LAPACK's lower-band Cholesky layout."""
    d, n = lower.shape[0] - 1, lower.shape[1]
    z = np.zeros((d + 1, n))
    for i in range(n - 1, -1, -1):
        end = min(n, i + d + 1)
        for j in range(i + 1, end):
            total = 0.0
            for k in range(i + 1, end):
                zkj = z[j - k, k] if k <= j else z[k - j, j]
                total += (lower[k - i, i] / lower[0, i]) * zkj
            z[j - i, i] = -total
        z[0, i] = (1.0 / lower[0, i] ** 2 -
                   sum((lower[k - i, i] / lower[0, i]) * z[k - i, i]
                       for k in range(i + 1, end)))
    return z


def test_theoretical_identities() -> None:
    rng = np.random.default_rng(20261103)
    verified = 0
    for n, d in [(8, 1), (11, 2), (15, 3), (20, 4)]:
        D = np.diff(np.eye(n), n=d, axis=0)
        Q = D.T @ D
        r = n - d
        eigvals = np.linalg.eigvalsh(Q)[d:]
        assert np.all(eigvals > 0)
        if d == 1:
            expected = 2 - 2 * np.cos(np.pi * np.arange(1, n) / n)
            np.testing.assert_allclose(eigvals, expected, atol=1e-12)
        gram = D @ D.T
        gram_sign, gram_logdet = np.linalg.slogdet(gram)
        assert gram_sign > 0
        for lam in (0.05, 2.4, 15.0):
            mu = 0.15
            y = rng.normal(size=n)
            A = np.eye(n) + lam * Q
            ab = np.zeros((d + 1, n))
            for k in range(d + 1):
                ab[k, : n - k] = np.diag(A, k=-k)
            L = cholesky_banded(ab, lower=True, check_finite=True)
            fitted = cho_solve_banded(
                (L, True), y + lam * mu * D.T @ np.ones(r),
                check_finite=True
            )
            direct = np.linalg.solve(
                A, y + lam * mu * D.T @ np.ones(r))
            np.testing.assert_allclose(fitted, direct, rtol=2e-10, atol=2e-10)
            selected = selected_inverse_from_band_factor(L)
            H = np.linalg.inv(A)
            np.testing.assert_allclose(
                selected[0], np.diag(H), rtol=2e-9, atol=2e-9)
            s_banded = (n - selected[0].sum()) / r
            s_spectral = np.mean(lam * eigvals / (1 + lam * eigvals))
            assert isclose(s_banded, s_spectral,
                           abs_tol=5e-10, rel_tol=5e-10)
            p = np.linalg.lstsq(D, mu * np.ones(r), rcond=None)[0]
            z = y - p
            quadratic = z @ (np.eye(n) - H) @ z
            j_direct = (np.linalg.norm(y - fitted) ** 2 +
                        lam * np.linalg.norm(D @ fitted - mu) ** 2)
            np.testing.assert_allclose(
                quadratic, j_direct, rtol=2e-9, atol=2e-9)
            positive_logdet = np.log(1 + 1 / (lam * eigvals)).sum()
            # Cholesky factor itself supplies log(det(A)) as 2*sum(log(L_ii)).
            band_logdet = (2 * np.log(L[0]).sum() -
                           r * np.log(lam) - gram_logdet)
            np.testing.assert_allclose(
                positive_logdet, band_logdet, rtol=2e-9, atol=2e-9)
            verified += 1
    print(f"Verified {verified} small deterministic cases: "
          "DCT eigenvalues, banded solve, Takahashi inverse diagonal, "
          "smoothness, profiled quadratic and log determinant.")


if __name__ == "__main__":
    test_theoretical_identities()
