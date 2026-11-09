"""Experiment005 scientific and reproducibility checks.

These unit tests use analytically known synthetic signals solely to verify
simulation mechanics, not as substitute evidence for the full run.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "paper" / "ngsim-jerk-case-study" / "experiments" / "experiment005" / "run.py"
spec = importlib.util.spec_from_file_location("paper_c_exp005_simulation", SCRIPT)
assert spec is not None and spec.loader is not None
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)
CONFIG = json.loads(sim.CONFIG_FILE.read_text(encoding="utf-8"))


def test_pilot_and_confirm_scenarios_and_seed_disjointness():
    pilot = sim.rows_for_stage(CONFIG, "pilot")
    confirm = sim.rows_for_stage(CONFIG, "confirm")
    assert len(pilot) == 96
    assert len(confirm) == 1296
    assert {row["seed"] for row in pilot}.isdisjoint(
        {row["seed"] for row in confirm}
    )
    assert {row["regime"] for row in pilot} == set(
        CONFIG["true_movement"]["regimes"]
    )
    assert len({row["seed"] for row in confirm}) == len(confirm)


@pytest.mark.parametrize("regime", CONFIG["true_movement"]["regimes"])
def test_known_motion_derivative_consistency(regime):
    t = np.arange(100, dtype=float) * 0.1
    x, v, a, j = sim.truth(regime, t, CONFIG)
    assert all(np.all(np.isfinite(arr)) for arr in (x,v,a,j))
    assert np.all(v >= 0)
    assert np.max(np.abs(a)) < 6.0
    assert np.max(np.abs(j)) <= 1.0
    assert np.allclose(np.diff(x), 0.5 * (v[1:] + v[:-1]) * 0.1, atol=1e-3)
    if regime.startswith("constant"):
        d3 = np.diff(x, n=3) / 0.1**3
        np.testing.assert_allclose(
            d3, np.full(len(d3), j[0]), rtol=0, atol=3e-8
        )


def test_oracle_mu_is_unavailable_without_clean_truth():
    t=np.arange(80,dtype=float)*0.1
    x=18*t+0.25*t**3/6
    rng=np.random.default_rng(7)
    y=x+rng.normal(0,0.1,size=len(x))
    mu=sim.mu_policies(y,x,0.1)
    assert set(mu) == {"zero","sample","ols_global","ols_tail25","oracle"}
    assert mu["zero"] == 0
    assert abs(mu["oracle"]/0.1**3-0.25) < 1e-8
    assert abs(mu["ols_global"]-mu["oracle"]) > 1e-9


def test_recurrence_and_local_continuation_exact_for_clean_cubic():
    from trendestimation import TrendSmoother
    t=np.arange(100)*0.1
    clean=15*t+0.25*t**3/6
    historical=clean[:80]
    mu=float(np.diff(historical,n=3).mean())
    smoother=TrendSmoother(80,order=3)
    trend=smoother.fit(historical,lambda_=0.3,mu=mu).trend
    for method, predictions in sim.forecasts_of_trend(trend,mu,20).items():
        np.testing.assert_allclose(predictions,clean[80:100],
                                   atol=5e-7,rtol=0,err_msg=method)


def test_fixed_s_crossing_is_additive_for_same_lambda():
    from trendestimation import TrendSmoother
    dt=0.1
    t=np.arange(80)*dt
    y=17*t+0.3*t**3/6+0.1*np.sin(4*t)
    mu=float(np.mean(np.diff(y,n=3)))
    smoother=TrendSmoother(80,order=3)
    lam=smoother.lambda_for_smoothness(0.6)
    zero=smoother.fit(y,lambda_=lam,mu=0).trend
    ref=smoother.fit(y,lambda_=lam,mu=mu).trend
    for rule in ("guerrero_last3","local25"):
        def f(trend, continuation_mu):
            return sim.forecasts_of_trend(trend,continuation_mu,20)[rule]
        interaction=f(ref,mu)-f(ref,0)-f(zero,mu)+f(zero,0)
        np.testing.assert_allclose(interaction,0,atol=1e-8,rtol=0)


def test_stable_noise_seed_and_endpoint_contamination_only_at_training_endpoint():
    t=np.arange(100)*0.1
    x=20*t
    kwargs={
        "sigma":0.3, "noise_type":"last_train_outlier",
        "train_n":80,"config":CONFIG,"trial_index":0
    }
    y1=sim.observations(x,rng=np.random.default_rng(42),**kwargs)
    y2=sim.observations(x,rng=np.random.default_rng(42),**kwargs)
    assert np.array_equal(y1,y2)
    baseline=sim.observations(
        x,rng=np.random.default_rng(42),
        sigma=0.3,noise_type="iid_gaussian",
        train_n=80,config=CONFIG,trial_index=0,
    )
    diff=y1-baseline
    assert abs(diff[79]-1.2) < 1e-12
    np.testing.assert_allclose(np.delete(diff,79),0,atol=1e-12)


def test_reject_overwriting_existing_result_directory(tmp_path):
    destination=tmp_path/"already-there"
    destination.mkdir()
    with pytest.raises(FileExistsError):
        sim.simulate(CONFIG,"pilot",destination)


def test_fit_and_continuation_interfaces_return_finite():
    from trendestimation import TrendSmoother
    t=np.arange(80)*0.1
    y=18*t+0.1*np.sin(2*t)
    smoother=TrendSmoother(80,order=3)
    penalties=tuple(smoother.lambda_for_smoothness(s)
                    for s in CONFIG["policies"]["smoothness_grid"])
    for criterion in ("gcv","mle"):
        choice=sim.select_lambda(smoother,y,criterion=criterion,mu=0.0,
                                 grid=penalties,method="grid")
        assert np.isfinite(choice.score)
        fitted=smoother.fit(y,lambda_=choice.lambda_,mu=0.0).trend
        assert np.isfinite(fitted).all()
        preds=sim.forecasts_of_trend(fitted,0,20)
        assert set(preds)=={"guerrero_last3","local25"}
        assert all(p.shape==(20,) and np.all(np.isfinite(p))
                   for p in preds.values())
    others=sim.other_methods(y,0.1,20)
    assert set(others)=={
        "spline_gcv_taylor2","savgol21_taylor2","raw_local_quad25"
    }
