"""Reproducible real-vehicle PLS jerk case study and out-of-sample forecasts.

Inputs are ONLY the archived unmodified FHWA NGSIM raw position subset.
Selected five tracks are fixed by fetch_ngsim.py BEFORE seeing errors.
No simulated trajectories/noise and no random train/test splits.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import linalg
from scipy.signal import savgol_filter
from scipy.special import binom
from trendestimation import TrendSmoother, score_lambda

PAPER=Path(__file__).resolve().parent
DATA=PAPER/"data"
RESULTS=PAPER/"results"
RESULTS.mkdir(exist_ok=True)
DT=.1
TRAIN_N=80
ORIGINS=(95,140,185)
HORIZONS=(5,10,20)
ORDERS=(1,2,3,4)
CRITERIA=("cv","gcv","aicc","bic","mle")
S_GRID=np.array([0,.05,.1,.2,.3,.4,.5,.6,.7,.8,.9,.95,.975,.99,.995,1.])
MU_POLICIES=("zero","sample")
FT_M=0.3048


def source_tracks():
    path=DATA/"ngsim_us101_selected_raw_positions.csv"
    if not path.is_file():raise RuntimeError("Real FHWA subset absent; never synthesize.")
    provenance=json.loads((DATA/"provenance.json").read_text())
    raw_bytes=path.read_bytes()
    actual=hashlib.sha256(raw_bytes).hexdigest()
    canonical_crlf=hashlib.sha256(raw_bytes.replace(b"\r\n",b"\n").replace(b"\n",b"\r\n")).hexdigest()
    if provenance["subset_sha256"] not in (actual,canonical_crlf):
        raise RuntimeError("FHWA subset checksum changed beyond Git newline normalization.")
    groups=defaultdict(list)
    with path.open() as f:
        for r in csv.DictReader(f):
            groups[int(r["track_number"])].append((
                int(r["global_time_ms"]), float(r["longitudinal_m"])
            ))
    tracks={}
    for no,items in sorted(groups.items()):
        items.sort()
        t=np.array([r[0] for r in items],dtype=np.int64)
        y=np.array([r[1] for r in items],dtype=float)
        if len(y)<max(ORIGINS)+max(HORIZONS) or np.any(np.diff(t)!=100):
            raise RuntimeError(f"Track {no} not long/regular enough")
        tracks[no]=y-y[0]
    assert len(tracks)==5
    return tracks,provenance


def continuation(trend, order, mu, horizon):
    """Extrapolate only a LOCAL polynomial of fitted trend near cutoff.

    For D_d tau=mu, tau is polynomial of degree d-1 plus mu*binom(t,d).
    Least-squares over last 25 smoothed points estimates polynomial
    boundary conditions; this extension is NOT the PLS training fit.
    """
    n=len(trend)
    i=np.arange(n,dtype=float)
    futuro=np.arange(n,n+horizon,dtype=float)
    ref=mu*binom(i,order)
    future_ref=mu*binom(futuro,order)
    k=min(25,n)
    x=np.arange(-k+1,1,dtype=float)*DT
    predx=np.arange(1,horizon+1,dtype=float)*DT
    p=np.polynomial.Polynomial.fit(x,(trend-ref)[-k:],deg=order-1).convert()
    return np.asarray(p(predx)+future_ref,dtype=float)


def polynomial_baseline(y, horizon, degree, window):
    k=min(window,len(y))
    x=np.arange(-k+1,1,dtype=float)*DT
    poly=np.polynomial.Polynomial.fit(x,y[-k:],deg=degree).convert()
    return np.asarray(poly(np.arange(1,horizon+1)*DT),dtype=float)


def baseline_forecasts(y,h):
    sg=savgol_filter(y,window_length=21,polyorder=3,mode="interp")
    return {
        "constant_velocity":polynomial_baseline(y,h,1,20),
        "constant_acceleration":polynomial_baseline(y,h,2,30),
        "savgol_velocity":polynomial_baseline(sg,h,1,20),
    }


def prepare_solvers():
    models={}
    for d in ORDERS:
        smoother=TrendSmoother(TRAIN_N,order=d)
        penalties=[smoother.lambda_for_smoothness(float(s))
                   for s in S_GRID]
        for s,lam in zip(S_GRID,penalties):
            if np.isfinite(lam) and not np.isclose(smoother.smoothness(lam),s,
                                                   rtol=0,atol=1e-7):
                raise RuntimeError(f"Smoothness inversion failed: {d,s}")
        models[d]=(smoother,penalties)
    return models


def choose(smoother, y, penalties, mu, criterion):
    scores=[]
    for s,lam in zip(S_GRID,penalties):
        if criterion=="bic" and s<.1:
            scores.append(np.inf);continue
        try:
            value=score_lambda(smoother,y,lambda_=float(lam),
                               criterion=criterion,mu=float(mu))
        except (FloatingPointError,ValueError,OverflowError,np.linalg.LinAlgError):
            value=np.inf
        scores.append(value if np.isfinite(value) else np.inf)
    scores=np.array(scores)
    if not np.any(np.isfinite(scores)):
        return None
    k=int(np.argmin(scores))
    return k,float(scores[k])


def run_forecasts():
    tracks,provenance=source_tracks()
    models=prepare_solvers()
    records=[]
    illustration=None
    selections=[]
    for track_no,y in tracks.items():
        for origin in ORIGINS:
            train=y[origin-TRAIN_N:origin]
            for d,(smoother,penalties) in models.items():
                data_mu=float(np.mean(np.diff(train,n=d)))
                for policy in MU_POLICIES:
                    mu=0. if policy=="zero" else data_mu
                    for criterion in CRITERIA:
                        answer=choose(smoother,train,penalties,mu,criterion)
                        if answer is None:
                            selections.append({"track":track_no,"origin":origin,
                                "d":d,"mu_policy":policy,"criterion":criterion,
                                "status":"no_finite_score"})
                            continue
                        k,score=answer
                        lam=float(penalties[k])
                        fit=smoother.fit(train,lambda_=lam,mu=mu)
                        selections.append({"track":track_no,"origin":origin,
                            "d":d,"mu_policy":policy,"criterion":criterion,
                            "status":"ok","S":float(S_GRID[k]),
                            "lambda":lam,"score":score,"mu":mu})
                        for h in HORIZONS:
                            truth=y[origin:origin+h]
                            forecast=continuation(fit.trend,d,mu,h)
                            finite=np.all(np.isfinite(forecast))
                            mse=float(np.mean((truth-forecast)**2)) if finite else np.nan
                            mae=float(np.mean(np.abs(truth-forecast))) if finite else np.nan
                            records.append({"track":track_no,"origin":origin,
                                "horizon":h,"method":f"PLS_{criterion}",
                                "criterion":criterion,"order":d,"mu_policy":policy,
                                "S":float(S_GRID[k]),"mse":mse,"mae":mae,
                                "valid":bool(finite)})
                            if illustration is None and track_no==1 and origin==185 \
                               and d==3 and policy=="zero" and criterion=="gcv":
                                illustration={"train":train.tolist(),
                                    "holdout":y[origin:origin+20].tolist(),
                                    "trend":fit.trend.tolist(),
                                    "S":float(S_GRID[k]),"mu":mu,
                                    "forecast":continuation(fit.trend,d,mu,20).tolist(),
                                    "track":track_no,"origin":origin,
                                    "dt":DT,"criterion":"GCV", "order":d}
            for method,forecast in baseline_forecasts(train,max(HORIZONS)).items():
                for h in HORIZONS:
                    truth=y[origin:origin+h]
                    pred=forecast[:h]
                    records.append({"track":track_no,"origin":origin,
                       "horizon":h,"method":method,"criterion":"baseline",
                       "order":None,"mu_policy":"none","S":None,
                       "mse":float(np.mean((truth-pred)**2)),
                       "mae":float(np.mean(np.abs(truth-pred))),
                       "valid":True})
    if illustration is None:raise RuntimeError("Illustrative track missing")
    (RESULTS/"holdout_predictions.json").write_text(json.dumps(illustration,indent=2)+"\n")
    (RESULTS/"forecast_rows.json").write_text(json.dumps(records,indent=2,allow_nan=False)+"\n")
    (RESULTS/"selection_rows.json").write_text(json.dumps(selections,indent=2)+"\n")
    summary=[]
    keys=sorted({(str(r["method"]),str(r["order"]),str(r["mu_policy"]),r["horizon"])
                 for r in records})
    for method,d,mu,h in keys:
        rows=[r for r in records if r["method"]==method
              and str(r["order"])==d and str(r["mu_policy"])==mu
              and r["horizon"]==h and r["valid"]]
        n_total=sum(1 for r in records if r["method"]==method
              and str(r["order"])==d and str(r["mu_policy"])==mu
              and r["horizon"]==h)
        if not rows:continue
        summary.append({"method":method,"order":d,"mu_policy":mu,"horizon":h,
            "n_evaluated":len(rows),"n_total":n_total,
            "rmse_m":float(np.sqrt(np.mean([x["mse"] for x in rows]))),
            "mae_m":float(np.mean([x["mae"] for x in rows]))})
    (RESULTS/"forecast_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("Folds",len(tracks)*len(ORIGINS), "records",len(records),
          "selected",len(selections),flush=True)
    return tracks,models,summary,illustration


def backend_validation(tracks,models):
    """Seven real-position numerical pathways; one fixed 0.9 S, not grid scoring."""
    n=TRAIN_N;I=np.eye(n)
    d=3
    smoother,penalties=models[d]
    k=int(np.flatnonzero(np.isclose(S_GRID,.9))[0]);lam=float(penalties[k])
    D=smoother.D
    Q=D.T@D
    from scipy.linalg import cholesky_banded, cho_solve_banded,cho_factor,cho_solve
    # Lower band storage ab[j,col] = A[col+j,col].
    lb=np.zeros((d+1,n))
    for j in range(d+1):
        lb[j,:n-j]=np.diag(Q,k=-j)
    rows=[]
    for tr,yall in tracks.items():
        y=yall[ORIGINS[0]-n:ORIGINS[0]]
        for mode in MU_POLICIES:
            mu=0. if mode=="zero" else float(np.mean(np.diff(y,n=d)))
            rhs=y+lam*mu*(D.T@np.ones(n-d))
            ref=smoother.fit(y,lambda_=lam,mu=mu).trend
            for name in ("svd","dense_solve","dense_cholesky","general_banded",
                         "banded_cholesky","eigh","dual_svd"):
                try:
                    def solve():
                        if name=="svd":return smoother.fit(y,lambda_=lam,mu=mu).trend
                        if name=="dense_solve":return np.linalg.solve(I+lam*Q,rhs)
                        if name=="dense_cholesky":
                            f=cho_factor(I+lam*Q,lower=True,check_finite=False)
                            return cho_solve(f,rhs,check_finite=False)
                        if name=="general_banded":
                            ab=np.zeros((2*d+1,n))
                            for ii in range(n):
                                for jj in range(max(0,ii-d),min(n,ii+d+1)):
                                    ab[d+ii-jj,jj]=float(ii==jj)+lam*Q[ii,jj]
                            return linalg.solve_banded((d,d),ab,rhs,check_finite=False)
                        if name=="banded_cholesky":
                            ab=lam*lb.copy()
                            ab[0]+=1
                            f=cholesky_banded(ab,lower=True,check_finite=False)
                            return cho_solve_banded((f,True),rhs,check_finite=False)
                        if name=="eigh":
                            ev,U=np.linalg.eigh(Q)
                            # Reference shift prevents treating near-zero numerical eigenvalues as physical penalty.
                            ev=np.maximum(ev,0)
                            return U@((U.T@rhs)/(1+lam*ev))
                        if name=="dual_svd":
                            u,s,vh=linalg.svd(D,full_matrices=False)
                            v=vh.T
                            w=lam*s*s/(1+lam*s*s)
                            return y-v@(w*(v.T@y)-mu*(w/s)*(u.T@np.ones(n-d)))
                        raise AssertionError(name)
                    measurements=[]
                    pred=None
                    for _ in range(3):
                        t0=time.perf_counter()
                        pred=solve()
                        measurements.append(time.perf_counter()-t0)
                    err=float(np.linalg.norm(pred-ref)/max(np.linalg.norm(ref),1e-12))
                    rows.append({"track":tr,"mu_policy":mode,"method":name,
                        "S":float(S_GRID[k]),"d":d,"median_ms":float(np.median(measurements)*1000),
                        "relative_fit_error":err,"valid":bool(np.isfinite(err))})
                except Exception as exc:
                    rows.append({"track":tr,"mu_policy":mode,"method":name,
                        "S":float(S_GRID[k]),"d":d,"valid":False,
                        "reason":type(exc).__name__})
    (RESULTS/"solver_validation.json").write_text(json.dumps(rows,indent=2)+"\n")
    return rows


def main():
    tracks,models,summary,illustration=run_forecasts()
    backends=backend_validation(tracks,models)
    result={
        "source":"FHWA NGSIM US-101, raw 10Hz recorded longitudinal positions",
        "data_not_simulated":True,"tracks":len(tracks),
        "n_train":TRAIN_N,"origins":list(ORIGINS),
        "horizons":list(HORIZONS),"orders":list(ORDERS),
        "criteria":list(CRITERIA),"mu_policies":list(MU_POLICIES),
        "s_grid":S_GRID.tolist(),"bics_min_S":0.1,
        "holdout_target":"future measured location (no latent trend ground truth)",
        "n_forecast_records":sum(int(x["n_evaluated"]) for x in summary),
        "solver_records":len(backends),
        "interpretation":"PLS extrapolation by local polynomial extension; not package native forecast API",
        "limitations":"overlapping track origins, no p values; plug-in mu conditional criterion not exact reestimated LOOCV; no ground truth jerk"
    }
    (RESULTS/"run_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2),flush=True)

if __name__=="__main__":main()
