"""Deterministic verification of GCV smoothing-spline NGSIM benchmarks."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"paper"/"ngsim-jerk-case-study"/"experiments"/"experiment003"/"run.py"
spec=importlib.util.spec_from_file_location("ngsim_exp003_test",SCRIPT)
assert spec is not None and spec.loader is not None
exp=importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp)


def test_training_only_spline_gcv_forecasts_are_finite():
    t=np.arange(80,dtype=float)*0.1
    clean=2.5+0.8*t
    y=clean+0.005*np.sin(t*4.0)
    outputs=exp.forecasts(y,20)
    assert tuple(outputs)==exp.METHODS
    for pred in outputs.values():
        assert pred.shape==(20,)
        assert np.all(np.isfinite(pred))


def test_gcv_spline_linear_reference_signal():
    t=np.arange(80,dtype=float)*0.1
    y=5.0+1.5*t
    forecast=exp.forecasts(y,10)
    target=5.0+1.5*(t[-1]+np.arange(1,11)*0.1)
    for key in ("spline_gcv_taylor2","spline_gcv_taylor3",
                "spline_gcv_native","spline_gcv_local25"):
        np.testing.assert_allclose(forecast[key],target,rtol=0,atol=2e-6)


@pytest.mark.parametrize("y,horizon",[
    ([1.0,2.0,3.0],20),
    (np.ones(80),0),
    (np.full(80,np.nan),5),
])
def test_gcv_spline_rejects_invalid_inputs(y,horizon):
    with pytest.raises(ValueError):
        exp.forecasts(np.asarray(y,dtype=float),horizon)
