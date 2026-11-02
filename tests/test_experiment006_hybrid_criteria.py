"""Explicit hybrid full-criterion parity for external fit backends."""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pytest

from trendestimation import PreparedPLSSolver, TrendSmoother, score_lambda, difference_matrix

DIR=Path(__file__).resolve().parents[1]/"paper"/"benchmarks"/"experiment006"
sys.path.insert(0,str(DIR))
from run import Evaluator, HYBRID_METHODS, sample  # noqa: E402


@pytest.mark.parametrize("method",[
    "banded_lu_banded_trace","sparse_lu_banded_trace",
    "pcg_fft_banded_trace","pcg_dst_banded_trace",
    "pcg_jacobi_banded_trace"])
@pytest.mark.parametrize("d",[1,2,3,6])
@pytest.mark.parametrize("criterion",["cv","gcv","aicc","bic","mle"])
def test_external_fit_plus_exact_banded_diagnostics(method,d,criterion):
    n=35
    y=sample(n,123+d,"high") / 1e6
    mu=.15
    lam=.1
    backend=Evaluator(n,d,method)
    actual=backend.evaluate(y,mu,lam,criterion,reuse_factor=False)
    expected=score_lambda(TrendSmoother(n,d),y,lambda_=lam,
                          criterion=criterion,mu=mu)
    if criterion=="mle":
        D=difference_matrix(n,d)
        sign,logdet=np.linalg.slogdet(D@D.T)
        assert sign>0
        expected+=logdet
    np.testing.assert_allclose(actual,expected,rtol=1e-5,atol=1e-5)


def test_reused_hybrid_factor_and_trace_match_uncached():
    n,d=38,2
    y=sample(n,77,"low")
    backend=Evaluator(n,d,"sparse_lu_banded_trace")
    for criterion in ("cv","gcv","mle"):
        a=backend.evaluate(y,0.15,1.1,criterion,reuse_factor=True)
        b=backend.evaluate(y,0.15,1.1,criterion,reuse_factor=False)
        np.testing.assert_allclose(a,b,rtol=1e-9,atol=1e-9)
    assert backend.banded.trace_calls>0


def test_complete_hybrid_names_explicitly_pair_a_fit_with_diagnostics():
    assert len(HYBRID_METHODS)==6
    assert all(name.endswith("_banded_trace") for name in HYBRID_METHODS)
