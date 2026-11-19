"""Regression tests for Paper C's rank-normalized smoothness interpretation.

These checks are algebraic, not additional statistical experiments.
"""

import numpy as np


def _third_differences(n: int) -> np.ndarray:
    d = np.zeros((n - 3, n))
    for i in range(n - 3):
        d[i, i : i + 4] = [-1.0, 3.0, -3.0, 1.0]
    return d


def test_guerrero_original_versus_rank_normalized_index():
    n = 8
    d = _third_differences(n)
    q = d.T @ d
    m = n - 3
    delta = np.linalg.eigvalsh(d @ d.T)
    previous = -1.0
    for lam in (0.0, 0.01, 0.1, 1.0, 10.0, 1000.0):
        h = np.linalg.solve(np.eye(n) + lam * q, np.eye(n))
        normalized = float(np.mean(lam * delta / (1.0 + lam * delta)))
        guerrero = 1.0 - np.trace(h) / n
        np.testing.assert_allclose(guerrero, (m / n) * normalized, atol=1e-12)
        np.testing.assert_allclose(np.trace(h), n - m * normalized, atol=1e-12)
        assert normalized >= previous
        previous = normalized

    assert normalized < 1.0
    assert normalized > 0.99
    assert (m / n) * normalized < 0.625


def test_precision_and_differenced_covariance_noise_share():
    n = 8
    d = _third_differences(n)
    m = n - 3
    sigma_e2, sigma_u2 = 0.04, 0.0025
    lam = sigma_e2 / sigma_u2
    q = d.T @ d
    j = np.eye(n) / sigma_e2 + q / sigma_u2
    p = q / sigma_u2
    rank_share = float(np.trace(np.linalg.solve(j, p)) / m)
    b = d @ d.T
    observed_diff_cov = sigma_u2 * np.eye(m) + sigma_e2 * b
    covariance_share = float(
        np.trace(np.linalg.solve(observed_diff_cov, sigma_e2 * b)) / m
    )
    delta = np.linalg.eigvalsh(b)
    normalized = float(np.mean(lam * delta / (1.0 + lam * delta)))
    np.testing.assert_allclose(rank_share, normalized, atol=1e-11)
    np.testing.assert_allclose(covariance_share, normalized, atol=1e-11)


def test_normalized_smoothness_depends_only_on_variance_ratio():
    d = _third_differences(8)
    delta = np.linalg.eigvalsh(d @ d.T)
    for scale in (1.0, 4.0, 17.0):
        sigma_e = scale * 0.05
        sigma_u = scale * 0.002
        lam = sigma_e**2 / sigma_u**2
        s = float(np.mean(lam * delta / (1.0 + lam * delta)))
        if scale == 1.0:
            reference = s
        else:
            np.testing.assert_allclose(s, reference, rtol=1e-13)
