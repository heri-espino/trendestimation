"""Regression tests for Paper C's *fixed-tuning* plug-in trace identities.

No archived experiment or selected lambda/rank is recalculated.
The estimated cubic reference changes the smoother's hat matrix.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "paper" / "ngsim-jerk-case-study" / "experiments" / "experiment008" / "run.py"
spec = importlib.util.spec_from_file_location("paper_c_svd_trace", MODULE)
assert spec and spec.loader
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)
from trendestimation import TrendSmoother  # noqa: E402


def test_full_plug_in_edf_trace_and_fitted_map_for_fixed_tuning():
    n, lam, rank = 80, 250.0, 23
    smoother = TrendSmoother(n, order=3)
    svd = app.RoughnessSVD(smoother)
    t = np.arange(n, dtype=float) * app.DT
    design = np.vander(t, N=4, increasing=True)
    a = 6 * app.DT**3 * np.linalg.pinv(design)[3, :]
    q1 = svd.particular(1.0)
    np.testing.assert_allclose(float(a @ q1), 1.0, rtol=1e-9, atol=1e-9)
    ident = np.eye(n)
    H = np.linalg.solve(ident + lam * smoother.D.T @ smoother.D, ident)
    basis = np.column_stack((svd.V0, svd.Vp[:, :rank]))
    P = basis @ basis.T
    A_pls = H + np.outer((ident - H) @ q1, a)
    A_svd = P + np.outer((ident - P) @ q1, a)
    rng = np.random.default_rng(702)
    y = 50 + 1.3*t - .3*t**2 + .05*t**3 + rng.normal(0, .1, n)
    mu = float(a @ y)
    np.testing.assert_allclose(
        np.asarray(smoother.fit(y, lambda_=lam, mu=mu).trend),
        A_pls @ y, rtol=1e-8, atol=1e-8
    )
    np.testing.assert_allclose(
        svd.fit(y, mu, rank), A_svd @ y,
        rtol=1e-8, atol=1e-8
    )
    np.testing.assert_allclose(
        np.trace(A_pls),
        np.trace(H) + float(a @ (ident-H) @ q1), atol=1e-9
    )
    np.testing.assert_allclose(
        np.trace(A_svd), 3 + rank + float(a @ (ident-P) @ q1),
        atol=1e-9
    )


def test_archived_tsvd_rank_rule_uses_conditional_gcv_denominator():
    smoother = TrendSmoother(80, order=3)
    svd = app.RoughnessSVD(smoother)
    rng = np.random.default_rng(736)
    y = rng.normal(0, 1, 80)
    mu = 0.00051
    rank, score = svd.gcv_rank(y, mu)
    fit = svd.fit(y, mu, rank)
    residual = np.linalg.norm(y-fit)**2
    expected = 80 * residual / (77-rank)**2
    np.testing.assert_allclose(score, expected, rtol=5e-8, atol=1e-9)
    assert 0 <= rank < 77
