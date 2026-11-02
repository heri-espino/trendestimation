"""Experiment006 high-order QA: independent 85-digit truth and forward errors.

Not a performance ranking. Never count a fitted series as correct solely
because a double-precision KKT residual is below a fixed threshold.

Run: python paper/benchmarks/experiment006/audit_high_d.py --output DIR
Uses Python standard-library decimal; no additional package installation.
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

from decimal import Decimal, localcontext
import numpy as np
from scipy.linalg import cho_solve_banded

from trendestimation import TrendSmoother, PreparedPLSSolver
from selected_inverse import BandedTrace
from run import sample


def _decimal_linear_solve(matrix, vector):
    """Small dense Gaussian elimination in exact user-selected precision."""
    size=len(vector)
    a=[list(row)+[v] for row,v in zip(matrix,vector)]
    for i in range(size):
        pivot=max(range(i,size),key=lambda j:abs(a[j][i]))
        if a[pivot][i]==0:
            raise ArithmeticError("Singular constrained polynomial projection")
        a[i],a[pivot]=a[pivot],a[i]
        scale=a[i][i]
        for col in range(i,size+1):
            a[i][col]/=scale
        for j in range(i+1,size):
            weight=a[j][i]
            for col in range(i,size+1):
                a[j][col]-=weight*a[i][col]
    sol=[Decimal(0)]*size
    for i in range(size-1,-1,-1):
        sol[i]=a[i][size]-sum(
            (a[i][j]*sol[j] for j in range(i+1,size)),Decimal(0))
    return sol


def high_precision_reference(y,d,mu,lam,digits=85):
    """Independent dual banded solve entirely in decimal arithmetic.

    Only Python's standard-library decimal module is needed. Inputs are
    fixed float64 observations, mu and lambda converted exactly by
    Decimal.from_float. No user-package or system installation.
    """
    with localcontext() as context:
        context.prec=digits
        n=len(y)
        m=n-d
        coeff=[(-1)**(d-j)*math.comb(d,j) for j in range(d+1)]
        obs=[Decimal.from_float(float(v)) for v in y]
        mean=Decimal.from_float(float(mu))
        zero=Decimal(0)
        if np.isposinf(lam):
            # D tau=mu, polynomial nullspace basis binomial(t,k), k<d.
            B=[[Decimal(math.comb(i,k)) for k in range(d)]
               for i in range(n)]
            centered=[obs[i]-mean*math.comb(i,d) for i in range(n)]
            gram=[[sum((B[i][j]*B[i][k] for i in range(n)),zero)
                   for k in range(d)] for j in range(d)]
            rhs=[sum((B[i][j]*centered[i] for i in range(n)),zero)
                 for j in range(d)]
            coef=_decimal_linear_solve(gram,rhs)
            result=[mean*math.comb(i,d)+sum(
                (B[i][k]*coef[k] for k in range(d)),zero)
                for i in range(n)]
        else:
            penalty=Decimal.from_float(float(lam))
            drhs=[sum((coeff[j]*obs[i+j] for j in range(d+1)),zero)-mean
                  for i in range(m)]
            band=[Decimal((-1)**k*math.comb(2*d,d-k))
                  for k in range(d+1)]
            alpha=1/penalty
            lower=[[zero for _ in range(d+1)] for _ in range(m)]
            for i in range(m):
                lower[i][0]=(band[0]+alpha-sum(
                    (lower[i][i-k]**2 for k in range(max(0,i-d),i)),
                    zero)).sqrt()
                for j in range(i+1,min(m,i+d+1)):
                    subtotal=sum((
                        lower[j][j-k]*lower[i][i-k]
                        for k in range(max(0,j-d),i)
                        if i-k<=d and j-k<=d),zero)
                    lower[j][j-i]=(band[j-i]-subtotal)/lower[i][0]
            forward=[]
            for i in range(m):
                forward.append((drhs[i]-sum((
                    lower[i][i-j]*forward[j]
                    for j in range(max(0,i-d),i)),zero))/lower[i][0])
            u=[zero]*m
            for i in range(m-1,-1,-1):
                u[i]=(forward[i]-sum((
                    lower[j][j-i]*u[j]
                    for j in range(i+1,min(i+d+1,m))),zero)
                    )/lower[i][0]
            result=obs.copy()
            for i in range(m):
                for j in range(d+1):
                    result[i+j]-=coeff[j]*u[i]
        difference_residual=[
            sum((coeff[j]*result[i+j] for j in range(d+1)),zero)-mean
            for i in range(m)]
        if np.isfinite(lam):
            kkt=[result[i]-obs[i] for i in range(n)]
            for i in range(m):
                for j in range(d+1):
                    kkt[i+j]+=penalty*coeff[j]*difference_residual[i]
            residual=float(max(abs(v) for v in kkt))
        else:
            residual=float(max(abs(v) for v in difference_residual))
        return np.array([float(v) for v in result]),residual


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
              python=sys.version,decimal_digits=digits,numpy=np.__version__,
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
