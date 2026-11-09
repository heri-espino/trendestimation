"""Independent Experiment006 pipeline tests: leakage, pairing and outputs."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "paper" / "ngsim-jerk-case-study" / "experiments" / "experiment006"
sys.path.insert(0,str(SCRIPTS))
spec=importlib.util.spec_from_file_location("paper_c_exp006_runner", SCRIPTS/"run.py")
assert spec is not None and spec.loader is not None
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def make_sample():
    t=np.arange(100,dtype=float)*0.1
    truth=18*t+0.2*t**3/6
    rng=np.random.default_rng(20261109)
    observed=truth+rng.normal(0,.15,len(truth))
    return {
        "id":"test_trial_001","stratum":"constant_positive|0.15|iid",
        "site":"simulation","session":"constant_positive|0.15|iid",
        "train":observed[:80],"future":truth[80:100],
        "truth_train":truth[:80],"noise":"iid_gaussian",
    }


def test_all_continuous_and_grid_policies_are_finite():
    sample=make_sample()
    models=runner.CachedModels()
    choices,trends=runner.estimate_methods(sample["train"],models)
    assert set(choices)==set(runner.METHODS)
    for name,choice in choices.items():
        assert np.isfinite(choice.mu)
        assert np.isfinite(choice.score)
        assert 0 <= choice.smoothness <= 1
        assert trends[name].shape==(80,)
        assert np.isfinite(trends[name]).all()
    assert choices["fixed_zero_continuous"].mu==0.0
    assert abs(choices["plugin_sample_continuous"].mu-runner.raw_mu(sample["train"]))<1e-12


def test_nested_selection_is_training_only():
    sample=make_sample()
    cache=runner.CachedModels()
    a=runner.evaluate_one(sample,cache)
    changed={**sample,"future":sample["future"]+200}
    b=runner.evaluate_one(changed,cache)
    assert a["selections"]==b["selections"]
    assert a["cv"]==b["cv"]
    assert len(a["cv"])==6
    assert len(a["selections"])==5
    assert len(a["forecasts"])==(5*2+2)*3
    assert len(a["jerk"])==5+6
    assert all(r["status"]=="ok" for rows in a.values() for r in rows)
    for r in a["cv"]:
        assert r["selected_alpha"] in (0,.5,1)
        assert max(json.loads(r["fold_origins"])) + r["horizon_frames"] <= 80


def test_shrinkage_predictor_is_affine_in_reference_mean():
    sample=make_sample()
    y=sample["train"]
    cache=runner.CachedModels()
    s,reml=cache.get(len(y))
    selected=reml.optimize(y)
    zero=s.fit(y,lambda_=selected.lambda_,mu=0).trend
    nonzero=s.fit(y,lambda_=selected.lambda_,mu=selected.mu).trend
    for alpha in (.0,.5,1.):
        direct=s.fit(y,lambda_=selected.lambda_,mu=alpha*selected.mu).trend
        np.testing.assert_allclose(
            direct,(1-alpha)*zero+alpha*nonzero,atol=1e-8,rtol=1e-9
        )
        for rule in runner.RULES:
            expected=runner.continuation(direct,alpha*selected.mu,rule)
            interpolated=(
                (1-alpha)*runner.continuation(zero,0,rule)
                +alpha*runner.continuation(nonzero,selected.mu,rule)
            )
            np.testing.assert_allclose(expected,interpolated,atol=1e-7,rtol=1e-8)


def test_output_refuses_overwriting_old_runs(tmp_path):
    dest=tmp_path/"existing"
    dest.mkdir()
    with pytest.raises(FileExistsError):
        runner.run("synthetic",tmp_path/"missing.gz",dest,"pilot")


def test_pipeline_has_no_external_source_or_oracle_reference():
    assert "oracle" not in "|".join(runner.METHODS)
    assert set(runner.HORIZONS)=={5,10,20}
    assert runner.CONFIG["continuous_search"]["log_lambda_nodes"]==61
    assert runner.CONFIG["source_reuse"].startswith("Read archived")


def test_real_data_has_no_direct_jerk_labels():
    sample=make_sample()
    sample.update({"site":"us-101","session":"us-101_1000",
                   "stratum":"us-101_1000","truth_train":None,
                   "noise":"recorded"})
    r=runner.evaluate_one(sample,runner.CachedModels())
    assert all(row["jerk_mse_m2_s6"]=="" for row in r["jerk"])
    assert len(r["forecasts"])==36
