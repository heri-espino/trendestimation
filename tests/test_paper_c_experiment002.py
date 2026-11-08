"""Deterministic checks for Paper C conventional forecast benchmark.

Tests do not modify the archived original Paper C results. They run small
synthetic signal checks and a bounded read-only NGSIM comparison.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "paper" / "ngsim-jerk-case-study"
SCRIPT = CASE / "experiments" / "experiment002" / "run.py"
spec = importlib.util.spec_from_file_location("ngsim_exp002_testmodule", SCRIPT)
assert spec is not None and spec.loader is not None
exp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp)


def test_spline_sg_polynomial_forecasts_finite_and_shape():
    t = np.arange(80) * 0.1
    clean = 4 + 2*t - 0.08*t*t + 0.002*t*t*t
    rng = np.random.default_rng(61042)
    noise = rng.normal(0, 0.007, size=len(t))
    for y in (clean, clean+noise):
        forecasts, sigma = exp.forecasts(y, 20)
        assert 0.01 <= sigma <= 0.75
        assert tuple(forecasts) == exp.METHODS
        assert all(pred.shape == (20,) and np.all(np.isfinite(pred))
                   for pred in forecasts.values())


def test_raw_cubic_predicts_true_cubic_without_noise():
    t = np.arange(80) * 0.1
    y = 4 + t - 0.04*t**2 + 0.002*t**3
    forecast, _ = exp.forecasts(y, 20)
    expected = 4 + np.arange(80,100)*0.1 - 0.04*(np.arange(80,100)*0.1)**2
    expected += 0.002*(np.arange(80,100)*0.1)**3
    np.testing.assert_allclose(forecast["raw_local_cubic25"], expected,
                               rtol=0, atol=2e-9)
    np.testing.assert_allclose(forecast["spline_cubic_taylor3"], expected,
                               rtol=0, atol=2e-8)


def test_frozen_case_comparator_outputs_preserve_shape():
    rows, summary, manifest, report = exp.calculate()
    assert len(rows) == 315
    assert len(summary) == 21
    assert manifest["distinct_vehicle_ids"] == 2
    assert manifest["n_origins"] == 15
    assert set(row["method"] for row in rows) == set(exp.METHODS)
    assert "PLS_GCV_guerrero_last3_zero" in report
    assert all(np.isfinite(row["mse_m2"]) for row in rows)
