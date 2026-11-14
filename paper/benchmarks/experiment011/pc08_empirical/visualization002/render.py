"""Rebuild the Springer main figures and a comprehensive supplementary gallery.

Inputs are the immutable complete-criterion sparse timing tensor and
previously computed seed-cluster bootstrap summaries. No smoothing,
selection, benchmark, random simulation, or numerical tolerance change.

Run (on PCAG103A-08):
  conda run -n trendestimation python paper/benchmarks/experiment011/pc08_empirical/visualization002/render.py --tex-core
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd

from awesomefigures_config import (
    Exporter,initialize,COLORS,CRITERION,METHOD,METHOD_NAMES,INK,sha
)

HERE=Path(__file__).resolve().parent
ORIGINAL=HERE.parent/"derived"/"42636962129"
PREVIOUS=HERE.parent/"visualization001"/"render.py"
MAIN=("fig01_reliability_stacked","fig02_runtime_distributions",
      "fig03_mapping_distributions","fig04_workload_stacked",
      "fig05_grid_completion","fig06_order4_failures",
      "fig07_crossover_distributions","fig08_memory_scaling")
CATS=("cv","gcv","aicc","bic","mle")
METH=("banded_cholesky","spectral_svd","naive_inverse",
      "sparse_cholesky_banded_trace")


def load(root):
    required=("timing_tensor.csv.gz","paired_backend_rows.csv.gz",
              "paired_coordinate_rows.csv.gz",
              "paired_backend_seed_bootstrap.csv",
              "paired_coordinate_seed_bootstrap.csv",
              "timing_cell_summary.csv","analysis_summary.json")
    for f in required:
        if not (root/f).is_file():raise FileNotFoundError(root/f)
    t=pd.read_csv(root/"timing_tensor.csv.gz",low_memory=False)
    p=pd.read_csv(root/"paired_backend_rows.csv.gz",low_memory=False)
    c=pd.read_csv(root/"paired_coordinate_rows.csv.gz",low_memory=False)
    b=pd.read_csv(root/"paired_backend_seed_bootstrap.csv",low_memory=False)
    cb=pd.read_csv(root/"paired_coordinate_seed_bootstrap.csv",low_memory=False)
    cell=pd.read_csv(root/"timing_cell_summary.csv",low_memory=False)
    summary=json.loads((root/"analysis_summary.json").read_text(encoding="utf-8"))
    assert (len(t),len(p),len(c),len(b)>0)==(92679,48700,38110,True)
    assert (int(t.status.eq("ok").sum()),int(summary["recorded_jobs"]))==(76220,2813)
    return t,p,c,b,cb,cell,summary


def statuses(t):
    com=t.comment.fillna("").astype(str)
    status=t.status.fillna("").astype(str)
    return np.select((status.eq("ok"),
                      com.str.contains("PLS KKT failed",regex=False),
                      com.str.contains("Inaccurate S inversion",regex=False),
                      status.eq("budget_exceeded")),
                     ("Complete","KKT rejection","Smoothness inversion","Work-budget skip"),
                     default="Unavailable/other")


def per_seed(frame,value,keys):
    d=frame[frame[value].notna() & np.isfinite(frame[value]) & frame[value].gt(0)].copy()
    d["_log"]=np.log(d[value])
    return d.groupby(keys,as_index=False)["_log"].mean().assign(ratio=lambda x:np.exp(x["_log"]))


def legend_methods(ax,which=("banded_cholesky","spectral_svd"),loc="best",ncol=2):
    ax.legend(handles=[Patch(facecolor=METHOD[m],label=METHOD_NAMES[m]) for m in which],
              loc=loc,ncol=ncol,fontsize=7.3,frameon=False)


def square_heat(ax,piv,title,*,palette="viridis",percent=False):
    # Missing n/d combinations are white/NaN, not silently zero.
    from awesomefigures import named_colormap
    # named_colormap exposes established AwesomeFigures scientific maps.
    cmap=named_colormap(palette)
    z=np.ma.masked_invalid(piv.to_numpy(dtype=float))
    ax.imshow(z,aspect="auto",cmap=cmap,
              vmin=0 if percent else None,vmax=1 if percent else None)
    ax.set_xticks(range(len(piv.columns)),[str(x) for x in piv.columns],fontsize=7.4)
    ax.set_yticks(range(len(piv.index)),[str(x) for x in piv.index],fontsize=7.4)
    ax.set_title(title,fontsize=9,weight="bold")
    ax.set_xlabel("Difference order $d$")
    ax.set_ylabel("Series length $n$")
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            if not np.ma.is_masked(z[i,j]):
                val=float(z[i,j])
                ax.text(j,i,f"{val:.0%}" if percent else f"{val:.2g}",
                        ha="center",va="center",fontsize=6.4,
                        color="white" if (percent and val>.65) else INK)


def main_legacy(collector,t,p,c,b,cb,cell,root):
    spec=importlib.util.spec_from_file_location("springer_previous_renderer",str(PREVIOUS))
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.FROZEN=root
    mod.C.update(METHOD)
    mod.save=lambda fig,_out,stem,ledger,desc: (
        collector.export(fig,stem,section="Main manuscript",caption=desc,primary=True),
        ledger.append({"figure":stem,"description":desc})
    )
    mod.render(t,p,b,c,cell,collector.output)
    return mod


def failure_composition(t,collect):
    t=t.copy(); t["failure"]=statuses(t)
    names=["Complete","KKT rejection","Smoothness inversion",
           "Work-budget skip","Unavailable/other"]
    for crit in CATS:
        sub=t[t.criterion.eq(crit)&t.method.isin(METH)]
        if sub.empty:continue
        count=sub.groupby(["method","failure"]).size().unstack(fill_value=0).reindex(index=list(METH),fill_value=0)
        count=count.reindex(columns=names,fill_value=0)
        rates=count.div(count.sum(axis=1),axis=0).fillna(0)
        fig,ax=plt.subplots(figsize=(6.7,2.9))
        fig.subplots_adjust(left=.30,right=.97,bottom=.18,top=.84)
        left=np.zeros(len(METH))
        for k,name in enumerate(names):
            values=rates[name].to_numpy()
            for i,(meth,value) in enumerate(zip(METH,values)):
                if not value:continue
                col=METHOD[meth] if k==0 else "#E5EAF0"
                ax.barh(i,value,left=left[i],height=.66,
                        color=col,edgecolor=METHOD[meth],linewidth=.5,
                        hatch="" if k==0 else ("///" if k==1 else "xx" if k==2 else ".." if k==3 else "\\\\"))
            left+=values
        ax.set_yticks(range(len(METH)),[METHOD_NAMES[m] for m in METH],fontsize=7.8)
        ax.set_xlim(0,1);ax.invert_yaxis()
        ax.set_xlabel("Fraction of recorded observations")
        ax.grid(axis="x",alpha=.17)
        ax.set_title(f"Acceptance and failure composition: {crit.upper()}",weight="bold")
        collect.export(fig,f"supp_status_{crit}",section="Numerical reliability",
                       caption="Method-colored complete rows and patterned failure mechanisms; denominators differ by method")


def speed_distributions(t,p,b,collect):
    valid=p[(p.method=="spectral_svd")&(p.baseline=="banded_cholesky")&
            (p.coordinate=="direct_s")&(p.phase_workers==24)&
            (p.workload=="grid_one_series")&(p.M.gt(1))&
            (p.ratio_baseline_over_method.gt(0))]
    grp=per_seed(valid,"ratio_baseline_over_method",
                 ["case_id","criterion","n","d","M","seed_index"])
    for crit in CATS:
        sub=grp[grp.criterion.eq(crit)]
        sizes=sub.groupby("case_id").seed_index.nunique().sort_values(ascending=False)
        chosen=list(sizes[sizes>=20].index[:9])
        if not chosen:continue
        vectors=[]; labels=[]
        for case in chosen:
            s=sub[sub.case_id.eq(case)]
            v=s.ratio.to_numpy()
            vectors.append(v)
            i=s.iloc[0];labels.append(rf"$n={int(i.n)}$, $d={int(i.d)}$, $M={int(i.M)}$")
        fig,ax=plt.subplots(figsize=(7.3,3.9))
        fig.subplots_adjust(left=.25,right=.98,bottom=.16,top=.88)
        pos=np.arange(len(chosen))
        viol=ax.violinplot(vectors,positions=pos,vert=False,showextrema=False)
        for body in viol["bodies"]:
            body.set(facecolor=CRITERION[crit],edgecolor=CRITERION[crit],alpha=.18)
        box=ax.boxplot(vectors,positions=pos,vert=False,widths=.22,
                       showfliers=False,patch_artist=True)
        for item in box["boxes"]:item.set(facecolor=CRITERION[crit],alpha=.46)
        for k in ("medians","caps","whiskers"):
            for item in box[k]:item.set(color=INK,linewidth=.9)
        ax.set_yticks(pos,labels,fontsize=7.5);ax.invert_yaxis()
        ax.axvline(1,ls="--",lw=1,color=INK)
        ax.set_xscale("log");ax.grid(axis="x",alpha=.17)
        ax.set_xlabel("Banded/SVD time ratio (log scale)")
        ax.set_title(f"Paired seed distributions: {crit.upper()} full-grid selection",fontsize=10,weight="bold")
        collect.export(fig,f"supp_speed_violin_{crit}",section="Paired runtime",
                       caption="Valid full-grid per-seed ratios; cases are not pooled into a fictitious sample")
    for crit in CATS:
        source=b[(b.method=="spectral_svd")&(b.baseline=="banded_cholesky")&
                 (b.coordinate=="direct_s")&(b.phase_workers==24)&
                 (b.workload=="grid_one_series")&(b.M.gt(1))&
                 (b.independent_seeds.ge(20))]
        source=source[source.criterion.eq(crit)].sort_values("independent_seeds",ascending=False).head(13)
        if source.empty:continue
        fig,ax=plt.subplots(figsize=(7.6,4.1))
        fig.subplots_adjust(left=.27,right=.96,bottom=.15,top=.89)
        for i,(_,r) in enumerate(source.iterrows()):
            x=float(r.geometric_ratio);lo=float(r.bootstrap95_low);hi=float(r.bootstrap95_high)
            ax.errorbar(x,i,xerr=[[max(0,x-lo)],[max(0,hi-x)]],fmt="o",
                        ms=3.6,lw=1,color=CRITERION[crit],capsize=2)
        ax.axvline(1,ls="--",color=INK,lw=.8)
        ax.set_xscale("log")
        ax.set_yticks(range(len(source)),
            [rf"$n={int(r.n)}$, $d={int(r.d)}$, $M={int(r.M)}$" for _,r in source.iterrows()],fontsize=7.1)
        ax.invert_yaxis()
        ax.set_xlabel("Geometric banded/SVD time ratio (95% seed CI)")
        ax.set_title(f"Matched speedup estimates: {crit.upper()}",weight="bold")
        ax.grid(axis="x",alpha=.17)
        collect.export(fig,f"supp_speed_forest_{crit}",section="Paired runtime",
                       caption="Seed-cluster bootstrap 95% intervals; only valid matched complete grids")


def completion_heatmaps(t,collect):
    d=t[t.method.isin(("banded_cholesky","spectral_svd"))&
        t.phase_workers.eq(24)&t.workload.str.startswith("grid",na=False)].copy()
    d["is_complete"]=d.status.eq("ok").astype(float)
    for crit in CATS:
        sub=d[d.criterion.eq(crit)]
        if sub.empty:continue
        fig,axs=plt.subplots(1,2,figsize=(7.5,3.3),sharey=True)
        fig.subplots_adjust(left=.12,right=.98,bottom=.17,top=.84,wspace=.32)
        for ax,method in zip(axs,("banded_cholesky","spectral_svd")):
            m=sub[sub.method.eq(method)]
            if m.empty:ax.set_axis_off();continue
            mat=m.groupby(["n","d"]).is_complete.mean().unstack()
            square_heat(ax,mat,METHOD_NAMES[method],palette="viridis",percent=True)
        fig.suptitle(f"Observed full-grid completion: {crit.upper()}",fontsize=10.4,weight="bold")
        collect.export(fig,f"supp_completion_heatmap_{crit}",section="Numerical reliability",
                       caption="Completion fractions in observed n-d cells; absent cells are masked, not zero")


def coordinate_plots(c,collect):
    sub=c[(c.phase_workers==24)&(c.workload=="grid_multiple_series")&
          (c.mapped_over_direct_s.gt(0))].copy()
    sub=per_seed(sub,"mapped_over_direct_s",
                 ["case_id","seed_index","method","criterion","n","d","M"])
    for method in METH:
        data=sub[sub.method.eq(method)]
        if data.empty:continue
        fig,axs=plt.subplots(1,2,figsize=(7.6,3.25))
        fig.subplots_adjust(left=.10,right=.97,bottom=.23,top=.83,wspace=.24)
        for ax,crit in zip(axs,("cv","gcv")):
            s=data[data.criterion.eq(crit)]
            values=[];labels=[]
            for M in sorted(s.M.unique()):
                arr=s[s.M.eq(M)].ratio.values
                if len(arr)<15:continue
                values.append(arr);labels.append(str(int(M)))
            if not values:ax.set_axis_off();continue
            v=ax.violinplot(values,showextrema=False)
            for body in v["bodies"]:body.set(facecolor=METHOD[method],edgecolor=METHOD[method],alpha=.26)
            ax.boxplot(values,widths=.21,showfliers=False)
            ax.set_xticks(range(1,len(labels)+1),labels,fontsize=7.5)
            ax.axhline(1,ls="--",color=INK,lw=.8)
            ax.set_title(crit.upper());ax.grid(axis="y",alpha=.16)
            ax.set_xlabel("Number of candidates")
        axs[0].set_ylabel("Once-mapped/direct-$S$ cold time")
        fig.suptitle(f"Penalty-map reuse: {METHOD_NAMES[method]}",weight="bold",fontsize=10.4)
        collect.export(fig,f"supp_mapping_{method}",section="Coordinate reuse",
                       caption="Descriptive case-seed mapping ratio distributions across observed workloads")


def paired_scatter(p,collect):
    for case,label in (("confirm_data_cv_n256_d3_m100","CV $n=256,d=3$"),
                       ("pilot_gcv_n64_d1_m100","GCV $n=64,d=1$")):
        d=p[(p.case_id==case)&(p.method=="spectral_svd")&
            (p.baseline=="banded_cholesky")&(p.coordinate=="direct_s")&
            (p.workload=="grid_one_series")&(p.phase_workers==24)&(p.M==100)]
        if d.empty:continue
        s=d.groupby("seed_index")[["baseline_cold_s","method_cold_s"]].median()
        fig,ax=plt.subplots(figsize=(5.3,4.35))
        fig.subplots_adjust(left=.17,right=.98,bottom=.15,top=.87)
        ax.scatter(s.method_cold_s,s.baseline_cold_s,
                   s=15,alpha=.5,color=METHOD["spectral_svd"],edgecolors="none")
        minn=float(min(s.min()));maxx=float(max(s.max()))
        ax.plot([minn,maxx],[minn,maxx],ls="--",color=INK,lw=1,label="Equal time")
        ax.set(xlabel="SVD complete cold time (s)",
               ylabel="Banded complete cold time (s)")
        ax.set_title(f"Paired seed-level timing: {label}",weight="bold",fontsize=10)
        ax.grid(alpha=.16)
        collect.export(fig,f"supp_paired_scatter_{case}",section="Paired runtime",
                       caption="Each point is an independent seed cluster's paired median")


def runtime_workloads(t,collect):
    for case,label in (("pilot_gcv_n64_d1_m100","GCV $n=64,d=1$"),
                       ("confirm_data_cv_n256_d3_m100","CV $n=256,d=3$")):
        s=t[(t.case_id==case)&t.status.eq("ok")&(t.phase_workers==24)&
            (t.coordinate=="direct_s")&(t.method.isin(("banded_cholesky","spectral_svd")))]
        if s.empty:continue
        fig,axs=plt.subplots(1,2,figsize=(7.7,3.2))
        fig.subplots_adjust(left=.11,right=.97,bottom=.21,top=.83,wspace=.28)
        for ax,method in zip(axs,("banded_cholesky","spectral_svd")):
            frame=s[s.method.eq(method)]
            values=[];labels=[]
            for workload,lbl in (("one_s_one_series","1x1"),("one_s_multiple_series","1x3"),
                                 ("grid_one_series","100x1"),("grid_multiple_series","100x3")):
                sub=frame[frame.workload.eq(workload)]
                if len(sub)<3:continue
                seed=sub.groupby("seed_index").total_cold_s.median().dropna().values
                if not len(seed):continue
                values.append(seed);labels.append(lbl)
            if not values:ax.set_axis_off();continue
            vi=ax.violinplot(values,showextrema=False)
            for body in vi["bodies"]:body.set(facecolor=METHOD[method],alpha=.30)
            ax.boxplot(values,widths=.2,showfliers=False)
            ax.set_xticks(range(1,len(labels)+1),labels,fontsize=7.7)
            ax.set_yscale("log");ax.set_title(METHOD_NAMES[method])
            ax.set_xlabel("Candidates x series");ax.grid(axis="y",alpha=.15)
        axs[0].set_ylabel("Complete cold time (s; log scale)")
        fig.suptitle(f"Workload time distributions: {label}",fontsize=10.3,weight="bold")
        collect.export(fig,f"supp_workload_{case}",section="Runtime decomposition",
                       caption="Recorded cold-time distribution, conditional on complete admissible method rows")


def diagnostic_views(t,collect):
    t=t.copy();t["failure"]=statuses(t)
    # Failure by grid size, without conflating actual absence with numerical rejection.
    sub=t[t.M.gt(1)&t.method.isin(("banded_cholesky","spectral_svd"))]
    tab=sub.groupby(["method","M","failure"]).size().unstack(fill_value=0)
    fig,axs=plt.subplots(1,2,figsize=(7.8,3.35),sharey=True)
    fig.subplots_adjust(left=.11,right=.97,bottom=.20,top=.81,wspace=.19)
    order=["Complete","KKT rejection","Smoothness inversion","Work-budget skip"]
    for ax,method in zip(axs,("banded_cholesky","spectral_svd")):
        try:r=tab.loc[method]
        except KeyError:ax.set_axis_off();continue
        values=r.reindex(columns=order,fill_value=0)
        den=values.sum(axis=1)
        y=np.arange(len(values));bottom=np.zeros(len(values))
        for k,key in enumerate(order):
            height=(values[key]/den).fillna(0).values
            ax.bar(y,height,bottom=bottom,color=METHOD[method] if k==0 else "#cfd7df",
                   edgecolor=METHOD[method],hatch="" if k==0 else "///" if k==1 else "xx",
                   width=.7,linewidth=.5)
            bottom+=height
        ax.set_xticks(y,[str(int(x)) for x in values.index])
        ax.set_xlabel("Grid size M")
        ax.set_title(METHOD_NAMES[method]);ax.grid(axis="y",alpha=.15)
    axs[0].set_ylabel("Share of available method rows")
    fig.suptitle("Full-grid completion and failure by number of candidates",
                 weight="bold",fontsize=10.3)
    collect.export(fig,"supp_failure_by_candidate_count",section="Numerical reliability",
                   caption="Recorded method-level status fractions, not matched failure probabilities")

    # Case-size vs seed heatmap: fraction of valid banded grid rows per case-seed.
    for crit in ("cv","gcv","mle"):
        s=t[(t.criterion==crit)&(t.method=="banded_cholesky")&
            (t.workload.str.startswith("grid",na=False))]
        if s.empty:continue
        mat=s.assign(complete=s.status.eq("ok").astype(float)).groupby(
            ["case_id","seed_index"]).complete.mean().unstack()
        if len(mat)>16:mat=mat.iloc[:16]
        fig,ax=plt.subplots(figsize=(7.5,max(2.6,.22*len(mat)+1.6)))
        fig.subplots_adjust(left=.26,right=.98,bottom=.18,top=.87)
        img=ax.imshow(np.ma.masked_invalid(mat.values),aspect="auto",
                      cmap="cividis",vmin=0,vmax=1,interpolation="nearest")
        ax.set_yticks(range(len(mat)),[
           str(r).replace("pilot_","").replace("confirm_","").replace("smoke_","")[:29]
           for r in mat.index],fontsize=6.4)
        ax.set_xlabel("Independent seed index")
        ax.set_title(f"Observed banded full-grid completion by seed: {crit.upper()}",
                     fontsize=10,weight="bold")
        ax.set_xticks(range(0,len(mat.columns),max(1,len(mat.columns)//8)),
                     [str(x) for x in mat.columns[::max(1,len(mat.columns)//8)]],fontsize=7)
        fig.colorbar(img,ax=ax,fraction=.025,pad=.025,label="Complete fraction")
        collect.export(fig,f"supp_case_seed_{crit}",section="Numerical reliability",
                       caption="Case-seed completion heatmap; white denotes absent data")

    # Distinct failure mechanisms by series length and difference order.
    for method in ("banded_cholesky","spectral_svd"):
        s=t[t.method.eq(method)&t.workload.str.startswith("grid",na=False)]
        s=s.assign(failed=lambda x:~x.status.eq("ok"))
        grid=s.groupby(["n","d"]).failed.mean().unstack()
        fig,ax=plt.subplots(figsize=(5.7,3.2))
        fig.subplots_adjust(left=.16,right=.95,bottom=.15,top=.86)
        square_heat(ax,grid,"Recorded grid noncompletion: "+METHOD_NAMES[method],
                    palette="magma",percent=True)
        collect.export(fig,f"supp_failure_size_{method}",section="Numerical reliability",
                       caption="Observed conditional noncompletion by n,d; no unmeasured cell is filled")


def derived_summaries(t,p,b,cb,collect):
    # Evaluation coverage by phase is descriptive only.
    phase=t.drop_duplicates(["case_id","seed_index"]).phase_workers.value_counts().sort_index()
    fig,ax=plt.subplots(figsize=(5.8,3.2))
    fig.subplots_adjust(left=.16,right=.95,bottom=.19,top=.86)
    bars=ax.bar([str(int(x)) for x in phase.index],phase.values,
                color=COLORS[4],width=.58)
    for bar,val in zip(bars,phase.values):
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height(),str(int(val)),
                ha="center",va="bottom",fontsize=8)
    ax.set_xlabel("Maximum concurrent worker phase")
    ax.set_ylabel("Distinct scheduled case-seed jobs")
    ax.set_title("Coverage of the three execution phases",weight="bold",fontsize=10.4)
    ax.grid(axis="y",alpha=.17)
    collect.export(fig,"supp_worker_phase_coverage",section="Study design",
                   caption="Counts of scheduled jobs by phase, not measured processor occupancy")

    valid=t[t.status.eq("ok")].copy()
    valid=valid[valid.total_cold_s.gt(0)&valid.total_warm_s.gt(0)]
    valid["factor"]=valid.total_cold_s/valid.total_warm_s
    s=valid[(valid.criterion=="gcv")&(valid.n==64)&(valid.M==100)&
            (valid.workload=="grid_one_series")&(valid.phase_workers==24)]
    means=[];labels=[]
    for method in METH:
        sub=s[s.method.eq(method)]
        if len(sub)<3:continue
        means.append(sub.groupby("seed_index").factor.median().to_numpy())
        labels.append(method)
    if means:
        fig,ax=plt.subplots(figsize=(6.3,3.2))
        fig.subplots_adjust(left=.27,right=.96,bottom=.18,top=.84)
        bp=ax.boxplot(means,vert=False,patch_artist=True,showfliers=False)
        for box,method in zip(bp["boxes"],labels):box.set(facecolor=METHOD[method],alpha=.50)
        ax.set_yticks(range(1,len(labels)+1),[METHOD_NAMES[x] for x in labels],fontsize=8)
        ax.axvline(1,ls="--",color=INK,lw=.8)
        ax.set_xlabel("Recorded cold/warm accounting ratio")
        ax.set_title("Setup amortization in a fixed GCV grid",fontsize=10,weight="bold")
        ax.grid(axis="x",alpha=.16)
        collect.export(fig,"supp_cold_warm_amortization",section="Runtime decomposition",
                       caption="Valid n=64 GCV M=100 rows; accounting ratio, not separate process runs")

    # Pair availability, not unpaired method winner counts.
    src=b[(b.method=="spectral_svd")&(b.baseline=="banded_cholesky")&
          (b.coordinate=="direct_s")&(b.independent_seeds.ge(5))]
    mat=src.groupby(["criterion","workload"]).independent_seeds.sum().unstack(fill_value=0)
    if not mat.empty:
        fig,ax=plt.subplots(figsize=(7.2,3.2))
        fig.subplots_adjust(left=.14,right=.97,bottom=.28,top=.83)
        x=np.arange(len(mat));base=np.zeros(len(mat))
        for i,work in enumerate(mat.columns):
            vals=mat[work].values
            ax.bar(x,vals,bottom=base,color=COLORS[i%len(COLORS)],label=work.replace("_"," "))
            base+=vals
        ax.set_xticks(x,[s.upper() for s in mat.index])
        ax.set_ylabel("Summed seed support across matching cells")
        ax.set_title("Available valid paired comparison support",weight="bold",fontsize=10.4)
        ax.legend(ncol=2,fontsize=7,loc="upper center",bbox_to_anchor=(.5,-.20))
        collect.export(fig,"supp_valid_paired_support",section="Study design",
                       caption="Cellwise independent-seed support summed across heterogeneous paired configurations")

    # Case-by-case SVD/banded ratio versus grid M; descriptive of distinct cases.
    base=b[(b.method=="spectral_svd")&(b.baseline=="banded_cholesky")&
           (b.coordinate=="direct_s")&(b.phase_workers==24)&
           (b.workload=="grid_one_series")&(b.independent_seeds.ge(20))]
    agg=base.groupby(["criterion","M"]).geometric_ratio.median().reset_index()
    if not agg.empty:
        fig,ax=plt.subplots(figsize=(6.25,3.15))
        fig.subplots_adjust(left=.15,right=.97,bottom=.18,top=.83)
        for crit in CATS:
            s=agg[agg.criterion==crit].sort_values("M")
            if not s.empty:ax.plot(s.M,s.geometric_ratio,"o-",color=CRITERION[crit],
                                   lw=1.3,ms=4,label=crit.upper())
        ax.axhline(1,ls="--",color=INK,lw=.8)
        ax.set_xscale("log")
        ax.set_xlabel("Observed number of smoothing candidates M")
        ax.set_ylabel("Median case-level banded/SVD geometric ratio")
        ax.set_title("Descriptive candidate-count comparison",fontsize=10.4,weight="bold")
        ax.legend(ncol=3,fontsize=7,loc="best");ax.grid(alpha=.17)
        collect.export(fig,"supp_ratio_by_M",section="Paired runtime",
                       caption="Descriptive medians across distinct measured cases, not a controlled M-sweep")

    # KKT failure residual distributions only among recorded rejections.
    com=t.comment.fillna("").astype(str)
    failed=t[com.str.contains("PLS KKT failed",regex=False)].copy()
    err=failed.comment.str.extract(r"backward_error=([0-9.eE+-]+)",expand=False).astype(float)
    failed["eta"]=err
    assert len(failed)==9096 and failed.eta.gt(1e-7).all()
    fig,ax=plt.subplots(figsize=(6.4,3.0))
    fig.subplots_adjust(left=.14,right=.96,bottom=.20,top=.85)
    bins=np.geomspace(1e-7,1.2e-6,22)
    arrays=[failed[failed.criterion==c].eta.values for c in ("cv","gcv","mle")]
    ax.hist(arrays,bins=bins,stacked=True,color=[CRITERION[x] for x in ("cv","gcv","mle")],
            label=["CV","GCV","Marginal likelihood"],edgecolor="white",linewidth=.2)
    ax.set_xscale("log")
    ax.axvline(1e-7,ls="--",color=INK,lw=1)
    ax.set_xlabel("Recorded scaled optimality residual (log)")
    ax.set_ylabel("Rejected method-level rows")
    ax.set_title("Post-solve KKT residuals, conditional on rejection",weight="bold",fontsize=10.4)
    ax.legend(fontsize=7,loc="upper right")
    collect.export(fig,"fig09_kkt_rejections",section="Main manuscript",
                   caption="KKT residual distribution conditional on failure; accepted residual magnitudes unobserved",primary=True)
    fig,ax=plt.subplots(figsize=(6.4,3.0))
    fig.subplots_adjust(left=.14,right=.96,bottom=.18,top=.84)
    for crit in ("cv","gcv","mle"):
        x=np.sort(failed[failed.criterion==crit].eta.to_numpy())
        if not len(x):continue
        ax.step(x,np.arange(1,len(x)+1)/len(x),color=CRITERION[crit],
                where="post",lw=1.35,label=crit.upper())
    ax.axvline(1e-7,ls="--",color=INK,lw=.8)
    ax.set_xscale("log")
    ax.set_xlabel("Recorded rejected optimality residual")
    ax.set_ylabel("Conditional empirical CDF")
    ax.set_title("Tail shape among rejected KKT diagnostics",weight="bold",fontsize=10.3)
    ax.legend()
    collect.export(fig,"supp_kkt_ecdf",section="Numerical reliability",
                   caption="Empirical CDF conditional on rejection; cannot estimate all-solve error distribution")


def make_gallery(out,manifest):
    try:
        from pypdf import PdfReader,PdfWriter
    except ImportError as e:
        raise RuntimeError("Supplement PDF assembly requires paper dependency pypdf") from e
    writer=PdfWriter()
    for item in manifest["figures"]:
        if item["primary"]:continue
        doc=PdfReader(str(out/item["pdf"]))
        if len(doc.pages)!=1:
            raise RuntimeError("Each exported supplementary figure must fit one vector page")
        writer.add_page(doc.pages[0])
    dest=out/"supplementary_figure_gallery.pdf"
    with dest.open("wb") as f:writer.write(f)
    return dest,len(writer.pages)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen",type=Path,default=ORIGINAL)
    parser.add_argument("--out",type=Path,default=HERE)
    parser.add_argument("--tex-core",action="store_true")
    args=parser.parse_args()
    initialize()
    t,p,c,b,cb,cell,summary=load(args.frozen)
    # protect and assert expected source version; hashes are also in manifest.
    expected="a25f674981b1c20df678638287df289c4d888ae62417a3f58ed8a6b2a08fce13"
    if sha(args.frozen/"timing_tensor.csv.gz")!=expected:
        raise RuntimeError("Frozen source hash changed; do not regenerate a plausible figure from altered data")
    output=Exporter(args.out,exact_tex=args.tex_core)
    main_legacy(output,t,p,c,b,cb,cell,args.frozen)
    failure_composition(t,output)
    speed_distributions(t,p,b,output)
    completion_heatmaps(t,output)
    coordinate_plots(c,output)
    paired_scatter(p,output)
    runtime_workloads(t,output)
    diagnostic_views(t,output)
    derived_summaries(t,p,b,cb,output)
    assert len(output.items)>=30,(len(output.items),[x["id"] for x in output.items])
    assert sum(x["primary"] for x in output.items)==9
    info=output.save_manifest(
        [args.frozen/f for f in ("timing_tensor.csv.gz","paired_backend_rows.csv.gz",
             "paired_coordinate_rows.csv.gz","paired_backend_seed_bootstrap.csv",
             "paired_coordinate_seed_bootstrap.csv")],
        {"worker_phase_mixed":True,"log_ratio_seed_clustering":True,
         "exact_tex_primary":args.tex_core,"original_report_sha256":summary["report_sha256"]}
    )
    gallery,pages=make_gallery(args.out,info)
    print(f"[FINAL] {len(info['figures'])} AwesomeFigures vector figures; {pages} supplementary pages; "
          f"{info['primary_count']} manuscript figures; input SHA verified.",flush=True)


if __name__=="__main__":
    main()
