"""Deterministic numerical identities for the consolidated theoretical paper.

No statistical simulation, grid search, empirical timing, or Windows runner use.
Run from repository root: python paper/csda-unified-theory/verify_theory.py
"""
from __future__ import annotations

from math import comb
import numpy as np


def verify() -> None:
    rng = np.random.default_rng(20261109)
    cases = 0
    for n, d in [(10, 1), (13, 2), (16, 3), (19, 4), (22, 5)]:
        D = np.diff(np.eye(n), n=d, axis=0)
        U, singular, Vt = np.linalg.svd(D, full_matrices=False)
        V = Vt.T
        Q = D.T @ D
        B = D @ D.T
        assert np.linalg.matrix_rank(D) == n - d
        np.testing.assert_allclose(
            D @ np.array([comb(t, d) for t in range(n)], float),
            np.ones(n-d), rtol=0, atol=5e-10,
        )
        y = rng.normal(size=n)
        for mu in (0.0, 0.15, -0.27):
            p = mu * np.array([comb(t, d) for t in range(n)], float)
            target = mu * np.ones(n-d)
            constrained = y - D.T @ np.linalg.solve(B, D @ y - target)
            spectral_limit = y - V @ (
                V.T @ y - mu * (U.T @ np.ones(n-d)) / singular
            )
            np.testing.assert_allclose(
                constrained, spectral_limit, rtol=1e-8, atol=1e-8
            )
            prev_s = -1.0
            for lam in (0.0, 0.005, 0.2, 2.0, 30.0):
                A = np.eye(n) + lam * Q
                H = np.linalg.inv(A)
                direct = np.linalg.solve(A, y + lam * D.T @ target)
                w = lam * singular**2 / (1 + lam * singular**2)
                shiftfree = y - V @ (
                    w * (V.T @ y)
                    - mu * (w / singular) * (U.T @ np.ones(n-d))
                )
                affine = p + H @ (y - p)
                np.testing.assert_allclose(
                    direct, shiftfree, rtol=1e-8, atol=1e-8
                )
                np.testing.assert_allclose(
                    affine, shiftfree, rtol=1e-8, atol=1e-8
                )
                s = np.mean(w)
                np.testing.assert_allclose(
                    s, (n - np.trace(H)) / (n-d),
                    rtol=1e-9, atol=1e-9,
                )
                assert s >= prev_s
                prev_s = s
                np.testing.assert_allclose(
                    np.diag(H), 1.0 - (V**2) @ w,
                    rtol=1e-9, atol=1e-9,
                )
                if lam > 0:
                    z = V.T @ (y-p)
                    c = 1 + 1 / (lam * singular**2)
                    J_direct = np.linalg.norm(y-direct)**2 + (
                        lam * np.linalg.norm(D @ direct-target)**2
                    )
                    np.testing.assert_allclose(
                        J_direct, np.sum(z*z/c),
                        rtol=1e-8, atol=1e-8,
                    )
                    detleft = np.log(c).sum()
                    detright = (
                        np.linalg.slogdet(A)[1]
                        - (n-d)*np.log(lam)
                        - np.linalg.slogdet(B)[1]
                    )
                    np.testing.assert_allclose(
                        detleft, detright, rtol=1e-8, atol=1e-8
                    )
                cases += 1
        bound = 4**d
        assert np.linalg.eigvalsh(Q).max() <= bound + 1e-8
    print(
        f"PASS: {cases} deterministic nonzero-mu spectral/affine fits, "
        "smoothness/leverage identities, limits, Gaussian quadratic, "
        "determinant and conditioning bounds; no benchmarks run."
    )


if __name__ == "__main__":
    verify()
