"""Render only source-backed Experiment008 scientific benchmark figures.

Uses immutable completed Experiment008 synthetic and real summary CSV plus
the previously archived Experiment006 real spline-Taylor benchmark.
No new fitting/selection of any smoothing method occurs here.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    import awesomefigures as af
    af.set_style("elegante",palette="okabe-ito",font="DejaVu Sans",
                 use_tex=False,rasterize=False)
except ImportError as e:
    raise ImportError("Existing AwesomeFigures is needed for manuscript visuals") from e

BLUE="#27679a";ORANGE="#c07532";CYAN="#3796ae";VIOLET="#76669f";INK="#19344c";GRAY="#8593a1"
NAMES={
  "pls_profileml_cubic_ols":"PLS, profile ML",
  "tsvd_matched_edf":"SVD, matched complexity",
  "tsvd_gcv_cubic_ols":"SVD, GCV rank",
  "cubic_spline_gcv":"Smoothing spline, GCV",
  "savitzky_golay_21_3":"Savitzky--Golay",
}
C={"pls_profileml_cubic_ols":BLUE,"tsvd_matched_edf":ORANGE,
   "tsvd_gcv_cubic_ols":VIOLET,"cubic_spline_gcv":CYAN,"savitzky_golay_21_3":GRAY}
ORDER=list(NAMES)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"pdf.fonttype":42,
                     "svg.fonttype":"none","axes.spines.right":False,
                     "axes.spines.top":False,"axes.titleweight":"bold",
                     "figure.facecolor":"white"})

def read(path):
    with path.open(encoding="utf-8",newline="") as h:
        return list(csv.DictReader(h))

def hash_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):
            h.update(b)
    return h.hexdigest()

def build(sim,real,archived,out):
    if not out.is_dir():raise FileNotFoundError(out)
    names=("exp008_known_jerk_benchmarks","exp008_real_forecast_benchmarks")
    for name in names:
        for suf in ("pdf","png","svg"):
            if (out/(name+"."+suf)).exists():
                raise FileExistsError(f"Refusing to overwrite derived figure {name}.{suf}")
    simrows=read(sim)
    realrows=read(real)
    oldrows=read(archived)
    def lookup(rows,method,target,rule="",horizon=""):
        got=[r for r in rows if r["method"]==method and
             r["target"]==target and r["continuation"]==rule and
             str(r["horizon_frames"])==str(horizon)]
        if len(got)!=1:raise ValueError(f"Missing matching outcome: {method} {target} {rule} {horizon}")
        return float(got[0]["rmse"])
    jerks=[lookup(simrows,m,"known_jerk") for m in ORDER]
    future=[lookup(simrows,m,"future_clean_position","local25",10) for m in ORDER]
    fig,(a,b)=plt.subplots(1,2,figsize=(7.15,2.95),
                           gridspec_kw={"width_ratios":[1,1.03]})
    x=np.arange(len(ORDER))
    colors=[C[m] for m in ORDER]
    a.bar(x,jerks,color=colors,width=.7)
    a.set_yscale("log")
    a.set_ylim(.7,1000)
    a.set(ylabel="Historical jerk RMSE (m/s³)",
          title="A. Recovering known synthetic jerk")
    b.bar(x,future,color=colors,width=.7)
    b.set(ylabel="1-s clean-position RMSE (m)",
          title="B. Forecasting clean synthetic position")
    b.set_ylim(0,max(future)*1.3)
    for ax,values in ((a,jerks),(b,future)):
        ax.set_xticks(x,[NAMES[k].replace(", ","\n") for k in ORDER],
                      rotation=22,ha="right",fontsize=6.7)
        ax.grid(axis="y",alpha=.15);ax.set_axisbelow(True)
        for i,v in enumerate(values):
            ax.text(i,v*(1.1 if ax is a else 1.03),f"{v:.2f}",
                    ha="center",va="bottom",fontsize=6.5,color=INK)
    fig.subplots_adjust(left=.08,bottom=.34,right=.98,top=.84,wspace=.29)
    save(fig,out,names[0])

    fig,ax=plt.subplots(figsize=(7.15,3.0))
    t=np.array([.5,1,2])
    for m in ORDER:
        vals=[lookup(realrows,m,"future_recorded_position",
                    "guerrero_last3",h) for h in (5,10,20)]
        ax.plot(t,vals,lw=1.9,marker="o",ms=5,color=C[m],label=NAMES[m])
    ref=[]
    for h in (5,10,20):
        data=[r for r in oldrows if r["method"]=="archived:spline_gcv_taylor2"
              and int(r["horizon_frames"])==h]
        if len(data)!=1:raise ValueError("Missing archived GCV spline quadratic Taylor")
        ref.append(float(data[0]["rmse_m"]))
    ax.plot(t,ref,color=INK,ls="--",lw=1.9,marker="D",
            label="GCV spline, quadratic Taylor")
    ax.set(xticks=t,xticklabels=["0.5","1","2"],xlabel="Future horizon (s)",
           ylabel="Future recorded-position RMSE (m)",
           title="Recorded NGSIM trajectories: 200 episodes, identical historical cutoffs")
    ax.set_ylim(0,2.65)
    ax.grid(alpha=.15);ax.set_axisbelow(True)
    ax.legend(frameon=False,ncol=3,loc="upper left",fontsize=7)
    fig.subplots_adjust(left=.095,bottom=.18,right=.98,top=.87)
    save(fig,out,names[1])
    return names

def save(fig,out,name):
    for fmt in ("pdf","svg","png"):
        fig.savefig(out/(name+"."+fmt),dpi=220 if fmt=="png" else 130,
                    format=fmt,bbox_inches="tight",pad_inches=.08)
    plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--synthetic",required=True,type=Path)
    p.add_argument("--real",required=True,type=Path)
    p.add_argument("--exp006-real",required=True,type=Path)
    p.add_argument("--figures",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    a=p.parse_args()
    if a.manifest.exists():raise FileExistsError(a.manifest)
    names=build(a.synthetic,a.real,a.exp006_real,a.figures)
    out={"status":"success","plots":{},
         "sources":{str(v):hash_file(v) for v in
           (a.synthetic,a.real,a.exp006_real)}}
    for name in names:
        out["plots"][name]={ext:{"sha256":hash_file(a.figures/(name+"."+ext)),
                                  "bytes":(a.figures/(name+"."+ext)).stat().st_size}
                            for ext in ("pdf","png","svg")}
    a.manifest.parent.mkdir(parents=True,exist_ok=True)
    a.manifest.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))
if __name__=="__main__":
    main()
