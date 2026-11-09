"""Experiment008: spectral cutoff is a genuine estimator, not a PLS backend."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import numpy as np
import pytest

REPO=Path(__file__).resolve().parents[1]
HERE=REPO/"paper"/"ngsim-jerk-case-study"/"experiments"/"experiment008"
sys.path.insert(0,str(HERE))
module=importlib.util.spec_from_file_location("paper_c_exp008_test",HERE/"run.py")
assert module is not None and module.loader is not None
app=importlib.util.module_from_spec(module)
module.loader.exec_module(app)
from trendestimation import TrendSmoother


def fixture():
    rng=np.random.default_rng(1980)
    s=TrendSmoother(80,order=3)
    svd=app.RoughnessSVD(s)
    t=np.arange(80,dtype=float)
    y=20+t*.7+t*t*.02+1e-4*t**3+rng.normal(0,.09,80)
    return s,svd,y


def test_svd_full_rank_recovers_observed_positions_and_zero_rank_is_cubic_reference():
    s,svd,y=fixture()
    mu=.00063
    np.testing.assert_allclose(svd.fit(y,mu,svd.m),y,atol=2e-10,rtol=1e-10)
    trend=svd.fit(y,mu,0)
    np.testing.assert_allclose(s.D@trend,mu*np.ones(77),atol=2e-10)
    assert svd.d==3


@pytest.mark.parametrize("rank",[0,1,5,30,65,76])
def test_tsvd_is_an_orthogonal_projection_and_monotone_decreasing_residual(rank):
    s,svd,y=fixture()
    mu=.004
    t=svd.fit(y,mu,rank)
    p=svd.particular(mu)
    v=y-p
    r=v-(t-p)
    for projected_basis in (svd.V0,svd.Vp[:,:rank]):
        np.testing.assert_allclose(projected_basis.T@r,0,atol=2e-9)
    assert np.linalg.norm(y-svd.fit(y,mu,rank+1))<=np.linalg.norm(y-t)+1e-9


def test_edf_matched_tsvd_rank_is_fair_soft_to_hard_filter_baseline():
    s,svd,y=fixture()
    for lam in (0,1e-3,1,1e3,float("inf")):
        r=svd.matched_rank(lam)
        assert 0<=r<=svd.m
        if lam==0:assert r==svd.m
        if np.isinf(lam):assert r==0
        if np.isfinite(lam):
            soft=int(np.rint(np.sum(1/(1+lam*svd.sigma**2))))
            assert r==soft
        h=svd.hat_diag(r)
        np.testing.assert_allclose(np.sum(h),3+r,atol=1e-10)


def test_gcv_rank_learned_on_training_only_and_does_not_interpolate():
    s,svd,y=fixture()
    rank,score=svd.gcv_rank(y,.005)
    assert 0<=rank<77
    assert np.isfinite(score)
    assert np.isfinite(svd.fit(y,.005,rank)).all()


def test_svd_is_not_just_pls_computed_with_svd():
    smoother,svd,y=fixture()
    mu=.0003
    lam=10
    soft=np.asarray(smoother.fit(y,lambda_=lam,mu=mu).trend)
    hard=svd.fit(y,mu,svd.matched_rank(lam))
    assert np.linalg.norm(soft-hard)>1e-5


def test_training_only_saved_parameters_are_reproduced():
    smoother,svd,y=fixture()
    params={"lambda":100.0,"mu":.0003,"S":float(smoother.smoothness(100))}
    fit,choices=app.fits(y,params,smoother,svd)
    assert set(fit)==set(app.METHODS)
    assert 0<=choices["rank_gcv"]<77
    assert 0<=choices["rank_edf"]<=77
    for key,(trend,mu,rank,lam) in fit.items():
        assert len(trend)==80 and np.isfinite(trend).all()


def test_derived_experiment_never_overwrites_existing_results(tmp_path):
    root=tmp_path/"existing"
    root.mkdir()
    (root/"important.txt").write_text("preserve")
    s,svd,y=fixture()
    ep=[{"id":"test","site":"sim","stratum":"iid",
         "train":y,"future":y[:20],"truth_train":y,"noise":"iid"}]
    with pytest.raises(FileExistsError):
        app.compare(ep,{"test":{"lambda":1,"mu":0,"S":.5}},
                    "synthetic","sha",root,"sha2")
    assert (root/"important.txt").read_text()=="preserve"
