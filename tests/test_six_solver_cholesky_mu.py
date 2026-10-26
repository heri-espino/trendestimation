"""Correctness checks for the extended paper benchmark's six solver routes."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PAPER_BENCH = Path(__file__).resolve().parents[1] / "paper" / "benchmarks"
sys.path.insert(0, str(PAPER_BENCH))

from cholesky_comparison import (  # noqa: E402
    METHODS, TRACE_METHODS, fit_workloads, make_six_fitter,
    make_six_trace, measure_fits, measure_traces,
)
from run_benchmarks import make_fitter  # noqa: E402


def test_correct_six_distinct_methods_and_paired_mu_cases():
    assert METHODS == ("dense_fresh", "dense_cached", "spectral", "banded",
                       "dense_cholesky", "banded_cholesky")
    assert len(TRACE_METHODS) == len(METHODS)
    cases = fit_workloads("quick")
    assert len(cases) == 16
    assert {(n,d,M) for n,d,M,mu in cases if mu == 0.0} == {
        (n,d,M) for n,d,M,mu in cases if mu == .15
    }


def test_all_six_trends_agree_at_nonzero_mu_and_change_with_mu():
    for d in (1,2,3):
        n=26
        rng=np.random.default_rng(891+d)
        y=rng.normal(size=n)
        for mu in (0.0,0.15,-0.2):
            ref=make_fitter("banded",y,d,mu)
            for lam in (1e-3, 0.1, 10, 1000):
                expected=ref(lam)
                for method in METHODS:
                    computed=make_six_fitter(method,y,d,mu)(lam)
                    np.testing.assert_allclose(
                        computed,expected,atol=3e-7,rtol=3e-7,
                        err_msg=f"{method} d={d} mu={mu} lambda={lam}"
                    )
        positive=make_six_fitter("banded_cholesky",y,d,0.15)(10)
        zero=make_six_fitter("banded_cholesky",y,d,0.0)(10)
        assert np.max(abs(positive-zero)) > 1e-6


def test_six_trace_implementations_and_mu_invariance():
    for n,d in ((18,1),(22,2),(26,3)):
        spectral=make_six_trace("spectral_trace",n,d)
        for lam in (1e-3,0.1,10,1000):
            true=spectral(lam)
            for method in TRACE_METHODS:
                assert np.isclose(make_six_trace(method,n,d)(lam),true,
                                  rtol=1e-8,atol=1e-8),method
    # By construction trace evaluators have no mu argument:
    # H(lambda)=(I+lambda*D.T@D)^-1 does not depend on mu.


def test_smoke_measures_six_methods_without_timing_speed_assumptions():
    fits=measure_fits(18,2,3,.15,1234,1)
    trace=measure_traces(18,2,3,1)
    assert {r["method"] for r in fits}==set(METHODS)
    assert {r["method"] for r in trace}==set(TRACE_METHODS)
    assert max(r["max_error_banded"] for r in fits)<3e-6
    assert max(r["max_abs_trace_error"] for r in trace)<1e-6
    assert all(r["total_median_s"]>0 for r in fits+trace)
