"""Experiment006 high-order QA: independent 85-digit truth and forward errors.

Not a performance ranking. Never count a fitted series as correct solely
because a double-precision KKT residual is below a fixed threshold.

Run: python paper/benchmarks/experiment006/audit_high_d.py --output DIR
Requires the repo's existing mpmath in the designated Conda environment.
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

import mpmath as mp
import numpy as np
from scipy.linalg import cho_solve_banded

from trendestimation import TrendSmoother, PreparedPLSSolver
from selected_inverse import BandedTrace
from run import sample


def high_precision_reference(y, d, mu, lam, digits=85):
    """Fixed-float64-input arbitrary-precision dual normal-equation solve.

    Adapted from Experiment004/verify_bic_precision.py (previously tested
    against 55/85/110-digit references). All arithmetic, including D,
    the dual factor, and the reconstructed fitted vector, is mp.mpf.
    """
    with mp.workdps(digits):
        n=len(y)
        m=n-d
        coeff=[(-1)**(d-j)*math.comb(d,j) for j in range(d+1)]
        obs=[mp.mpf(float(v)) for v in y]
        mean=mp.mpf(float(mu))
        if np.isposinf(lam):
            # Exact constrained polynomial projection onto D tau = mu 1.
            # Falling binomial basis columns k=0,...,d-1 span null(D).
            shifted=[obs[i]-mean*math.comb(i,d) for i in range(n)]
            basis=mp.matrix([[mp.mpf(math.comb(i,k)) for k in range(d)]
                              for i in range(n)])
            gram=basis.T*basis
            coeffs=mp.lu_solve(gram,basis.T*mp.matrix(shifted))
            result=[mean*math.comb(i,d)+
                    mp.fsum(basis[i,k]*coeffs[k] for k in range(d))
                    for i in range(n)]
        else:
            penalty=mp.mpf(float(lam))
            rhs=[mp.fsum(coeff[j]*obs[i+j] for j in range(d+1))-mean
                 for i in range(m)]
            band=[mp.mpf((-1)**k*math.comb(2*d,d-k)) for k in range(d+1)]
            alpha=1/penalty
            lower=[[mp.mpf(0) for _ in range(d+1)] for _ in range(m)]
            for i in range(m):
                lower[i][0]=mp.sqrt(
                    band[0]+alpha-mp.fsum(
                        lower[i][i-k]**2 for k in range(max(0,i-d),i)))
                for j in range(i+1,min(m,i+d+1)):
                    remainder=mp.fsum(
                        lower[j][j-k]*lower[i][i-k]
                        for k in range(max(0,j-d),i)
                        if i-k<=d and j-k<=d)
                    lower[j][j-i]=(band[j-i]-remainder)/lower[i][0]
            forward=[]
            for i in range(m):
                forward.append((rhs[i]-mp.fsum(
                    lower[i][i-j]*forward[j]
                    for j in range(max(0,i-d),i)))/lower[i][0])
            u=[mp.mpf(0) for _ in range(m)]
            for i in range(m-1,-1,-1):
                u[i]=(forward[i]-mp.fsum(
                    lower[j][j-i]*u[j] for j in range(i+1,min(i+d+1,m))
                ))/lower[i][0]
            result=obs.copy()
            for i in range(m):
                for j in range(d+1):
                    result[i+j]-=coeff[j]*u[i]
        if np.isfinite(lam):
            lp=mp.mpf(float(lam))
            penalty_residual=[mp.fsum(
                coeff[j]*result[i+j] for j in range(d+1))-mean
                for i in range(m)]
            kkt=[result[i]-obs[i] for i in range(n)]
            for i in range(m):
                for j in range(d+1):
                    kkt[i+j]+=lp*coeff[j]*penalty_residual[i]
            reference_kkt=float(max(abs(v) for v in kkt))
        else:
            reference_kkt=float(max(abs(
                mp.fsum(coeff[j]*result[i+j] for j in range(d+1))-mean)
                for i in range(m)))
        return np.asarray([float(v) for v in result]), reference_kkt


def native_kkt_error(y, fit, d, mu, lam, D):
    if np.isposinf(lam):
        return float(np.linalg.norm(D@fit-mu)/
                     max(1.,np.linalg.norm(y)))
    rhs=y+lam*mu*np.asarray(D.T@np.ones(len(y)-d)).ravel()
    residual=lam*np.asarray(D.T@(D@fit-mu)).ravel()
    return float(np.linalg.norm(y-fit-residual)/
                 max(1.,np.linalg.norm(y),np.linalg.norm(rhs)))


def audit(output:Path, *,digits=85, n=128, orders=(5,6),
          levels=(.75,.85,.9,.91,.95,.99,1.), seeds=(20261103,20261104)):
    from time import perf_counter
    if output.exists():
        raise FileExistsError(f"Do not overwrite archived numerical QA: {output}")
    output.mkdir(parents=True)
    rows=[]
    started=perf_counter()
    for d in orders:
        spectral=TrendSmoother(n,d)
        structure=BandedTrace(n,d)
        D=structure.D
        for seed in seeds:
            y=sample(n,seed+29*n+7*d,"high")
            mu=.15
            for target in levels:
                lam=(float("inf") if target==1
                     else float(spectral.lambda_for_smoothness(float(target))))
                ref,kkt=high_precision_reference(y,d,mu,lam,digits)
                if np.isfinite(lam):
                    check,_=high_precision_reference(y,d,mu,lam,55)
                    agreement=float(np.linalg.norm(ref-check)/
                                    max(1.,np.linalg.norm(ref)))
                    if agreement>1e-10:
                        raise ArithmeticError(
                            f"Reference precision not converged: {agreement}")
                else:agreement=0.
                scale=max(1.,float(np.linalg.norm(ref)))
                candidate_methods=("svd","cholesky","sparse_lu","pcg")
                for method in candidate_methods:
                    try:
                        if method in ("svd","cholesky"):
                            solver=PreparedPLSSolver(n,d,method=method)
                        elif method=="pcg":
                            solver=PreparedPLSSolver(
                                n,d,method="pcg",preconditioner="fft",
                                cg_rtol=1e-9,cg_maxiter=5000)
                        else:
                            solver=PreparedPLSSolver(n,d,method="sparse_lu")
                        fit=solver.fit(y,lambda_=lam,mu=mu)
                        err=float(np.linalg.norm(fit-ref)/scale)
                        maxerr=float(np.max(np.abs(fit-ref)))
                        backward=native_kkt_error(y,fit,d,mu,lam,D)
                        status="valid" if err<=1e-6 else "inaccurate"
                        detail=""
                    except (ArithmeticError,ValueError,np.linalg.LinAlgError,
                            OverflowError,ImportError) as exc:
                        err=maxerr=backward=float("nan")
                        status="solver_failed"
                        detail=f"{type(exc).__name__}: {exc}"[:180]
                    rows.append(dict(n=n,d=d,mu=mu,seed=seed,s=target,
                        lambda_=lam,method=method,reference_digits=digits,
                        reference_kkt=kkt,reference_precision_agreement=agreement,
                        relative_forward_error=err,maximum_absolute_error=maxerr,
                        float64_kkt_backward_error=backward,status=status,
                        explanation=detail))
                print(f"QA d={d}, seed={seed}, S={target} completed",flush=True)
    csv_path=output/"high_d_forward_accuracy.csv"
    with csv_path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    counts={}
    for row in rows:
        key=row["method"]+":"+row["status"]
        counts[key]=counts.get(key,0)+1
    meta=dict(experiment="experiment006_high_d_forward_error_audit",
              created_utc=datetime.now(timezone.utc).isoformat(),platform=platform.platform(),
              python=sys.version,mpmath=mp.__version__,numpy=np.__version__,
              n=n,orders=list(orders),s_targets=list(levels),seeds=list(seeds),
              high_precision_digits=digits,rows=len(rows),status_counts=counts,
              elapsed_seconds=perf_counter()-started,
              source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              note=("Numerical accuracy compared to independent 85-digit "
                    "dual normal equations and 55-digit convergence check; "
                    "this is NOT statistical trend RMSE or a runtime ranking. "
                    "KKT residuals alone are not forward-error certificates."))
    (output/"metadata.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
    return rows,meta


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--digits",type=int,default=85)
    args=parser.parse_args()
    rows,meta=audit(args.output,digits=args.digits)
    print(json.dumps({k:meta[k] for k in
        ("rows","status_counts","elapsed_seconds")},indent=2))
