#!/usr/bin/env python3
"""Analysis-only plots from completed experiment003 CSVs (no numerical work)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    import awesomefigures as af
except ImportError:
    af=None

COLORS=("#0072B2","#009E73","#D55E00","#CC79A7","#56B4E9","#E69F00")
WORKFLOWS=(
    "chol_lambda_cold", "chol_lambda_cached",
    "chol_S_band_eigs_cached", "spectral_S_trends",
    "spectral_S_GCV_native", "spectral_S_GCV_cached",
)
LABELS={
    "chol_lambda_cold":"Banded Cholesky, uncached λ",
    "chol_lambda_cached":"Banded Cholesky, cached λ",
    "chol_S_band_eigs_cached":"S→λ + cached Cholesky",
    "spectral_lambda_trends":"Spectral full trends, λ supplied",
    "spectral_S_trends":"S→λ + spectral full trends",
    "spectral_lambda_GCV":"Spectral GCV, λ supplied",
    "spectral_S_GCV_native":"Spectral GCV, repeated S inversion",
    "spectral_S_GCV_cached":"Spectral GCV, cached S grid",
}
ROOT=Path(__file__).resolve().parents[2]


def rows(path):
    with Path(path).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def style():
    if af is None:
        raise RuntimeError(
            "Install pinned AwesomeFigures using paper/requirements.txt; "
            "analysis plotting does not rerun benchmarks."
        )
    af.set_style("elegante",palette="okabe-ito",font="DejaVu Sans",
                 use_tex=False,rasterize=True)


def save(fig,out):
    images=[]
    for suffix in (".pdf",".svg",".png"):
        target=out.with_suffix(suffix)
        af.save_figure(fig,target,dpi=175)
        images.append(target.name)
    plt.close(fig)
    return images


def _find(r,**constraints):
    out=[]
    for record in r:
        if all(str(record[k])==str(v) for k,v in constraints.items()):
            out.append(record)
    return out


def write(run_dir):
    directory=Path(run_dir).resolve()
    manifest=directory/"manifest.json"
    if not manifest.is_file():
        raise FileNotFoundError("Require complete benchmark manifest; no rerun")
    baseline=json.loads(manifest.read_text())
    if not baseline.get("complete"):
        raise ValueError("Partial benchmark; do not label it as complete")
    source_names=(
        "raw_phases.csv","raw_workflows.csv","phase_summary.csv",
        "workflow_summary.csv","numerical_validation.csv",
        "seed_level_phases.csv","seed_level_workflows.csv",
    )
    before={name:digest(directory/name) for name in source_names}
    for name in source_names:
        if baseline["files"].get(name)!=before[name]:
            raise ArithmeticError(f"Numerical archive checksum differs: {name}")
    work=rows(directory/"workflow_summary.csv")
    phase=rows(directory/"phase_summary.csv")
    environment=json.loads((directory/"environment.json").read_text())
    style()
    images=[]

    # Scientific comparison: equal M,R,mu,d across growing n.
    fig,ax=plt.subplots(figsize=(10,5.1),layout="constrained")
    present=False
    for i,method in enumerate(WORKFLOWS):
        subset=[v for v in work if int(v["d"])==2 and int(v["M"])==21
                and int(v["R"])==4 and float(v["mu"])==0
                and v["workflow"]==method]
        subset.sort(key=lambda v:int(v["n"]))
        if len(subset)>=2:
            present=True
            ax.plot([int(v["n"]) for v in subset],
                    [float(v["median_seconds"])*1000 for v in subset],
                    marker=("o","s","^","D","v","P")[i],
                    color=COLORS[i],lw=1.7,label=LABELS[method])
    if not present:
        ax.text(.5,.5,"No matched-length scaling group in this preset",
                ha="center",va="center",transform=ax.transAxes)
    else:
        ax.set_yscale("log")
    ax.set(title="Large-series matched workload: M=21, R=4, d=2, μ=0",
           xlabel="Series length n",
           ylabel="Total elapsed time (ms; log axis where applicable)")
    ax.grid(alpha=.22)
    ax.legend(frameon=False,fontsize=8,ncol=2)
    images+=save(fig,directory/"scaling_matched_workloads")

    # Selected-size breakdown: charge conversion only to S-based strategies.
    subset=[v for v in work if int(v["d"])==2 and int(v["M"])==21
            and int(v["R"])==4 and float(v["mu"])==0]
    if subset:
        n=max(int(v["n"]) for v in subset)
        phase_lookup={v["phase"]:float(v["median_seconds"])
                      for v in phase if int(v["n"])==n
                      and int(v["d"])==2 and int(v["M"])==21
                      and int(v["R"])==4 and float(v["mu"])==0}
        setup=["bands_setup","band_eigenvalues_setup","svd_setup",
               "s_grid_map_banded","s_grid_map_svd","chol_factor_grid"]
        fig,ax=plt.subplots(figsize=(10.5,5.5),layout="constrained")
        labels=[k.replace("_"," ") for k in setup]
        amounts=[1000*phase_lookup.get(k,0) for k in setup]
        ax.barh(labels,amounts,color=COLORS[:len(labels)])
        ax.invert_yaxis()
        ax.set(xlabel="Elapsed time (ms)",
               title=f"Separately measured preparation costs: n={n}, d=2, M=21")
        ax.grid(axis="x",alpha=.2)
        images+=save(fig,directory/"preparation_breakdown")

    # R varied at constant n,d,M,mu: real reuse crossover.
    maxn=max(int(v["n"]) for v in work)
    possible=[v for v in work if int(v["d"])==2 and int(v["M"])==21
              and float(v["mu"])==0]
    if possible:
        n=max((int(v["n"]) for v in possible
               if len({int(z["R"]) for z in possible if z["n"]==v["n"]})>=2),
              default=512)
        fig,ax=plt.subplots(figsize=(9,4.7),layout="constrained")
        for i,key in enumerate(("chol_lambda_cold","chol_lambda_cached",
                                 "chol_S_band_eigs_cached","spectral_S_trends")):
            sample=[v for v in possible if int(v["n"])==n and v["workflow"]==key]
            sample.sort(key=lambda v:int(v["R"]))
            if len(sample)>=2:
                ax.plot([int(v["R"]) for v in sample],
                        [1000*float(v["median_seconds"]) for v in sample],
                        lw=1.7,color=COLORS[i],marker=("o","s","^","D")[i],
                        label=LABELS[key])
        ax.set(xlabel="Independent series R (fixed n,d,M)",
               ylabel="Total measured-component time (ms)",
               title=f"Reuse versus independent series, n={n}, d=2, M=21")
        ax.grid(alpha=.22)
        ax.legend(frameon=False,fontsize=8)
        images+=save(fig,directory/"reused_series")

    # Automatically authored CSV-backed report, never guessed timings.
    text=[
        "# Experiment003 — Archived results",
        "",
        f"- Run folder: \`{directory.name}\`",
        f"- Preset: \`{environment['preset']}\`",
        f"- Python and SciPy versions: {environment['python'].split()[0]}, "
        f"{environment['scipy']}",
        f"- Numerical precision: float64; BLAS threads: {environment['blas_threads']}",
        f"- Root source revision: \`{environment['git_revision']}\`",
        f"- Numerical maximum absolute trend error: "
        f"{environment['max_abs_trend_error']:.3e}",
        "",
        "**Interpretation:** These are within-host technical timing medians. "
        "Seed-level medians are separately archived. They are not "
        "publication-grade uncertainty intervals by themselves.",
        "",
        "## Matched-workload end-to-end costs",
        "",
        "All times below include appropriate setup, mapping and/or "
        "factorization costs. These are sums of separately measured "
        "components, not a single independently timed monolithic call.",
        "",
        "| n | d | M | R | μ | Workflow | Median total (ms) |",
        "|---:|---:|---:|---:|---:|---|---:|",
    ]
    for v in sorted(work,key=lambda r:(
        int(r["n"]),int(r["d"]),int(r["M"]),int(r["R"]),float(r["mu"]),
        r["workflow"])):
        text.append("| {n} | {d} | {M} | {R} | {mu} | {work} | {ms:.3f} |".format(
            n=v["n"],d=v["d"],M=v["M"],R=v["R"],mu=v["mu"],
            work=LABELS.get(v["workflow"],v["workflow"]),
            ms=1000*float(v["median_seconds"])))
    text+=["","## Figures","","All diagrams use pinned AwesomeFigures APIs."]
    text.extend("- "+filename for filename in images)
    text+=["","## Limitations",
        "- Do not compare distinct M or R as if only n changed.",
        "- The S-grid and internal penalties are matched across solvers.",
        "- The known-lambda baseline intentionally omits the cost of choosing S.",
        "- S inversion from banded eigenvalues costs setup and iterations; "
        "it is not free or inherent to a Cholesky factorization.",
        "- GCV scoring uses the spectral eigensystem; it is a different "
        "workload from M full reconstructed trends.",
        "- The timings are hardware-, thread-, workload- and reuse-dependent.",
        "- Technical repetitions are not independent data seeds.",
        ""]
    (directory/"ANALYSIS.md").write_text("\n".join(text),encoding="utf-8")
    after={name:digest(directory/name) for name in source_names}
    if before!=after:
        raise RuntimeError("Numerical result changed during analysis")
    checks=json.loads(manifest.read_text())
    checks["analysis_files"]={
        p.name:digest(p) for p in directory.iterdir()
        if p.name=="ANALYSIS.md" or p.name in images
    }
    (directory/"manifest.json").write_text(
        json.dumps(checks,indent=2)+"\n",encoding="utf-8")
    )
    print(f"[experiment003] Saved {len(images)} AwesomeFigures images; "
          "all numerical CSV checksums unchanged.",flush=True)
    return images


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir",type=Path,required=True)
    args=parser.parse_args()
    write(args.run_dir)


if __name__=="__main__":
    main()
