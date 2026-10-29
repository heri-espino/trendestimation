"""Experiment004: matched S-grid latent-trend RMSE pilot and numerical QA.

Standalone implementation of the formulas in trendestimation.core,
trendestimation.criteria and trendestimation.likelihood for independent
reproducibility. Run from repo root after installing numpy and scipy:

    python paper/benchmarks/experiment004/run_pilot.py --out paper/benchmarks/experiment004/runs/<unique-id>

Never overwrite results. Experimental results do not assert predictive RMSE.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from scipy.linalg import svd, cholesky_banded, cho_solve_banded
from scipy.optimize import brentq
from scipy.special import expit, binom
from threadpoolctl import threadpool_limits, threadpool_info

CRITERIA = ("cv", "gcv", "aicc", "bic", "mle")
ORDERS = (1, 2, 3, 4, 5, 6)
S_GRID = np.unique(np.r_[np.arange(100) / 100.0,
     .995, .999, .9995, .9999, .99999, .999999, 1 - 1e-8,
     1 - 1e-10, 1 - 1e-12, 1.0])
QA_TARGETS = (.01, .5, .9, .99, .999, .999999, 1-1e-8, 1-1e-12)


def difference_matrix(n, d):
    from math import comb
    D = np.zeros((n-d, n))
    rows = np.arange(n-d)
    for j in range(d+1):
        D[rows, rows+j] = (-1.)**(d-j) * comb(d, j)
    return D


def inverse_s_grid(delta):
    logs = np.log(delta)
    out = np.empty(len(S_GRID))
    out[0], out[-1] = 0., np.inf
    max_relative_tail_error = 0.
    for i, s in enumerate(S_GRID[1:-1], 1):
        high = s > .5
        tail = 1-s if high else s
        logit = math.log(s) - math.log1p(-s)
        lo, hi = logit - float(logs.max()) - 2., logit - float(logs.min()) + 2.
        if high:
            objective = lambda x: (1-s)-float(np.mean(expit(-x-logs)))
        else:
            objective = lambda x: float(np.mean(expit(x+logs)))-s
        root = brentq(objective, lo, hi, xtol=1e-12)
        out[i] = math.exp(root)
        realized_tail = float(np.mean(expit(-root-logs) if high else expit(root+logs)))
        max_relative_tail_error = max(max_relative_tail_error, abs(realized_tail-tail)/tail)
    return out, max_relative_tail_error


def prepare(n,d):
    D = difference_matrix(n,d)
    _, singular, vh = svd(D, full_matrices=True, check_finite=True)
    delta = singular**2
    if not np.all(delta > 0):
        raise ArithmeticError(f"Numerical rank deficient at n={n} d={d}")
    U = vh[:n-d,:].T.copy()
    lambdas, inv_error = inverse_s_grid(delta)
    z = np.log(lambdas[1:-1,None]) + np.log(delta)[None,:]
    w = np.zeros((len(S_GRID),n-d))
    w[1:-1] = expit(z)
    w[-1] = 1.
    return dict(n=n,d=d,D=D,delta=delta,U=U,U2=U*U,
                lambdas=lambdas,w=w,inv_error=inv_error)


def reference(n,d,mu):
    return mu * binom(np.arange(n,dtype=float),d)


def score_all(model,y,mu):
    n,d=model['n'],model['d']
    U,U2,w,delta,lambdas = (model[k] for k in ('U','U2','w','delta','lambdas'))
    z = U.T @ (y-reference(n,d,mu))
    # row = smoothness candidate, column = penalized eigen-coordinate
    wz = w*z[None,:]
    rss=np.sum(wz*wz,axis=1)
    edf=n-np.sum(w,axis=1)
    out={}
    # Exact fixed-mu classical LOOCV: residual_i / (1-h_ii).
    # At S=0 this is undefined, not the limiting quotient.
    # Scale very-small lambda by lambda to avoid 0/0 underflow.
    u=U@wz.T
    v=U2@w.T
    with np.errstate(divide='ignore',invalid='ignore',over='ignore'):
        loo=u/v
        cv=np.mean(loo*loo,axis=0)
    cv[0]=np.inf
    cv[~np.isfinite(cv)]=np.inf
    out['cv']=cv
    den=1-edf/n
    with np.errstate(divide='ignore',invalid='ignore'):
        gcv=(rss/n)/(den**2)
    gcv[0]=np.inf
    gcv[~np.isfinite(gcv)]=np.inf
    out['gcv']=gcv
    eps=np.finfo(float).eps*max(1.,float(z@z))
    good=rss>eps
    logmean=np.full(len(S_GRID), np.inf)
    logmean[good]=np.log(rss[good]/n)
    bic=logmean+edf*np.log(n)/n
    bic[~np.isfinite(bic)]=np.inf
    out['bic']=bic
    aicc=logmean.copy()
    valid=(n-edf-2)>0
    aicc[valid]+=((2*edf[valid]+1)/(n-edf[valid]-2))
    aicc[~valid]=np.inf
    aicc[~np.isfinite(aicc)]=np.inf
    out['aicc']=aicc
    # Profiled Gaussian marginal likelihood over positive spectral subspace.
    logc=np.logaddexp(0.,-np.log(lambdas[1:-1,None])-np.log(delta)[None,:])
    weighted=np.sum(z[None,:]**2*np.exp(-logc),axis=1)
    ml=np.full(len(S_GRID),np.inf)
    okay=weighted>0
    ml[1:-1][okay]=(n-d)*np.log(weighted[okay]/(n-d))+np.sum(logc[okay],axis=1)
    atinf=float(z@z)
    if atinf>0:
        ml[-1]=(n-d)*math.log(atinf/(n-d))
    out['mle']=ml
    return out,z


def truth(n,kind):
    t=np.linspace(0,1,n)
    if kind=='smooth':
        return .5*t + .4*np.sin(2*np.pi*t) + .15*np.cos(4*np.pi*t)
    if kind=='kink':
        return .4*t + .8*np.maximum(t-.52,0) - .2*np.maximum(t-.82,0)
    raise ValueError(kind)


def noise(n,kind,rng):
    e=rng.standard_normal(n)
    if kind=='iid':
        return .30*e
    if kind=='ar1':
        phi=.65
        out=np.empty(n)
        out[0]=e[0]
        for i in range(1,n):out[i]=phi*out[i-1]+math.sqrt(1-phi**2)*e[i]
        return .30*out
    raise ValueError(kind)


def numerical_qa(model,y,mu,outputs,policy):
    """Independent banded factor, H diagonal, determinant QA; never hide fails."""
    n,d=model['n'],model['d']
    D,U,w,lambdas=model['D'],model['U'],model['w'],model['lambdas']
    ref=reference(n,d,mu)
    coords=U.T@(y-ref)
    from math import comb
    stencil=np.asarray([(-1.)**(d-j)*comb(d,j) for j in range(d+1)])
    qb=np.zeros((d+1,n))
    for row in range(n-d):
        for a in range(d+1):
            for b in range(a,d+1):
                qb[b-a,row+a]+=stencil[a]*stencil[b]
    details=[]
    for s in QA_TARGETS:
        j=int(np.argmin(abs(S_GRID-s)))
        lam=float(lambdas[j])
        record=dict(n=n,d=d,mu_policy=policy,s=float(S_GRID[j]),lambda_=lam,
                    error='',status='unknown',fit_relative_error='',cv_relative_error='',
                    gcv_relative_error='',mle_relative_error='',spectral_norm='')
        spectral=y-U@(w[j]*coords)
        record['spectral_norm']=float(np.linalg.norm(spectral))
        bands=lam*qb.copy(); bands[0,:]+=1.
        try:
            L=cholesky_banded(bands,lower=True,check_finite=False)
            fitted=ref+cho_solve_banded((L,True),y-ref,check_finite=False)
            rel=float(np.linalg.norm(fitted-spectral)/max(1.,np.linalg.norm(spectral)))
            record['fit_relative_error']=rel
            record['status']='ok' if rel<=1e-5 else 'disagreement'
            # Full inverse for small n only, deliberately outside all timing.
            if n<=64 and s in (.01,.5,.9):
                H=cho_solve_banded((L,True),np.eye(n),check_finite=False)
                edf=float(np.trace(H));residual=y-fitted
                diag=np.diag(H)
                cv=float(np.mean((residual/(1-diag))**2))
                gcv=float((residual@residual/n)/(1-edf/n)**2)
                record['cv_relative_error']=float(abs(cv-outputs['cv'][j])/max(1.,abs(outputs['cv'][j])))
                record['gcv_relative_error']=float(abs(gcv-outputs['gcv'][j])/max(1.,abs(outputs['gcv'][j])))
                # Determinant identity: log det marginal covariance on the
                # penalized subspace = log det A - sum(log(lambda*delta)).
                logdetA=2*float(np.log(L[0]).sum())
                logdetpos=float(np.log(lam*model['delta']).sum())
                quad=float((y-ref)@residual)
                if quad>0:
                    mle=(n-d)*np.log(quad/(n-d)) +logdetA-logdetpos
                    record['mle_relative_error']=float(abs(mle-outputs['mle'][j])/max(1.,abs(outputs['mle'][j])))
        except (np.linalg.LinAlgError,ValueError,OverflowError,FloatingPointError) as e:
            record['status']='factorization_failed'
            record['error']=type(e).__name__
        details.append(record)
    return details


def write_csv(path,rows):
    if not rows:raise ValueError('Empty rows')
    with path.open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def run(out,seeds):
    if out.exists():raise FileExistsError(f'Never overwrite an existing run: {out}')
    out.mkdir(parents=True)
    results=[];qa=[];mapping=[]
    t0=perf_counter()
    with threadpool_limits(limits=1):
        for n in (64,128):
            for d in ORDERS:
                model=prepare(n,d)
                mapping.append(dict(n=n,d=d,grid_size=len(S_GRID),
                                    largest_finite_lambda=float(model['lambdas'][-2]),
                                    inverse_max_relative_tail_error=float(model['inv_error']),
                                    smallest_positive_eigenvalue=float(model['delta'].min()),
                                    largest_positive_eigenvalue=float(model['delta'].max())))
                for kind in ('smooth','kink'):
                    actual=truth(n,kind)
                    for err in ('iid','ar1'):
                        for seed in range(seeds):
                            rng=np.random.default_rng(np.random.SeedSequence([20261028,n,seed,0 if kind=='smooth' else 1,0 if err=='iid' else 1]))
                            y=actual+noise(n,err,rng)
                            for policy in ('fixed_zero','observed_difference'):
                                mu=0. if policy=='fixed_zero' else float(np.mean(model['D']@y))
                                scores,z=score_all(model,y,mu)
                                # Oracle is computed from true latent trend for *every* available S.
                                residuals=(model['U']@(model['w']*z[None,:]).T).T
                                estimates=y[None,:]-residuals
                                errors=np.sqrt(np.mean((estimates-actual[None,:])**2,axis=1))
                                oracle=int(np.argmin(errors))
                                for criterion in CRITERIA:
                                    values=scores[criterion]
                                    valid=np.isfinite(values)
                                    selected=int(np.argmin(np.where(valid,values,np.inf))) if valid.any() else -1
                                    results.append(dict(n=n,d=d,shape=kind,noise=err,seed=seed,mu_policy=policy,
                                        mu_value=mu,criterion=criterion,selection_status='ok' if selected>=0 else 'no_finite_score',
                                        selected_s=float(S_GRID[selected]) if selected>=0 else '',
                                        selected_lambda=float(model['lambdas'][selected]) if selected>=0 else '',
                                        selected_score=float(values[selected]) if selected>=0 else '',
                                        trend_rmse=float(errors[selected]) if selected>=0 else '',
                                        oracle_rmse=float(errors[oracle]),oracle_s=float(S_GRID[oracle]),
                                        excess_rmse=float(errors[selected]-errors[oracle]) if selected>=0 else '',
                                        finite_scores=int(valid.sum())))
                                if seed==0 and kind=='smooth' and err=='iid':
                                    qa.extend(numerical_qa(model,y,mu,scores,policy))
    write_csv(out/'pilot_rmse.csv',results)
    write_csv(out/'numerical_qa.csv',qa)
    write_csv(out/'mapping_qa.csv',mapping)
    elapsed=perf_counter()-t0
    # Correctness first: no silent acceptance of large differences at moderate S.
    report=dict(study='experiment004',run_kind='RMSE+QA pilot',
        created_utc=datetime.now(timezone.utc).isoformat(),
        independent_seeds_per_configuration=seeds,elapsed_seconds=elapsed,
        grid_size=len(S_GRID),n=[64,128],d=list(ORDERS),
        trend_shapes=['smooth','kink'],noise=['iid','ar1'],
        mu_policies=['fixed_zero','observed_difference'],criteria=list(CRITERIA),
        python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
        machine=platform.platform(),cpu=platform.processor(),threadpools=threadpool_info(),
        rows=len(results),qa_rows=len(qa),
        experimental_notes=['RMSE is in-sample latent-trend recovery, not forecasting.',
        'Mean(D_d y) is conditional plug-in, not exact adaptive CV, EDF or joint MLE.',
        'd=0 excluded by design.',
        'Spectral solver is shared for all criteria and fixed/observed-difference mean.',
        'No actual self-hosted runner timing was performed.'],
        max_mapping_tail_error=max(x['inverse_max_relative_tail_error'] for x in mapping),
        max_qa_fit_relative_error=max(float(x['fit_relative_error']) for x in qa if x['fit_relative_error']!=''),
        max_qa_gcv_relative_error=max(float(x['gcv_relative_error']) for x in qa if x['gcv_relative_error']!=''),
        qa_status_counts={st:sum(r['status']==st for r in qa) for st in sorted({r['status'] for r in qa})})
    (out/'environment.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
    for filename in ('pilot_rmse.csv','numerical_qa.csv','mapping_qa.csv'):
        report[filename+'_sha256']=hashlib.sha256((out/filename).read_bytes()).hexdigest()
    (out/'environment.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
    print(json.dumps({k:report[k] for k in ('rows','qa_rows','elapsed_seconds','grid_size','max_mapping_tail_error','max_qa_fit_relative_error','max_qa_gcv_relative_error')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--seeds',type=int,default=20)
    args=parser.parse_args()
    if args.seeds<1:parser.error('--seeds must be >=1')
    run(args.out,args.seeds)
