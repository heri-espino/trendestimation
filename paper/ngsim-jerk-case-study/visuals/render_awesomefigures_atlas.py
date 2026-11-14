"""AwesomeFigures atlas of *archived* Paper C scientific outcomes.

Never generates trajectories, reselects smoothing parameters or downloads NGSIM.
Reads Experiment008 (synthetic fitted/summary and real episode forecasts),
Experiment007 (calibration cell/effect/robustness summaries) and Experiment006
(known jerk reference-policy summary). All inputs originate from immutable
results-only Git branches mounted by the Windows publishing workflow.

Examples:
  python render_awesomefigures_atlas.py --exp008-synthetic-fitted ... \
    --exp008-synthetic-summary ... --exp008-real-forecasts ... \
    --exp007-cells ... --exp007-calibration ... --exp007-effects ... \
    --exp006-jerk ... --out-dir ... --manifest ...

Output: ten named PDF/SVG/PNG vector/scalable/preview triplets and exact
source/output SHA-256 inventory. Nothing is overwritten without explicit
--replace-owned, which is confined to the ten atlas filenames.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import awesomefigures as af
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

PAPER = Path(__file__).resolve().parents[1]
STEMS = (
    "atlas_known_jerk_regimes",
    "atlas_tsvd_rank_pathology",
    "atlas_paired_jerk_losses",
    "atlas_method_tradeoff",
    "atlas_ngsim_by_site",
    "atlas_ngsim_paired_delta",
    "atlas_spectral_calibration_grid",
    "atlas_misspecification_matrix",
    "atlas_noise_jerk_interventions",
    "atlas_reference_policy",
)
METHODS = (
    "pls_profileml_cubic_ols",
    "tsvd_matched_edf",
    "tsvd_gcv_cubic_ols",
    "cubic_spline_gcv",
    "savitzky_golay_21_3",
)
LABELS = {
    METHODS[0]: "PLS · profile ML",
    METHODS[1]: "TSVD · matched rank",
    METHODS[2]: "TSVD · conditional GCV",
    METHODS[3]: "Natural cubic spline",
    METHODS[4]: "Savitzky–Golay",
}
REGIMES = (
    "constant_zero", "constant_positive", "constant_negative",
    "sinusoidal", "sign_reversal", "braking_pulse",
)
REGIME_LABEL = (
    "Zero jerk", "Positive constant", "Negative constant",
    "Sinusoidal", "Abrupt reversal", "Braking pulse",
)
SCHEMES = ("iid", "ar1", "sign_reversal")
NOISES = ("iid", "ar1", "last_point_outlier")
NOISE_LABELS = ("IID", "AR(1)", "Terminal outlier")
DYNAMIC_LABELS = ("IID jerk", "AR(1) jerk", "Jerk reversal")
CAL_METHODS = ("joint_reml", "global_ols_plugin_mle",
               "known_mu_reml", "gcv_zero_mu")
CAL_LABELS = (
    "Joint REML", "Cubic OLS + profile ML",
    "Known-reference control", "Zero-reference GCV",
)
# Colors are obtained only from the pinned AwesomeFigures palette, never
# redefined as arbitrary Matplotlib hex values.
PALETTE = tuple(af.color_palette("okabe-ito", as_hex=True))
if len(PALETTE) != 8:
    raise RuntimeError("Expected AwesomeFigures Okabe-Ito eight-color scheme")
C = dict(zip(METHODS, (PALETTE[4], PALETTE[0], PALETTE[6],
                      PALETTE[2], PALETTE[5])))
INK, MUTED = PALETTE[7], "#697781"
af.set_style("elegante", palette="okabe-ito", font="DejaVu Sans",
             use_tex=False, rasterize=False)
METHOD_SCHEME = tuple(af.plot_scheme(
    "okabe-ito", markers=("o","s","D","^","v","P","X","*"),
    linestyles=("-", "--", ":", "-.", "-", "--", ":", "-.")))
if len(METHOD_SCHEME) != 8:
    raise RuntimeError("AwesomeFigures plot scheme changed unexpectedly")
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.6,
    "axes.titlesize": 10.0, "axes.titleweight": "semibold",
    "axes.labelsize": 8.4, "legend.fontsize": 7.4,
    "xtick.labelsize": 7.7, "ytick.labelsize": 7.7,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "svg.fonttype": "none", "pdf.fonttype": 42,
    "axes.spines.right": False, "axes.spines.top": False,
})


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError("Missing immutable source: " + str(path))
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("Empty frozen source: " + str(path))
    return df


def check_inputs(fitted, synthetic, real, cells, calibration, effects, ref):
    if len(fitted) != 6480 or fitted.sample_id.nunique() != 1296:
        raise ValueError("Experiment008 must have 1296 × 5 immutable synthetic fits")
    if set(fitted.method) != set(METHODS):
        raise ValueError("Wrong Experiment008 fitted historical comparison")
    if fitted.groupby("sample_id").size().nunique() != 1 or (
        fitted.groupby("sample_id").size().iloc[0] != 5
    ):
        raise ValueError("Unpaired synthetic fits")
    if len(real) != 6000 or real.sample_id.nunique() != 200:
        raise ValueError("Real NGSIM source must have 200 episodes × 5 × 2 × 3")
    if set(real.method) != set(METHODS):
        raise ValueError("Wrong real forecast methods")
    if set(real.horizon_frames) != {5, 10, 20}:
        raise ValueError("Unexpected recorded forecast windows")
    if set(real.continuation) != {"guerrero_last3", "local25"}:
        raise ValueError("Unexpected real continuation policies")
    if set(real.site) != {"us-101", "i-80"}:
        raise ValueError("Missing official NGSIM site")
    if len(cells) != 324 or len(calibration) != 36 or len(effects) != 108:
        raise ValueError("Missing Experiment007 72-parent calibration design")
    if set(cells.method) != set(CAL_METHODS) or set(calibration.method) != set(CAL_METHODS):
        raise ValueError("Unexpected Gaussian selection policies")
    if len(ref) < 5 or "known_discrete_jerk_rmse_m_s3" not in ref:
        raise ValueError("Experiment006 reference policy summary missing")
    if not (
        (synthetic.method == METHODS[0])
        & (synthetic.target == "known_jerk")
    ).any():
        raise ValueError("Experiment008 clean historical jerk comparison missing")
    if fitted.historical_jerk_mse_m2_s6.isna().any() or (
        fitted.historical_jerk_mse_m2_s6 < 0
    ).any():
        raise ValueError("Archived synthetic jerk losses must be nonnegative")
    for method, known in ((METHODS[0], 2.4412570862016945),
                          (METHODS[1], 2.9416214671451617),
                          (METHODS[2], 250.71810360983292)):
        mse = fitted.loc[fitted.method == method, "historical_jerk_mse_m2_s6"]
        if abs(np.sqrt(mse.mean()) - known) > 1e-8:
            raise ValueError("Frozen historical-jerk RMSE checksum mismatch: " + method)


def axes_style(ax, *, x=False, y=True):
    ax.grid(axis="y" if y and not x else "x" if x and not y else "both",
            alpha=.14, linewidth=.65)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.5, width=.7)


def finish(fig, name, output):
    for suffix in ("pdf", "svg", "png"):
        dest = output / (name + "." + suffix)
        af.save_figure(fig, dest, dpi=240 if suffix == "png" else 160)
        if not dest.is_file() or dest.stat().st_size < 500:
            raise RuntimeError("AwesomeFigures export is missing or truncated: " + str(dest))
    plt.close(fig)


def known_jerk_regimes(fitted, output):
    d = fitted.copy()
    d["regime"] = d.stratum.str.split("|", regex=False).str[0]
    if set(d.regime) != set(REGIMES):
        raise ValueError("Six synthetic jerk regimes missing")
    grouped = (d.groupby(["regime", "method"], as_index=False)
               .historical_jerk_mse_m2_s6.mean())
    grouped["rmse"] = np.sqrt(grouped.historical_jerk_mse_m2_s6)
    fig, ax = plt.subplots(figsize=(7.55, 4.15))
    y = np.arange(6)
    offsets = np.linspace(-.26, .26, len(METHODS))
    for i, m in enumerate(METHODS):
        sel = grouped[grouped.method == m].set_index("regime").loc[list(REGIMES)]
        ax.scatter(sel.rmse, y+offsets[i], marker=("o","s","D","^","v")[i],
                   s=36, color=C[m], label=LABELS[m], zorder=4)
    ax.set_yticks(y, REGIME_LABEL)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(.18, 1000)
    ax.set(xlabel="Historical discrete-jerk RMSE (m/s³) · log scale",
           title="Sensitivity to the six simulated jerk regimes")
    ax.legend(loc="lower right", ncol=2, fontsize=7.0, frameon=False)
    axes_style(ax, x=True, y=False)
    fig.subplots_adjust(left=.22, bottom=.14, right=.98, top=.89)
    finish(fig, STEMS[0], output)


def rank_pathology(fitted, output):
    d = fitted.loc[fitted.method == METHODS[2], ["rank_retained", "historical_jerk_mse_m2_s6"]]
    ranks = d.rank_retained.astype(int).to_numpy()
    sq = d.historical_jerk_mse_m2_s6.to_numpy()
    if len(ranks) != 1296:
        raise ValueError("TSVD conditional-GCV fitted cases missing")
    bins = np.bincount(ranks, minlength=77)
    loss = np.bincount(ranks, weights=sq, minlength=77)
    close = ranks >= 75
    if close.sum() != 145 or abs(sq[close].sum()/sq.sum() - .7894650568496807) > 1e-8:
        raise ValueError("Frozen near-interpolation evidence changed")
    fig,(a,b) = plt.subplots(1,2,figsize=(7.5,3.25), gridspec_kw={"width_ratios": [1.08, 1]})
    a.bar(np.arange(77), bins, width=.86, color=PALETTE[4])
    a.bar([75,76], bins[[75,76]], color=PALETTE[5])
    a.set(xlim=(-1,78), xlabel="Retained positive roughness modes (of 77)",
          ylabel="Number of trajectories", title="A · GCV-selected rank")
    a.text(.03,.95,"145/1,296 retain ranks 75–76",
           transform=a.transAxes, ha="left",va="top",fontsize=7.8)
    axes_style(a)
    cumulative = np.cumsum(loss) / np.sum(loss)
    b.step(np.arange(77),cumulative,where="mid",color=PALETTE[4],linewidth=2)
    b.fill_between([74.5,76.8],0,1,alpha=.13,color=PALETTE[5])
    b.scatter([74],[cumulative[74]],color=PALETTE[5],zorder=4,s=23)
    b.annotate("78.9% of squared jerk error\nfrom ranks 75–76",
               xy=(75, cumulative[74]),xytext=(21,.46),fontsize=7.5,
               arrowprops={"arrowstyle":"->","color":MUTED})
    b.set(xlim=(-1,78),ylim=(0,1.02),
          xlabel="Rank threshold",ylabel="Cumulative squared-error share",
          title="B · Error concentration by rank")
    axes_style(b)
    fig.subplots_adjust(left=.09, right=.98, bottom=.20, top=.87,wspace=.32)
    finish(fig,STEMS[1],output)


def paired_jerk_losses(fitted, output):
    d=fitted.pivot(index="sample_id", columns="method", values="historical_jerk_mse_m2_s6")
    regimes=fitted.loc[fitted.method==METHODS[0],["sample_id","stratum"]].set_index("sample_id")
    d=d.join(regimes)
    d["regime"]=d.stratum.str.split("|",regex=False).str[0]
    fig,axes=plt.subplots(2,3,figsize=(7.6,4.55),sharex=True,sharey=True)
    x=np.sqrt(d[METHODS[0]].clip(lower=1e-12))
    y=np.sqrt(d[METHODS[1]].clip(lower=1e-12))
    allvalues=np.concatenate((x.to_numpy(),y.to_numpy()))
    hi=10**np.ceil(np.log10(np.nanmax(allvalues)))
    lo=10**np.floor(np.log10(np.nanmin(allvalues)))
    for i,(ax,reg,label) in enumerate(zip(axes.ravel(), REGIMES,REGIME_LABEL)):
        ix=d.regime==reg
        ax.scatter(x[ix],y[ix],s=8,color=C[METHODS[1]],alpha=.45,
                   edgecolors="none",rasterized=True)
        ax.plot([lo,hi],[lo,hi],ls="--",lw=.85,color=MUTED)
        wins=int((y[ix]>x[ix]).sum())
        ax.text(.04,.96,f"PLS lower error: {wins}/{int(ix.sum())}",
                transform=ax.transAxes,va="top",fontsize=7.0)
        ax.set(xscale="log",yscale="log",xlim=(lo,hi),ylim=(lo,hi),
               title=label)
        axes_style(ax)
    fig.supxlabel("PLS trajectory-wise jerk RMSE (m/s³)",y=.035,fontsize=8.5)
    fig.supylabel("Matched-TSVD trajectory-wise jerk RMSE (m/s³)",x=.025,fontsize=8.5)
    fig.subplots_adjust(left=.12,right=.99,bottom=.12,top=.91,hspace=.32,wspace=.18)
    finish(fig,STEMS[2],output)


def method_tradeoff(fitted, synthetic, output):
    m=fitted.groupby("method").historical_jerk_mse_m2_s6.mean().pow(.5)
    mask=(synthetic.target=="future_clean_position") & (
        synthetic.continuation=="local25") & (pd.to_numeric(synthetic.horizon_frames, errors="coerce")==10)
    f=synthetic.loc[mask].set_index("method").rmse
    if set(f.index)!=set(METHODS):
        raise ValueError("Missing 1-s matched continuation outcomes")
    fig,ax=plt.subplots(figsize=(7.3,3.5))
    for method in METHODS:
        x=float(f[method]);y=float(m[method])
        ax.scatter(x,y,color=C[method],s=65,zorder=4)
        shift=7 if method!=METHODS[4] else -35
        ax.annotate(LABELS[method],(x,y),xytext=(shift,6),
                    textcoords="offset points",fontsize=7.2,
                    color=C[method])
    ax.set(xlabel="Clean position RMSE through 1 s (m)",
           ylabel="Known historical jerk RMSE (m/s³, log scale)",
           yscale="log", xlim=(.41,.55), ylim=(1.5,500),
           title="Historical derivative accuracy is not forecast accuracy")
    axes_style(ax)
    fig.subplots_adjust(left=.13,right=.94,bottom=.18,top=.87)
    finish(fig,STEMS[3],output)


def ngsim_by_site(real, output):
    d=real[real.continuation=="guerrero_last3"].copy()
    agg=(d.groupby(["site","method","horizon_frames"]).mse_m2.mean().pow(.5))
    if len(agg)!=2*5*3:
        raise ValueError("Incomplete site × method × window forecast comparison")
    fig,axes=plt.subplots(1,2,figsize=(7.5,3.65),sharey=True)
    for ax,site,label in zip(axes,("us-101","i-80"),("US-101","I-80")):
        for i,method in enumerate(METHODS):
            vals=[agg.loc[(site,method,h)] for h in (5,10,20)]
            ax.plot([.5,1,2],vals,color=C[method],lw=1.65,
                    ls=("-", "--", ":", "-.", "-")[i],
                    marker=("o","s","D","^","v")[i],markersize=4.4,
                    label=LABELS[method])
        ax.set(xlabel="Cumulative evaluation window through (s)",title=label,
               xticks=[.5,1,2],xlim=(.43,2.07))
        axes_style(ax)
    axes[0].set_ylabel("Recorded-position window RMSE (m)")
    axes[0].legend(loc="upper left",ncol=2,fontsize=6.7)
    fig.subplots_adjust(left=.105,right=.99,bottom=.18,top=.88,wspace=.14)
    finish(fig,STEMS[4],output)


def ngsim_paired_delta(real, output):
    d=real[(real.continuation=="guerrero_last3") & (
        real.horizon_frames==10)]
    wide=d.pivot(index=["sample_id","site"],columns="method",values="mse_m2")
    if len(wide)!=200 or wide.isna().any().any():
        raise ValueError("Missing paired real 1-second MSE records")
    fig,axes=plt.subplots(1,2,figsize=(7.5,3.35),sharey=True)
    rng=np.random.default_rng(20261114)
    for ax,(title,meth) in zip(axes,(
        ("Nominal matched TSVD − PLS",METHODS[1]),
        ("GCV spline − PLS",METHODS[3]),
    )):
        for i,site in enumerate(("us-101","i-80")):
            ix=wide.index.get_level_values("site")==site
            values=(wide.loc[ix,meth]-wide.loc[ix,METHODS[0]]).to_numpy()
            # A nonlinear symmetric display is appropriate for a few large
            # episode losses; the raw signed differences are never dropped.
            transformed=np.sign(values)*np.log1p(np.abs(values)/.01)
            x=rng.normal(i,.035,len(values))
            ax.scatter(x,transformed,color=PALETTE[4] if i==0 else PALETTE[0],
                       s=11,alpha=.42,linewidths=0,rasterized=True)
            median=np.median(transformed)
            ax.plot([i-.17,i+.17],[median,median],color=INK,lw=2.1)
        ax.axhline(0,color=MUTED,lw=1,ls="--")
        ax.set(xlim=(-.45,1.45),xticks=[0,1],xticklabels=["US-101","I-80"],
               xlabel="Recorded site",title=title)
        axes_style(ax)
    axes[0].set_ylabel("Signed log(1 + |ΔMSE| / 0.01 m²)")
    fig.suptitle("Paired episode losses · one-second cumulative window",
                 fontsize=10,y=.99)
    fig.subplots_adjust(left=.105,right=.99,bottom=.16,top=.82,wspace=.16)
    finish(fig,STEMS[5],output)


def spectral_calibration(cells, output):
    d=cells[(cells.dynamics=="iid") & (cells.noise_type=="iid")]
    fig,axes=plt.subplots(2,2,figsize=(7.4,5.7),sharex=True,sharey=True)
    for ax,m,label in zip(axes.ravel(),CAL_METHODS,CAL_LABELS):
        z=d[d.method==m].sort_values(["sigma_e_m","sigma_j_m_s3"])
        if len(z)!=9:
            raise ValueError("Missing correct-model 3 × 3 calibration cells")
        s=z.sigma_e_m.to_numpy()
        marker_sizes=30 + 15*np.searchsorted(np.sort(np.unique(s)),s)
        ax.scatter(z.true_S_covariance,z.mean_S,s=marker_sizes,
                   facecolors=PALETTE[4] if m=="joint_reml" else PALETTE[0],
                   alpha=.78,edgecolors="white",linewidths=.7)
        ax.plot([0,1],[0,1],color=MUTED,lw=1,ls="--")
        ax.set(xlim=(0,1.025),ylim=(0,1.025),title=label)
        axes_style(ax)
    fig.supxlabel("True spectral measurement-noise fraction",fontsize=8.5,y=.04)
    fig.supylabel("Mean selected normalized smoothness S",fontsize=8.5,x=.03)
    fig.suptitle("Model-correct Gaussian calibration · 24 parents/cell",
                 fontsize=10,y=.98)
    fig.subplots_adjust(left=.13,right=.98,bottom=.12,top=.91,hspace=.27,wspace=.17)
    finish(fig,STEMS[6],output)


def misspecification(calibration, output):
    fig,axes=plt.subplots(2,2,figsize=(7.6,5.65))
    low=0
    high=max(.12,float(calibration.mae_S.max()))
    images=[]
    for ax,m,label in zip(axes.ravel(),CAL_METHODS,CAL_LABELS):
        arr=np.full((3,3),np.nan)
        for i,reg in enumerate(SCHEMES):
            for j,noise in enumerate(NOISES):
                z=calibration[(calibration.method==m)&
                              (calibration.dynamics==reg)&
                              (calibration.noise_type==noise)]
                if len(z)!=1:raise ValueError("Incomplete calibration grid")
                arr[i,j]=float(z.mae_S.iloc[0])
        im=ax.imshow(arr,cmap="Blues",vmin=low,vmax=high,aspect="auto")
        images.append(im)
        ax.set_xticks(range(3), NOISE_LABELS,rotation=22,ha="right")
        ax.set_yticks(range(3),DYNAMIC_LABELS)
        ax.set_title(label)
        for i in range(3):
            for j in range(3):
                ax.text(j,i,f"{arr[i,j]:.3f}",ha="center",va="center",
                        fontsize=8,color="white" if arr[i,j]>.62*high else INK)
        ax.tick_params(length=0)
    cbar=fig.colorbar(images[-1],ax=list(axes.ravel()),
                      fraction=.025,pad=.03,shrink=.8)
    cbar.set_label("Absolute S calibration error",fontsize=8)
    fig.suptitle("Covariance misspecification across all four tuning policies",
                 fontsize=10,y=.98)
    fig.subplots_adjust(left=.15,right=.87,bottom=.10,top=.90,hspace=.42,wspace=.41)
    finish(fig,STEMS[7],output)


def noise_jerk_interventions(effects, output):
    d=effects[effects.method=="joint_reml"]
    fig,axes=plt.subplots(1,2,figsize=(7.6,4.15),sharey=True)
    names=[(a,b) for a in SCHEMES for b in NOISES]
    for ax,intervention,title in zip(
        axes,("noise_increase","jerk_variability_increase"),
        ("Increase measurement noise", "Increase true jerk volatility")):
        z=d[d.intervention==intervention]
        for i,(reg,noise) in enumerate(names):
            row=z[(z.dynamics==reg) & (z.noise_type==noise)]
            if len(row)!=1:raise ValueError("Incomplete paired intervention")
            row=row.iloc[0]
            v=float(row.mean_delta_selected_S)
            lo=float(row.ci_95_low_cluster)
            hi=float(row.ci_95_high_cluster)
            ax.errorbar(v,i,xerr=[[v-lo],[hi-v]],marker="o",
                        markersize=4.7,color=PALETTE[4],capsize=2.2,lw=1.2)
            ax.scatter(float(row.mean_delta_true_S),i,marker="D",
                       edgecolors=PALETTE[0],facecolors="white",
                       linewidths=1.1,s=26,zorder=5)
        ax.axvline(0,lw=.8,color=MUTED,ls="--")
        ax.set(title=title,xlabel="Change in selected S")
        axes_style(ax,x=True,y=False)
    axes[0].set_yticks(range(9),
        [f"{DYNAMIC_LABELS[i]} / {NOISE_LABELS[j]}" for i in range(3) for j in range(3)])
    axes[0].invert_yaxis()
    axes[1].tick_params(labelleft=False)
    axes[1].legend(handles=[
        Line2D([0],[0],marker="o",color=PALETTE[4],linestyle="",
               label="Joint REML ± parent 95% CI"),
        Line2D([0],[0],marker="D",color=PALETTE[0],markerfacecolor="white",
               linestyle="",label="Known covariance effect")
    ],loc="lower left",fontsize=6.7)
    fig.subplots_adjust(left=.28,right=.99,bottom=.17,top=.86,wspace=.16)
    finish(fig,STEMS[8],output)


def reference_policy(ref, output):
    z=ref[(ref.horizon_frames.astype(str)=="all")].copy()
    labels={
        "plugin_global_ols_continuous":"Cubic OLS + profile ML",
        "fixed_zero_continuous":"Zero reference + profile ML",
        "joint_reml_continuous":"Joint unknown-mean REML",
        "joint_reml_grid":"Joint REML, 15-point grid",
        "plugin_sample_continuous":"Raw difference mean + ML",
    }
    if set(z.method)!=set(labels):
        raise ValueError("Incomplete Experiment006 reference policies")
    z=z.set_index("method").loc[list(labels)]
    x=z.known_discrete_jerk_rmse_m_s3.to_numpy()
    y=np.arange(len(x))
    fig,ax=plt.subplots(figsize=(7.3,3.05))
    for i,v in enumerate(x):
        ax.plot([0,v],[i,i],color=PALETTE[4],alpha=.28,lw=3)
        ax.scatter(v,i,s=55,color=PALETTE[4] if i==0 else PALETTE[0])
        ax.text(v+.08,i,f"{v:.3f}",va="center",fontsize=7.8)
    ax.set_yticks(y,list(labels.values()))
    ax.invert_yaxis()
    ax.set(xlim=(0,max(x)*1.18),
           xlabel="Historical synthetic discrete-jerk RMSE (m/s³)",
           title="Reference mean and penalty selection matter")
    axes_style(ax,x=True,y=False)
    fig.subplots_adjust(left=.31,right=.97,bottom=.19,top=.86)
    finish(fig,STEMS[9],output)


def run(opts):
    sources={
        "exp008_synthetic_fitted":opts.exp008_synthetic_fitted,
        "exp008_synthetic_summary":opts.exp008_synthetic_summary,
        "exp008_real_forecasts":opts.exp008_real_forecasts,
        "exp007_cells":opts.exp007_cells,
        "exp007_calibration":opts.exp007_calibration,
        "exp007_effects":opts.exp007_effects,
        "exp006_jerk":opts.exp006_jerk,
    }
    data={name:read_csv(path) for name,path in sources.items()}
    check_inputs(data["exp008_synthetic_fitted"],
                 data["exp008_synthetic_summary"],
                 data["exp008_real_forecasts"],data["exp007_cells"],
                 data["exp007_calibration"],data["exp007_effects"],
                 data["exp006_jerk"])
    if opts.manifest.exists() and not opts.replace_owned:
        raise FileExistsError("Preserve existing atlas manifest: "+str(opts.manifest))
    opts.out_dir.mkdir(parents=True, exist_ok=True)
    for stem in STEMS:
        for ext in ("pdf","svg","png"):
            file=opts.out_dir/(stem+"."+ext)
            if file.exists():
                if not opts.replace_owned:
                    raise FileExistsError("Do not overwrite existing "+str(file))
                file.unlink()
    f=data
    known_jerk_regimes(f["exp008_synthetic_fitted"],opts.out_dir)
    rank_pathology(f["exp008_synthetic_fitted"],opts.out_dir)
    paired_jerk_losses(f["exp008_synthetic_fitted"],opts.out_dir)
    method_tradeoff(f["exp008_synthetic_fitted"],f["exp008_synthetic_summary"],opts.out_dir)
    ngsim_by_site(f["exp008_real_forecasts"],opts.out_dir)
    ngsim_paired_delta(f["exp008_real_forecasts"],opts.out_dir)
    spectral_calibration(f["exp007_cells"],opts.out_dir)
    misspecification(f["exp007_calibration"],opts.out_dir)
    noise_jerk_interventions(f["exp007_effects"],opts.out_dir)
    reference_policy(f["exp006_jerk"],opts.out_dir)
    manifest={
        "status":"validated",
        "library":"awesomefigures",
        "library_version":af.__version__,
        "pinned_source":"paper/requirements.txt",
        "awesomefigures_APIs":["set_style","color_palette","plot_scheme","save_figure"],
        "paper":"Paper C physical-jerk visual atlas",
        "n_figures":len(STEMS),"formats":["pdf","svg","png"],
        "immutable_input_sha256":{
            name:sha(path) for name,path in sources.items()
        },
        "figures":{
            stem:{ext:{"sha256":sha(opts.out_dir/(stem+"."+ext)),
                       "bytes":(opts.out_dir/(stem+"."+ext)).stat().st_size}
                  for ext in ("pdf","svg","png")}
            for stem in STEMS
        },
        "interpretation":{
            "synthetic_n":1296,
            "real_episode_n":200,
            "real_blocks_are_independent":False,
            "experiment007_independent_parent_draws":72,
            "TSVD_75_76_n":145,
            "TSVD_high_rank_jerk_squared_error_fraction":.7894650568496807,
            "no_real_jerk_ground_truth":True,
            "forecast_targets":"cumulative frame 1..H RMSE, not terminal frame",
            "no_retuning_or_recomputation_of_experiments":True,
        },
    }
    if opts.manifest.exists():
        opts.manifest.unlink()
    opts.manifest.parent.mkdir(parents=True, exist_ok=True)
    opts.manifest.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",
                             encoding="utf-8")
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("exp008-synthetic-fitted","exp008-synthetic-summary",
                 "exp008-real-forecasts","exp007-cells",
                 "exp007-calibration","exp007-effects","exp006-jerk"):
        p.add_argument("--"+name, required=True, type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    p.add_argument("--replace-owned",action="store_true")
    opts=p.parse_args()
    result=run(opts)
    print(json.dumps({"status":result["status"],"library":result["library"],
                     "figures":result["n_figures"],
                     "source_sha256":result["immutable_input_sha256"]},
                     indent=2),flush=True)


if __name__=="__main__":
    main()
