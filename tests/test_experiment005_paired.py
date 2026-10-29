"""Regression and pipeline smoke tests for Experiment005.

Tests never assert a method's wall-clock rank.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pytest

HERE=Path(__file__).resolve().parents[1]/"paper"/"benchmarks"/"experiment005"
sys.path.insert(0,str(HERE))
# mpmath is a paper-only dependency; core CI may omit it.
pytest.importorskip("mpmath")
from run import METHODS, fit_once, prepare_method, stable_reference, run  # noqa: E402
from run_pilot import difference_matrix  # noqa: E402


def test_all_nine_fitters_match_independent_reference_at_moderate_s():
    n,d=18,3
    D=difference_matrix(n,d)
    rng=np.random.default_rng(11234)
    y=rng.standard_normal(n)
    mu=.015
    lam=2.5
    high,kkt,status=stable_reference(n,d,y,mu,lam,75,{})
    assert status=="ok" and kkt<1e-18
    assert len(METHODS)==9
    for method in METHODS:
        prepared=prepare_method(method,n,d,D)
        computed=fit_once(method,prepared,D,y,mu,lam)
        np.testing.assert_allclose(computed,high,rtol=2e-7,atol=2e-7,
                                  err_msg=f"{method} reference mismatch")


def test_exact_smoothness_endpoints_have_independent_references():
    from run import precise_endpoint
    n,d=18,3
    D=difference_matrix(n,d)
    y=np.random.default_rng(19).normal(size=n)
    for mu in (0.,.08):
        zero,k0,status0=precise_endpoint(n,d,y,mu,0.,75)
        np.testing.assert_array_equal(zero,y)
        assert status0=="ok" and k0==0.
        limit,k1,status1=precise_endpoint(n,d,y,mu,float("inf"),75)
        assert status1=="ok" and k1<1e-18
        np.testing.assert_allclose(D@limit,mu,atol=1e-10)
        # The limiting PLS trend is the orthogonal projection of y
        # onto the affine polynomial-constraint subspace.
        t=np.arange(n,dtype=float)
        basis=np.column_stack([t**i for i in range(d)])
        assert np.max(abs(basis.T@(y-limit)))<1e-8


def test_reference_cache_is_independent_and_reused():
    n,d=14,3
    y=np.random.default_rng(87).normal(size=n)
    cache={}
    first=stable_reference(n,d,y,0.,5.,75,cache)
    second=stable_reference(n,d,y,0.,5.,75,cache)
    assert first[2]=="ok" and second[2]=="ok"
    assert len(cache)==1
    np.testing.assert_array_equal(first[0],second[0])


def test_smoke_pair_measures_errors_and_runtime_without_overwrite(tmp_path):
    out=tmp_path/"pilot"
    report=run(out,"smoke",repeats=1,digits=65)
    assert report["fit_rows"]==2*2*3*len(METHODS)
    assert report["selection_rows"]==2*2*5*3*2
    assert report["grid_size"]==17
    assert report["selection_valid"]<=report["selection_rows"]
    assert (out/"grid_mapping_times.csv").is_file()
    assert report["fit_valid"]>0
    import csv
    with (out/"selection_accuracy_timing.csv").open(newline="") as f:
        rows=list(csv.DictReader(f))
    assert {"native_s","cached_s"}=={r["policy"] for r in rows}
    assert all(r["grid_count"]=="17" for r in rows)
    assert all(r["d"] in ("3","6") for r in rows)
    try:
        run(out,"smoke",repeats=1,digits=65)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Experiment output was overwritten")
