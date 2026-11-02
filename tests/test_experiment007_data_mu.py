"""Experiment007 correctness and provenance contracts."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]/"paper"/"benchmarks"/"experiment007"
sys.path.insert(0,str(ROOT))
from run import (N_LEVELS,D_LEVELS,S_LEVELS,WORKLOADS,make_series,  # noqa: E402
                 fitted_mu,run)
from summarize import analyze  # noqa: E402


def test_default_is_observed_difference_mean_not_manually_assigned():
    n=64
    for d in D_LEVELS:
        observed,latent=make_series(n,d,"high",seed=2)
        assert fitted_mu(observed,d,"data")==pytest.approx(
            float(np.mean(np.diff(observed,n=d))),rel=1e-14)
        assert fitted_mu(observed,d,"zero")==0.0
        # The latent difference mean is a diagnostic and is usually
        # NOT equal to the estimated observed-difference mean.
        oracle=float(np.mean(np.diff(latent,n=d)))
        assert np.isfinite(oracle)


def test_four_requested_fit_workloads_are_distinct():
    assert len(WORKLOADS)==4
    assert {(len(s),r) for _,s,r in WORKLOADS}=={(1,1),(7,1),(1,3),(7,3)}
    assert 1. in S_LEVELS
    assert N_LEVELS==(64,128,256)


def test_observed_mu_and_solvers_measured_without_oracle_leakage(tmp_path):
    output=tmp_path/"run001"
    raw,qc,meta=run(output,n_levels=(64,),d_levels=(2,),
        seeds=(0,),s_levels=(.5,.9),scales=("low",),
        policies=("data","zero"),methods=("svd","cholesky"),
        high_precision=False)
    assert len(raw)==16
    assert len(qc)==2*3*2*2
    assert {x["mu_policy"] for x in raw}=={"data","zero"}
    assert {x["workload"] for x in raw}=={name for name,_,_ in WORKLOADS}
    assert all(x["status"]=="ok" for x in raw), raw
    assert {x["reference"] for x in qc}=={"svd_proxy"}
    assert all(x["status"]=="agreement" for x in qc), qc
    assert (output/"raw_times.csv").is_file()
    assert (output/"forward_accuracy.csv").is_file()
    assert (output/"metadata.json").is_file()
    status,timing,winners=analyze(output)
    assert len(status)>0 and len(timing)>0 and len(winners)>0
    assert (output/"accuracy_by_nd.csv").is_file()
    assert (output/"provisional_winners.csv").is_file()
    assert (output/"RESULTS.md").is_file()
    with pytest.raises(FileExistsError):
        run(output,n_levels=(64,),d_levels=(2,),high_precision=False)


def test_decimal_high_order_audit_with_actual_mu_data(tmp_path):
    output=tmp_path/"highd"
    raw,qc,meta=run(output,n_levels=(64,),d_levels=(6,),
        seeds=(0,),s_levels=(.9,1.),scales=("low",),
        policies=("data",),methods=("svd","cholesky"),
        high_precision=True)
    refs=[x for x in qc if x["reference"]=="decimal85"]
    assert refs
    assert all(x["mu_estimated"]!=0 for x in refs)
    assert all(x["status"]=="agreement" for x in refs if x["method"]=="svd")
    assert meta["total_rows_accuracy"]==len(qc)
