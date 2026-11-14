"""Experiment008: application-only TSVD vs PLS, spline and SG on frozen data.

SVD is a *distinct baseline* only when we truncate low-roughness
singular vectors: an untruncated SVD used to solve PLS is NOT a baseline.

No Experiment005/006/007 large scientific source is rerun; we read its
immutable clean/noisy simulated trajectories, official NGSIM episodes and
previously selected PLS lambda/mu from successful PC08 archives.

Run from repository root:
python paper/ngsim-jerk-case-study/experiments/experiment008/run.py \
  --mode synthetic --source <exp005 confirm/trajectories.jsonl.gz> \
  --selections <exp006 confirm/selections_rows.csv> \
  --output-dir <new append-only directory>
python .../run.py --mode real --source <exp004/data> \
  --selections <exp006 real/selections_rows.csv> \
  --output-dir <different append-only directory>
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np
from scipy.interpolate import make_smoothing_spline
from scipy.signal import savgol_filter
from scipy.special import binom

PAPER=Path(__file__).resolve().parents[2]
REPO=PAPER.parents[1]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(REPO/"src"))
sys.path.insert(0,str(HERE.parent/"experiment006"))
from trendestimation import TrendSmoother  # noqa: E402

spec=importlib.util.spec_from_file_location(
    "paper_c_exp006_exact_archive_loader",HERE.parent/"experiment006"/"run.py")
assert spec is not None and spec.loader is not None
archive=importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)
DT=0.1
N=80
H=(5,10,20)
D=3
METHODS=("pls_profileml_cubic_ols","tsvd_gcv_cubic_ols",
         "tsvd_matched_edf","cubic_spline_gcv","savitzky_golay_21_3")


def sha256(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(2**20),b""):
            h.update(block)
    return h.hexdigest()


class RoughnessSVD:
    """Orthonormal SVD basis for D3: retain LOW roughness modes.

    D=U diag(sigma) Vp.T, positive sigma sorted ASCENDING; the remaining
    d=3 V columns span the quadratic unpenalized nullspace. A retained
    penalized mode has TSVD filter 1, rejected mode filter 0, while PLS
    uses continuous filter 1/(1+lambda*sigma²).
    """

    def __init__(self,smoother):
        self.Dmat=np.asarray(smoother.D,dtype=float)
        _,singular,vt=np.linalg.svd(self.Dmat,full_matrices=True)
        self.n=self.Dmat.shape[1]
        self.m=self.Dmat.shape[0]
        self.d=self.n-self.m
        if self.d!=3:
            raise ValueError("Requires order-3 D")
        idx=np.argsort(singular)
        self.sigma=singular[idx]
        self.Vp=vt[idx].T
        self.V0=vt[self.m:].T
        if self.V0.shape!=(self.n,3):
            raise RuntimeError("SVD nullspace missing")
        if np.max(np.abs(self.Dmat@self.V0))>1e-9:
            raise RuntimeError("SVD quadratic nullspace validation failed")

    def particular(self,mu):
        return float(mu)*binom(np.arange(self.n,dtype=float),3)

    def fit(self,y,mu,rank):
        if not isinstance(rank,(int,np.integer)) or not(0<=rank<=self.m):
            raise ValueError("TSVD rank out of bounds")
        y=np.asarray(y,dtype=float)
        if y.shape!=(self.n,) or not np.isfinite(y).all():
            raise ValueError("Historical observations must have length n")
        p=self.particular(mu)
        centered=y-p
        null=self.V0@(self.V0.T@centered)
        return p+null+self.Vp[:,:rank]@(self.Vp[:,:rank].T@centered)

    def gcv_rank(self,y,mu):
        centered=np.asarray(y,dtype=float)-self.particular(mu)
        scores=self.Vp.T@centered
        # Residual squared norms of successively retained smallest
        # roughness singular vectors; all 3 nullspace modes always kept.
        trailing=np.cumsum(scores[::-1]**2)[::-1]
        n=self.n
        values=np.asarray([
            n*trailing[r]/(self.m-r)**2 for r in range(self.m)
        ],dtype=float)
        if not np.isfinite(values).all():
            raise ValueError("Nonfinite TSVD-GCV")
        return int(np.argmin(values)),float(np.min(values))

    def matched_rank(self,lam):
        if lam<0:
            raise ValueError("lambda must be nonnegative")
        if np.isinf(lam):
            return 0
        edf=float(np.sum(1/(1+lam*self.sigma**2)))
        return int(np.clip(np.rint(edf),0,self.m))

    def hat_diag(self,rank):
        return np.sum(self.V0**2,axis=1)+np.sum(self.Vp[:,:rank]**2,axis=1)


def saved_pls_selections(path):
    out={}
    with path.open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):
            if row["method"]!="plugin_global_ols_continuous":
                continue
            key=row["sample_id"]
            if key in out: raise ValueError("Duplicate archived PLS selection "+key)
            if row["status"]!="ok":
                raise ValueError("Archived ML source contains invalid PLS selection")
            out[key]={"lambda":float(row["lambda"]),
                      "mu":float(row["reference_mu_discrete_m"]),
                      "S":float(row["smoothness"])}
    return out


def fits(y,selection,smoother,tsvd):
    x=np.arange(N)*DT
    mu=selection["mu"]
    lam=selection["lambda"]
    trend_pls=np.asarray(smoother.fit(y,lambda_=lam,mu=mu).trend)
    rank_gcv,gcv_score=tsvd.gcv_rank(y,mu)
    rank_edf=tsvd.matched_rank(lam)
    trend_gcv=tsvd.fit(y,mu,rank_gcv)
    trend_edf=tsvd.fit(y,mu,rank_edf)
    trend_spline=np.asarray(make_smoothing_spline(x,y,lam=None)(x))
    trend_sg=np.asarray(savgol_filter(y,21,3,mode="interp"))
    data={
        "pls_profileml_cubic_ols":(trend_pls,mu,"",lam),
        "tsvd_gcv_cubic_ols":(trend_gcv,mu,rank_gcv,""),
        "tsvd_matched_edf":(trend_edf,mu,rank_edf,lam),
        "cubic_spline_gcv":(trend_spline,0.0,"",""),
        "savitzky_golay_21_3":(trend_sg,0.0,"",""),
    }
    assert set(data)==set(METHODS)
    return data,{"rank_gcv":rank_gcv,"rank_edf":rank_edf,"gcv":gcv_score}


def compare(episodes,selections,mode,source_hash,output,selection_hash):
    if output.exists():raise FileExistsError("Cannot overwrite "+str(output))
    if mode not in ("synthetic","real"):raise ValueError(mode)
    smoother=TrendSmoother(N,order=3)
    tsvd=RoughnessSVD(smoother)
    allrows=[]
    frows=[]
    idset={e["id"] for e in episodes}
    if idset != set(selections):
        raise ValueError("Archived selection IDs do not match exact episodes")
    for idx,e in enumerate(episodes):
        sid=e["id"]
        y=e["train"]
        past_truth=e["truth_train"]
        models,params=fits(y,selections[sid],smoother,tsvd)
        for method,(trend,mu,rank,lam) in models.items():
            if not np.isfinite(trend).all():raise ValueError(method+" nonfinite trend")
            row={
                "sample_id":sid,"site":e["site"],"stratum":e["stratum"],
                "method":method,"n_training":N,
                "reference_mu_discrete_m":mu,
                "lambda":lam,"rank_retained":rank,
                "effective_df":3+int(rank) if rank!="" else (
                    3+77*(1-selections[sid]["S"]) if method=="pls_profileml_cubic_ols"
                    else ""
                ),
                "S_equiv":(1-int(rank)/77) if rank!="" else
                    (selections[sid]["S"] if method=="pls_profileml_cubic_ols" else ""),
                "historical_position_mse_m2":(float(np.mean((trend-past_truth)**2))
                    if past_truth is not None else ""),
                "historical_jerk_mse_m2_s6":(
                    float(np.mean(((smoother.D@trend-smoother.D@past_truth)/DT**3)**2))
                    if past_truth is not None else ""
                ),
                "status":"ok",
            }
            allrows.append(row)
            for rule in ("local25","guerrero_last3"):
                pred=archive.continuation(trend,mu,rule,20)
                for h in H:
                    diff=pred[:h]-e["future"][:h]
                    if not np.isfinite(diff).all():raise ValueError("Nonfinite forecast")
                    frows.append({
                        "sample_id":sid,"site":e["site"],"stratum":e["stratum"],
                        "method":method,"continuation":rule,"horizon_frames":h,
                        "mse_m2":float(np.mean(diff**2)),
                        "mae_m":float(np.mean(np.abs(diff))),
                        "status":"ok",
                    })
        if (idx+1)%100==0:
            print(f"Experiment008 {mode}: {idx+1}/{len(episodes)} episodes",flush=True)
    import collections
    groups=collections.defaultdict(list)
    for row in allrows:
        if row["historical_jerk_mse_m2_s6"]!="":
            groups[(row["method"],"known_jerk")].append(float(row["historical_jerk_mse_m2_s6"]))
    for row in frows:
        groups[(row["method"],row["continuation"],int(row["horizon_frames"]))].append(float(row["mse_m2"]))
    summary=[]
    for k,values in sorted(groups.items()):
        if len(k)==2:
            method,_=k
            summary.append({"method":method,"target":"known_jerk",
                            "continuation":"","horizon_frames":"",
                            "n":len(values),"rmse":float(np.sqrt(np.mean(values))),
                            "unit":"m/s^3"})
        else:
            method,rule,h=k
            summary.append({"method":method,"target":"future_clean_position" if mode=="synthetic"
                            else "future_recorded_position",
                            "continuation":rule,"horizon_frames":h,"n":len(values),
                            "rmse":float(np.sqrt(np.mean(values))),"unit":"m"})
    output.mkdir(parents=True,exist_ok=False)
    def write(name,rows):
        p=output/name
        with p.open("x",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    write("fitted_rows.csv",allrows)
    write("forecast_rows.csv",frows)
    write("summary.csv",summary)
    text=[
        "# Experiment008: TSVD is a smoothing method, not an SVD solver timing benchmark",
        "",
        f"**Mode:** {mode}; **matched source windows:** {len(episodes)}.",
        "Every numeric candidate used only the first 80 historical positions.",
        "",
        "| Method | Target | Continuation | Horizon (frames) | RMSE | Units |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for r in summary:
        text.append(f"| {r['method']} | {r['target']} | {r['continuation']} | "
                    f"{r['horizon_frames']} | {r['rmse']:.6f} | {r['unit']} |")
    text+=["","## Interpretation and limitations",
          "- PLS smoothing and TSVD spectral truncation use the SAME d=3 difference basis.",
          "- SVD full factorization alone is NOT a method; hard spectral truncation is.",
          "- TSVD-GCV selects retained rank from training-only in-sample GCV.",
          "- TSVD-matched-EDF uses the PLS archived EDF, so it is NOT an independently",
          "  optimized alternative; it isolates soft versus hard shrinkage at matched complexity.",
          "- The cubic reference mean and PLS lambda were frozen in Experiment006; they",
          "  were NOT re-estimated here. Other methods see the same historical observations.",
          "- True physical jerk is known only for synthetic clean trajectories.",
          "- Real NGSIM future camera-recorded positions are not independent clean truth.",
          "- Same-trajectory overlapping horizons and five coarse recording-session blocks",
          "  do not support population-level independent-sample claims.",
          "- Do not use this as a computational backend/time comparison.",
          ""]
    (output/"RESULTS.md").write_text("\n".join(text),encoding="utf-8")
    manifest={
      "experiment":"experiment008","status":"complete","mode":mode,
      "n_samples":len(episodes),"n_fitted_rows":len(allrows),
      "n_forecast_rows":len(frows),"n_methods":len(METHODS),
      "reference":"global cubic OLS mu and lambda selected from archived Experiment006",
      "source_sha256":source_hash,"selection_rows_sha256":selection_hash,
      "source_commit":os.environ.get("GITHUB_SHA","manual"),
      "output_dir":str(output.resolve()),"runner":os.environ.get("RUNNER_NAME","manual"),
      "n_synthetic_with_known_truth":sum(x["truth_train"] is not None for x in episodes),
      "d":3,"dt_seconds":DT,
      "tsvd":"hard cutoff of ascending singular values of D3, retain quadratic nullspace",
      "tsvd_gcv":"training-only rank minimization, exclude interpolating r=m",
      "tsvd_matched_edf":"rank round(sum 1/(1+lambda*sigma_j^2)), lambda from same archived PLS",
      "continuations":["local25","guerrero_last3"],
    }
    (output/"run_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print((output/"RESULTS.md").read_text()[:14000],flush=True)
    return manifest


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--mode",required=True,choices=["synthetic","real"])
    a.add_argument("--source",required=True,type=Path)
    a.add_argument("--selections",required=True,type=Path)
    a.add_argument("--output-dir",required=True,type=Path)
    args=a.parse_args()
    if args.mode=="synthetic":
        episodes,h=archive.load_synthetic(args.source,"confirm")
    else:
        episodes,h=archive.load_real(args.source)
    selected=saved_pls_selections(args.selections)
    compare(episodes,selected,args.mode,h,args.output_dir,sha256(args.selections))


if __name__=="__main__":
    main()
