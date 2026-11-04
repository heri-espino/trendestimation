"""Experiment005: reproducible *descriptive* pilot analysis and AwesomeFigures.

All figures use original archived Experiment005 rows. No simulation and no
new timing call occurs here. Complete paired validity is required.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter,defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import awesomefigures as af

METHODS=("svd","eigh","banded_cholesky")
LABEL={"svd":"Shift-free SVD","eigh":"Gram eigendecomposition",
       "banded_cholesky":"Banded Cholesky"}
COLORS={"svd":"#21618c","eigh":"#b87835",
        "banded_cholesky":"#529b88"}
ORDERS=(2,3,5,6)


def csv_rows(path):
    with Path(path).open(encoding="utf8",newline="") as f:
        return list(csv.DictReader(f))


def field(row,k):
    try:
        return float(row[k])
    except (ValueError,TypeError):
        return float("nan")


def configure():
    af.set_style("elegante",palette="okabe-ito",
                 font="DejaVu Sans",use_tex=False,rasterize=False)
    plt.rcParams.update({
        "font.size":9.0,"axes.titlesize":10.0,
        "pdf.fonttype":42,"svg.fonttype":"none",
        "figure.facecolor":"white","savefig.facecolor":"white"
    })


def export(fig,out,stem):
    for extension in ("pdf","svg"):
        fig.savefig(out/(stem+"."+extension),
                    bbox_inches="tight",pad_inches=.12)
    plt.close(fig)


def paired_id(r):
    return tuple(r[k] for k in (
        "n","d","shape","noise","seed","mu_policy","criterion"))


def analyze(source,output):
    if output.exists():
        raise FileExistsError("Do not overwrite previously archived analysis: "+str(output))
    output.mkdir(parents=True)
    figures=output/"figures"
    figures.mkdir()
    configure()
    metadata=json.loads((source/"summary.json").read_text())
    fits=csv_rows(source/"fit_accuracy_runtime.csv")
    selected=csv_rows(source/"selection_accuracy_runtime.csv")
    assert len(fits)==metadata["fit_rows"]
    assert len(selected)==metadata["selection_rows"]

    fit_counts={m:dict(Counter(r["status"] for r in fits
                               if r["method"]==m)) for m in METHODS}
    select_counts={m:dict(Counter(r["status"] for r in selected
                                  if r["method"]==m)) for m in METHODS}
    valid_by_order={}
    for d in ORDERS:
        valid_by_order[str(d)]={
            m:{
                "valid":sum(r["status"]=="valid" for r in selected
                            if int(r["d"])==d and r["method"]==m),
                "total":sum(int(r["d"])==d and r["method"]==m
                            for r in selected)
            } for m in METHODS
        }

    svd={paired_id(r):r for r in selected if r["method"]=="svd"}
    eig={paired_id(r):r for r in selected if r["method"]=="eigh"}
    common=[(eig[k],svd[k]) for k in eig
            if k in svd and eig[k]["status"]=="valid"
            and svd[k]["status"]=="valid"]
    ratios=[field(e,"warm_selection_ms")/field(s,"warm_selection_ms")
            for e,s in common]
    assert len(common)>0 and all(np.isfinite(ratios))
    selected_s_gap=max(abs(field(e,"selected_s")-field(s,"selected_s"))
                       for e,s in common)
    selected_rmse_gap=max(abs(field(e,"selected_true_rmse")-
                              field(s,"selected_true_rmse"))
                          for e,s in common)
    stats={
        "experiment":"experiment005_joint_accuracy_runtime_analysis",
        "input":str(source),
        "source_summary_sha256":hashlib.sha256(
            (source/"summary.json").read_bytes()).hexdigest(),
        "raw_fit_count":len(fits),"raw_selection_count":len(selected),
        "fit_counts":fit_counts,"selection_counts":select_counts,
        "selected_valid_by_order":valid_by_order,
        "eigh_svd_complete_paired_cases":len(common),
        "eigh_over_svd_warm_time_median_ratio":statistics.median(ratios),
        "eigh_svd_max_selected_s_absolute_gap":selected_s_gap,
        "eigh_svd_max_selected_rmse_absolute_gap":selected_rmse_gap,
        "limitations":[
            "One seed per shape/noise cell: no independent-seed confidence intervals.",
            "Reported paired times are descriptive host-specific medians.",
            "Banded Cholesky had no fully valid selection grid in this pilot.",
            "Complete grid includes extreme S near 1 and analytic endpoints.",
            "Do not infer algorithmic universal optimum or forecasting accuracy.",
            "Endpoint fitting error is against an analytic, not 85-digit independent, reference."
        ]
    }

    # Figure 1: time against reference error, every individual measured fit.
    fig,ax=plt.subplots(figsize=(7.4,4.1))
    for m in METHODS:
        data=[r for r in fits if r["method"]==m
              and r["status"]!="failure"
              and np.isfinite(field(r,"reference_rel_l2"))
              and field(r,"fit_ms")>0]
        x=np.asarray([field(r,"fit_ms") for r in data])
        y=np.asarray([max(field(r,"reference_rel_l2"),1e-18) for r in data])
        ax.scatter(x,y,s=11,alpha=.30,edgecolors="none",
                   color=COLORS[m],label=f"{LABEL[m]} (n={len(data)})")
    ax.axhline(1e-5,color="#a24f4f",ls="--",lw=1,
               label=r"Admissible threshold $10^{-5}$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set(xlabel="Measured full-curve fit time (ms)",
           ylabel=r"Relative fit error versus reference",
           title="Same fitted curves: numerical error versus elapsed time")
    ax.legend(frameon=False,fontsize=7,loc="upper left")
    export(fig,figures,"paired_fit_error_vs_time")

    # Figure 2: full 17-point criterion validity rates.
    fig,ax=plt.subplots(figsize=(7.4,3.65))
    x=np.arange(len(ORDERS))
    width=.24
    for j,m in enumerate(METHODS):
        vals=[valid_by_order[str(d)][m]["valid"]/
              valid_by_order[str(d)][m]["total"]*100
              for d in ORDERS]
        bars=ax.bar(x+(j-1)*width,vals,width,label=LABEL[m],color=COLORS[m])
        for b,val in zip(bars,vals):
            ax.text(b.get_x()+b.get_width()/2,
                    max(1.,b.get_height())+1.7,f"{val:.0f}%",
                    ha="center",va="bottom",fontsize=7)
    ax.set_xticks(x,[str(d) for d in ORDERS])
    ax.set_ylim(0,112)
    ax.set(xlabel="Difference order d",
           ylabel="Valid complete selections (%)",
           title="All 17 smoothness targets required for a valid result")
    ax.legend(frameon=False,fontsize=7,ncol=3,loc="lower center",
              bbox_to_anchor=(.5,-.34))
    export(fig,figures,"complete_grid_validity")

    # Figure 3: matched-admissible SVD/eigh timings by order. Banded omitted
    # because NO full grid passed the numerical gate in these observations.
    by_d=defaultdict(list)
    for e,s in common:
        by_d[int(e["d"])].append((
            field(e,"warm_selection_ms"),field(s,"warm_selection_ms")))
    fig,ax=plt.subplots(figsize=(7.3,3.5))
    for j,m in enumerate(("svd","eigh")):
        xs=list(range(min(ORDERS),max(ORDERS)+1))
        ys=[]
        for d in xs:
            arr=by_d.get(d,[])
            ys.append(
                statistics.median(pair[1 if m=="svd" else 0]
                                  for pair in arr)
                if arr else float("nan")
            )
        # Explicit NaN at d=4 prevents interpolating a non-measured order.
        ax.plot(xs,ys,marker="o" if m=="svd" else "s",
                color=COLORS[m],lw=1.8,label=LABEL[m])
    ax.set_xticks(ORDERS)
    ax.set(xlabel="Difference order d",
           ylabel="Median warm full-selection time (ms)",
           title=f"Matched valid SVD/eigh cases (total {len(common)})")
    ax.legend(frameon=False)
    export(fig,figures,"paired_valid_selection_times")

    report=[
        "# Experiment005 — completed paired pilot",
        "",
        "These results are from a **new experiment** on one hosted Linux "
        "environment. Fit error and timing were measured for the "
        "**same numerical outputs**. 85-digit references were computed "
        "outside the measured runtime.",
        "",
        f"- {len(fits):,} individual fitted-curve observations.",
        f"- {len(selected):,} complete-grid criterion-selection attempts.",
        f"- {metadata['reference_rows']:,} matched reference records.",
        "- Grid: 17 exact normalized smoothness levels including both "
        "endpoints and values near one.",
        "- n=32,64; d=2,3,5,6; two reference-mean policies; "
        "CV/GCV/AICc/restricted-BIC/marginal ML.",
        "",
        "## Complete-workload status",
        "",
        "| Backend | Valid selections | Numerically invalid grids | "
        "Selected fit inaccurate | Failures |",
        "|---|---:|---:|---:|---:|",
    ]
    for m in METHODS:
        c=select_counts[m]
        report.append(
            f"| {LABEL[m]} | {c.get('valid',0)} | "
            f"{c.get('invalid_complete_grid',0)} | "
            f"{c.get('selected_fit_inaccurate',0)} | "
            f"{c.get('failed',0)} |")
    report.extend([
        "",
        "The failures are **not** included as fast algorithms in any "
        "accuracy–time ranking. Full-grid near-one smoothing is "
        "a demanding numerical regime.",
        "",
        f"Across {len(common)} paired, complete, accurate SVD/eigh "
        "selections, the median ratio of eigendecomposition to SVD "
        f"warm time was **{statistics.median(ratios):.3f}**. "
        "Ratios are descriptive because the pilot uses one independent "
        "seed per scenario and times are host-specific.",
        "",
        f"Maximum selected-s difference within that paired valid set: "
        f"{selected_s_gap:.3g}. Maximum selected true-trend RMSE gap: "
        f"{selected_rmse_gap:.3g}.",
        "",
        "## Methods and qualifications",
        "",
        "The first figure shows reference error against the elapsed time "
        "of the same fit. The second counts complete-grid validity, not "
        "individual successful candidate values. The third compares "
        "latencies only for matched SVD/eigh cases where both are "
        "numerically admissible; Cholesky is not ranked because it "
        "has no admissible complete-selection cases in this pilot.",
        "",
        "This is **historical latent-trend recovery** rather than forecast "
        "accuracy. BIC is restricted to S>=0.10 without claiming "
        "that this resolves the criterion's statistical pathology. "
        "The empirical reference mean is a conditional plug-in, "
        "not reestimated LOOCV or joint maximum likelihood.",
        "",
        "No confidence intervals are justified by the timing repeats, "
        "which are nested within observations. A follow-up with "
        "multiple independent random seeds, broader n and additional "
        "numerically stable structured algorithms is needed before "
        "a publication-quality global accuracy–cost frontier.",
        "",
        "## Reproduction",
        "",
        "Source: \`paper/benchmarks/experiment005/run_joint.py\`. "
        "Raw data are archived under \`paper/benchmarks/experiment005/runs/\` "
        "and are not overwritten by this analysis. "
        "Rebuild these plots from \`analyze_joint.py\` with the explicit "
        "\`--input\` and \`--out\` arguments.",
    ])
    (output/"findings.md").write_text("\n".join(report)+"\n",encoding="utf8")
    (output/"analysis.json").write_text(json.dumps(stats,indent=2)+"\n",
                                        encoding="utf8")
    (output/"manifest.json").write_text(json.dumps({
        "input_summary_sha256":stats["source_summary_sha256"],
        "outputs_sha256":{
            str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*")) if p.is_file()
            and p.name!="manifest.json"
        },
        "figure_style":"AwesomeFigures elegante / okabe-ito, vector PDF and SVG",
    },indent=2)+"\n",encoding="utf8")
    print(json.dumps({
        "valid_selected":{k:v.get("valid",0) for k,v in select_counts.items()},
        "paired_n":len(common),"paired_time_ratio":statistics.median(ratios)
    },indent=2))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    analyze(args.input,args.out)


if __name__=="__main__":
    main()
