"""Experiment005 — paired numerical accuracy, statistical RMSE and CPU time.

Run from the REPOSITORY ROOT with an editable installation:
    python paper/benchmarks/experiment005/run.py --preset smoke --out paper/benchmarks/experiment005/runs/<unique>

The measurement unit is a matched (data, order, mean, smoothness, method)
on ONE machine. High-precision reference solves are OUTSIDE timed regions.
No published accuracy/time cross-host ratios are inferred. Never overwrite.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

import mpmath
import numpy as np
import scipy
from scipy.linalg import cholesky_banded, cho_solve_banded, eigh, lstsq, svd
from scipy.special import expit
from threadpoolctl import threadpool_info, threadpool_limits

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
EXP004 = BENCH / "experiment004"
for directory in (str(EXP004), str(BENCH)):
    if directory not in sys.path:
        sys.path.insert(0, directory)

import run_pilot as pilot
from verify_bic_precision import precise_dual_banded
from verify_stable_solvers import METHODS, observations, mean_value, penalty_bands
from full_s_backend_criteria import Backend, complete_s_grid
from trendestimation import TrendSmoother, score_lambda

SELECTION_BACKENDS = ("svd", "eigh", "banded_cholesky")
CRITERIA = ("cv", "gcv", "aicc", "bic", "mle")
FIT_BY_BACKEND = {
    "svd": "svd_shift_free",
    "eigh": "eigh_gram",
    "banded_cholesky": "primal_banded_cholesky",
}
# Explicitly record what is and is not independently timed.
PRESETS = {
    "smoke": dict(ns=(24,), orders=(3,6), shapes=("smooth",),
                  noises=("iid",), seeds=1,
                  high_s=(.5,.999999,1-1e-12)),
    "quick": dict(ns=(32,64), orders=(1,3,5,6),
                  shapes=("smooth","kink"), noises=("iid","ar1"),
                  seeds=2, high_s=(.5,.99,.999999,1-1e-12)),
    "full": dict(ns=(48,96,128), orders=(1,2,3,4,5,6),
                 shapes=("smooth","kink"), noises=("iid","ar1"),
                 seeds=10, high_s=(.5,.9,.99,.999999,1-1e-12)),
}


def median_seconds(fn, repeats):
    """Median across identical single-thread timings; failures are explicit."""
    result = None
    times = []
    for _ in range(repeats):
        t0 = perf_counter_ns()
        result = fn()
        times.append((perf_counter_ns()-t0)*1e-9)
    return result, statistics.median(times), statistics.median(
        abs(x-statistics.median(times)) for x in times)


def prepare_method(method, n, d, D):
    """Method-specific reusable structures. Setup is timed separately."""
    if method in ("svd_polynomial_reference", "svd_shift_free",
                  "svd_min_norm_reference", "dual_svd"):
        return svd(D, full_matrices=False, check_finite=False)
    if method == "dual_banded_cholesky":
        return np.array([
            np.full(n-d, (-1)**k*math.comb(2*d,d-k), dtype=float)
            for k in range(d+1)
        ])
    if method == "primal_banded_cholesky":
        return penalty_bands(n,d)
    if method == "eigh_gram":
        vals, V = eigh(D.T@D,check_finite=False)
        vals[:d] = 0.0
        if np.any(vals[d:]<=0):
            raise ArithmeticError("eigh Gram unresolved positive eigenvalues")
        return vals,V
    if method in ("scaled_augmented_qr_gelsy","scaled_augmented_svd_gelsd"):
        return D
    raise ValueError(method)


def fit_once(method, prepared, D, y, mu, lam):
    """Nine distinct Experiment004 fit implementations at ONE fixed lambda."""
    n = len(y)
    d = n-D.shape[0]
    if not np.isfinite(lam) or lam<=0:
        raise ValueError("fit comparison uses positive finite lambda")
    if method in ("svd_polynomial_reference","svd_shift_free",
                  "svd_min_norm_reference","dual_svd"):
        U,sigma,vt=prepared
        V=vt.T
        w=expit(math.log(lam)+2*np.log(sigma))
        if method=="svd_polynomial_reference":
            ref=pilot.reference(n,d,mu)
            return y-V@(w*(vt@(y-ref)))
        if method=="svd_shift_free":
            return y-V@(w*(vt@y)-mu*(w/sigma)*(U.T@np.ones(n-d)))
        if method=="svd_min_norm_reference":
            p=V@((mu/sigma)*(U.T@np.ones(n-d)))
            return y-V@(w*(vt@(y-p)))
        alpha=1/lam
        rhs=D@y-mu*np.ones(n-d)
        sol=U@((U.T@rhs)/(sigma*sigma+alpha))
        return y-D.T@sol
    if method in ("scaled_augmented_qr_gelsy","scaled_augmented_svd_gelsd"):
        alpha=1/lam
        stacked=np.vstack((D,math.sqrt(alpha)*np.eye(n)))
        rhs=np.r_[np.full(n-d,mu),math.sqrt(alpha)*y]
        driver="gelsy" if method=="scaled_augmented_qr_gelsy" else "gelsd"
        return lstsq(stacked,rhs,cond=1e-15,lapack_driver=driver,
                    check_finite=False)[0]
    if method=="dual_banded_cholesky":
        B=prepared.copy()
        B[0]+=1/lam
        L=cholesky_banded(B,lower=True,check_finite=False)
        dual=cho_solve_banded((L,True),D@y-mu*np.ones(n-d),
                              check_finite=False)
        return y-D.T@dual
    if method=="primal_banded_cholesky":
        B=lam*prepared.copy()
        B[0]+=1
        L=cholesky_banded(B,lower=True,check_finite=False)
        reference=pilot.reference(n,d,mu)
        return reference+cho_solve_banded(
            (L,True),y-reference,check_finite=False)
    if method=="eigh_gram":
        val,V=prepared
        reference=pilot.reference(n,d,mu)
        alpha=1/(1+lam*val)
        return reference+V@(alpha*(V.T@(y-reference)))
    raise ValueError(method)


def precise_endpoint(n,d,y,mu,lam,digits):
    """Independent exact endpoint reference, with analytical constraint QA.

    S=0: interpolation exactly y.
    S=1: minimize ||y-tau|| over D_d tau = mu*1, parameterized
    as a degree-(d-1) polynomial plus mu*binomial(i,d).
    Multiprecision QR avoids the shifted high-degree double polynomial.
    """
    if lam==0:
        return np.asarray(y,dtype=float).copy(),0.,"ok"
    with mpmath.workdps(digits):
        yy=[mpmath.mpf(float(a)) for a in y]
        mm=mpmath.mpf(float(mu))
        z=[mpmath.mpf(2*i-(n-1))/(n-1) for i in range(n)]
        A=mpmath.matrix([[t**j for j in range(d)] for t in z])
        target=mpmath.matrix([
            yy[i]-mm*mpmath.binomial(i,d) for i in range(n)
        ])
        coeff,_=mpmath.qr_solve(A,target)
        fitted=[
            mpmath.fsum(A[i,j]*coeff[j] for j in range(d))
            +mm*mpmath.binomial(i,d) for i in range(n)
        ]
        residual=[yy[i]-fitted[i] for i in range(n)]
        gradient=max(
            abs(mpmath.fsum(A[i,j]*residual[i] for i in range(n)))
            for j in range(d))
        stencil=[(-1)**(d-j)*math.comb(d,j) for j in range(d+1)]
        penalty=max(
            abs(mpmath.fsum(stencil[j]*fitted[i+j] for j in range(d+1))-mm)
            for i in range(n-d))
        kkt=float(max(gradient,penalty))
        return np.asarray([float(x) for x in fitted]),kkt,(
            "ok" if kkt<1e-18 else "limit_qa_failure")


def stable_reference(n,d,y,mu,lam,digits,cache):
    """Independent 85-digit banded dual; NOT charged to method runtime."""
    if lam==0 or np.isposinf(lam):
        key=(float(mu),float(lam))
        if key not in cache:
            cache[key]=precise_endpoint(n,d,y,mu,lam,digits)
        return cache[key]
    key=(float(mu),float(lam))
    if key not in cache:
        try:
            expected,kkt=precise_dual_banded(
                n,d,y,mu,lam,decimal_digits=digits)
            cache[key]=(expected,kkt,"ok" if kkt<1e-18 else "kkt_failure")
        except (ValueError,ArithmeticError,OverflowError,ZeroDivisionError) as e:
            cache[key]=(None,None,type(e).__name__)
    return cache[key]


def output_rows(path,rows):
    if not rows: raise AssertionError(f"No measurements: {path.name}")
    with path.open("w",newline="",encoding="utf8") as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def fit_accuracy_case(n,d,shape,noise,seed,mu_policy,
                      sentinel_indices,smoother,methods,repeats,digits,
                      prepared_cache,setup_cache,D,reference_cache):
    actual,y=observations(n,shape,noise,seed)
    mu=mean_value({"D":D},y,mu_policy)
    rows=[]
    for j in sentinel_indices:
        s=float(pilot.S_GRID[j])
        lam=float(smoother.lambda_for_smoothness(s))
        high,kkt,ref_status=stable_reference(
            n,d,y,mu,lam,digits,reference_cache)
        for method in methods:
            setup=setup_cache.get(method,float("nan"))
            row=dict(n=n,d=d,shape=shape,noise=noise,seed=seed,
                     mu_policy=mu_policy,mu_value=mu,s=s,lambda_=lam,
                     method=method,setup_seconds=setup,
                     fit_median_seconds="",fit_mad_seconds="",
                     relative_l2_numerical_error="",max_abs_numerical_error="",
                     true_trend_rmse="",reference_kkt=kkt or "",
                     reference_status=ref_status,status="pending",detail="")
            if method not in prepared_cache:
                row.update(status="setup_failure",detail="setup unavailable")
            else:
                try:
                    def one(): return fit_once(method,prepared_cache[method],D,y,mu,lam)
                    # Each method computes only itself, not a group of nine.
                    fit,elapsed,mad=median_seconds(one,repeats)
                    if not np.all(np.isfinite(fit)):
                        raise ArithmeticError("non-finite fitted values")
                    row.update(fit_median_seconds=elapsed,fit_mad_seconds=mad,
                               true_trend_rmse=float(np.sqrt(
                                   np.mean((fit-actual)**2))))
                    if high is not None and ref_status=="ok":
                        err=fit-high
                        numerical=float(np.linalg.norm(err)/max(1.,np.linalg.norm(high)))
                        row.update(relative_l2_numerical_error=numerical,
                                   max_abs_numerical_error=float(np.max(np.abs(err))),
                                   status="ok" if numerical <= 1e-5 else "inaccurate")
                    else:
                        row.update(status="reference_unverified")
                except (ValueError,ArithmeticError,OverflowError,
                        FloatingPointError,np.linalg.LinAlgError) as e:
                    row.update(status="failure",detail=type(e).__name__)
            rows.append(row)
    return rows


def _score_backend(backend,smoother,y,mu,criterion,lam):
    """One backend's actual criterion evaluation; endpoints analytic."""
    if lam==0 or np.isposinf(lam):
        return float(score_lambda(smoother,y,lambda_=float(lam),
                                  mu=mu,criterion=criterion))
    return float(backend.calculate(y,lam,mu,criterion)[0])


def evaluate_selection(backend,smoother,y,mu,criterion,
                       grid,penalties,policy,bic_floor):
    selected_scores=[]
    t0=perf_counter_ns()
    for s,penalty in zip(grid,penalties):
        try:
            lam = (smoother.lambda_for_smoothness(float(s))
                   if policy=="native_s" else float(penalty))
            selected_scores.append(_score_backend(
                backend,smoother,y,mu,criterion,lam))
        except (ValueError,ArithmeticError,OverflowError,
                FloatingPointError,np.linalg.LinAlgError):
            selected_scores.append(float("nan"))
    search_seconds=(perf_counter_ns()-t0)*1e-9
    # Verification outside timer: compare ALL candidates (not only winner).
    disagreements=0;failures=0;undefined=0;max_error=0.
    for lam,score in zip(penalties,selected_scores):
        expected=float(score_lambda(smoother,y,lambda_=float(lam),
                                     mu=mu,criterion=criterion))
        if np.isposinf(expected) and np.isposinf(score):
            undefined+=1
        elif np.isfinite(expected) and np.isfinite(score):
            e=abs(expected-score)/max(1.,abs(expected))
            max_error=max(max_error,e)
            disagreements+=int(e>1e-5)
        else:
            failures+=1
    full_valid=(disagreements==0 and failures==0)
    eligible=[
        i for i,(s,v) in enumerate(zip(grid,selected_scores))
        if np.isfinite(v) and (criterion!="bic" or s>=bic_floor)
    ]
    choice=min(eligible,key=lambda i:selected_scores[i]) if eligible else None
    return dict(selection_seconds=search_seconds,
                score_disagreements=disagreements,
                failed_candidate_scores=failures,
                criterion_undefined_nodes=undefined,
                max_score_relative_error=max_error,full_grid_valid=full_valid,
                index=choice,
                best_score=selected_scores[choice] if choice is not None else None)


def run(out,preset,repeats,digits,seed_offset=0):
    if out.exists():raise FileExistsError(f"Refusing to overwrite {out}")
    if digits<55 or repeats<1:raise ValueError("digits>=55 and repeats>=1 required")
    config=PRESETS[preset]
    out.mkdir(parents=True)
    fit_rows=[]; selection_rows=[]; map_rows=[]
    t_all=perf_counter_ns()
    targets=complete_s_grid() if preset=="smoke" else pilot.S_GRID
    assert targets[0]==0 and targets[-1]==1
    with threadpool_limits(limits=1):
        measured_threadpools=threadpool_info()
        for n in config["ns"]:
            for d in config["orders"]:
                D=pilot.difference_matrix(n,d)
                prepared={}; setup={}
                for method in METHODS:
                    try:
                        t0=perf_counter_ns()
                        prepared[method]=prepare_method(method,n,d,D)
                        setup[method]=(perf_counter_ns()-t0)*1e-9
                    except (ValueError,ArithmeticError,OverflowError,
                            FloatingPointError,np.linalg.LinAlgError):
                        setup[method]=float("nan")
                t0=perf_counter_ns()
                sm=TrendSmoother(n,order=d)
                smoother_setup=(perf_counter_ns()-t0)*1e-9
                t0=perf_counter_ns()
                mapped=np.array(
                    [sm.lambda_for_smoothness(float(s)) for s in targets])
                mapping_seconds=(perf_counter_ns()-t0)*1e-9
                np.testing.assert_allclose(
                    [sm.smoothness(float(l)) for l in mapped],
                    targets,atol=4e-10,rtol=0)
                map_rows.append(dict(n=n,d=d,candidate_count=len(targets),
                                     smoother_setup_seconds=smoother_setup,
                                     grid_mapping_seconds=mapping_seconds,
                                     largest_finite_lambda=float(mapped[-2])))
                sent_idx=[int(np.argmin(abs(pilot.S_GRID-s))) for s in config["high_s"]]
                sent_idx=list(dict.fromkeys(sent_idx))
                for shape in config["shapes"]:
                    for noise in config["noises"]:
                        for seed_i in range(config["seeds"]):
                            seed=seed_i+seed_offset
                            truth,y=observations(n,shape,noise,seed)
                            for mu_policy in ("fixed_zero","observed_difference"):
                                mu=mean_value({"D":D},y,mu_policy)
                                reference_cache={}
                                fit_rows.extend(fit_accuracy_case(
                                    n,d,shape,noise,seed,mu_policy,
                                    sent_idx,sm,METHODS,repeats,digits,
                                    prepared,setup,D,reference_cache))
                                # Single-series, same-CPU selection, with each
                                # backend/scoring criterion evaluated on same S grid.
                                for backend_name in SELECTION_BACKENDS:
                                    for criterion in CRITERIA:
                                        try:
                                            t0=perf_counter_ns()
                                            backend=Backend(n,d,backend_name,criterion=criterion)
                                            setup_seconds=(perf_counter_ns()-t0)*1e-9
                                        except (ValueError,ArithmeticError,OverflowError,
                                                FloatingPointError,np.linalg.LinAlgError) as e:
                                            backend=None
                                            setup_seconds=float("nan")
                                            err=type(e).__name__
                                        for policy in ("native_s","cached_s"):
                                            bic_floor=.10
                                            row=dict(
                                                n=n,d=d,shape=shape,noise=noise,
                                                seed=seed,mu_policy=mu_policy,
                                                mu_value=mu,criterion=criterion,
                                                bic_smin=(bic_floor if criterion=="bic" else ""),
                                                backend=backend_name,policy=policy,
                                                grid_count=len(targets),setup_seconds=setup_seconds,
                                                smoother_setup_seconds=smoother_setup,
                                                mapping_once_seconds=(mapping_seconds if policy=="cached_s" else 0.),
                                                selection_seconds="",fit_seconds="",
                                                cold_phase_sum_seconds="",warm_selection_fit_seconds="",
                                                selected_s="",selected_lambda="",selected_score="",
                                                complete_grid_valid=False,
                                                score_failures="",score_disagreements="",
                                                criterion_undefined_nodes="",max_score_relative_error="",
                                                true_trend_rmse="",oracle_rmse="",
                                                excess_oracle_rmse="",
                                                numerical_relative_l2_error="",numerical_reference_status="",
                                                status="setup_failure",failure_detail=err if backend is None else "")
                                            if backend is not None:
                                                try:
                                                    result=evaluate_selection(
                                                        backend,sm,y,mu,criterion,
                                                        targets,mapped,policy,bic_floor)
                                                    row.update(
                                                        selection_seconds=result["selection_seconds"],
                                                        complete_grid_valid=result["full_grid_valid"],
                                                        score_failures=result["failed_candidate_scores"],
                                                        score_disagreements=result["score_disagreements"],
                                                        criterion_undefined_nodes=result["criterion_undefined_nodes"],
                                                        max_score_relative_error=result["max_score_relative_error"])
                                                    idx=result["index"]
                                                    if idx is None:
                                                        row["status"]="no_finite_candidate"
                                                    else:
                                                        lam=float(mapped[idx])
                                                        method=FIT_BY_BACKEND[backend_name]
                                                        if method not in prepared:
                                                            raise ArithmeticError("No corresponding fit backend")
                                                        start=perf_counter_ns()
                                                        fit=fit_once(method,prepared[method],D,y,mu,lam) if 0<lam<np.inf else sm.fit(y,lambda_=lam,mu=mu).trend
                                                        elapsed=(perf_counter_ns()-start)*1e-9
                                                        if not np.all(np.isfinite(fit)):
                                                            raise ArithmeticError("Nonfinite selection fit")
                                                        row.update(
                                                            fit_seconds=elapsed,selected_s=float(targets[idx]),
                                                            selected_lambda=lam,selected_score=result["best_score"],
                                                            true_trend_rmse=float(np.sqrt(np.mean((fit-truth)**2))))
                                                        high,kkt,ref_status=stable_reference(
                                                            n,d,y,mu,lam,digits,reference_cache)
                                                        row["numerical_reference_status"]=ref_status
                                                        if high is not None and ref_status=="ok":
                                                            row["numerical_relative_l2_error"]=float(
                                                                np.linalg.norm(fit-high)/max(1.,np.linalg.norm(high)))
                                                        # Oracle uses the trusted SVD smoother on exact same grid.
                                                        if "oracle" not in reference_cache:
                                                            oracle_errs=[]
                                                            for lam_ref in mapped:
                                                                fitted=sm.fit(y,lambda_=float(lam_ref),mu=mu).trend
                                                                oracle_errs.append(
                                                                    np.sqrt(np.mean((fitted-truth)**2)))
                                                            reference_cache["oracle"]=float(min(oracle_errs))
                                                        row["oracle_rmse"]=reference_cache["oracle"]
                                                        row["excess_oracle_rmse"]=row["true_trend_rmse"]-row["oracle_rmse"]
                                                        row["warm_selection_fit_seconds"]=result["selection_seconds"]+elapsed
                                                        row["cold_phase_sum_seconds"]=(
                                                            smoother_setup+mapping_seconds+setup_seconds+
                                                            setup.get(method,0.)+result["selection_seconds"]+elapsed
                                                            if policy=="cached_s" else
                                                            smoother_setup+setup_seconds+setup.get(method,0.)+
                                                            result["selection_seconds"]+elapsed)
                                                        row["status"]=(
                                                            "ok" if result["full_grid_valid"] and
                                                            ref_status=="ok" and
                                                            row["numerical_relative_l2_error"]!="" and
                                                            float(row["numerical_relative_l2_error"])<=1e-5
                                                            else "invalid_or_unverified")
                                                except (ValueError,ArithmeticError,OverflowError,
                                                        FloatingPointError,np.linalg.LinAlgError) as e:
                                                    row.update(status="failure",failure_detail=type(e).__name__)
                                            selection_rows.append(row)
                            print(f"[experiment005] n={n} d={d} {shape}/{noise} seed={seed}",flush=True)
    output_rows(out/"fit_accuracy_timing.csv",fit_rows)
    output_rows(out/"selection_accuracy_timing.csv",selection_rows)
    output_rows(out/"grid_mapping_times.csv",map_rows)
    summary={
        "experiment":"experiment005","preset":preset,
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds":(perf_counter_ns()-t_all)*1e-9,
        "n":list(config["ns"]),"d":list(config["orders"]),
        "seeds_per_case":config["seeds"],"seed_offset":seed_offset,
        "shape":list(config["shapes"]),"noise":list(config["noises"]),
        "mu_policies":["fixed_zero","observed_difference"],
        "numerical_fit_methods":list(METHODS),
        "selection_backends":list(SELECTION_BACKENDS),
        "criteria":list(CRITERIA),
        "search_policies":["native_s","cached_s"],
        "grid_size":len(targets),
        "high_s_sentinels":list(config["high_s"]),
        "repeats":repeats,"decimal_digits":digits,
        "high_precision_reference":"independent mp banded dual at finite lambda; mp constrained polynomial QR at S=1; exact y at S=0",
        "reference_outside_timers":True,
        "mp_endpoint_policy":"S=1 constrained multiprecision polynomial QR; S=0 y exactly",
        "statistical_error":"RMSE to known in-sample latent trend, not forecasting",
        "numerical_error":"relative L2 versus 85-digit reference at same frozen lambda",
        "score_validity":"all finite candidates compared to spectral double reference outside timer",
        "selection_runtime":"measured score sweep plus selected fit; phase-summed cold and warm costs are not directly timed monolithic spans",
        "setup_note":"Some selection and fit helper structures are separately created; cold sum intentionally charges both.",
        "invalid_policy":"No method with incomplete or discrepant criterion grid qualifies as winner.",
        "bic_policy":"S>=0.10 restricted sensitivity; not a repaired criterion",
        "blas_threads":1,"threadpools":measured_threadpools,
        "platform":platform.platform(),"python":sys.version,
        "numpy":np.__version__,"scipy":scipy.__version__,
        "mpmath":mpmath.__version__,
        "fit_rows":len(fit_rows),"selection_rows":len(selection_rows),
        "fit_valid":sum(x["status"]=="ok" for x in fit_rows),
        "selection_valid":sum(x["status"]=="ok" for x in selection_rows),
    }
    for name in ("fit_accuracy_timing.csv","selection_accuracy_timing.csv",
                 "grid_mapping_times.csv"):
        summary[name+"_sha256"]=hashlib.sha256((out/name).read_bytes()).hexdigest()
    (out/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
    print(json.dumps({k:summary[k] for k in (
        "elapsed_seconds","fit_rows","selection_rows","fit_valid","selection_valid")},indent=2))
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preset",choices=tuple(PRESETS),default="smoke")
    p.add_argument("--repeats",type=int,default=3)
    p.add_argument("--digits",type=int,default=85)
    p.add_argument("--seed-offset",type=int,default=0)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.out,a.preset,a.repeats,a.digits,a.seed_offset)


if __name__=="__main__":
    main()
