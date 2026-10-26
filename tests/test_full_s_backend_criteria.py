"""Full-S backend factorial: support vs numerical stability, not speed assertions."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

BENCH=Path(__file__).resolve().parents[1]/"paper"/"benchmarks"
sys.path.insert(0,str(BENCH))

from full_s_backend_criteria import (  # noqa: E402
    BACKENDS, CRITERIA, Backend, complete_s_grid, observation, run,
)
from trendestimation import TrendSmoother, score_lambda


def test_entire_s_grid_both_exact_limits_and_extreme_tail():
    s=complete_s_grid()
    assert len(s)==17
    assert s[0]==0. and s[-1]==1.
    assert np.all(np.diff(s)>0)
    for item in (0.,.1,.9,.95,.99,.999,.9999,.999999,.999999999999,1.):
        assert np.any(np.isclose(s,item,rtol=0,atol=1e-15))


def test_all_seven_method_names_and_five_selection_criteria():
    assert BACKENDS==("dense_fresh","dense_cached","general_banded",
                      "dense_cholesky","banded_cholesky","eigh","svd")
    assert CRITERIA==("cv","gcv","aicc","bic","mle")


def test_near_zero_and_infinity_are_not_false_finite_fits():
    for d in range(6):
        sm=TrendSmoother(19,d)
        assert sm.lambda_for_smoothness(0)==0
        assert np.isinf(sm.lambda_for_smoothness(1))
        assert np.isclose(sm.smoothness(float("inf")),1,atol=0)
        for mu in (0,.15):
            y=observation(19,129)
            z=sm.fit(y,lambda_=float("inf"),mu=mu).trend
            if d==0:
                np.testing.assert_allclose(z,mu,atol=1e-9)
            else:
                np.testing.assert_allclose(sm.D@z,mu,atol=2e-5)
            assert np.isinf(score_lambda(sm,y,lambda_=0,criterion="cv",mu=mu))
            assert np.isinf(score_lambda(sm,y,lambda_=0,criterion="gcv",mu=mu))


def test_one_representative_finite_penalty_scores_agree_across_backends():
    for d in range(6):
        sm=TrendSmoother(19,d)
        y=observation(19,2026+d)
        lam=sm.lambda_for_smoothness(.5)
        for mu in (0.,.15):
            for criterion in CRITERIA:
                if criterion=="mle" and d==0:
                    continue
                expected=score_lambda(sm,y,lambda_=lam,
                                      criterion=criterion,mu=mu)
                if not np.isfinite(expected):
                    continue
                for method in BACKENDS:
                    value,edf,rnorm=Backend(19,d,method).calculate(
                        y,lam,mu,criterion)
                    np.testing.assert_allclose(
                        value,expected,rtol=1e-5,atol=1e-5,
                        err_msg=f"{d=} {mu=} {criterion=} {method=}")


def test_smoke_reports_every_cell_and_analytic_limit_without_fake_time(tmp_path):
    rows,summaries=run("smoke",1,20261026,1,tmp_path)
    assert {int(r["d"]) for r in rows}==set(range(6))
    assert {r["method"] for r in rows}==set(BACKENDS)
    assert {r["criterion"] for r in rows}==set(CRITERIA)
    assert {float(r["mu"]) for r in rows}=={0.,.15}
    assert any(r["status"]=="not_applicable_d0_mle" for r in rows)
    assert any(r["status"]=="analytic_limit" and r["S"]==1. for r in rows)
    assert all(r["elapsed_s"]==0 for r in rows if r["status"]=="analytic_limit")
    assert any(r["S"]==.999999999999 for r in rows)
    assert len(summaries)==6*2*4*7 + 5*2*1*7
    assert (tmp_path/"s_lambda_grid.csv").exists()
    assert (tmp_path/"candidate_scores_and_times.csv").exists()
    assert (tmp_path/"environment.json").exists()
