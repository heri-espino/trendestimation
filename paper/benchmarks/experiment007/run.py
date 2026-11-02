"""Experiment007: observed-difference mean, numerical validity and backend crossovers.

Full-fit study only: no CV/GCV/AICc/BIC/ML score timings are conflated
with trend-fit costs. The pilot executes four fit workloads and audits
independent high-order Decimal reference fits when feasible.

mu='data': mean(np.diff(y,n=d)); mu='zero': fixed 0 control.
For synthetic signal tau, mean(D*tau) is reported as an *oracle
diagnostic*, never supplied to a competing solver as a fitted mu.

Use the existing non-admin Conda environment; no package installations.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import sys
from collections import Counter
from statistics import median
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from threadpoolctl import threadpool_limits
from trendestimation import PreparedPLSSolver, TrendSmoother

import sys as _sys
_sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiment006"))
from audit_high_d import high_precision_reference

N_LEVELS=(64,128,256)
D_LEVELS=(1,2,3,4,5,6)
S_LEVELS=(.2,.5,.75,.9,.95,.99,1.)
POLICIES=("data","zero")
SCALES=("low","high")
METHODS=("svd","cholesky","sparse_lu","pcg_fft")
WORKLOADS=(("one_s_one_series",(.9,),1),
           ("grid_one_series",S_LEVELS,1),
           ("one_s_three_series",(.9,),3),
           ("grid_three_series",S_LEVELS,3))


def make_series(n,d,scale,seed):
    """Independently observed noisy smooth trend, no data leakage."""
    rng=np.random.default_rng(np.random.SeedSequence([20261102,n,d,seed]))
    t=np.linspace(0,1,n)
    true_trend=(
        .25*np.sin(2*np.pi*t)+.16*(t-.5)+.08*(t-.5)**4
    )
    observations=true_trend+rng.normal(0,.05,size=n)
    a=1e-3 if scale=="low" else 1e6
    return a*observations,a*true_trend


def fitted_mu(y,d,policy):
    return float(np.mean(np.diff(y,n=d))) if policy=="data" else 0.


def solver(n,d,method,cache):
    if method=="pcg_fft":
        return PreparedPLSSolver(n,d,method="pcg",preconditioner="fft",
                                 cg_rtol=1e-9,cg_maxiter=5000)
    return PreparedPLSSolver(n,d,method=method,
                             factor_cache=cache if method=="sparse_lu" else False)


def run(output:Path,*,n_levels=N_LEVELS,d_levels=D_LEVELS,seeds=(0,1),
        s_levels=S_LEVELS,scales=SCALES,policies=POLICIES,
        methods=METHODS,high_precision=True,threads=1,timing_repeats=1):
    if timing_repeats<1:raise ValueError("timing_repeats must be >=1")
    if output.exists():raise FileExistsError(f"Refusing to overwrite results: {output}")
    output.mkdir(parents=True)
    raw=[]
    qc=[]
    errors=[]
    started=perf_counter()
    with threadpool_limits(limits=threads):
        for n in n_levels:
            for d in d_levels:
                if d>=n:continue
                spectral=TrendSmoother(n,d)
                # Mapping preparation excluded from this FIT-ONLY study;
                # lambda is the exact same frozen candidate for each fit backend.
                lambdas={s:(float("inf") if s==1
                        else float(spectral.lambda_for_smoothness(s)))
                         for s in s_levels}
                sref=PreparedPLSSolver(n,d,method="svd")
                # Prepare each backend ONCE for numerical validation.
                # Otherwise thousands of redundant dense SVD factorizations
                # would make a correctness audit needlessly expensive.
                qa_solvers={}
                for name in methods:
                    try:
                        qa_solvers[name]=solver(n,d,name,False)
                    except (ValueError,ImportError) as exc:
                        qa_solvers[name]=exc
                for scale in scales:
                    for seed in seeds:
                        series=[make_series(n,d,scale,seed*11+k)
                                for k in range(3)]
                        for policy in policies:
                            for s in s_levels:
                                lam=lambdas[s]
                                for k,(y,true) in enumerate(series):
                                    mu=fitted_mu(y,d,policy)
                                    mu_true=float(np.mean(np.diff(true,n=d)))
                                    mu_gap=mu-mu_true
                                    reference_method="svd_proxy"
                                    reference=None
                                    # independent 85-digit sample is intentionally
                                    # separate from all timed operations.
                                    if (high_precision and n<=128 and d>=5 and
                                            s>=.9 and k==0):
                                        reference,ref_kkt=high_precision_reference(
                                            y,d,mu,lam,digits=85)
                                        if s!=1:
                                            check,_=high_precision_reference(
                                                y,d,mu,lam,digits=55)
                                            if np.linalg.norm(check-reference) / max(
                                                1.,np.linalg.norm(reference))>1e-10:
                                                raise ArithmeticError("Decimal truth failed 55/85-digit convergence")
                                        reference_method="decimal85"
                                    else:
                                        reference=sref.fit(y,lambda_=lam,mu=mu)
                                        ref_kkt=float("nan")
                                    for method in methods:
                                        try:
                                            candidate=qa_solvers[method]
                                            if isinstance(candidate,Exception):
                                                raise candidate
                                            fit=candidate.fit(y,lambda_=lam,
                                                              mu=("data" if policy=="data" else 0.))
                                            error=float(np.linalg.norm(fit-reference)/
                                                        max(1.,np.linalg.norm(reference)))
                                            status=("agreement" if error<=1e-6
                                                    else "inaccurate")
                                            info=""
                                            cg_iter=candidate.cg_iterations
                                            cg_res=candidate.cg_relative_residual
                                        except (ArithmeticError,ValueError,
                                                OverflowError,np.linalg.LinAlgError,
                                                ImportError) as exc:
                                            error=float("nan")
                                            status="solver_failed"
                                            info=f"{type(exc).__name__}: {exc}"[:220]
                                            cg_iter=cg_res=None
                                        qc.append(dict(
                                            n=n,d=d,scale=scale,policy=policy,
                                            seed=seed,series_id=k,s=s,lambda_=lam,
                                            mu_estimated=mu,mu_oracle_true=mu_true,
                                            mu_gap=mu_gap,method=method,
                                            reference=reference_method,
                                            reference_kkt=ref_kkt,
                                            relative_fit_error=error,status=status,
                                            cg_iterations=cg_iter,
                                            cg_relative_residual=cg_res,
                                            exception=info))
                            for workload_index,(workload,targets,n_series) in enumerate(WORKLOADS):
                                if "grid" in workload:
                                    targets=s_levels
                                yy=[series[k][0] for k in range(n_series)]
                                # Counterbalance call-order effects across
                                # independent seed blocks; all algorithms see
                                # identical observations and S candidates.
                                method_order=np.random.default_rng(
                                    np.random.SeedSequence([
                                        7007,n,d,seed,workload_index,
                                        int(scale=="high"),int(policy=="data")
                                    ])).permutation(methods)
                                for method in method_order:
                                    trials=[]
                                    comment=""
                                    cached=0
                                    state="ok"
                                    for _repeat in range(timing_repeats):
                                        setup=fit_time=0.0
                                        fit_start=None
                                        try:
                                            t0=perf_counter()
                                            prepar=solver(n,d,method,cache=(n_series>1))
                                            setup=perf_counter()-t0
                                            fit_start=perf_counter()
                                            for y in yy:
                                                for s in targets:
                                                    _=prepar.fit(
                                                        y,lambda_=lambdas[s],
                                                        mu=("data" if policy=="data" else 0.))
                                            fit_time=perf_counter()-fit_start
                                            cached=prepar.cached_factor_count
                                            trials.append((setup,fit_time))
                                        except (ArithmeticError,ValueError,
                                                OverflowError,np.linalg.LinAlgError,
                                                ImportError,MemoryError) as exc:
                                            state="solver_failed"
                                            comment=f"{type(exc).__name__}: {exc}"[:220]
                                            break
                                    if trials:
                                        # Median of *independent cold*
                                        # setup+work phases from same seed.
                                        chosen=min(trials,key=lambda item:
                                            abs(sum(item)-median(sum(x) for x in trials)))
                                        setup,fit_time=chosen
                                    else:
                                        setup=fit_time=0.
                                    if len(trials)!=timing_repeats:
                                        state="solver_failed"
                                    raw.append(dict(n=n,d=d,scale=scale,
                                        mu_policy=policy,seed=seed,method=str(method),
                                        workload=workload,M=len(targets),R=n_series,
                                        setup_s=setup,total_fit_s=fit_time,
                                        cold_total_s=setup+fit_time,
                                        factor_cache_count=cached,
                                        status=state,exception=comment))
                            print(f"done n={n} d={d} scale={scale} mu={policy} seed={seed}",
                                  flush=True)
    def save(path,rows):
        with path.open("w",newline="",encoding="utf-8") as stream:
            w=csv.DictWriter(stream,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    save(output/"raw_times.csv",raw)
    save(output/"forward_accuracy.csv",qc)
    state=Counter((x["method"],x["status"]) for x in qc)
    counts={method:{"agree":state[method,"agreement"],
                    "inaccurate":state[method,"inaccurate"],
                    "failed":state[method,"solver_failed"]} for method in methods}
    meta=dict(experiment="experiment007",created_utc=datetime.now(timezone.utc).isoformat(),
              n_levels=list(n_levels),d_levels=list(d_levels),
              scales=list(scales),policies=list(policies),
              methods=list(methods),smoothness=list(s_levels),
              seeds=list(seeds),threads=threads,timing_repeats=timing_repeats,
              timing_method_order='seeded_permutation',
              numerical_reference=("85-digit independent decimal for "
                 "n<=128 d>=5 S>=.9 first series only; elsewhere SVD proxy"),
              python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
              machine=platform.platform(),runner_name=os.environ.get("RUNNER_NAME"),
              source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              total_rows_time=len(raw),total_rows_accuracy=len(qc),
              status_counts=counts,elapsed_s=perf_counter()-started,
              caveat=("This is FIT ONLY: no full criterion selection. "
                "SVD proxy agreement is NOT independent numerical truth. "
                "Recorded actual mu='data' per independent series; "
                "mu_oracle_true never supplied for fitting. "
                "Fit methods are compared on same lambda candidates."))
    (output/"metadata.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
    return raw,qc,meta


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--preset",choices=("smoke","pilot","confirm"),default="smoke")
    args=parser.parse_args()
    if args.preset=="smoke":
        run(args.output,n_levels=(64,),d_levels=(2,6),
            seeds=(0,),s_levels=(.5,.9,.99,1.),scales=("low",),
            high_precision=True)
    elif args.preset=="confirm":
        run(args.output,seeds=tuple(range(12)),timing_repeats=3)
    else:
        run(args.output)
