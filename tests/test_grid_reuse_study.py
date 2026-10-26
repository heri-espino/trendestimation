"""Mathematical parity, candidate coverage and factor reuse for actual GCV."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

BENCH = Path(__file__).resolve().parents[1]/"paper"/"benchmarks"
sys.path.insert(0,str(BENCH))

from grid_reuse_study import (  # noqa: E402
    CandidateSearch, METHODS, data_vectors, grids, measure_cell, workload,
)


@pytest.mark.parametrize("d",[1,2,3,4])
@pytest.mark.parametrize("mu",[0.0,0.15])
def test_gcv_scores_match_for_all_backends_across_orders_and_mu(d,mu):
    n,M,R=28,5,2
    candidates,bounds,_=grids(n,d,M)
    assert 0 < bounds[0] < bounds[1] < 1
    yy=data_vectors(n,d,20261026,R)
    for policy,grid in candidates.items():
        assert len(grid)==M
        assert np.all(np.isfinite(grid))
        assert np.all(np.diff(grid)>0)
        ref=CandidateSearch(n,d,mu,"spectral",grid,reuse=True)
        expected=np.array([ref.scores(y) for y in yy])
        assert np.all(np.isfinite(expected)),policy
        for method in METHODS:
            cold=np.array([
                CandidateSearch(n,d,mu,method,grid,reuse=False).scores(y)
                for y in yy])
            warm=CandidateSearch(n,d,mu,method,grid,reuse=True)
            cached=np.array([warm.scores(y) for y in yy])
            np.testing.assert_allclose(cold,expected,atol=2e-5,rtol=2e-5,
                                       err_msg=f"{d} {mu} {policy} {method} cold")
            np.testing.assert_allclose(cached,expected,atol=2e-5,rtol=2e-5,
                                       err_msg=f"{d} {mu} {policy} {method} warm")
            np.testing.assert_allclose(cached,cold,atol=2e-5,rtol=2e-5)


def test_identical_grid_bounds_but_interior_candidate_positions_differ():
    grids_by_policy,_,_=grids(48,2,11)
    a,b=grids_by_policy["log_lambda"],grids_by_policy["uniform_s"]
    np.testing.assert_allclose(a[[0,-1]],b[[0,-1]],rtol=1e-12)
    assert np.max(np.abs(np.log(a[1:-1]/b[1:-1])))>0.1


def test_repeated_data_uses_seeded_prefix_and_both_means_see_same_series():
    first=data_vectors(48,2,45,1)
    many=data_vectors(48,2,45,4)
    np.testing.assert_array_equal(first[0],many[0])
    assert not np.array_equal(many[0],many[1])


def test_cold_vs_warm_timing_records_have_matched_optimizers():
    g,_,_=grids(24,2,4)
    rows=measure_cell(24,2,4,2,0.15,20261026,
                      "log_lambda",g["log_lambda"],1)
    assert len(rows)==12
    for method in METHODS:
        both={r["reuse"]:r for r in rows if r["method"]==method}
        np.testing.assert_allclose(
            both["warm"]["selected_score_mean"],
            both["cold"]["selected_score_mean"],rtol=2e-6,atol=2e-7)
        assert both["warm"]["total_median_s"]>0
        assert both["cold"]["total_median_s"]>0


def test_presets_include_multiple_d_grid_budgets_and_repeated_runs():
    n,d,M,R=workload("quick")
    assert d==(1,2,3,4)
    assert len(M)>1 and len(R)>1
    assert R[0]==1 and R[-1]>1
    assert 5 in workload("full")[1]
