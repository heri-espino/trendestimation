"""Paper C experiment001: deterministic d=3 extrapolation and archive parity."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
from scipy.special import binom


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "paper" / "ngsim-jerk-case-study"
RUNNER = CASE / "experiments" / "experiment001" / "run.py"
spec = importlib.util.spec_from_file_location("paper_c_d3_case", CASE / "run_case.py")
assert spec is not None and spec.loader is not None
case = importlib.util.module_from_spec(spec)
spec.loader.exec_module(case)


@pytest.mark.parametrize("mu", [0.0, 0.00012, -0.00016])
def test_d3_three_point_recurrence_exact_for_cubic_polynomial(mu):
    n = 80
    horizon = 20
    t = np.arange(n, dtype=float)
    future = np.arange(n, n + horizon, dtype=float)
    # Polynomial and particular solution written in the same index units as D3.
    trend = 2.0 + 0.4 * t + 0.001 * t * t + mu * binom(t, 3)
    truth = 2.0 + 0.4 * future + 0.001 * future * future + mu * binom(future, 3)
    actual = case.continuation_guerrero_d3(trend, mu, horizon)
    np.testing.assert_allclose(actual, truth, atol=2e-9, rtol=1e-11)
    local = case.continuation(trend, order=3, mu=mu, horizon=horizon)
    np.testing.assert_allclose(actual, local, atol=2e-9, rtol=1e-11)


def test_d3_recurrence_one_step_identity():
    rng = np.random.default_rng(20261108)
    trend = rng.normal(size=80)
    mu = 0.004
    pred = case.continuation_guerrero_d3(trend, mu, 2)
    last, prev, prev2 = trend[-1], trend[-2], trend[-3]
    np.testing.assert_allclose(pred[0], 3 * last - 3 * prev + prev2 + mu)
    np.testing.assert_allclose(
        pred[1], last + 2 * (last - prev)
        + 3 * (last - 2 * prev + prev2) + 4 * mu
    )


@pytest.mark.parametrize("trend,mu,horizon", [
    ([1.0, 2.0], 0.0, 1),
    ([1.0, float("nan"), 3.0], 0.0, 1),
    ([1.0, 2.0, 3.0], float("nan"), 1),
    ([1.0, 2.0, 3.0], 0.0, 0),
    ([1.0, 2.0, 3.0], 0.0, 1.5),
])
def test_d3_recurrence_invalid_inputs(trend, mu, horizon):
    with pytest.raises(ValueError):
        case.continuation_guerrero_d3(trend, mu, horizon)


def test_archived_d3_comparison_recomputes_without_modifying_data():
    done = subprocess.run(
        [sys.executable, str(RUNNER), "--verify"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert "Verified all saved experiment001 rows" in done.stdout
