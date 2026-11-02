"""Experiment006 end-to-end smoke tests: axes, actual timings, preservation."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

HERE=Path(__file__).resolve().parents[1]/"paper"/"benchmarks"/"experiment006"
sys.path.insert(0,str(HERE))
from run import grid_of_s, run_slice, memory_budget_status, SCENARIOS  # noqa: E402
from plan import manifest  # noqa: E402


def test_exact_requested_grids_include_analytic_S_one():
    for m in (100,1000,10000,100000):
        grid=grid_of_s(m)
        assert grid.shape==(m,)
        assert grid[-1]==1.
        assert grid[0]==1/m
        assert np.all(np.diff(grid)>0)


def test_full_factorial_plan_explicitly_contains_requested_extremes():
    rows=manifest(repeats=1,R=2)
    found_small=found_large=found_unavailable=False
    statuses=set()
    for row in rows:
        statuses.add(row["status"])
        if (row["n"]==64 and row["d"]==1
                and row["mu"]=="0.15" and row["amplitude"]=="low"
                and row["method"]=="naive_inverse"
                and row["criterion"]=="cv"):
            found_small=True
        if (row["n"]==131072 and row["d"]==6
                and row["grid_denominator"]==100000 and
                row["scenario"]=="grid_multiple_series"):
            found_large=True
            assert row["status"]!="eligible"
        if row["method"]=="pcg_fft":
            found_unavailable=True
            if row["mu"]=="data" and row["criterion"]!="mle":
                assert row["status"]=="statistical_not_applicable"
            else:
                assert row["status"]=="fit_only_not_complete_criterion"
        if row["mu"]=="data" and row["criterion"]=="cv":
            assert row["status"]=="statistical_not_applicable"
    assert found_small and found_large and found_unavailable
    assert "eligible" in statuses


def test_huge_dense_workload_is_not_allocated():
    assert (memory_budget_status(
        131072,6,"naive_inverse",100,2*1024**3,
        1e9,"one_s_one_series",1,1)=="infeasible_dense_memory")


def test_four_workloads_are_truly_timed_with_matched_s_grid(tmp_path):
    path=tmp_path/"experiment006"
    rows,summary=run_slice(
        n=64,d=2,mu=.15,amplitude="low",criterion="gcv",
        denominator=100,methods=("banded_cholesky","spectral_svd"),
        repeats=1,R=2,output=path,max_work=5e7,
    )
    assert (path/"raw_times.csv").is_file()
    assert (path/"summary.csv").is_file()
    assert (path/"environment.json").is_file()
    assert {x["workload"] for x in rows}==set(SCENARIOS)
    assert {x["coordinate"] for x in rows}=={"direct_s","mapped_lambda"}
    assert all(x["status"]=="ok" for x in rows), rows
    for method in ("banded_cholesky","spectral_svd"):
        for scenario in SCENARIOS:
            pair={x["coordinate"]:x for x in rows
                  if x["method"]==method and x["workload"]==scenario}
            assert abs(pair["direct_s"]["selected_s"]-
                       pair["mapped_lambda"]["selected_s"])<=1e-12
            expected=100 if scenario.startswith("grid") else 1
            assert pair["direct_s"]["M"]==expected
            assert pair["mapped_lambda"]["M"]==expected
            assert pair["direct_s"]["s_to_lambda_s"]>=0
            assert pair["mapped_lambda"]["total_cold_s"]>0
    with pytest.raises(FileExistsError):
        run_slice(n=64,d=2,mu=.15,denominator=100,
                  methods=("banded_cholesky",),repeats=1,R=2,
                  output=path)
    assert len(summary)==2*len(SCENARIOS)*2


def test_mle_plug_in_only_and_invalid_metadata(tmp_path):
    with pytest.raises(ValueError):
        run_slice(n=64,d=2,mu="data",criterion="cv",
                  output=tmp_path/"bad")
