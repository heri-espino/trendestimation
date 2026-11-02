"""Hard-case numerical guard and 85-digit reference regression checks."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from trendestimation import PreparedPLSSolver, TrendSmoother, score_lambda

HERE=Path(__file__).resolve().parents[1]/"paper"/"benchmarks"/"experiment006"
sys.path.insert(0,str(HERE))
from audit_high_d import high_precision_reference  # noqa: E402
from run import Evaluator, memory_budget_status, sample  # noqa: E402


@pytest.mark.parametrize("d",[1,2,3,4,5,6])
def test_guarded_method_records_actual_backend(d):
    e=Evaluator(32,d,"guarded_svd_cholesky")
    assert e.actual_backend==("spectral_svd" if d>=5 else "banded_cholesky")


@pytest.mark.parametrize("d",[5,6])
@pytest.mark.parametrize("s",[.85,.91,.99,1.])
def test_guarded_high_order_matches_independent_decimal_truth(d,s):
    n=64
    y=sample(n,20261103+29*n+7*d,"high")
    mu=.15
    spectral=TrendSmoother(n,d)
    lam=float("inf") if s==1 else spectral.lambda_for_smoothness(s)
    actual=PreparedPLSSolver(n,d,method="svd").fit(y,lambda_=lam,mu=mu)
    truth,kkt=high_precision_reference(y,d,mu,lam,digits=85)
    error=np.linalg.norm(actual-truth)/max(1.,np.linalg.norm(truth))
    assert error<2e-7, (d,s,error)
    assert np.isfinite(kkt)
    e=Evaluator(n,d,"guarded_svd_cholesky")
    result=e.evaluate(y,mu,lam,"cv",coordinates=e.prepare_series(y,mu))
    expected=score_lambda(spectral,y,lambda_=lam,mu=mu,criterion="cv")
    np.testing.assert_allclose(result,expected,atol=1e-7,rtol=2e-7)


def test_guarded_method_refuses_unaffordable_high_order_dense_setup():
    for d in (5,6):
        assert (memory_budget_status(131072,d,"guarded_svd_cholesky",
               100,2*1024**3,1e9,"one_s_one_series",1,1)
                =="infeasible_dense_memory")


def test_decimal_truth_independent_55_and_85_digit_convergence():
    n,d=48,6
    y=sample(n,41,"high")
    mu=.15
    lam=TrendSmoother(n,d).lambda_for_smoothness(.99)
    a,_=high_precision_reference(y,d,mu,lam,55)
    b,_=high_precision_reference(y,d,mu,lam,85)
    np.testing.assert_allclose(a,b,rtol=1e-11,atol=1e-7)
