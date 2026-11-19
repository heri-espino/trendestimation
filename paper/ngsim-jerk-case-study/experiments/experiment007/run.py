"""Experiment007: paired factorial calibration of PLS normalized smoothness S.

Does a selected S track relative observation-noise attribution when
observation SD and genuine third-difference/jerk volatility are varied
independently? The generated clean positions and observation errors are
fully known; noisy series are never reused to define theoretical truth.

Source of statistical estimators: existing TrendSmoother, select_lambda,
and Experiment006 DifferenceLikelihood. No production API is modified.

Usage: python paper/ngsim-jerk-case-study/experiments/experiment007/run.py \
    --stage pilot --output-dir /unique/pilot
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gzip
import importlib.util
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np
from scipy import __version__ as scipy_version
from scipy.linalg import solve

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE.parent / "experiment006"))
from trendestimation import TrendSmoother, select_lambda  # noqa: E402
from reml import DifferenceLikelihood  # noqa: E402

CONFIG_PATH = HERE / "config.json"
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
N = int(CONFIG["model"]["n"])
DT = float(CONFIG["model"]["dt_s"])
D = int(CONFIG["model"]["difference_order"])
METHODS = (
    "known_mu_reml", "joint_reml", "global_ols_plugin_mle", "gcv_zero_mu"
)


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def seed_for(stage: str, kind: str, replicate: int, stream: str) -> int:
    identity = f"experiment007|20261109|{stage}|{kind}|{replicate}|{stream}"
    return int.from_bytes(hashlib.sha256(identity.encode()).digest()[:8], "little")


def stationary_ar1(z: np.ndarray, rho: float):
    """Transform a seeded iid-N(0,1) vector into unit marginal SD AR1."""
    out = np.empty(len(z), dtype=float)
    out[0] = z[0]
    for index in range(1, len(z)):
        out[index] = rho*out[index-1] + math.sqrt(1-rho*rho)*z[index]
    return out


def unit_draws(stage: str, dynamics: str, rep: int):
    """Same parent noise and jerk draws across ALL intervention treatments."""
    jerk_rng = np.random.default_rng(seed_for(stage, dynamics, rep, "jerk"))
    noise_rng = np.random.default_rng(seed_for(stage, dynamics, rep, "observation"))
    sign_rng = np.random.default_rng(seed_for(stage, dynamics, rep, "outlier_sign"))
    z_jerk = jerk_rng.standard_normal(N-D)
    z_noise = noise_rng.standard_normal(N)
    sign = 1.0 if sign_rng.integers(0,2) == 1 else -1.0
    return z_jerk, z_noise, sign


def discrete_jerk(stage: str, dynamics: str, rep: int,
                  sigma_j: float, z_jerk: np.ndarray):
    """Exact prescribed jerk in m/s^3 on N-3 third-difference rows."""
    base=float(CONFIG["model"]["mean_jerk_m_s3"])
    if dynamics == "ar1":
        u = stationary_ar1(z_jerk, float(CONFIG["factors"]["jerk_ar1_rho"]))
    elif dynamics in ("iid","sign_reversal"):
        u = z_jerk
    else:
        raise ValueError(f"Unknown jerk structure: {dynamics}")
    jerk = base + sigma_j*u
    if dynamics == "sign_reversal":
        # D3 row i corresponds to the interval [t_i,t_{i+3}].
        t=(np.arange(N-D,dtype=float)+1.5)*DT
        jerk += float(CONFIG["factors"]["reversal_jerk_step_m_s3"]) * (
            t >= float(CONFIG["factors"]["reversal_time_s"])
        )
    return jerk


def positions_from_jerk(jerk: np.ndarray):
    """Integrate D3(x)=dt^3*j exactly via third-difference recurrence."""
    x=np.empty(N,dtype=float)
    v=float(CONFIG["model"]["baseline_speed_m_s"])
    x[0]=float(CONFIG["model"]["baseline_position_m"])
    x[1]=x[0]+v*DT
    x[2]=x[0]+2*v*DT
    for i,value in enumerate(jerk):
        x[i+3]=3*x[i+2]-3*x[i+1]+x[i]+DT**3*float(value)
    return x


def standardized_measurement(z_noise: np.ndarray, noise_type: str, sign: float):
    factors=CONFIG["factors"]
    if noise_type == "iid":
        return z_noise.copy()
    if noise_type == "ar1":
        return stationary_ar1(z_noise,float(factors["observation_ar1_rho"]))
    if noise_type == "last_point_outlier":
        result=z_noise.copy()
        result[-1]+=sign*float(factors["last_point_outlier_sd_multiplier"])
        return result
    raise ValueError(f"Unknown observation noise model: {noise_type}")


def covariance_rho(length: int, rho: float):
    idx=np.arange(length)
    return rho**np.abs(idx[:,None]-idx[None,:])


def theoretical_cell(smoother: TrendSmoother, solver: DifferenceLikelihood,
                     sigma_e: float, sigma_j: float, dynamics: str, noise_type: str):
    """Theoretical *unconditional spectral covariance fraction*.

    For iid noise and iid jerk this equals the normalized PLS S(lambda_true).
    Under correlation/outliers the scalar-penalty S is generally
    MISSPECIFIED, though the full-covariance fraction remains defined.
    The randomized ±4-sigma endpoint spike contributes an extra
    16 sigma_e^2 to the final observation covariance.
    """
    factor=CONFIG["factors"]
    m=N-D
    Dmat=smoother.D
    noise_R=np.eye(N)
    if noise_type == "ar1":
        noise_R=covariance_rho(N,float(factor["observation_ar1_rho"]))
    elif noise_type == "last_point_outlier":
        noise_R[-1,-1]+=float(factor["last_point_outlier_sd_multiplier"])**2
    jerk_R=np.eye(m)
    if dynamics == "ar1":
        jerk_R=covariance_rho(m,float(factor["jerk_ar1_rho"]))
    noise_cov=sigma_e**2*(Dmat @ noise_R @ Dmat.T)
    jerk_cov=(DT**3*sigma_j)**2*jerk_R
    total_cov=noise_cov+jerk_cov
    true_fraction=float(np.trace(
        solve(total_cov,noise_cov,assume_a="pos",check_finite=False)
    )/m)
    ratio=(sigma_e/(DT**3*sigma_j))**2
    nominal=float(np.mean(ratio*solver.delta/(1+ratio*solver.delta)))
    if not(0 <= true_fraction <= 1.0000001 and 0 <= nominal <= 1):
        raise ValueError("Spectral noise fractions must lie in [0,1]")
    return {
        "sigma_e_m":sigma_e,
        "sigma_j_m_s3":sigma_j,
        "dynamics":dynamics,"noise_type":noise_type,
        "true_lambda_ratio":ratio,
        "S_nominal_iid":nominal,
        "S_true_covariance":true_fraction,
        "model_correct":dynamics=="iid" and noise_type=="iid",
        "noise_correlation_or_outlier":noise_type!="iid",
        "jerk_correlation_or_changepoint":dynamics!="iid",
        "absolute_core_precision_m_minus2":1.0/sigma_e**2,
    }


def global_ols_mu(y: np.ndarray):
    t=np.arange(N,dtype=float)*DT
    fit=np.polynomial.Polynomial.fit(t,y,deg=3).convert()
    return float(6*fit.coef[3]*DT**3)


def estimated_variances(solver: DifferenceLikelihood, projected: np.ndarray,
                        lam: float, mu: float, *, unknown_mu: bool):
    """Gaussian covariance components at selected lambda; boundary-aware."""
    k=solver.m-int(unknown_mu)
    residual=projected-mu*solver.one
    if np.isinf(lam):
        q=float(np.sum((residual**2)/solver.delta))
        return q/k,0.0
    w=1.0+lam*solver.delta
    q=float(np.sum(residual**2/w))
    uvar=q/k
    return lam*uvar,uvar


def estimator_rows(smoother,solver,y,true_x,true_jerk,true_mu,
                   theory,meta,grid):
    coords=solver.transform(y)
    rows=[]
    for name in METHODS:
        try:
            if name=="known_mu_reml":
                fit=solver.optimize(y,fixed_mu=true_mu)
            elif name=="joint_reml":
                fit=solver.optimize(y)
            elif name=="global_ols_plugin_mle":
                fit=solver.optimize(y,fixed_mu=global_ols_mu(y))
            elif name=="gcv_zero_mu":
                chosen=select_lambda(
                    smoother,y,criterion="gcv",mu=0.0,
                    grid=grid,method="grid"
                )
                fit=type("Selection",(),{
                    "lambda_":chosen.lambda_,"mu":0.0,"score":chosen.score,
                    "smoothness":chosen.smoothness,"position":"finite_grid",
                    "n_evaluations":len(grid),
                })()
            else:
                raise AssertionError(name)
            trend=np.asarray(
                smoother.fit(y,lambda_=fit.lambda_,mu=fit.mu).trend,dtype=float
            )
            if not(np.isfinite(trend).all() and np.isfinite(fit.smoothness)):
                raise FloatingPointError("Nonfinite PLS trend or selected smoothness")
            jerr=(smoother.D@trend-smoother.D@true_x)/DT**3
            est_e,est_u = (
                estimated_variances(solver,coords,fit.lambda_,fit.mu,
                                    unknown_mu=name=="joint_reml")
                if name!="gcv_zero_mu" else (None,None)
            )
            row={
                **meta, "method":name,"status":"ok","reason":"",
                "lambda":float(fit.lambda_),
                "mu_discrete_m":float(fit.mu),
                "mu_jerk_m_s3":float(fit.mu/DT**3),
                "S_selected":float(fit.smoothness),
                "S_true_covariance":theory["S_true_covariance"],
                "S_nominal_iid":theory["S_nominal_iid"],
                "S_error":float(fit.smoothness-theory["S_true_covariance"]),
                "selection_policy":fit.position,
                "selection_score":float(fit.score),
                "n_objective_evaluations":fit.n_evaluations,
                "estimated_observation_variance_m2":est_e,
                "estimated_jerk_innovation_variance_discrete_m2":est_u,
                "historical_jerk_mse_m2_s6":float(np.mean(jerr*jerr)),
                "historical_position_mse_m2":float(np.mean((trend-true_x)**2)),
            }
        except (ValueError, FloatingPointError, ArithmeticError,
                np.linalg.LinAlgError) as exc:
            row={
                **meta, "method":name,"status":"invalid",
                "reason":f"{type(exc).__name__}: {exc}"[:400],
                "lambda":"","mu_discrete_m":"","mu_jerk_m_s3":"",
                "S_selected":"","S_true_covariance":theory["S_true_covariance"],
                "S_nominal_iid":theory["S_nominal_iid"],
                "S_error":"","selection_policy":"","selection_score":"",
                "n_objective_evaluations":"",
                "estimated_observation_variance_m2":"",
                "estimated_jerk_innovation_variance_discrete_m2":"",
                "historical_jerk_mse_m2_s6":"","historical_position_mse_m2":"",
            }
        rows.append(row)
    return rows


def stage_cases(stage: str):
    if stage not in ("pilot","confirm"):
        raise ValueError(f"Stage must be pilot or confirm: {stage}")
    repcount=int(CONFIG["stages"][stage+"_replicates_per_structure"])
    out=[]
    for dynamics in CONFIG["factors"]["jerk_structures"]:
        for rep in range(repcount):
            for sigj in CONFIG["factors"]["latent_jerk_innovation_sd_m_s3"]:
                for noise_type in CONFIG["factors"]["observation_noise_models"]:
                    for sige in CONFIG["factors"]["position_noise_sd_m"]:
                        out.append({
                            "stage":stage, "dynamics":dynamics,"replicate":rep,
                            "parent_id":f"{stage}|{dynamics}|{rep:04d}",
                            "sigma_j_m_s3":float(sigj),
                            "noise_type":noise_type,"sigma_e_m":float(sige),
                        })
    if len(out)!=int(CONFIG["stages"][stage+"_cases"]):
        raise AssertionError("Predeclared case count differs from Cartesian design")
    return out


def save_csv(path: Path,records):
    if not records:
        raise ValueError(f"No rows for {path}")
    with path.open("x",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def run(stage: str,output: Path):
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing directory: {output}")
    started=time.perf_counter()
    cases=stage_cases(stage)
    smoother=TrendSmoother(N,order=D)
    solver=DifferenceLikelihood(smoother)
    grid=tuple(
        float(smoother.lambda_for_smoothness(s))
        for s in CONFIG["selection"]["gcv_s_grid"]
    )
    out_theory={}
    for case in cases:
        key=(case["sigma_e_m"],case["sigma_j_m_s3"],
             case["dynamics"],case["noise_type"])
        if key not in out_theory:
            out_theory[key]=theoretical_cell(
                smoother,solver,*key
            )
    output.mkdir(parents=True,exist_ok=False)
    (output/"config.json").write_text(
        json.dumps(CONFIG,indent=2)+"\n",encoding="utf-8"
    )
    theory=[dict(record) for record in out_theory.values()]
    save_csv(output/"theory_cells.csv",theory)
    generated=output/"trials.jsonl.gz"
    selections=[]
    counts=Counter()
    meta_seed=[]
    with gzip.open(generated,"xt",encoding="utf-8") as archive:
        for index,case in enumerate(cases):
            parent=case["parent_id"]
            dynamics=case["dynamics"]
            rep=case["replicate"]
            sigma_j=case["sigma_j_m_s3"]
            sigma_e=case["sigma_e_m"]
            noise_type=case["noise_type"]
            z_j,z_e,outlier_sign=unit_draws(stage,dynamics,rep)
            jerk=discrete_jerk(stage,dynamics,rep,sigma_j,z_j)
            clean=positions_from_jerk(jerk)
            eps_unit=standardized_measurement(z_e,noise_type,outlier_sign)
            observed=clean+sigma_e*eps_unit
            if not(np.isfinite(clean).all() and np.isfinite(observed).all()):
                raise FloatingPointError("Nonfinite known/noisy positions")
            trial_id=f"{stage}_{index:06d}"
            key=(sigma_e,sigma_j,dynamics,noise_type)
            metainfo={
                "trial_id":trial_id,"parent_id":parent,
                "stage":stage, "dynamics":dynamics,
                "noise_type":noise_type,"replicate":rep,
                "sigma_e_m":sigma_e,"sigma_j_m_s3":sigma_j,
                "model_correct":out_theory[key]["model_correct"],
                "true_lambda_ratio":out_theory[key]["true_lambda_ratio"],
                "true_mu_discrete_m":float(CONFIG["model"]["mean_jerk_m_s3"])*DT**3,
                "true_observation_variance_m2":sigma_e**2,
                "true_jerk_variance_discrete_m2":(sigma_j*DT**3)**2,
            }
            archive.write(json.dumps({
                **metainfo,
                "jerk_seed":seed_for(stage,dynamics,rep,"jerk"),
                "noise_seed":seed_for(stage,dynamics,rep,"observation"),
                "outlier_seed":seed_for(stage,dynamics,rep,"outlier_sign"),
                "outlier_sign":outlier_sign,
                "true_position_m":clean.tolist(),
                "true_discrete_jerk_m_s3":jerk.tolist(),
                "standardized_jerk_innovations":z_j.tolist(),
                "standardized_observation_errors":eps_unit.tolist(),
                "observed_position_m":observed.tolist(),
            },allow_nan=False)+"\n")
            selections.extend(estimator_rows(
                smoother,solver,observed,clean,jerk,
                metainfo["true_mu_discrete_m"],out_theory[key],metainfo,grid
            ))
            counts["trials"]+=1
            if (index+1)%50==0 or index+1==len(cases):
                print(f"Experiment007 {stage}: {index+1}/{len(cases)} cases",
                      flush=True)
    save_csv(output/"selections.csv",selections)
    if counts["trials"]!=len(cases):
        raise AssertionError("Partial trial coverage")
    if len(selections)!=len(cases)*len(METHODS):
        raise AssertionError("Missing method selection rows")
    status=Counter(row["status"] for row in selections)
    # This is a diagnostic experiment. An invalid method is not silently
    # dropped, and is reported in the manifest and analyses.
    # A different experiment also has an analyze.py. Resolve the explicit
    # file path under a unique module name to protect full pytest collection.
    spec = importlib.util.spec_from_file_location(
        "paper_c_experiment007_diagnostics", HERE / "analyze.py"
    )
    assert spec is not None and spec.loader is not None
    analyzer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analyzer)
    summaries=analyzer.produce(output,CONFIG,stage)
    manifest={
        "schema":1,"experiment":"experiment007","stage":stage,
        "status":"complete" if status["invalid"]==0 else "completed_with_invalid_methods",
        "started_utc":datetime.now(timezone.utc).isoformat(),
        "source_commit":os.environ.get("GITHUB_SHA","manual"),
        "runner":os.environ.get("RUNNER_NAME","manual"),
        "source_config_sha256":sha256(CONFIG_PATH),
        "n_trials":len(cases),"n_selection_rows":len(selections),
        "status_counts":dict(status),
        "n_theory_cells":len(theory),
        "n_independent_replicate_parent_draws":
            len({case["parent_id"] for case in cases}),
        "simulation_observation_generation":"new paired factorial Experiment007; no rerun of Experiment005",
        "theory_truth":"covariance-trace fraction from known DGP; not estimated from observed data",
        "bootstrap_grouping":"independent parent stage/dynamics/replicate; dependent factorial cases never counted as independent",
        "statistics":summaries,
        "elapsed_seconds":time.perf_counter()-started,
        "output_dir":str(output.resolve()),
        "numpy_version":np.__version__,"scipy_version":scipy_version,
    }
    (output/"run_manifest.json").write_text(
        json.dumps(manifest,indent=2,allow_nan=False)+"\n",encoding="utf-8"
    )
    print((output/"RESULTS.md").read_text(encoding="utf-8")[:15000],flush=True)
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage",choices=("pilot","confirm"),required=True)
    p.add_argument("--output-dir",required=True,type=Path)
    args=p.parse_args()
    run(args.stage,args.output_dir)


if __name__=="__main__":
    main()
