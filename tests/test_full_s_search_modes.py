"""One-point vs full-domain grid and native-S/lambda/translated coordinate QA."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from trendestimation import TrendSmoother, score_lambda

BENCH = Path(__file__).resolve().parents[1] / "paper" / "benchmarks"
sys.path.insert(0, str(BENCH))

from full_s_backend_criteria import Backend, complete_s_grid, observation  # noqa: E402
from full_s_search_modes import (  # noqa: E402
    CONTINUOUS_POLICIES, GRID_POLICIES, SINGLE_POLICIES,
    continuous_search, design, evaluate_grid, measure_one, workloads,
)


def test_mode_names_capture_single_grid_and_bounded_optimization():
    assert SINGLE_POLICIES == (
        "single_native_s", "single_lambda", "single_mapped_s_lambda")
    assert GRID_POLICIES == (
        "native_s", "mapped_s_lambda", "native_log_lambda")
    assert CONTINUOUS_POLICIES == ("continuous_s", "continuous_log_lambda")


@pytest.mark.parametrize("d", [0, 1, 2, 5])
def test_all_candidate_mapping_includes_exact_zero_infinity(d):
    sm = TrendSmoother(18, d)
    targets, mapped, log_lambda, elapsed = design(sm)
    np.testing.assert_array_equal(targets, complete_s_grid())
    assert len(targets) == len(mapped) == len(log_lambda) == 17
    assert elapsed >= 0
    assert mapped[0] == log_lambda[0] == 0
    assert np.isposinf(mapped[-1]) and np.isposinf(log_lambda[-1])
    np.testing.assert_allclose(mapped[[1, -2]], log_lambda[[1, -2]])
    np.testing.assert_allclose(
        [sm.smoothness(float(lam)) for lam in mapped], targets, atol=3e-10)


@pytest.mark.parametrize("d,criterion", [(0,"cv"),(1,"gcv"),(2,"aicc"),
                                          (3,"bic"),(5,"mle")])
def test_matched_native_s_and_mapped_lambda_scores_identical(d,criterion):
    sm = TrendSmoother(19, d)
    targets, mapped, independent, _ = design(sm)
    y = observation(19, 123+d)
    method = Backend(19,d,"svd",criterion)
    for mu in (0., .15):
        a = evaluate_grid(method,sm,y,mu,criterion,"native_s",targets)
        b = evaluate_grid(method,sm,y,mu,criterion,"mapped_s_lambda",mapped)
        assert a["valid"] and b["valid"]
        np.testing.assert_allclose(a["scores"], b["scores"],rtol=1e-9,
                                   atol=1e-9)
        assert np.isclose(a["s"],b["s"],atol=1e-12)
        np.testing.assert_allclose(a["score"], b["score"])
        different = evaluate_grid(
            method,sm,y,mu,criterion,"native_log_lambda",independent)
        assert different["valid"]
        assert len(different["scores"]) == 17


def test_single_candidate_and_repeat_cold_warm_are_real_different_workloads():
    n,d=18,1
    sm=TrendSmoother(n,d)
    targets,mapped,independent,map_s=design(sm)
    res=[]
    for reuse in ("cold","shared"):
        for policy in SINGLE_POLICIES+GRID_POLICIES:
            r=measure_one(n,d,0.15,"gcv","svd",2,policy,1927,1,
                          sm,targets,mapped,independent,map_s,reuse)
            assert r["success"],r
            assert r["R"]==2 and r["candidate_evaluations"] in (2,34)
            assert r["total_backend_only_s"]>0
            assert r["total_standalone_s"]>=r["total_backend_only_s"]
            res.append(r)
    selected=[r["selected_s"] for r in res
              if r["policy"] in ("native_s","mapped_s_lambda")]
    assert max(selected)-min(selected) < 1e-9
    one=[r for r in res if r["workload"]=="single"]
    assert all(r["candidate_evaluations"]==2 for r in one)


def test_local_continuous_coordinate_optimizers_return_a_real_score():
    n,d=19,2
    sm=TrendSmoother(n,d)
    targets,mapped,_,_=design(sm)
    y=observation(n,213)
    backend=Backend(n,d,"svd","gcv")
    for policy in CONTINUOUS_POLICIES:
        result=continuous_search(backend,sm,y,.15,"gcv",policy,
                                 mapped,check=True)
        assert result["calls"] > 1
        assert result["local_success"]
        assert result["valid"]
        assert 0 <= result["s"] <= 1
        assert np.isfinite(result["score"])
        # Check only score parity; nonconvex local minima need not match.
        s=result["s"]
        lam=sm.lambda_for_smoothness(s)
        assert np.isclose(result["score"],
                          score_lambda(sm,y,lambda_=lam,
                                       criterion="gcv",mu=.15),
                          rtol=1e-5,atol=1e-5)


def test_mle_d0_is_explicitly_not_applicable_for_every_search():
    sm=TrendSmoother(16,0)
    t,lam,ind,map_s=design(sm)
    for policy in SINGLE_POLICIES+GRID_POLICIES+CONTINUOUS_POLICIES:
        row=measure_one(16,0,0.,"mle","svd",1,policy,123,1,
                        sm,t,lam,ind,map_s,"shared")
        assert row["status"]=="not_applicable_d0_mle"


def test_smoke_preset_and_quick_preset_axes():
    smoke=workloads("smoke")
    quick=workloads("quick")
    assert smoke[3] == (0,2,5)
    assert quick[3] == tuple(range(6))
    assert quick[4] == ("cv","gcv","aicc","bic","mle")
    assert len(quick[5]) == 7
    assert quick[1] == (1,3)
