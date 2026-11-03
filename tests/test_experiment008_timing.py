"""Experiment008 four-workload timing orchestration and observed-mu semantics."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]/"paper"/"benchmarks"
sys.path.insert(0,str(ROOT/"experiment006"))
sys.path.insert(0,str(ROOT/"experiment008"))
spec=importlib.util.spec_from_file_location("experiment008_batch_runner",
                                           ROOT/"experiment008"/"run_batches.py")
assert spec and spec.loader
batch=importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
from run import run_slice  # noqa: E402


def test_pilot_crosses_every_difference_order_and_selection_criterion():
    plans=batch.configurations("pilot")
    assert {x["d"] for x in plans}==set(range(1,7))
    assert {x["criterion"] for x in plans}=={"cv","gcv","bic","aicc","mle"}
    assert {x["denominator"] for x in plans}=={100,1000,10000,100000}
    assert {x["mu"] for x in plans}=={"0","data"}
    assert {x["n"] for x in plans}=={64,128,256,512,1024}


def test_opt_in_conditional_observed_mu_runs_and_labels_correctly(tmp_path):
    with pytest.raises(ValueError):
        run_slice(n=64,d=2,mu="data",criterion="cv",
                  output=tmp_path/"refused")
    rows,_=run_slice(n=64,d=2,mu="data",criterion="cv",
        denominator=100,methods=("spectral_svd","banded_cholesky"),
        repeats=1,R=2,output=tmp_path/"conditional",
        max_work=5e7,conditional_data_mu=True)
    assert len(rows)==16
    assert {r["workload"] for r in rows}==set(batch.SCENARIOS)
    assert {r["coordinate"] for r in rows}==set(batch.POLICIES)
    assert (tmp_path/"conditional"/"raw_times.csv").is_file()
    meta=json.loads((tmp_path/"conditional"/"environment.json").read_text())
    assert meta["mean_policy_note"]=="conditional_plugin_not_refitted"
    assert all(r["status"]=="ok" for r in rows), rows


def test_large_dense_ineligible_and_four_grid_sizes_explicit():
    assert (batch.memory_budget_status(
        131072,6,"naive_inverse",100,2*1024**3,
        1e12,"one_s_one_series",1,1)=="infeasible_dense_memory")
    assert batch.GRID_DENOMINATORS==(100,1000,10000,100000)
