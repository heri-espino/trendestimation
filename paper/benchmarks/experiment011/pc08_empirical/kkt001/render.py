"""Audit plot of the KKT rejection-residual distribution from frozen data.

Read-only postprocessing: no smoothing-parameter searches or numerical
solver calls. The distribution is CONDITIONAL on failure (not the
distribution of all optimality residuals).
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
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "derived" / "42636962129" / "timing_tensor.csv.gz"
OUTPUT = Path(__file__).resolve().parent
THRESHOLD = 1e-7
REGEX = r"PLS KKT failed: backward_error=([0-9.eE+-]+)"


def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tensor",type=Path,default=DEFAULT)
    p.add_argument("--out",type=Path,default=OUTPUT)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    keep=["comment","status","criterion","method","case_id","seed_index","workload"]
    df=pd.read_csv(args.tensor,usecols=keep,low_memory=False)
    mask=df.comment.fillna("").astype(str).str.contains("PLS KKT failed",regex=False)
    failed=df.loc[mask].copy()
    assert len(df)==92679 and len(failed)==9096
    assert failed.method.eq("banded_cholesky").all()
    assert failed.status.eq("numerical_failed").all()
    err=failed.comment.str.extract(REGEX,expand=False)
    assert err.notna().all()
    failed["eta_opt"]=err.astype(float)
    assert np.all(np.isfinite(failed.eta_opt))
    assert failed.eta_opt.gt(THRESHOLD).all()
    counts=failed.criterion.value_counts().to_dict()
    assert counts=={"cv":3384,"gcv":4160,"mle":1552},counts

    plt.rcParams.update({"font.family":"sans-serif","font.size":8.7,
                         "pdf.fonttype":42,"axes.spines.top":False,
                         "axes.spines.right":False,"axes.edgecolor":"#74818a"})
    fig,ax=plt.subplots(figsize=(7.25,3.4))
    fig.subplots_adjust(left=.10,right=.98,bottom=.20,top=.87)
    crit=("cv","gcv","mle")
    palette={"cv":"#236A9A","gcv":"#D17B36","mle":"#748F7B"}
    bins=np.geomspace(THRESHOLD,1.12e-6,27)
    observations=[failed.loc[failed.criterion.eq(c),"eta_opt"].to_numpy() for c in crit]
    ax.hist(observations,bins=bins,stacked=True,linewidth=.35,
            edgecolor="white",color=[palette[c] for c in crit],
            label=[f"{c.upper()} ({counts[c]:,})" for c in crit])
    ax.set_xscale("log")
    ax.axvline(THRESHOLD,color="#bd424b",lw=1.6,ls="--",zorder=4)
    med=float(failed.eta_opt.median())
    ax.axvline(med,color="#25313a",lw=1.2,ls=":",zorder=4)
    ax.set_xlabel(r"Recorded scaled optimality residual $\eta_{\mathrm{opt}}$ (log scale)")
    ax.set_ylabel("Rejected method-level observations")
    ax.set_title("Magnitude of the rejected first-order optimality residuals",
                 fontsize=10.8,weight="bold",pad=10)
    ax.grid(axis="y",alpha=.17)
    ax.legend(loc="upper right",frameon=False,fontsize=8)
    ax.text(.98,.75,
            "Rejection threshold: 1e-7\nMedian of rejected records: "+format(med,".2e"),
            fontsize=8,ha="right",va="top",transform=ax.transAxes,
            color="#273946",bbox={"facecolor":"white","edgecolor":"none","alpha":.8})
    pdf=args.out/"kkt_rejection_distribution.pdf"
    png=args.out/"kkt_rejection_distribution.png"
    fig.savefig(pdf,bbox_inches="tight",pad_inches=.12)
    fig.savefig(png,bbox_inches="tight",pad_inches=.12,dpi=190)
    plt.close(fig)

    summary={
      "source":"frozen complete-criterion timing tensor",
      "tensor_sha256":sha256(args.tensor),
      "rows":len(df),
      "rejected_timing_rows":len(failed),
      "independent_case_seed_clusters":int(failed.groupby(["case_id","seed_index"]).ngroups),
      "recorded_criterion_counts":counts,
      "threshold":THRESHOLD,
      "min":float(failed.eta_opt.min()),
      "median":med,
      "max":float(failed.eta_opt.max()),
      "mean":float(failed.eta_opt.mean()),
      "plot":"kkt_rejection_distribution.pdf",
      "interpretation":"Conditional distribution of rejected method-level timing records; not an independent sample of error probabilities or a sample of accepted residuals.",
      "accuracy_warning":"Residual normalization differs from the standard normwise linear-system backward error."
    }
    (args.out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    failed.groupby("criterion").eta_opt.agg(["count","median","min","max"]).to_csv(
      args.out/"criterion_residual_summary.csv")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
