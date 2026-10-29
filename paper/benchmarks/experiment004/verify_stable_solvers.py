"""Experiment004: stable double-precision solvers vs 85-digit dual PLS; restricted BIC.

All results use the exact S grid of run_pilot.py and never overwrite a run.
This is a numerical-accuracy study, NOT a runtime comparison.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from scipy.linalg import cholesky_banded, cho_solve_banded, eigh, lstsq, svd
from scipy.special import expit
from threadpoolctl import threadpool_limits, threadpool_info

import run_pilot as pilot
from verify_bic_precision import precise_dual_banded

METHODS = (
    "svd_polynomial_reference", "svd_shift_free",
    "svd_min_norm_reference", "scaled_augmented_qr_gelsy",
    "scaled_augmented_svd_gelsd", "dual_svd",
    "dual_banded_cholesky", "primal_banded_cholesky", "eigh_gram",
)
HIGH_S = (.9, .99, .999, .999999, 1-1e-8, 1-1e-12)
POLICIES = ("fixed_zero", "observed_difference")


def observations(n, shape, noise, seed):
    truth = pilot.truth(n, shape)
    rng = np.random.default_rng(np.random.SeedSequence(
        [20261028, n, seed, int(shape == "kink"), int(noise == "ar1")]
    ))
    return truth, truth + pilot.noise(n, noise, rng)


def mean_value(model, y, policy):
    return 0. if policy == "fixed_zero" else float(np.mean(model["D"] @ y))


def penalty_bands(n, d):
    bands = np.zeros((d+1, n))
    c = [(-1)**(d-j)*math.comb(d,j) for j in range(d+1)]
    for first in range(n-d):
        for a in range(d+1):
            for b in range(a,d+1):
                bands[b-a, first+a] += c[a]*c[b]
    return bands


def fit_comparators(model, y, mu, lam, left_svd, qbands):
    n, d = model["n"], model["d"]
    D, Vbase, delta = model["D"], model["U"], model["delta"]
    weights = expit(math.log(lam) + np.log(delta))
    reference = pilot.reference(n, d, mu)
    result = {
        "svd_polynomial_reference":
            y - Vbase @ (weights * (Vbase.T @ (y-reference)))
    }

    left, sigma, vt = left_svd
    V = vt.T
    w = expit(math.log(lam) + 2*np.log(sigma))
    ones_proj = left.T @ np.ones(n-d)
    # Mathematically identical, but no high-degree polynomial p_mu constructed:
    # tau=y-V[w*(V.T@y)-mu*(w/sigma)*(U.T@1)].
    effect = w*(vt@y) - mu*(w/sigma)*ones_proj
    result["svd_shift_free"] = y - V@effect
    minimum_norm_reference = V@((mu/sigma)*ones_proj)
    result["svd_min_norm_reference"] = (
        y - V@(w*(vt@(y-minimum_norm_reference)))
    )

    alpha = 1./lam
    # Minimize ||D*tau-mu*1||² + alpha||tau-y||² by an AUGMENTED
    # least-squares system. QR avoids explicitly forming D.T@D.
    stacked = np.vstack([D, math.sqrt(alpha)*np.eye(n)])
    b = np.r_[np.full(n-d,mu), math.sqrt(alpha)*y]
    for name, driver in [
        ("scaled_augmented_qr_gelsy","gelsy"),
        ("scaled_augmented_svd_gelsd","gelsd"),
    ]:
        try:
            result[name] = lstsq(
                stacked, b, cond=1e-15, lapack_driver=driver,
                check_finite=False
            )[0]
        except (ValueError, np.linalg.LinAlgError) as exc:
            result[name] = exc

    dual_rhs = D@y - mu*np.ones(n-d)
    u = left@((left.T@dual_rhs)/(sigma**2+alpha))
    result["dual_svd"] = y-D.T@u

    dual_bands = np.zeros((d+1,n-d))
    for k in range(d+1):
        dual_bands[k,:] = (-1)**k * math.comb(2*d,d-k)
    dual_bands[0] += alpha
    try:
        L = cholesky_banded(dual_bands,lower=True,check_finite=False)
        u = cho_solve_banded((L,True),dual_rhs,check_finite=False)
        result["dual_banded_cholesky"] = y-D.T@u
    except (ValueError, np.linalg.LinAlgError) as exc:
        result["dual_banded_cholesky"] = exc

    bands = lam*qbands.copy()
    bands[0] += 1.
    try:
        L = cholesky_banded(bands,lower=True,check_finite=False)
        result["primal_banded_cholesky"] = reference + cho_solve_banded(
            (L,True),y-reference,check_finite=False
        )
    except (ValueError, np.linalg.LinAlgError) as exc:
        result["primal_banded_cholesky"] = exc

    eigenvalues, vectors = eigh(D.T@D,check_finite=False)
    eigenvalues[:d] = 0
    h = 1./(1+lam*np.maximum(0.,eigenvalues))
    result["eigh_gram"] = reference + vectors@(h*(vectors.T@(y-reference)))
    return result


def precision_rows(nseeds, digits):
    rows = []
    for n in (64,128):
        for d in (5,6):
            model = pilot.prepare(n,d)
            left_svd = svd(model["D"],full_matrices=False,check_finite=False)
            bands = penalty_bands(n,d)
            for shape in ("smooth","kink"):
                for noise in ("iid","ar1"):
                    for seed in range(nseeds):
                        _, y = observations(n,shape,noise,seed)
                        for policy in POLICIES:
                            mu = mean_value(model,y,policy)
                            for s in HIGH_S:
                                j = int(np.argmin(abs(pilot.S_GRID-s)))
                                lam = float(model["lambdas"][j])
                                reference,kkt = precise_dual_banded(
                                    n,d,y,mu,lam,decimal_digits=digits
                                )
                                scale=max(1.,float(np.linalg.norm(reference)))
                                methods=fit_comparators(model,y,mu,lam,left_svd,bands)
                                for name in METHODS:
                                    fit = methods[name]
                                    ok = (not isinstance(fit,Exception)
                                        and np.all(np.isfinite(fit)))
                                    rows.append({
                                        "n":n,"d":d,"shape":shape,
                                        "noise":noise,"seed":seed,
                                        "mu_policy":policy,"mu":mu,
                                        "s":float(pilot.S_GRID[j]),
                                        "lambda_":lam,"method":name,
                                        "status":"ok" if ok else "failure",
                                        "relative_l2_error":(
                                            float(np.linalg.norm(fit-reference)/scale)
                                            if ok else ""
                                        ),
                                        "max_abs_error":(
                                            float(np.max(np.abs(fit-reference)))
                                            if ok else ""
                                        ),
                                        "reference_l2_norm":float(np.linalg.norm(reference)),
                                        "reference_kkt_max":kkt,
                                        "failure_detail":"" if ok else type(fit).__name__,
                                    })
    return rows


def restricted_bic_rows(nseeds):
    rows = []
    for n in (64,128):
        for d in range(1,7):
            model = pilot.prepare(n,d)
            for shape in ("smooth","kink"):
                truth = pilot.truth(n,shape)
                for noise in ("iid","ar1"):
                    for seed in range(nseeds):
                        _,y = observations(n,shape,noise,seed)
                        for policy in POLICIES:
                            mu = mean_value(model,y,policy)
                            score, z = pilot.score_all(model,y,mu)
                            curves = y[None,:] - (
                                model["U"]@(model["w"]*z[None,:]).T
                            ).T
                            errors = np.sqrt(np.mean(
                                (curves-truth[None,:])**2,axis=1
                            ))
                            oracle=int(np.argmin(errors))
                            for lower in (.05,.10):
                                valid = ((pilot.S_GRID >= lower)
                                         & np.isfinite(score["bic"]))
                                winner = int(np.argmin(np.where(
                                    valid,score["bic"],np.inf
                                )))
                                rows.append({
                                    "n":n,"d":d,"shape":shape,"noise":noise,
                                    "seed":seed,"mu_policy":policy,"mu":mu,
                                    "smin":lower,
                                    "selected_s":float(pilot.S_GRID[winner]),
                                    "bic_score":float(score["bic"][winner]),
                                    "true_trend_rmse":float(errors[winner]),
                                    "oracle_rmse":float(errors[oracle]),
                                    "oracle_s":float(pilot.S_GRID[oracle]),
                                    "boundary_selected":bool(
                                        pilot.S_GRID[winner] == lower
                                    ),
                                    "note":"constrained_bic_not_a_revised_formula",
                                })
    return rows


def csv_save(path,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--precision-seeds",type=int,default=3)
    parser.add_argument("--bic-seeds",type=int,default=20)
    parser.add_argument("--digits",type=int,default=85)
    args=parser.parse_args()
    if args.out.exists():
        parser.error("Refusing to overwrite an existing run directory")
    if min(args.precision_seeds,args.bic_seeds)<1 or args.digits<55:
        parser.error("Requires positive seed counts and >=55 decimal digits")
    args.out.mkdir(parents=True)
    start=perf_counter()
    with threadpool_limits(limits=1):
        precision=precision_rows(args.precision_seeds,args.digits)
        bic=restricted_bic_rows(args.bic_seeds)

    expected_precision=2*2*2*2*args.precision_seeds*2*6*len(METHODS)
    expected_bic=2*6*2*2*args.bic_seeds*2*2
    assert len(precision)==expected_precision,(len(precision),expected_precision)
    assert len(bic)==expected_bic,(len(bic),expected_bic)
    assert max(x["reference_kkt_max"] for x in precision)<1e-20

    csv_save(args.out/"stable_solver_precision.csv",precision)
    csv_save(args.out/"restricted_bic_rmse.csv",bic)
    summaries={}
    for name in METHODS:
        subset=[x for x in precision if x["method"]==name]
        values=np.asarray([
            x["relative_l2_error"] for x in subset if x["status"]=="ok"
        ],dtype=float)
        summaries[name]={
            "cases":len(subset),"failures":len(subset)-len(values),
            "errors_above_1e_5":int(np.sum(values>1e-5)),
            "max_relative_error":float(np.max(values)),
            "median_relative_error":float(np.median(values)),
        }
    bic_summary={}
    for minimum in (.05,.10):
        filtered=[r for r in bic if r["smin"]==minimum]
        bic_summary[str(minimum)]={
            "cases":len(filtered),
            "mean_rmse":float(np.mean([
                r["true_trend_rmse"] for r in filtered
            ])),
            "boundary_selected":sum(
                r["boundary_selected"] for r in filtered
            ),
            "mean_by_mu":{
                p:float(np.mean([
                    r["true_trend_rmse"] for r in filtered
                    if r["mu_policy"]==p
                ])) for p in POLICIES
            }
        }
    metadata={
        "experiment":"experiment004_stable_double_precision_validation",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "python":sys.version,"numpy":np.__version__,
        "scipy":scipy.__version__,"mpmath":__import__("mpmath").__version__,
        "platform":platform.platform(),
        "precision_seeds":args.precision_seeds,
        "bic_seeds":args.bic_seeds,"decimal_digits":args.digits,
        "elapsed_seconds":perf_counter()-start,
        "precision_rows":len(precision),"bic_rows":len(bic),
        "methods":summaries,"restricted_bic":bic_summary,
        "study_default":"full SVD of D with shift-free spectral reconstruction",
        "not_global_fit_default":True,
        "numerical_criterion_tolerance":1e-5,
        "special_conditions":[
            "Difference orders d=1..6; d=0 excluded.",
            "High precision compares FITS at frozen float64 lambda and mu.",
            "Restricted BIC is a sensitivity analysis, not a new statistical criterion.",
            "All methods use the same penalty candidate for each matched QA case.",
            "No execution-time ranking: this is a correctness validation.",
            "The high-S SVD reference is not yet the global library fit default.",
        ],
        "threadpools_after_run":threadpool_info(),
    }
    for name in ("stable_solver_precision.csv","restricted_bic_rmse.csv"):
        metadata[name+"_sha256"]=hashlib.sha256(
            (args.out/name).read_bytes()
        ).hexdigest()
    (args.out/"summary.json").write_text(
        json.dumps(metadata,indent=2)+"\n",encoding="utf-8"
    )
    print(json.dumps({
        "precision_rows":len(precision),"bic_rows":len(bic),
        "methods":summaries,"restricted_bic":bic_summary,
        "elapsed_seconds":metadata["elapsed_seconds"]
    },indent=2))


if __name__=="__main__":
    main()
