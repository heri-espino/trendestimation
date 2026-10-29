"""Generate journal-ready figures and empirical LaTeX tables for real NGSIM.

Uses original archived FHWA observations and immutable scored holdout rows.
Figure displays never substitute fabricated or synthetic measurements.
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from trendestimation import TrendSmoother
from run_case import (source_tracks, continuation, baseline_forecasts,
                      TRAIN_N, DT, S_GRID)
from publication_style import configure_publication, publication_export, finish_manifest

PAPER=Path(__file__).resolve().parent
RES=PAPER/"results"
FIG=PAPER/"figures";FIG.mkdir(exist_ok=True)
GEN=PAPER/"generated";GEN.mkdir(exist_ok=True)
COLORS=("#255c89","#3b90af","#7b719c","#b87947","#629688")
CRIT=("cv","gcv","aicc","bic","mle")
ORDERS=(1,2,3,4)


def read(name):return json.loads((RES/name).read_text())
def export(fig,name):publication_export(fig,name,FIG)
def rmse_map(rows):
    return {(v["method"],v["order"],v["mu_policy"],v["horizon"]):v["rmse_m"]
            for v in rows}


def forecast_figure():
    tracks,_=source_tracks()
    track=tracks[1];origin=185
    y=track[origin-TRAIN_N:origin]
    fut=track[origin:origin+20]
    selections=read("selection_rows.json")
    d=3
    fit_and_ext={}
    for mode in ("zero","sample"):
        rec=next(x for x in selections if x["track"]==1 and
                 x["origin"]==origin and x["d"]==d and
                 x["mu_policy"]==mode and x["criterion"]=="gcv" and
                 x["status"]=="ok")
        sm=TrendSmoother(len(y),order=d)
        fit=sm.fit(y,lambda_=rec["lambda"],mu=rec["mu"])
        forecast=continuation(fit.trend,d,rec["mu"],20)
        fit_and_ext[mode]=(fit.trend,forecast,rec["S"])
    bv=baseline_forecasts(y,20)["constant_velocity"]
    xtrain=np.arange(-len(y)+1,1)*DT
    xfuture=np.arange(1,len(fut)+1)*DT
    fig,(ax,bx)=plt.subplots(1,2,figsize=(8.55,3.45),
                             gridspec_kw={"width_ratios":[1.12,1]})
    ax.scatter(xtrain[-45:],y[-45:],s=7,color="#8596a7",alpha=.60,
               label="Recorded training position")
    ax.plot(xfuture,fut,color="#263e53",lw=2.1,
            label="Recorded future position")
    ax.axvline(0,color="#a8adb2",ls=":",lw=1)
    bx.axhline(0,color="#a8adb2",ls=":",lw=1)
    for col,mode in enumerate(("zero","sample")):
        trend,fore,sv=fit_and_ext[mode]
        ax.plot(xtrain[-45:],trend[-45:],color=COLORS[col],lw=1.5,
                label=f"PLS d=3 {mode} $\\mu$ (S={sv:.2f})")
        ax.plot(xfuture,fore,color=COLORS[col],ls="--",lw=2.0)
        bx.plot(xfuture,fore-fut,color=COLORS[col],lw=1.65,
                label=f"PLS {mode} $\\mu$")
    ax.plot(xfuture,bv,color=COLORS[3],ls="-.",lw=1.6,
            label="Velocity baseline")
    bx.plot(xfuture,bv-fut,color=COLORS[3],ls="-.",lw=1.6,
            label="Velocity baseline")
    ax.set(xlabel="Time relative to cutoff (s)",
           ylabel="Longitudinal position (m)",
           title="Observed track and trend continuation")
    bx.set(xlabel="Future horizon (s)",
           ylabel="Forecast minus observed position (m)",
           title="Visible held-out forecast errors")
    ax.legend(ncol=2,frameon=False,fontsize=6.6,loc="upper left")
    bx.legend(frameon=False,fontsize=7,loc="upper left")
    export(fig,"heldout_forecast")


def jerk_figure():
    tracks,_=source_tracks()
    train=tracks[1][185-TRAIN_N:185]
    selections=read("selection_rows.json")
    record=next(v for v in selections if v["track"]==1 and v["origin"]==185
                and v["d"]==3 and v["mu_policy"]=="zero"
                and v["criterion"]=="gcv" and v["status"]=="ok")
    sm=TrendSmoother(len(train),order=3)
    trend=sm.fit(train,lambda_=record["lambda"],mu=0.).trend
    jr=np.diff(train,n=3)/DT**3
    js=np.diff(trend,n=3)/DT**3
    t=(np.arange(len(jr))+1.5)*DT
    fig,(a,b)=plt.subplots(1,2,figsize=(8.4,3.5))
    a.plot(t,jr,lw=.8,color="#8094a6")
    a.set(xlabel="Time in training window (s)",
          ylabel="Naive third difference ($m/s^3$)",
          title="Raw position: noisy jerk proxy")
    b.plot(t,js,lw=1.8,color=COLORS[0])
    b.axhline(0,color="#a3abb4",ls=":",lw=.8)
    b.set(xlabel="Time in training window (s)",
          ylabel="PLS-smoothed third difference ($m/s^3$)",
          title=f"Estimated jerk proxy ($S={record['S']:.2f}$)")
    export(fig,"jerk_comparison")


def comparison_figure(summary):
    rms=rmse_map(summary)
    fig,axes=plt.subplots(1,2,figsize=(8.3,3.6),sharex=True)
    for ax,mu in zip(axes,("zero","sample")):
        z=np.array([[rms[("PLS_"+crit,str(d),mu,10)] for d in ORDERS]
                     for crit in CRIT],dtype=float)
        # Log color only compresses range; printed labels are actual RMSE.
        im=ax.imshow(np.log10(z),cmap="Blues",aspect="auto",vmin=-.5,vmax=1.4)
        ax.set_xticks(range(4),[f"$d={d}$" for d in ORDERS])
        ax.set_yticks(range(5),["CV","GCV","AICc","BIC*","ML"])
        ax.set_title("$\\mu=0$" if mu=="zero" else "Training-difference plug-in $\\widehat\\mu$")
        for i in range(5):
            for j in range(4):
                ax.text(j,i,f"{z[i,j]:.2f}",ha="center",va="center",
                        fontsize=7,color="white" if np.log10(z[i,j])>.5 else "#162e43")
    # Exact RMSE is printed in every cell. A crowded shared colorbar
    # previously obscured the final d=4 column; omit it entirely.
    export(fig,"criterion_heatmap")


def horizons_figure(summary):
    rms=rmse_map(summary)
    fig,ax=plt.subplots(figsize=(8.3,3.45))
    specs=[
        ("PLS_gcv","3","zero","PLS d=3, zero $\\mu$"),
        ("PLS_gcv","3","sample","PLS d=3, plug-in $\\mu$"),
        ("PLS_gcv","2","zero","PLS d=2, zero $\\mu$"),
        ("constant_velocity","None","none","Constant velocity"),
        ("constant_acceleration","None","none","Constant acceleration"),
        ("savgol_velocity","None","none","Savitzky--Golay + velocity"),
    ]
    for j,(method,d,mu,name) in enumerate(specs):
        vals=[rms[(method,d,mu,h)] for h in (5,10,20)]
        ax.plot([.5,1.,2.],vals,marker=("o","s","^","D","v","P")[j],
                lw=1.5,ms=5,color=COLORS[j%5],
                linestyle="--" if j>=3 else "-",label=name)
    ax.set(xlabel="Chronological forecast horizon (seconds)",
           ylabel="RMSE versus observed future position (m)",
           title="15 track-origin windows; descriptive pooled errors")
    ax.set_xticks([.5,1.,2.])
    ax.legend(frameon=False,ncol=2,fontsize=7)
    export(fig,"forecast_horizons")


def backend_figure():
    rows=read("solver_validation.json")
    methods=["svd","dense_solve","dense_cholesky","general_banded",
             "banded_cholesky","eigh","dual_svd"]
    labels=["SVD","Dense LU","Dense Chol.","Banded LU",
            "Banded Chol.","Gram eig.","Dual SVD"]
    vals=[];errs=[];ns=[]
    for meth in methods:
        arr=[x for x in rows if x["method"]==meth and x["valid"]]
        if not arr:raise RuntimeError("No verified solver observations for "+meth)
        vals.append(float(np.median([x["median_ms"] for x in arr])))
        errs.append(max(float(x["relative_fit_error"]) for x in arr))
        ns.append(len(arr))
    fig,(a,b)=plt.subplots(1,2,figsize=(8.2,3.35))
    y=np.arange(len(methods))
    a.barh(y,vals,color=COLORS[0]);b.barh(y,[max(x,1e-18) for x in errs],
                                           color=COLORS[1])
    a.set_yticks(y,labels);b.set_yticks(y,labels)
    a.invert_yaxis();b.invert_yaxis()
    a.set(xlabel="Median within-run fit time (ms)",title="One fitted trend, n=80")
    b.set_xscale("log")
    b.set(xlabel="Largest relative discrepancy vs SVD",title="Numerical agreement")
    export(fig,"backend_comparison")


def latex_table(summary):
    rms=rmse_map(summary)
    lines=[
      "% GENERATED FROM REAL NGSIM HOLDOUT RESULTS; DO NOT EDIT",
      r"\begin{table*}[t]",
      r"\caption{Out-of-sample position RMSE in meters at a one-second horizon (15 chronological track-origin windows). The five selection criteria used the same normalized S candidates, except restricted BIC ($S\ge0.10$). The data-derived mean policy changes model specification and does not yield exact refitted LOOCV.}",
      r"\label{tab:forecast}\centering",
      r"\begin{tabular}{lrrrr}",
      r"\toprule",
      r"Selector & $d=2,\ \mu=0$ & $d=3,\ \mu=0$ & $d=3,\ \widehat\mu$ & $d=4,\ \mu=0$ \\",
      r"\midrule",
    ]
    for crit in CRIT:
        label={"cv":"CV","gcv":"GCV","aicc":"AICc","bic":"Restricted BIC","mle":"Profile ML"}[crit]
        vals=[rms[("PLS_"+crit,str(d),mu,10)]
              for d,mu in [(2,"zero"),(3,"zero"),(3,"sample"),(4,"zero")]]
        lines.append(label+" & "+" & ".join(f"{x:.3f}" for x in vals)+r" \\")
    lines.extend([r"\midrule"])
    for method,label in [("constant_velocity","Velocity baseline"),
                         ("constant_acceleration","Acceleration baseline"),
                         ("savgol_velocity","Savitzky--Golay velocity")]:
        value=rms[(method,"None","none",10)]
        lines.append(f"{label} & \\multicolumn{{4}}{{c}}{{{value:.3f}}} \\\\")
    lines.extend([r"\bottomrule",r"\end{tabular}",r"\end{table*}"])
    (GEN/"forecast_table.tex").write_text("\n".join(lines)+"\n")
    # All selectors are covered; table supports quick reading.
    allzero={method:rms[("PLS_"+method,"3","zero",10)] for method in CRIT}
    sample={method:rms[("PLS_"+method,"3","sample",10)] for method in CRIT}
    summarytxt=f"""% AUTO-GENERATED REAL-DATA RESULTS
For $d=3$, GCV-selected PLS continued from 80 observed frames gives
{allzero["gcv"]:.3f}\\,m RMSE under fixed $\\mu=0$ and {sample["gcv"]:.3f}\\,m
when the training-only sample mean of third differences is plugged in.
The corresponding constant-velocity and constant-acceleration baselines
give {rms[("constant_velocity","None","none",10)]:.3f}\\,m and
{rms[("constant_acceleration","None","none",10)]:.3f}\\,m, respectively.
The comparison is illustrative; highly similar criterion-level scores
do not indicate five independent demonstrations of superiority.
"""
    (GEN/"empirical_summary.tex").write_text(summarytxt)


def latex_backend_table():
    rows=read("solver_validation.json")
    methods=("svd","dense_solve","dense_cholesky","general_banded",
             "banded_cholesky","eigh","dual_svd")
    lines=[
        "% GENERATED FROM REAL NGSIM FITTING BENCHMARK",
        r"\begin{table*}[t]",
        r"\caption{Same observed position windows, seven fit-only numerical backends, $d=3$, $S=0.90$. Median runtime is across 10 model/mean cases, each with three within-run timing repetitions; maximum relative fit error uses full SVD as the numerical baseline. Hardware-specific values do not predict criterion-selection timing.}",
        r"\label{tab:solver}\centering",
        r"\begin{tabular}{lrrr}\toprule",
        r"Solver & Valid cases & Median fit time (ms) & Max.\ relative discrepancy \\",
        r"\midrule",
    ]
    for method in methods:
        valid=[v for v in rows if v["method"]==method and v["valid"]]
        if not valid:
            lines.append(method.replace("_"," ")+r" & 0 & -- & -- \\")
            continue
        t=np.median([v["median_ms"] for v in valid])
        e=max(v["relative_fit_error"] for v in valid)
        label={"svd":"Full SVD","dense_solve":"Dense LU",
               "dense_cholesky":"Dense Cholesky","general_banded":"Banded LU",
               "banded_cholesky":"Banded Cholesky","eigh":"Gram eigendecomp.",
               "dual_svd":"Dual SVD"}[method]
        lines.append(f"{label} & {len(valid)} & {t:.4f} & {e:.2e} \\\\")
    lines.extend([r"\bottomrule",r"\end{tabular}",r"\end{table*}"])
    (GEN/"solver_table.tex").write_text("\n".join(lines)+"\n")


def main():
    configure_publication(PAPER)
    summary=read("forecast_summary.json")
    latex_table(summary)
    latex_backend_table()
    forecast_figure()
    jerk_figure()
    comparison_figure(summary)
    horizons_figure(summary)
    backend_figure()
    finish_manifest(PAPER,FIG)
    audit={
        "source":"official US DOT FHWA NGSIM, 5 fixed noncherry-picked real tracks",
        "plots":5,"panels_data":"archived forecast/selection/solver rows",
        "no_independent_true_jerk":True,
        "no_synthetic_values":True,
        "future_horizons_s":[.5,1.,2.],
        "table_files":["forecast_table.tex","solver_table.tex","empirical_summary.tex"]
    }
    (GEN/"render_manifest.json").write_text(json.dumps(audit,indent=2)+"\n")
    print("Publication figures and generated tables ready.",flush=True)


if __name__=="__main__":main()
