"""Generate publication-facing matched-runtime figure and table from frozen evidence.

The original scientific data and their status masks are not modified.
This program does not execute smoothing algorithms or numerical experiments.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BASE = Path(__file__).resolve().parents[1]
FROZEN = BASE / "derived" / "42636962129"
OUT = Path(__file__).resolve().parent

# Choose representative, distinct mathematical settings; retain the full
# original tensor and matched-pair ledger for comprehensive comparisons.
SETTINGS = [
    ("pilot_cv_n64_d1_m100", "CV", 64, 1, "0"),
    ("smoke_cv_n64_d3_m100", "CV", 64, 3, "0"),
    ("pilot_cv_n128_d3_m100", "CV", 128, 3, "0"),
    ("pilot_data_cv_n128_d3_m100", "CV", 128, 3, "data"),
    ("confirm_data_cv_n256_d3_m100", "CV", 256, 3, "data"),
    ("pilot_gcv_n64_d1_m100", "GCV", 64, 1, "0"),
    ("pilot_gcv_n128_d3_m100", "GCV", 128, 3, "0"),
    ("pilot_data_gcv_n128_d3_m100", "GCV", 128, 3, "data"),
]


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def choose_all(path):
    with path.open(newline="",encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    result=[]
    for case,crit,n,d,mu in SETTINGS:
        chosen=[r for r in rows
                if r["case_id"]==case
                and r["method"]=="spectral_svd"
                and r["baseline"]=="banded_cholesky"
                and r["coordinate"]=="direct_s"
                and r["workload"]=="grid_one_series"
                and r["phase_workers"]=="24"
                and int(r["M"])==100]
        assert len(chosen)==1, (case,len(chosen))
        r=chosen[0]
        assert int(r["n"])==n and int(r["d"])==d and r["criterion"].upper()==crit
        estimate=float(r["geometric_ratio"])
        low=float(r["bootstrap95_low"])
        high=float(r["bootstrap95_high"])
        assert low < estimate < high and 1 < low
        assert int(r["independent_seeds"]) in (96,97)
        result.append({"case":case,"criterion":crit,"n":n,"d":d,"mu":mu,
                       "seeds":int(r["independent_seeds"]),
                       "ratio":estimate,"low":low,"high":high})
    return result


def write_table(path,rows):
    parts=[
       r"% Publication-facing table from the frozen paired-runtime bootstrap.",
       r"\begin{table}[t]",
       r"\caption{Matched complete-criterion cold-time ratios for 100 smoothing candidates and one series. The reference mean is fixed at zero ($\mu=0$) or computed once from the observed differences ($\mu=\overline{D_dy}$). All comparisons use the same execution phase and smoothing-coordinate policy. Intervals are 95\% percentile bootstrap intervals over independent random-seed clusters. Ratios exceeding one favor spectral SVD.}",
       r"\label{tab:empirical-paired}",
       r"\centering\small",
       r"\begin{tabular}{lrrlrrl}",
       r"\toprule",
       r"Criterion & $n$ & $d$ & Reference $\mu$ & Seeds & $\rho$ & 95\% CI\\",
       r"\midrule",
    ]
    for r in rows:
        mean = r"$\overline{D_dy}$" if r["mu"]=="data" else "$0$"
        parts.append(f'{r["criterion"]} & {r["n"]} & {r["d"]} & {mean} & {r["seeds"]} & {r["ratio"]:.2f} & [{r["low"]:.2f}, {r["high"]:.2f}]'+r"\\")
    parts.extend([r"\bottomrule",r"\end{tabular}",r"\end{table}"])
    path.write_text("\n".join(parts)+"\n",encoding="utf-8")


def make_figure(folder,rows):
    plt.rcParams.update({
      "font.family":"sans-serif","font.size":9,
      "pdf.fonttype":42,"axes.spines.top":False,
      "axes.spines.right":False,"axes.edgecolor":"#81909c",
      "axes.labelcolor":"#24394c","xtick.color":"#24394c","ytick.color":"#24394c"
    })
    fig,ax=plt.subplots(figsize=(6.8,4.05))
    colors={"CV":"#155989","GCV":"#a76631"}
    labels=[]
    for i,r in enumerate(rows):
        mu=(r"$\overline{D_dy}$" if r["mu"]=="data" else "$0$")
        labels.append(f'{r["criterion"]}: $n={r["n"]}$, $d={r["d"]}$, $\\mu={mu[1:-1]}$')
        ax.errorbar(r["ratio"],i,xerr=[[r["ratio"]-r["low"]],[r["high"]-r["ratio"]]],
                    fmt="o",ms=5,capsize=2.5,lw=1.4,color=colors[r["criterion"]])
    ax.set_yticks(range(len(rows)),labels,fontsize=8.3)
    ax.set_xlim(.7,6.2)
    ax.set_ylim(len(rows)-.4,-.6)
    ax.axvline(1,color="#66727c",ls="--",lw=1)
    ax.grid(axis="x",alpha=.2)
    ax.set_xlabel("Complete cold-time ratio  $T_{\\mathrm{banded}}/T_{\\mathrm{SVD}}$",fontsize=9)
    ax.set_title("Complete-criterion grids: matched spectral speed advantage",
                 fontsize=10.5,pad=12,weight="bold")
    ax.legend(handles=[Line2D([0],[0],marker="o",color=colors[k],lw=0,
                              label=k,markersize=6) for k in ("CV","GCV")],
              loc="lower right",frameon=False,ncol=2,fontsize=8)
    fig.tight_layout()
    folder.mkdir(parents=True,exist_ok=True)
    fig.savefig(folder/"paired_cv_gcv_publication.pdf",bbox_inches="tight",pad_inches=.10)
    fig.savefig(folder/"paired_cv_gcv_publication.png",bbox_inches="tight",pad_inches=.10,dpi=210)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=FROZEN/"paired_backend_seed_bootstrap.csv")
    p.add_argument("--output",type=Path,default=OUT)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    results=choose_all(args.source)
    write_table(args.output/"publication_table.tex",results)
    make_figure(args.output/"figures",results)
    manifest={"study":"Complete-criterion candidate-grid benchmark",
              "source_file":str(args.source).replace("\\","/"),
              "source_sha256":sha256(args.source),
              "parameter_grid_size":100,
              "comparison":"banded Cholesky / spectral SVD",
              "selection":"Eight distinct criterion/length/order/reference-mean configurations with valid matched grid comparisons",
              "worker_phase":24,"coordinate":"direct_s",
              "figure":"figures/paired_cv_gcv_publication.pdf",
              "table":"publication_table.tex",
              "interval":"Frozen independent-seed cluster bootstrap, 700 resamples",
              "results":results}
    (args.output/"publication_evidence.json").write_text(
         json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(f"Rendered {len(results)} mathematically identified comparisons; no numerical experiments rerun.")


if __name__=="__main__":
    main()
