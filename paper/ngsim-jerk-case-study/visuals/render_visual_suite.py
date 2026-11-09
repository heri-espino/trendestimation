"""Publication vector graphics for Paper C: Experiments006 and 007.

Read-only from immutable completed results archives. The script neither
regenerates Monte Carlo simulations nor changes any underlying estimates.
All figures retain PNG and editable SVG previews plus journal PDF vectors.

On a Windows runner with old results branches checked out as worktrees:
  python paper/ngsim-jerk-case-study/visuals/render_visual_suite.py
      --exp007-confirm <archived-exp007>/confirm
      --exp006-confirm <archived-exp006>/confirm
      --exp006-real <archived-exp006>/real
      --exp007-config paper/ngsim-jerk-case-study/experiments/experiment007/config.json
      --out-dir paper/ngsim-jerk-case-study/figures
      --manifest paper/ngsim-jerk-case-study/generated/visual_suite_manifest.json
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

PAPER = Path(__file__).resolve().parents[1]
REPO = PAPER.parents[1]
sys.path.insert(0, str(REPO / "src"))
from trendestimation import TrendSmoother  # noqa: E402

# Respect the source paper's existing AwesomeFigures editorial design.
# The output remains ordinary edit-ready SVG and vector PDF rather than
# forcing fragile PDF-to-PGF retypesetting or installing new fonts.
import awesomefigures as af  # noqa: E402
af.set_style("elegante", palette="okabe-ito", font="DejaVu Sans",
             use_tex=False, rasterize=False)

INK="#19344c"
BLUE="#27679a"
CYAN="#3796ae"
ORANGE="#c07532"
VIOLET="#76669f"
GRAY="#8593a1"
LIGHT="#e0e8ee"
ORDER=("known_mu_reml","joint_reml","global_ols_plugin_mle","gcv_zero_mu")
LABEL={
    "known_mu_reml":"Known reference (control)",
    "joint_reml":"Joint REML",
    "global_ols_plugin_mle":"Cubic OLS + profile ML",
    "gcv_zero_mu":"GCV, zero reference",
    "fixed_zero_continuous":"Zero reference + ML",
    "plugin_global_ols_continuous":"Cubic OLS + ML",
    "plugin_sample_continuous":"Raw sample mean + ML",
    "joint_reml_continuous":"Joint REML",
    "joint_reml_grid":"Joint REML, 15-S grid",
}
COLOR={
    "known_mu_reml":GRAY,"joint_reml":BLUE,
    "global_ols_plugin_mle":ORANGE,"gcv_zero_mu":VIOLET
}
FILES=("exp007_jerk_example","exp007_spectral_interpretation",
       "exp007_calibration","exp007_interventions",
       "exp007_misspecification","exp006_reconstruction_forecasting")

plt.rcParams.update({
    "font.family":"DejaVu Sans",
    "font.size":8.4,
    "axes.labelsize":8.5,
    "axes.titlesize":9.3,
    "axes.titleweight":"bold",
    "xtick.labelsize":7.6,
    "ytick.labelsize":7.6,
    "legend.fontsize":7.4,
    "figure.facecolor":"white",
    "axes.facecolor":"white",
    "savefig.facecolor":"white",
    "pdf.fonttype":42,
    "ps.fonttype":42,
    "svg.fonttype":"none",
    "axes.spines.top":False,
    "axes.spines.right":False,
    "axes.titlepad":8,
})
plt.rcParams["axes.prop_cycle"]=plt.cycler(color=[BLUE,CYAN,ORANGE,VIOLET,GRAY])


def load_csv(path:Path):
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))


def hash_path(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()


def typography(ax):
    ax.tick_params(axis="both",length=2.6,width=.7)
    ax.grid(alpha=.13,linewidth=.65,axis="y",zorder=0)
    ax.set_axisbelow(True)


def panel(ax,text):
    ax.text(-.08,1.035,text,transform=ax.transAxes,
            weight="bold",size=10.5,color=INK,va="bottom")


def publish(fig,name,out):
    fig.savefig(out/(name+".pdf"),format="pdf",
                facecolor="white",bbox_inches="tight",pad_inches=.08)
    fig.savefig(out/(name+".svg"),format="svg",
                facecolor="white",bbox_inches="tight",pad_inches=.08)
    fig.savefig(out/(name+".png"),dpi=240,format="png",
                facecolor="white",bbox_inches="tight",pad_inches=.08)
    plt.close(fig)


def jerk_example(trials,selections,out):
    # Fixed in advance, not selected by a good outcome: iid/iid,
    # confirm replicate 0, sigma_j=2m/s3, sigma_e=0.05m.
    trial_id="confirm_000010"
    with gzip.open(trials,"rt",encoding="utf-8") as f:
        record=None
        for line in f:
            item=json.loads(line)
            if item["trial_id"]==trial_id:
                record=item
                break
    if record is None:
        raise RuntimeError("Missing fixed example trial "+trial_id)
    assert (record["dynamics"]=="iid" and record["noise_type"]=="iid"
            and float(record["sigma_e_m"])==.05
            and float(record["sigma_j_m_s3"])==2.0)
    selected=[r for r in selections
              if r["trial_id"]==trial_id and r["method"]=="global_ols_plugin_mle"]
    if len(selected)!=1 or selected[0]["status"]!="ok":
        raise RuntimeError("Missing frozen fitted parameters for example")
    chosen=selected[0]
    observed=np.asarray(record["observed_position_m"],dtype=float)
    clean=np.asarray(record["true_position_m"],dtype=float)
    jerk=np.asarray(record["true_discrete_jerk_m_s3"],dtype=float)
    dt=.1
    smoother=TrendSmoother(len(observed),order=3)
    trend=smoother.fit(
        observed,lambda_=float(chosen["lambda"]),
        mu=float(chosen["mu_discrete_m"])
    ).trend
    raw=np.diff(observed,n=3)/dt**3
    fitted=np.diff(trend,n=3)/dt**3
    t=np.arange(len(observed))*dt
    jtime=(np.arange(len(jerk))+1.5)*dt
    fig,axes=plt.subplots(1,3,figsize=(7.25,2.6),
                          gridspec_kw={"width_ratios":[1.12,1,1]})
    axes[0].plot(t,clean,color=INK,lw=2,label="True")
    axes[0].scatter(t[::3],observed[::3],s=8,color=GRAY,alpha=.8,
                    label="Observed",zorder=2)
    axes[0].plot(t,trend,color=BLUE,lw=1.4,ls="--",label="PLS")
    axes[0].set(xlabel="Time (s)",ylabel="Position (m)",
                title="Recorded and latent position")
    axes[0].legend(frameon=False,loc="upper left",fontsize=6.4)
    axes[1].plot(jtime,raw,color=GRAY,lw=.75,label="Raw third difference")
    axes[1].axhline(0,color=INK,lw=.6,alpha=.45)
    axes[1].set(xlabel="Time (s)",ylabel="Jerk proxy (m/s³)",
                title="Direct differentiation")
    axes[2].plot(jtime,jerk,color=INK,lw=1.7,label="True jerk")
    axes[2].plot(jtime,fitted,color=BLUE,lw=1.4,
                 label="PLS-recovered jerk")
    axes[2].set(xlabel="Time (s)",ylabel="Jerk (m/s³)",
                title="Regularized jerk")
    axes[2].legend(frameon=False,loc="upper left",fontsize=6.4)
    for tag,ax in zip("ABC",axes):
        panel(ax,tag)
        typography(ax)
    fig.subplots_adjust(left=.055,right=.99,bottom=.23,top=.82,wspace=.37)
    publish(fig,"exp007_jerk_example",out)
    return {"trial_id":trial_id,"case":"iid/iid, sigma_e=0.05m, sigma_j=2m/s3",
            "method":"global_ols_plugin_mle",
            "source_fitted_lambda":float(chosen["lambda"]),
            "source_fitted_S":float(chosen["S_selected"]),
            "truth_max_abs_residual_m":float(np.max(np.abs(
                np.diff(clean,n=3)/dt**3-jerk
            )))}


def spectral_figure(config,out):
    smoother=TrendSmoother(80,order=3)
    eig=np.asarray(smoother.eigenvalues[:77],dtype=float)
    ratio=(.05/(.1**3*2))**2
    weights=ratio*eig/(1+ratio*eig)
    sort=np.sort(weights)
    S=float(np.mean(weights))
    fig,(a,b)=plt.subplots(1,2,figsize=(7.25,2.6),
                            gridspec_kw={"width_ratios":[1.05,1]})
    a.plot(np.arange(1,78),sort,color=BLUE,lw=2.1)
    a.fill_between(np.arange(1,78),sort,alpha=.13,color=BLUE)
    a.axhline(S,color=ORANGE,ls="--",lw=1.4,
              label=f"Average $S={S:.3f}$")
    a.set(xlabel="Ranked penalized spectral mode",
          ylabel="Observation-noise fraction",
          ylim=(-.04,1.045),
          title="Variance attribution by spectral mode")
    a.legend(frameon=False,loc="lower right")
    vals=np.linspace(0,1,201)
    df=80-77*vals
    b.plot(vals,df,color=BLUE,lw=2.2,label="Fixed reference mean")
    b.axhline(3,color=GRAY,ls=":",lw=1)
    b.annotate("Quadratic nullspace\n(3 degrees of freedom)",
               xy=(.99,3),xytext=(.43,22),size=7,
               arrowprops={"arrowstyle":"->","color":GRAY})
    b.set(xlabel="Normalized smoothness index $S$",
          ylabel="Conditional effective degrees of freedom",
          xlim=(0,1),ylim=(0,83),
          title="Interpretation as model complexity")
    for tag,ax in zip("AB",(a,b)):
        panel(ax,tag);typography(ax)
    fig.subplots_adjust(left=.09,right=.98,bottom=.22,top=.84,wspace=.31)
    publish(fig,"exp007_spectral_interpretation",out)


def calibration_figure(cells,out):
    fig,axes=plt.subplots(1,2,figsize=(7.25,3.05),sharex=True,sharey=True)
    for ax,noise in zip(axes,("iid","ar1")):
        for method in ("joint_reml","global_ols_plugin_mle","gcv_zero_mu"):
            sub=[r for r in cells
                 if r["dynamics"]=="iid" and r["noise_type"]==noise
                 and r["method"]==method]
            if len(sub)!=9:
                raise RuntimeError(f"Missing exact nine theoretical cells: {noise}/{method}")
            ax.scatter(
                [float(r["true_S_covariance"]) for r in sub],
                [float(r["mean_S"]) for r in sub],
                color=COLOR[method],s=23,marker={
                    "joint_reml":"o","global_ols_plugin_mle":"s",
                    "gcv_zero_mu":"^"
                }[method],alpha=.82,
                label=LABEL[method],zorder=3
            )
        ax.plot([0,1],[0,1],ls="--",color=INK,lw=1.1,
                label="Ideal calibration")
        ax.set(xlim=(0,1.01),ylim=(0,1.01),
               xlabel="Known true covariance noise fraction",
               title=("Independent observation noise" if noise=="iid"
                      else "Serially correlated observation noise"))
        typography(ax)
    axes[0].set_ylabel("Mean selected normalized smoothness $S$")
    axes[1].legend(loc="lower right",frameon=False,fontsize=6.4)
    panel(axes[0],"A");panel(axes[1],"B")
    fig.subplots_adjust(left=.092,right=.99,bottom=.19,top=.86,wspace=.16)
    publish(fig,"exp007_calibration",out)


def intervention_figure(effects,out):
    # Compare all 9 paired dynamics/noise regimes for joint REML.
    sub=[r for r in effects if r["method"]=="joint_reml"]
    dynamics=("iid","ar1","sign_reversal")
    noises=("iid","ar1","last_point_outlier")
    keys=[(d,n) for d in dynamics for n in noises]
    lookup={(r["dynamics"],r["noise_type"],r["intervention"]):r for r in sub}
    fig,axes=plt.subplots(1,2,figsize=(7.25,4.0),sharey=True)
    names={"iid":"IID","ar1":"AR(1)","sign_reversal":"Reversal",
           "last_point_outlier":"Outlier"}
    y=np.arange(len(keys))
    for ax,intervention,ttl in zip(axes,
           ("noise_increase","jerk_variability_increase"),
           ("Raise measurement-noise SD","Raise true jerk-volatility SD")):
        for i,(d,n) in enumerate(keys):
            r=lookup[(d,n,intervention)]
            z=float(r["mean_delta_selected_S"])
            lo=float(r["ci_95_low_cluster"])
            hi=float(r["ci_95_high_cluster"])
            tru=float(r["mean_delta_true_S"])
            ax.errorbar(
                z,i,xerr=np.array([[z-lo],[hi-z]]),
                fmt="o",capsize=2.3,ms=4.2,color=BLUE,
                ecolor=BLUE,lw=1.1,zorder=2
            )
            ax.scatter(tru,i,marker="D",s=20,facecolors="white",
                       edgecolors=ORANGE,linewidths=1,zorder=3)
        ax.axvline(0,color=GRAY,ls=":",lw=.8)
        ax.set(xlabel="Change in normalized $S$",title=ttl)
        ax.invert_yaxis()
        typography(ax)
    axes[0].set_yticks(y,[f"{names[d]} jerk / {names[n]} noise" for d,n in keys],
                        fontsize=7.0)
    axes[1].tick_params(labelleft=False)
    axes[1].legend(handles=[
        Line2D([0],[0],marker="o",color=BLUE,linestyle="",
               label="Estimated change (95% parent CI)"),
        Line2D([0],[0],marker="D",color=ORANGE,
               markerfacecolor="white",linestyle="",label="Theoretical change")
    ],loc="lower left",frameon=False,fontsize=6.3)
    for tag,ax in zip("AB",axes):
        panel(ax,tag)
    fig.subplots_adjust(left=.25,right=.985,bottom=.16,top=.86,wspace=.16)
    publish(fig,"exp007_interventions",out)


def robustness_figure(cal,out):
    dyn=("iid","ar1","sign_reversal")
    noise=("iid","ar1","last_point_outlier")
    methods=("joint_reml","global_ols_plugin_mle")
    fig,axes=plt.subplots(1,2,figsize=(7.25,3.15))
    allcells=np.zeros((2,3,3))
    for k,method in enumerate(methods):
        for i,d in enumerate(dyn):
            for j,n in enumerate(noise):
                matches=[r for r in cal if r["method"]==method
                         and r["dynamics"]==d and r["noise_type"]==n]
                if len(matches)!=1:
                    raise RuntimeError("Missing noise sensitivity cell "+str((method,d,n)))
                allcells[k,i,j]=float(matches[0]["mae_S"])
    mx=max(.12,float(np.max(allcells)))
    for k,ax in enumerate(axes):
        image=ax.imshow(allcells[k],vmin=0,vmax=mx,cmap="Blues",aspect="auto")
        ax.set_xticks(range(3),["IID","AR(1)","Outlier"])
        ax.set_yticks(range(3),["IID","AR(1)","Reversal"])
        ax.set(xlabel="Observation-error structure",
               title=LABEL[methods[k]])
        for i in range(3):
            for j in range(3):
                v=allcells[k,i,j]
                ax.text(j,i,f"{v:.3f}",ha="center",va="center",
                        fontsize=8,weight="bold",
                        color="white" if v>.65*mx else INK)
        panel(ax,"AB"[k])
        ax.tick_params(length=0)
    cbar=fig.colorbar(image,ax=axes.ravel().tolist(),fraction=.04,pad=.02)
    cbar.set_label("Calibration MAE of normalized $S$")
    fig.subplots_adjust(left=.125,right=.87,bottom=.18,top=.83,wspace=.32)
    publish(fig,"exp007_misspecification",out)


def exp006_tradeoff(confirm,real,out):
    jerk=load_csv(confirm/"known_jerk_summary.csv")
    sim=load_csv(confirm/"summary.csv")
    obs=load_csv(real/"summary.csv")
    names=(
        ("plugin_global_ols_continuous","Cubic OLS\n+ profile ML"),
        ("fixed_zero_continuous","Zero reference\n+ profile ML"),
        ("joint_reml_continuous","Joint REML"),
        ("joint_reml_grid","Joint REML\n15-S grid"),
        ("plugin_sample_continuous","Raw mean\n+ profile ML"),
    )
    jerkmap={r["method"]:float(r["known_discrete_jerk_rmse_m_s3"])
             for r in jerk if r["horizon_frames"]=="all"}
    def forecast_map(rows):
        return {(r["method"],int(r["horizon_frames"])):float(r["rmse_m"])
                for r in rows}
    simval=forecast_map(sim);realval=forecast_map(obs)
    def key(method):
        return method+"_local25"
    fig,axes=plt.subplots(1,3,figsize=(7.25,3.25))
    x=np.arange(len(names))
    vals=[
        [jerkmap[n] for n,l in names],
        [simval[(key(n),10)] for n,l in names],
        [realval[(key(n),10)] for n,l in names],
    ]
    titles=(
        "Recover known historical jerk\n(1,296 simulated trials)",
        "Predict clean future position\n(1,296 simulated trials)",
        "Predict recorded future position\n(200 NGSIM episodes)",
    )
    units=("Jerk RMSE (m/s³)","1-s position RMSE (m)","1-s position RMSE (m)")
    colors=[ORANGE,BLUE,CYAN,VIOLET,GRAY]
    for i,ax in enumerate(axes):
        ax.bar(x,vals[i],color=colors,width=.72,zorder=2,alpha=.92)
        ax.set_xticks(x,[n for m,n in names],rotation=43,ha="right",fontsize=6.3)
        ax.set(ylabel=units[i],title=titles[i])
        for j,v in enumerate(vals[i]):
            ax.text(j,v+max(vals[i])*.02,f"{v:.2f}",ha="center",va="bottom",
                    fontsize=6.5,color=INK)
        ax.set_ylim(0,max(vals[i])*1.22)
        panel(ax,"ABC"[i]);typography(ax)
    # Observed NGSIM favors the spline at 1 s; report directly rather than
    # hiding the best established benchmark from the visual story.
    spline=realval.get(("archived:spline_gcv_taylor2",10))
    if spline is not None:
        axes[2].axhline(spline,color=INK,ls="--",lw=1.1)
        axes[2].text(.02,spline+.035,
                     f"GCV spline: {spline:.2f} m",
                     fontsize=6.6,color=INK,
                     transform=axes[2].get_yaxis_transform())
    fig.subplots_adjust(left=.065,right=.997,bottom=.31,top=.79,wspace=.37)
    publish(fig,"exp006_reconstruction_forecasting",out)
    return {"synthetic_jerk_rmse":jerkmap,"spline_ngsim_1s_rmse":spline}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exp007-confirm",type=Path,required=True)
    p.add_argument("--exp006-confirm",type=Path,required=True)
    p.add_argument("--exp006-real",type=Path,required=True)
    p.add_argument("--exp007-config",type=Path,default=PAPER/"experiments/experiment007/config.json")
    p.add_argument("--out-dir",type=Path,default=PAPER/"figures")
    p.add_argument("--manifest",type=Path,default=PAPER/"generated/visual_suite_manifest.json")
    a=p.parse_args()
    src={
        "exp007_selections":a.exp007_confirm/"selections.csv",
        "exp007_trials":a.exp007_confirm/"trials.jsonl.gz",
        "exp007_cells":a.exp007_confirm/"per_cell.csv",
        "exp007_effects":a.exp007_confirm/"effects_summary.csv",
        "exp007_calibration":a.exp007_confirm/"calibration_summary.csv",
        "exp007_manifest":a.exp007_confirm/"run_manifest.json",
        "exp006_jerk":a.exp006_confirm/"known_jerk_summary.csv",
        "exp006_synthetic_forecast":a.exp006_confirm/"summary.csv",
        "exp006_real_forecast":a.exp006_real/"summary.csv",
        "exp006_manifest":a.exp006_confirm/"run_manifest.json",
        "exp007_frozen_config":a.exp007_config,
    }
    source_hashes={k:{"path":str(v.resolve()),"sha256":hash_path(v)}
                   for k,v in src.items()}
    m7=json.loads(src["exp007_manifest"].read_text(encoding="utf-8"))
    m6=json.loads(src["exp006_manifest"].read_text(encoding="utf-8"))
    if (m7["n_trials"]!=1944 or m7["n_selection_rows"]!=7776
         or m7["status"]!="complete"
         or m6["n_samples"]!=1296 or m6["status"]!="completed"):
        raise ValueError("Scientific source is not the verified complete experiment")
    if a.manifest.exists():
        raise FileExistsError("Publication figure manifest already exists; use a fresh checkout")
    a.out_dir.mkdir(parents=True,exist_ok=True)
    a.manifest.parent.mkdir(parents=True,exist_ok=True)
    for name in FILES:
        for extension in (".pdf",".svg",".png"):
            if (a.out_dir/(name+extension)).exists():
                raise FileExistsError("Refusing to overwrite prior figure asset: "+name+extension)
    rows=load_csv(src["exp007_selections"])
    cells=load_csv(src["exp007_cells"])
    effect=load_csv(src["exp007_effects"])
    cal=load_csv(src["exp007_calibration"])
    if len(rows)!=7776 or len(cells)!=324 or len(effect)!=108 or len(cal)!=36:
        raise ValueError("Archived complete Experiment007 calibration records missing")
    example=jerk_example(src["exp007_trials"],rows,a.out_dir)
    spectral_figure(json.loads(a.exp007_config.read_text(encoding="utf-8")),a.out_dir)
    calibration_figure(cells,a.out_dir)
    intervention_figure(effect,a.out_dir)
    robustness_figure(cal,a.out_dir)
    tradeoff=exp006_tradeoff(a.exp006_confirm,a.exp006_real,a.out_dir)
    files={
        name:{
            extension:{"relative_path":f"figures/{name}.{extension}",
                       "sha256":hash_path(a.out_dir/(name+"."+extension)),
                       "bytes":(a.out_dir/(name+"."+extension)).stat().st_size}
            for extension in ("pdf","svg","png")
        }
        for name in FILES
    }
    manifest={
        "schema":1,"paper":"Paper C NGSIM CAS two-column",
        "status":"rendered_verified",
        "renderer":"matplotlib with pinned AwesomeFigures elegant Okabe-Ito style",
        "journal_asset_policy":"Vector PDF in LaTeX, editable SVG plus 240-dpi PNG previews",
        "scientific_source_sha256":source_hashes,
        "example":example,"tradeoff":tradeoff,
        "n_new_multipanel_figures":len(FILES),
        "no_new_scientific_experiment":True,
        "no_observation_or_truth_fabrication":True,
        "model_correct_scope":"independent Gaussian jerk and observation noise",
        "figure_files":files,
    }
    a.manifest.write_text(json.dumps(manifest,indent=2,allow_nan=False)+"\n",
                          encoding="utf-8")
    print("Rendered "+str(len(FILES))+" reproducible multipanel figure sets.",
          flush=True)


if __name__=="__main__":
    main()
