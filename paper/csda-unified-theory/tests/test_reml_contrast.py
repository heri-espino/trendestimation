"""Small deterministic checks of the paper's profiled Gaussian contrast likelihood.

No simulation study, optimization sweep or benchmark is undertaken.
Run: python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_reml_contrast.py' -v
"""
import math
import unittest

import numpy as np


def difference_matrix(n, d):
    D = np.zeros((n - d, n))
    for i in range(n - d):
        for k in range(d + 1):
            D[i, i + k] = (-1) ** (d - k) * math.comb(d, k)
    return D


def checks(n, d, mu, lam):
    D = difference_matrix(n, d)
    r = n - d
    U, sigma, Vt = np.linalg.svd(D, full_matrices=True)
    V = Vt[:r, :].T
    W = Vt[r:, :].T
    delta = sigma**2
    p = mu * np.array([math.comb(t, d) if t >= d else 0 for t in range(n)])
    y = 0.1 * np.arange(n) ** 2 + np.cos(np.arange(n) * 1.17) + 0.08 * np.sin(np.arange(n) * 3.0)

    np.testing.assert_allclose(D @ p, mu * np.ones(r), atol=1e-12)
    np.testing.assert_allclose(D @ W, np.zeros((r, d)), atol=1e-12)
    np.testing.assert_allclose(V.T @ W, np.zeros((r, d)), atol=1e-12)

    z = V.T @ (y - p)
    z_without_polynomial = V.T @ y - mu * (U[:, :r].T @ np.ones(r)) / sigma
    np.testing.assert_allclose(z, z_without_polynomial, rtol=2e-9, atol=2e-9)

    c = 1 + 1 / (lam * delta)
    J = float(np.sum(z**2 / c))
    Q = D.T @ D
    A = np.eye(n) + lam * Q
    fit = np.linalg.solve(A, y + lam * mu * D.T @ np.ones(r))
    J_direct = float(np.sum((y - fit)**2) + lam * np.sum((D @ fit - mu)**2))
    np.testing.assert_allclose(J, J_direct, rtol=3e-10, atol=3e-10)

    B = D @ D.T
    sign_A, log_A = np.linalg.slogdet(A)
    sign_B, log_B = np.linalg.slogdet(B)
    assert sign_A > 0 and sign_B > 0
    spectral_logdet = float(np.sum(np.log(c)))
    np.testing.assert_allclose(spectral_logdet, log_A - r * np.log(lam) - log_B, rtol=3e-9, atol=3e-9)

    # Orthogonal error contrasts have covariance sigma_e^2 diag(c).
    sigma_eps_sq = 1.35
    sigma_u_sq = sigma_eps_sq / lam
    C_z = sigma_eps_sq * np.diag(c)
    C_Dy = sigma_eps_sq * B + sigma_u_sq * np.eye(r)
    dy = D @ y - mu * np.ones(r)
    quadratic_z = z @ np.linalg.solve(C_z, z)
    quadratic_dy = dy @ np.linalg.solve(C_Dy, dy)
    np.testing.assert_allclose(quadratic_z, quadratic_dy, rtol=4e-9, atol=4e-9)
    np.testing.assert_allclose(
        np.linalg.slogdet(C_Dy)[1] - np.linalg.slogdet(C_z)[1],
        log_B, atol=4e-9,
    )

    # Profile the observation variance in the actual Gaussian density.
    profile_variance = J / r
    profile_neg2loglik = (
        r * np.log(2 * np.pi * profile_variance)
        + np.sum(np.log(c))
        + J / profile_variance
    )
    criterion = r * np.log(J / r) + np.sum(np.log(c))
    np.testing.assert_allclose(profile_neg2loglik - criterion, r * (1 + np.log(2 * np.pi)), atol=5e-10)

    # Any choice of p_mu that differs by a nullspace vector gives same z.
    alternative_p = p + W @ np.arange(1, d + 1) * 0.07
    np.testing.assert_allclose(V.T @ (y - alternative_p), z, atol=2e-11)

    # The contrast covariance does not involve the fixed-effect coefficients beta.
    # Verify the diagonal independent variances in the SVD basis.
    np.testing.assert_allclose(
        V.T @ (sigma_u_sq * V @ np.diag(1 / delta) @ V.T + sigma_eps_sq * np.eye(n)) @ V,
        C_z, rtol=2e-11, atol=2e-11,
    )


class TestContrastReml(unittest.TestCase):
    def test_spectral_banded_rem_and_difference_likelihoods(self):
        for n, d in ((5, 1), (6, 2), (7, 3), (9, 2)):
            for mu, lam in ((0.0, 0.4), (0.35, 1.3), (-0.7, 7.0)):
                with self.subTest(n=n, d=d, mu=mu, lam=lam):
                    checks(n, d, mu, lam)


if __name__ == "__main__":
    unittest.main()
