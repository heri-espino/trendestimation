"""Experiment007 paired smoothness/precision calibration science guards.

Only small algebraic fixtures; the actual pilot and confirmation runs are
kept separately and archive all generated clean and noisy positions.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/"paper"/"ngsim-jerk-case-study"/"experiments"/"experiment007"
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"experiment006"))
spec=importlib.util.spec_from_file_location("paper_c_exp007_test_runner",HERE/"run.py")
assert spec is not None and spec.loader is not None
sim=importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)


def model():
    from trendestimation import TrendSmoother
    smoother=TrendSmoother(80,order=3)
    return smoother,sim.DifferenceLikelihood(smoother)


def test_full_design_is_sequential_and_has_disjoint_parent_seed_namespace():
    a=sim.stage_cases("pilot")
    b=sim.stage_cases("confirm")
    assert len(a)==162
    assert len(b)==1944
    assert len({x["parent_id"] for x in a})==6
    assert len({x["parent_id"] for x in b})==72
    assert set(x["parent_id"] for x in a).isdisjoint(
        set(x["parent_id"] for x in b)
    )
    assert sim.seed_for("pilot","iid",0,"observation") != sim.seed_for(
        "confirm","iid",0,"observation"
    )
    assert len({x["sigma_e_m"] for x in a})==3
    assert len({x["sigma_j_m_s3"] for x in a})==3


def test_true_covariance_fraction_equals_normalized_S_under_iid():
    smoother,solver=model()
    for se in (.01,.05,.2):
        for sj in (.5,2.,8.):
            truth=sim.theoretical_cell(smoother,solver,se,sj,"iid","iid")
            np.testing.assert_allclose(
                truth["S_true_covariance"],truth["S_nominal_iid"],
                rtol=2e-8,atol=2e-9
            )
            assert truth["model_correct"]
            np.testing.assert_allclose(
                truth["S_nominal_iid"],
                smoother.smoothness(truth["true_lambda_ratio"]),
                rtol=1e-8,atol=1e-10
            )


def test_theory_s_increases_with_noise_and_decreases_with_true_jerk_variability():
    smoother,solver=model()
    noise=[sim.theoretical_cell(
        smoother,solver,se,2.,"iid","iid"
    )["S_true_covariance"] for se in (.01,.05,.2)]
    innovation=[sim.theoretical_cell(
        smoother,solver,.05,sj,"iid","iid"
    )["S_true_covariance"] for sj in (.5,2.,8.)]
    assert noise[0]<noise[1]<noise[2]
    assert innovation[0]>innovation[1]>innovation[2]


def test_same_relative_variance_ratio_can_have_16x_absolute_precision_difference():
    smoother,solver=model()
    a=sim.theoretical_cell(smoother,solver,.05,2.,"iid","iid")
    b=sim.theoretical_cell(smoother,solver,.2,8.,"iid","iid")
    np.testing.assert_allclose(a["true_lambda_ratio"],b["true_lambda_ratio"])
    np.testing.assert_allclose(
        a["S_true_covariance"],b["S_true_covariance"],rtol=1e-10
    )
    assert a["absolute_core_precision_m_minus2"] == 16*b[
        "absolute_core_precision_m_minus2"
    ]


@pytest.mark.parametrize("dynamics",sim.CONFIG["factors"]["jerk_structures"])
def test_reconstruction_matches_known_discrete_third_difference(dynamics):
    smoother,_=model()
    z,_,_=sim.unit_draws("pilot",dynamics,0)
    j=sim.discrete_jerk("pilot",dynamics,0,2.,z)
    x=sim.positions_from_jerk(j)
    assert len(x)==80 and len(j)==77
    np.testing.assert_allclose(smoother.D@x / sim.DT**3,j,rtol=0,atol=3e-6)


def test_noise_intervention_reuses_identical_standardized_errors_and_jerk():
    z_j,z_e,sgn=sim.unit_draws("pilot","iid",1)
    z_j_again,z_e_again,sgn_again=sim.unit_draws("pilot","iid",1)
    np.testing.assert_array_equal(z_j,z_j_again)
    np.testing.assert_array_equal(z_e,z_e_again)
    assert sgn==sgn_again
    model_a=sim.standardized_measurement(z_e,"iid",sgn)
    model_b=sim.standardized_measurement(z_e,"last_point_outlier",sgn)
    np.testing.assert_allclose(model_b[:-1],model_a[:-1],rtol=0,atol=0)
    np.testing.assert_allclose(
        model_b[-1]-model_a[-1],
        4*sgn,rtol=0,atol=1e-14
    )


def test_observation_AR1_and_jerk_AR1_have_correct_positive_covariance():
    smoother,solver=model()
    a=sim.theoretical_cell(smoother,solver,.05,2.,"ar1","ar1")
    b=sim.theoretical_cell(smoother,solver,.05,2.,"iid","iid")
    assert not a["model_correct"]
    assert 0<a["S_true_covariance"]<1
    assert abs(a["S_true_covariance"]-a["S_nominal_iid"])>1e-4
    np.testing.assert_allclose(a["S_nominal_iid"],b["S_nominal_iid"])


def test_analytic_finite_vs_boundary_component_variances():
    smoother,solver=model()
    y=sim.positions_from_jerk(np.full(77,.2))
    y+=.04*np.random.default_rng(24).standard_normal(80)
    coordinates=solver.transform(y)
    for lam in (0.,5.,float("inf")):
        var_e,var_u=sim.estimated_variances(
            solver,coordinates,lam,sim.DT**3*.2,unknown_mu=False
        )
        assert np.isfinite(var_e) and np.isfinite(var_u)
        assert var_e>=0 and var_u>=0
    e0,u0=sim.estimated_variances(solver,coordinates,0.,0.,unknown_mu=True)
    einf,uinf=sim.estimated_variances(
        solver,coordinates,float("inf"),0.,unknown_mu=True
    )
    assert e0==0 and u0>=0 and uinf==0 and einf>=0


def test_one_trial_has_four_complete_model_scores_and_known_jerk_errors():
    smoother,solver=model()
    z,e,sgn=sim.unit_draws("pilot","iid",0)
    j=sim.discrete_jerk("pilot","iid",0,2.,z)
    clean=sim.positions_from_jerk(j)
    observed=clean+.05*sim.standardized_measurement(e,"iid",sgn)
    theory=sim.theoretical_cell(smoother,solver,.05,2.,"iid","iid")
    grid=tuple(smoother.lambda_for_smoothness(v)
               for v in sim.CONFIG["selection"]["gcv_s_grid"])
    rows=sim.estimator_rows(
        smoother,solver,observed,clean,j,
        sim.CONFIG["model"]["mean_jerk_m_s3"]*sim.DT**3,
        theory,{
            "trial_id":"fixture","parent_id":"pilot|iid|0000",
            "dynamics":"iid","noise_type":"iid","replicate":0,
            "sigma_e_m":.05,"sigma_j_m_s3":2,
            "model_correct":True,"true_observation_variance_m2":.05**2,
            "true_jerk_variance_discrete_m2":(2*sim.DT**3)**2,
        },grid,
    )
    assert set(x["method"] for x in rows)==set(sim.METHODS)
    assert all(x["status"]=="ok" for x in rows),rows
    assert all(0 <= x["S_selected"] <= 1 for x in rows)
    assert all(x["historical_jerk_mse_m2_s6"]>=0 for x in rows)
    assert all(x["estimated_observation_variance_m2"] is None
               if x["method"]=="gcv_zero_mu" else
               x["estimated_observation_variance_m2"]>=0 for x in rows)


def test_failed_or_existing_destination_cannot_overwrite_data(tmp_path):
    existing=tmp_path/"existing"
    existing.mkdir()
    (existing/"precious.txt").write_text("must stay")
    with pytest.raises(FileExistsError):
        sim.run("pilot",existing)
    assert (existing/"precious.txt").read_text()=="must stay"
