"""Rebuild CSDA vector figures from immutable Experiment004 CSV archives.

No simulation is repeated and no result is fabricated. All panels label
the data-generating scope and lack of inferential uncertainty estimates.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from publication_style import configure_publication, publication_export, finish_manifest

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parents[1]
EXPERIMENT = ROOT / "paper" / "benchmarks" / "experiment004" / "runs"
PILOT = EXPERIMENT / "pilot-hosted-40826487736"
VALID = EXPERIMENT / "validation-hosted-40828581992"
STABLE = EXPERIMENT / "stable-hosted-40830375100"
FIGURES = PAPER / "figures"
FIGURES.mkdir(exist_ok=True)
INK="#18334c"; BLUE="#2668aa"; CYAN="#3c9bc0"; GREY="#7b8794"
PALETTE=[INK, BLUE, CYAN, "#526b92", "#7c94b5", "#b2c7d9"]


def readcsv(path):
    if not path.is_file():
        raise FileNotFoundError(f"Missing archived source: {path}")
    with path.open(newline="",encoding="utf8") as f:
        return list(csv.DictReader(f))


def style():
    configure_publication(PAPER)


def export(fig, name):
    publication_export(fig, name, FIGURES)


def smoothness_map():
    n=64
    D=lambda d:np.diff(np.eye(n),n=d,axis=0)
    fig,ax=plt.subplots(figsize=(6.2,3.15))
    penalties=np.geomspace(1e-6,1e13,700)
    for idx,d in enumerate((1,2,3,4,5,6)):
        singular=np.linalg.svd(D(d),compute_uv=False)
        delta=singular**2
        z=np.log(penalties[:,None])+np.log(delta)[None,:]
        ss=np.mean(1/(1+np.exp(-np.clip(z,-700,700))),axis=1)
        ax.plot(penalties,ss,label=f"d={d}",lw=1.7,color=PALETTE[idx])
    ax.set_xscale("log")
    ax.set(xlabel=r"Internal penalty $\lambda$ (log scale)",
           ylabel=r"Normalized smoothness $S_d(\lambda)$",
           title=r"Smoothness across difference orders")
    ax.set_ylim(-.02,1.03)
    ax.axhline(1,ls=":",c=GREY,lw=.75)
    ax.legend(ncol=3,loc="lower right",frameon=False)
    export(fig,"smoothness_map")


def bic_boundary():
    rows=readcsv(VALID/"bic_small_s.csv")
    fig,ax=plt.subplots(figsize=(6.2,3.1))
    for idx,d in enumerate((1,2,5,6)):
        sub=sorted((r for r in rows if int(r["n"])==64
            and int(r["d"])==d and r["mu_policy"]=="fixed_zero"),key=lambda x:float(x["s"]))
        x=[float(r["s"]) for r in sub]
        y=[float(r["bic"]) for r in sub]
        ax.plot(x,y,label=f"d={d}",color=PALETTE[idx],lw=1.8,
                marker="o",ms=2.5)
    ax.axvline(.05,ls="--",lw=.8,c="#d18a60",label="Smin=.05")
    ax.axvline(.10,ls=":",lw=.9,c="#925e89",label="Smin=.10")
    ax.set(xscale="log",xlabel=r"Normalized smoothness $S$ (log scale)",
           ylabel="Implemented RSS-based BIC",
           title="RSS-BIC near interpolation")
    ax.legend(ncol=3,fontsize=7,frameon=False,loc="upper left")
    export(fig,"bic_boundary")


def rmse_criteria():
    rows=readcsv(PILOT/"pilot_rmse.csv")
    criteria=["cv","gcv","aicc","bic","mle"]
    means=["fixed_zero","observed_difference"]
    labels=["CV","GCV","AICc","BIC*","ML"]
    val={}
    for mode in means:
        for c in criteria:
            data=[float(r["trend_rmse"]) for r in rows
                if r["mu_policy"]==mode and r["criterion"]==c and r["trend_rmse"]]
            if not data:raise ValueError((mode,c))
            val[mode,c]=np.mean(data)
    fig,ax=plt.subplots(figsize=(6.4,3.25))
    x=np.arange(len(criteria));width=.35
    for i,mode in enumerate(means):
        heights=[val[mode,c] for c in criteria]
        ax.bar(x+(i-.5)*width,heights,width,color=BLUE if i==0 else CYAN,
               label="Fixed $\\mu=0$" if i==0 else "Plug-in $\\hat\\mu$")
    ax.set_xticks(x,labels)
    ax.set(ylabel="Mean latent-trend RMSE",title="Mean recovery error")
    ax.set_ylim(0,.36)
    ax.legend(loc="upper left",frameon=False,ncol=2)
    export(fig,"rmse_criteria")


def solver_accuracy():
    """Four paired rows, retaining results for all eight plotted methods.

    Each row shows two independently validated implementations; values are
    the same matched 576-case results used in the original paper.
    """
    rows = readcsv(STABLE / "stable_solver_precision.csv")
    pairs = [
        (("svd_shift_free", "Shift-free SVD"),
         ("scaled_augmented_qr_gelsy", "Scaled QR")),
        (("svd_polynomial_reference", "Polynomial SVD"),
         ("dual_svd", "Dual SVD")),
        (("scaled_augmented_svd_gelsd", "Stacked SVD"),
         ("dual_banded_cholesky", "Dual banded Chol.")),
        (("primal_banded_cholesky", "Primal banded Chol."),
         ("eigh_gram", "Gram eigendecomp.")),
    ]
    stats = {}
    for pair in pairs:
        for key, label in pair:
            sample = [r for r in rows if r["method"] == key]
            assert len(sample) == 576, (key, len(sample))
            values = np.asarray([
                float(r["relative_l2_error"]) for r in sample
                if r["status"] == "ok"
            ], dtype=float)
            stats[key] = {
                "max": float(np.max(values)),
                "bad": int(np.sum(values > 1e-5)),
                "fail": sum(r["status"] != "ok" for r in sample),
            }
    fig, (a, b) = plt.subplots(
        1, 2, figsize=(8.0, 3.35),
        gridspec_kw={"width_ratios": [1.18, 1.0]},
    )
    locs = np.arange(4, dtype=float)
    shifts = (-.17, .17)
    colors = (BLUE, CYAN)
    for col in range(2):
        for i, pair in enumerate(pairs):
            key, label = pair[col]
            y = locs[i] + shifts[col]
            datum = stats[key]
            a.barh(y, max(datum["max"], 1e-11), height=.29,
                   color=colors[col], alpha=.95)
            b.barh(y, datum["bad"], height=.29,
                   color=colors[col], alpha=.95)
            if datum["fail"]:
                b.barh(y, datum["fail"], height=.29,
                       left=datum["bad"], color="#a65c63")
    pair_labels = [
        "Shift-free / QR",
        "Polynomial / dual SVD",
        "Stacked / dual banded",
        "Primal banded / Gram eig.",
    ]
    for ax in (a, b):
        ax.set_yticks(locs, pair_labels)
        ax.invert_yaxis()
        ax.set_ylim(3.62, -.62)
        ax.tick_params(axis="y", length=0)
    a.set_xscale("log")
    a.axvline(1e-5, color="#aa5d57", linestyle="--", lw=.95)
    a.set_xlim(1e-10, 1e4)
    a.set(xlabel="Largest relative fit error", title="Accuracy")
    b.set_xlim(0, 570)
    b.set(xlabel="Number of cases (of 576)", title="Large error / failure")
    # Color refers to first/second method in each of the four paired rows.
    from matplotlib.patches import Patch
    b.legend(handles=[
        Patch(facecolor=BLUE, label="First"),
        Patch(facecolor=CYAN, label="Second"),
        Patch(facecolor="#a65c63", label="Failed"),
    ], loc="upper right", ncol=3, fontsize=7, frameon=False)
    export(fig, "solver_accuracy")


def bic_restriction():
    rows=readcsv(STABLE/"restricted_bic_rmse.csv")
    fig,(a,b)=plt.subplots(1,2,figsize=(7.9,3.1),gridspec_kw={"width_ratios":[1.15,1]})
    bounds=[.05,.10];means=["fixed_zero","observed_difference"]
    x=np.arange(2);width=.33
    for i,mode in enumerate(means):
        values=[]
        for bound in bounds:
            sample=[float(r["true_trend_rmse"]) for r in rows
                    if float(r["smin"])==bound and r["mu_policy"]==mode]
            values.append(np.mean(sample))
        a.bar(x+(i-.5)*width,values,width,label="Fixed mu=0" if i==0 else "Plug-in mu",
              color=BLUE if i==0 else CYAN)
    a.set_xticks(x,["$S\\geq 0.05$","$S\\geq 0.10$"])
    a.set(ylabel="Mean latent-trend RMSE",title="Restricted-BIC sensitivity")
    a.legend(frameon=False,fontsize=7)
    a.set_ylim(0,.35)
    counts=[sum(str(r["boundary_selected"])=="True" for r in rows if float(r["smin"])==bnd)
            for bnd in bounds]
    total=[sum(float(r["smin"])==bnd for r in rows) for bnd in bounds]
    b.bar(x,[100*counts[i]/total[i] for i in range(2)],color=[GREY,BLUE],width=.55)
    b.set_xticks(x,["$S\\geq 0.05$","$S\\geq 0.10$"])
    b.set_ylim(0,110)
    b.set(ylabel="Selections at imposed bound (%)",
          title="Boundary attraction remains")
    for idx in range(2):
        b.text(idx,100*counts[idx]/total[idx]+2,
               f"{counts[idx]}/{total[idx]}",ha="center",fontsize=8)
    export(fig,"restricted_bic")


def main():
    style()
    smoothness_map()
    bic_boundary()
    rmse_criteria()
    solver_accuracy()
    bic_restriction()
    expected=[FIGURES/f"{x}.{ext}" for x in
        ("smoothness_map","bic_boundary","rmse_criteria","solver_accuracy","restricted_bic")
        for ext in ("pdf","svg","pgf")]
    if not all(path.exists() and path.stat().st_size>1000 for path in expected):
        raise RuntimeError("One or more vector figure exports missing")
    finish_manifest(PAPER, FIGURES)


if __name__=="__main__":
    main()
