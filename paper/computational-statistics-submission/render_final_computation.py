"""Transform archived paired solver and inversion timings into journal artifacts.

Inputs MUST be measured by the VM. No simulation or synthetic timing values
are created in this renderer. Source paths and numeric validity checked.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from contrast_theme import (
    apply as apply_contrast, METHODS as METHOD_COLORS,
    SERIES as CONTRAST_SERIES, INK, MUTED, GRID,
)
apply_contrast()

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
STUDY=HERE/"research"/"final_vm"
PLOTS=HERE/"figures"


def _csv(path:Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"Measured research file missing: {path}")
    with path.open(newline="",encoding="utf-8") as fh:
        result=list(csv.DictReader(fh))
    if not result:
        raise ValueError(f"Empty measured result table: {path}")
    return result


def _tex(value:float,places:int=3) -> str:
    return f"{float(value):.{places}f}"


def _publication_sources() -> list[str]:
    """Copy audited existing Windows full-S charts into the submission."""
    PLOTS.mkdir(parents=True,exist_ok=True)
    names=(
        "windows_full_s_workloads",
        "windows_full_s_grid_coordinates",
        "windows_full_s_reuse_d",
        "windows_full_s_bounded",
        "windows_full_s_means",
    )
    copied=[]
    for name in names:
        for suffix in (".pdf",".svg"):
            source=REPO/"paper"/"figures"/(name+suffix)
            if not source.exists():
                raise FileNotFoundError(
                    f"Existing audited 80,640-search figure not found: {source}"
                )
            target=PLOTS/(name+suffix)
            if target.exists() and hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(source.read_bytes()).digest():
                continue
            shutil.copy2(source,target)
            copied.append(str(target.relative_to(REPO)))
    return copied


def _inversion(rows:list[dict]) -> dict:
    valid=[r for r in rows if int(r["d"])>0]
    for r in valid:
        if int(r["trials"])<1:
            raise ValueError("Empty root inversion comparison")
        if int(r["failures"])>int(r["trials"]):
            raise ValueError("Impossible inversion failure count")
    # Full method outcomes for two target smoothness levels (n=120,d=2
    # when available, otherwise choose an explicitly reported valid case).
    scenarios=sorted({(int(r["n"]),int(r["d"])) for r in valid})
    n,d=(120,2) if (120,2) in scenarios else scenarios[-1]
    targets=(".5",".98999999999999999")
    selected=[r for r in valid if int(r["n"])==n and int(r["d"])==d]
    by_target={}
    for r in selected:
        key=float(r["target"])
        if np.isclose(key,.5,atol=1e-15,rtol=0):
            by_target.setdefault(".5",[]).append(r)
        if np.isclose(key,.99,atol=1e-15,rtol=0):
            by_target.setdefault(".99",[]).append(r)
    lines=[
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"$S$ & Inversion method & Median $\mu$s & Fail / trials & Iterations & Max rel. tail error \\",
        r"\midrule",
    ]
    for key in (".5",".99"):
        if key not in by_target:
            raise ValueError(f"Missing target {key} for comparison")
        entries={r["method"]:r for r in by_target[key]}
        for method in ("brentq","newton","secant","bisect"):
            r=entries[method]
            med="NA" if not r["median_us"] else _tex(r["median_us"],2)
            steps="NA" if not r["median_iterations"] else _tex(r["median_iterations"],1)
            err=("NA" if not r["max_relative_tail_error"] else
                 f"{float(r['max_relative_tail_error']):.2g}")
            lines.append(
                f"{key} & {method} & {med} & "
                f"{r['failures']}/{r['trials']} & {steps} & {err}" + r" \\"
            )
    lines.extend([r"\bottomrule",r"\end{tabular}",""])
    (HERE/"final_inversion_table.tex").write_text(
        "\n".join(lines),encoding="utf-8",
    )

    fig,ax=plt.subplots(figsize=(7.7,4.4),layout="constrained")
    colors={"brentq":CONTRAST_SERIES[0],"newton":CONTRAST_SERIES[1],
            "secant":CONTRAST_SERIES[2],"bisect":CONTRAST_SERIES[3]}
    for method in ("brentq","newton","secant","bisect"):
        points=sorted((r for r in selected
                       if r["method"]==method and r["median_us"] is not None),
                      key=lambda x:float(x["target"]))
        xs=[np.log(float(r["target"])/(1-float(r["target"]))) for r in points]
        ys=[float(r["median_us"]) for r in points]
        ax.plot(xs,ys,color=colors[method],lw=1.7,marker="o",ms=4,label=method)
        failing=[r for r in points if int(r["failures"])]
        if failing:
            ax.scatter([np.log(float(r["target"])/(1-float(r["target"])))
                        for r in failing],
                       [float(r["median_us"]) for r in failing],
                       facecolors="none",edgecolors=CONTRAST_SERIES[5],s=70,zorder=5)
    ax.set(title=f"Smoothness inversion: n={n}, d={d}, float64",
           xlabel="Logit of target normalized smoothness",
           ylabel="Median successful call time (microseconds)")
    ax.set_yscale("log")
    ax.grid(alpha=.22)
    ax.legend(frameon=False,ncol=2)
    for suffix in ("pdf","svg","png"):
        fig.savefig(PLOTS/f"final_inversion_speed.{suffix}",dpi=160)
    plt.close(fig)
    return {"n":n,"d":d,"failed_trials":
            int(sum(int(r["failures"]) for r in valid)),
            "total_trials":int(sum(int(r["trials"]) for r in valid))}


def _solvers(timing:list[dict], comparisons:list[dict]) -> dict:
    # Explicitly select a few fixed mu=0 workloads. Complete 21-case
    # quick benchmark still gets Holm correction across ALL comparisons.
    selected=[r for r in comparisons
              if int(r["order"])==2 and float(r["mu"])==0 and
              int(r["evaluations"]) in (1,16,64)
              and r["method_a"]=="svd" and r["method_b"]=="cholesky"]
    selected.sort(key=lambda r:(int(r["n"]),int(r["evaluations"])))
    if not selected:
        selected=[r for r in comparisons
                  if r["method_a"]=="svd" and r["method_b"]=="cholesky"]
        selected.sort(key=lambda r:(int(r["n"]),int(r["evaluations"])))
    # Compact main-text 6 or fewer preselected examples; full data in CSV.
    display=selected[:6]
    lines=[
        r"\begin{tabular}{rrrrrr}",
        r"\toprule",
        r"$n$ & $d$ & $M$ & SVD / BChol & 95\% pointwise CI & Holm $p$ \\",
        r"\midrule",
    ]
    for r in display:
        p=r["p_holm_familywise"]
        pp="NA" if p in (None,"") else f"{float(p):.3g}"
        lines.append(
            f"{r['n']} & {r['order']} & {r['evaluations']} & "
            f"{_tex(r['speedup_a_over_b'],2)} & "
            f"[{_tex(r['ci95_low'],2)}, {_tex(r['ci95_high'],2)}] & "
            f"{pp}" + r" \\"
        )
    lines.extend([r"\bottomrule",r"\end{tabular}",""])
    (HERE/"final_solver_inference_table.tex").write_text(
        "\n".join(lines),encoding="utf-8",
    )
    relevant=[r for r in selected if int(r["order"])==2 and int(r["evaluations"])==16]
    if len(relevant)<2:
        relevant=selected
    relevant=sorted(relevant,key=lambda r:(int(r["n"]),int(r["evaluations"])))
    fig,ax=plt.subplots(figsize=(7.7,4.2),layout="constrained")
    xx=np.arange(len(relevant))
    ratios=np.array([float(r["speedup_a_over_b"]) for r in relevant])
    low=np.array([float(r["ci95_low"]) for r in relevant])
    upper=np.array([float(r["ci95_high"]) for r in relevant])
    ax.errorbar(xx,ratios,yerr=[ratios-low,upper-ratios],
                fmt="o",capsize=4,color=CONTRAST_SERIES[0])
    ax.axhline(1,ls=":",color=INK)
    ax.set_xticks(xx,[f"n={r['n']}, M={r['evaluations']}" for r in relevant],
                  rotation=16)
    ax.set(title="Paired SVD vs banded Cholesky: full trend workloads",
           ylabel="Geometric mean total-time ratio SVD / BChol")
    ax.grid(axis="y",alpha=.22)
    for suffix in ("pdf","svg","png"):
        fig.savefig(PLOTS/f"final_solver_inference.{suffix}",dpi=160,bbox_inches="tight")
    plt.close(fig)
    valid_p=[r for r in comparisons if r["p_holm_familywise"] not in (None,"")]
    sig=sum(float(r["p_holm_familywise"])<.05 for r in valid_p)
    return {"primary_comparisons":len(comparisons),
            "holm_tested":len(valid_p),"holm_significant":sig,
            "selected_rows":len(display)}


def render() -> dict:
    root=STUDY/"inversion"
    solver=STUDY/"solver"
    analysis=solver/"analysis"
    study=_csv(root/"summary.csv")
    timing=_csv(analysis/"timing_summary.csv")
    comparison=_csv(analysis/"paired_comparisons.csv")
    inversion_info=_inversion(study)
    solver_info=_solvers(timing,comparison)
    copied=_publication_sources()
    env={
        "inversion":json.loads((root/"environment.json").read_text(encoding="utf-8")),
        "solvers":json.loads((solver/"study_metadata.json").read_text(encoding="utf-8")),
        "solver_inference":json.loads(
            (analysis/"analysis_manifest.json").read_text(encoding="utf-8")),
        "results":{"inversion":inversion_info,"solvers":solver_info},
        "archived_windows_80k_figures_copied":copied,
    }
    (STUDY/"final_report_manifest.json").write_text(
        json.dumps(env,indent=2)+"\n",encoding="utf-8",
    )
    lines=[
        r"\noindent\textit{Author-host study.} ",
        f"Paired solver: {env['solvers']['independent_seeds']} independently seeded "
        f"data replicates per workload, {env['solvers']['timing_blocks_per_seed']} "
        "randomized timing blocks per seed, ",
        f"{len(env['solvers']['workload_cases'])} workload configurations, "
        f"{solver_info['primary_comparisons']} pairwise comparisons "
        f"({solver_info['holm_tested']} eligible for Holm adjustment). "
        "Inversion: ",
        f"{env['inversion']['repeats']} randomized timing blocks for each "
        "target, solver and finite-difference order, with ",
        f"{inversion_info['failed_trials']}/{inversion_info['total_trials']} "
        "failed attempted inversions for non-analytic orders. "
        "Timing repeats on one machine are not independent samples; "
        "bootstrap CIs are pointwise, not familywise adjusted. "
        "All comparisons are conditional on the archived host, "
        "numerical precision, software and workload. ",
    ]
    (HERE/"final_computation_environment.tex").write_text(
        "\n".join(lines)+"\n",encoding="utf-8",
    )
    print("[paper] Rendered measured solver/root tables, plots and archived Windows figures.")
    return env


if __name__=="__main__":
    render()
