#!/usr/bin/env python3
"""Journal-size publication dashboards from ARCHIVED result JSON only.

The historical experiment was already run on the author's Windows VM.
This script never imports or calls parameter selectors, root solvers, or
timing benchmarks. It renders numerical results into compact PDF/SVG/PNG
figures suitable for a short SN Computer Science original research paper.

Usage (repository root):
    python paper/computational-statistics-submission/sncs_dashboard.py
    python paper/computational-statistics-submission/sncs_dashboard.py --mu data
    python paper/computational-statistics-submission/sncs_dashboard.py --dataset co2_recent

Archived JSONs remain bit-for-bit unchanged. Old full 4x6 dashboards remain
available separately as supplement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from contrast_theme import (apply, INK, GRID, METHODS as METHOD_COLORS,
                            save_figure, named_colormap)

HERE=Path(__file__).resolve().parent
DATA=HERE/"data"
FIGURES=HERE/"figures"
METHODS=("cv","gcv","aicc","bic","mle","controlled")
ORDERS=(1,2,3,4)
LABELS=("CV","GCV","AICc","BIC","MLE","Controlled")
INPUTS={
    "co2_full":"Mauna Loa CO$_2$",
    "co2_recent":"Mauna Loa CO$_2$ (recent 120 months)",
    "fedfunds_full":"US effective federal funds rate",
}
VERSIONS=("zero","data")


def _hash(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_results(dataset:str)->tuple[dict,str]:
    if dataset not in INPUTS:
        raise ValueError(f"Unknown data series {dataset}")
    path=DATA/f"{dataset}_dashboards.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"Archived selection file missing: {path}. "
            "Do not automatically rerun experiments."
        )
    before=_hash(path)
    payload=json.loads(path.read_text(encoding="utf-8"))
    if payload.get("dataset")!=dataset:
        raise ValueError(f"Archived dataset identity mismatch: {path}")
    if payload.get("orders")!=list(ORDERS):
        raise ValueError("Incomplete archived difference-order matrix")
    if payload.get("methods")!=list(METHODS):
        raise ValueError("Incomplete archived selector matrix")
    if set(payload.get("mu_modes",[]))!=set(VERSIONS):
        raise ValueError("Archived mean-difference modes incomplete")
    for mode in VERSIONS:
        rows=payload["records"][mode]
        if len(rows)!=len(METHODS)*len(ORDERS):
            raise ValueError(f"Not exactly 24 archived cells for {mode}")
        for d in ORDERS:
            for method in METHODS:
                row=rows[f"d{d}_{method}"]
                for key in ("s","lambda","rmse","mae","mu","holdout_lambda","holdout_mu"):
                    if not np.isfinite(float(row[key])):
                        raise ArithmeticError(f"{dataset}/{mode}/d{d}/{method}: invalid {key}")
                if not (0<=float(row["s"])<=1):
                    raise ArithmeticError("Invalid archived normalized smoothness")
                if float(row["lambda"])<=0 or float(row["holdout_lambda"])<=0:
                    raise ArithmeticError("Invalid archived penalty")
                if float(row["rmse"])<0 or float(row["mae"])<0:
                    raise ArithmeticError("Invalid holdout loss")
    return payload,before


def as_matrix(payload:dict,mode:str,metric:str)->np.ndarray:
    if mode not in VERSIONS:
        raise ValueError(mode)
    if metric not in ("s","lambda","rmse","mae"):
        raise ValueError(metric)
    return np.array([
        [float(payload["records"][mode][f"d{d}_{m}"][metric]) for m in METHODS]
        for d in ORDERS
    ],dtype=float)


def _annotated_map(ax,values:np.ndarray,title:str,cmap:str,format_string:str,
                   *,vmin:float|None=None,vmax:float|None=None) -> None:
    image=ax.imshow(values,aspect="auto",cmap=named_colormap(cmap),vmin=vmin,vmax=vmax)
    ax.set_title(title,fontsize=11,weight="bold",pad=8)
    ax.set_xticks(np.arange(len(METHODS)),LABELS,fontsize=8)
    ax.set_yticks(np.arange(len(ORDERS)),[f"d={d}" for d in ORDERS],fontsize=9)
    ax.tick_params(axis="both",length=0)
    ax.set_xticks(np.arange(-.5,len(METHODS),1),minor=True)
    ax.set_yticks(np.arange(-.5,len(ORDERS),1),minor=True)
    ax.grid(which="minor",color="white",lw=2.3)
    ax.tick_params(which="minor",bottom=False,left=False)
    vals=np.asarray(values)
    tmin=float(np.min(vals)); tmax=float(np.max(vals))
    for (i,j),v in np.ndenumerate(vals):
        norm=(v-tmin)/(max(tmax-tmin,1e-12))
        color="white" if norm>.65 else INK
        ax.text(j,i,format(v,format_string),color=color,
                ha="center",va="center",fontsize=8.6,weight="bold")
    return image


def plot_compact(dataset_left:str="co2_full",dataset_right:str="fedfunds_full",
                 mu:str="zero",filename:str|None=None)->list[Path]:
    if mu not in VERSIONS:
        raise ValueError(mu)
    apply()
    left,hleft=read_results(dataset_left)
    right,hright=read_results(dataset_right)
    pair=((dataset_left,left),(dataset_right,right))
    fig,axes=plt.subplots(2,2,figsize=(13.5,8.1),layout="constrained")
    for i,(dataset,cached) in enumerate(pair):
        smooth=as_matrix(cached,mu,"s")
        rmse=as_matrix(cached,mu,"rmse")
        title=INPUTS[dataset]
        _annotated_map(axes[i,0],smooth,title+"  |  chosen $S$", "viridis",
                       ".2f",vmin=0,vmax=1)
        _annotated_map(axes[i,1],rmse,title+"  |  12-month RMSE",
                       "cividis",".2f")
    fig.suptitle(
        f"Smoothness selection and historical holdout  |  "
        +("$\\mu=0$" if mu=="zero" else "$\\mu=\\overline{D_dy_{train}}$"),
        fontsize=15,weight="bold"
    )
    fig.supxlabel(
        "Columns: four in-sample criteria, conditional Gaussian MLE, "
        "and user-prescribed S=0.86. Historical RMSE: one origin only.",
        fontsize=10,color=INK
    )
    FIGURES.mkdir(parents=True,exist_ok=True)
    basename=filename or ("sncs_compact_dashboard" if mu=="zero"
                          else "sncs_compact_dashboard_mu_data")
    out=[]
    for ext in (".pdf",".svg",".png"):
        dst=FIGURES/(basename+ext)
        save_figure(fig,dst,dpi=180)
        out.append(dst)
    plt.close(fig)
    if _hash(DATA/f"{dataset_left}_dashboards.json")!=hleft or (
       _hash(DATA/f"{dataset_right}_dashboards.json")!=hright):
        raise RuntimeError("Numerical archive modified while rendering")
    return out


def plot_tradeoff(dataset:str="co2_full",mu:str="zero")->list[Path]:
    """Supplementary selector-level scatter, computed from archived values."""
    apply()
    cached,before=read_results(dataset)
    fig,axes=plt.subplots(1,2,figsize=(12,4.3),layout="constrained")
    for i,metric in enumerate(("rmse","mae")):
        ax=axes[i]
        for method in METHODS:
            rows=[cached["records"][mu][f"d{d}_{method}"] for d in ORDERS]
            xs=[float(r["s"]) for r in rows]
            ys=[float(r[metric]) for r in rows]
            ax.plot(xs,ys,color=METHOD_COLORS[method],lw=1.2,
                    marker="o",ms=5,label=method.upper())
            for d,x,y in zip(ORDERS,xs,ys):
                ax.annotate(f"{d}",(x,y),xytext=(3,3),
                            textcoords="offset points",fontsize=8,color=INK)
        ax.set(xlabel="Selected normalized smoothness S",
               ylabel="Historical 12-month "+metric.upper(),
               title=f"One-origin {metric.upper()} vs S")
        ax.grid(alpha=.2)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc="outside upper center",ncol=6)
    fig.suptitle(INPUTS[dataset]+"  |  selected S and holdout errors",
                 weight="bold",fontsize=13)
    basename=f"sncs_tradeoff_{dataset}_mu_{mu}"
    FIGURES.mkdir(parents=True,exist_ok=True)
    out=[]
    for suffix in (".pdf",".svg",".png"):
        path=FIGURES/(basename+suffix)
        save_figure(fig,path,dpi=180)
        out.append(path)
    plt.close(fig)
    if _hash(DATA/f"{dataset}_dashboards.json")!=before:
        raise RuntimeError("Archived experiment changed during figure rendering")
    return out


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mu",choices=VERSIONS,default="zero")
    parser.add_argument("--dataset",choices=tuple(INPUTS),default="co2_full",
                        help="Dataset for the detailed supplementary tradeoff")
    parser.add_argument("--summary-only",action="store_true",
                        help="Only the 2x2 figure used in the short journal paper")
    args=parser.parse_args()
    output=plot_compact(mu=args.mu)
    if not args.summary_only:
        output+=plot_tradeoff(args.dataset,args.mu)
    print("Rendered from archived selected parameters and losses, with no fits or benchmarks:")
    for file in output:
        print("  "+str(file))


if __name__=="__main__":
    main()
