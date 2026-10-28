#!/usr/bin/env python3
"""Render expanded SN Computer Science tables and figures from archived results.

No Monte Carlo, no criterion tuning, no new timings, no root-solver benchmark.
Deterministically reconstruct fitted curves at SAVED lambda and mu only.
The two source hashes and archived numerical results remain immutable.

Run from repository root:
  python paper/computational-statistics-submission/sncs_expand_results.py
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
import numpy as np

from contrast_theme import (
    apply, INK, OBSERVED, TREND, GRID,
    METHODS as METHOD_COLORS, ORDER_COLORS, ORDER_MARKERS,
)
from make_current_examples import load_series
from sncs_dashboard import read_results, METHODS, ORDERS
from trendestimation import TrendSmoother

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DATA=HERE/"data"
BENCH=ROOT/"paper"/"benchmarks"
VM=HERE/"research"/"final_vm"
FIGURES=HERE/"figures"
METHOD_NAMES={"cv":"CV","gcv":"GCV","aicc":"AICc",
              "bic":"BIC","mle":"MLE","controlled":"Controlled"}
SERIES=(
    ("co2_full","Mauna Loa CO$_2$","ppm",
     "noaa_mlo_monthly_1990_2026_09.csv","average_ppm"),
    ("fedfunds_full","Effective federal funds rate","percentage points",
     "fred_fedfunds_2010_2026_09.csv","value"),
)
SOURCE_PATHS=(
    BENCH/"windows_full_s_analysis"/"selected_s.csv",
    BENCH/"full_s_reference"/"s_lambda_grid.csv",
    VM/"solver"/"analysis"/"paired_comparisons.csv",
    VM/"inversion"/"summary.csv",
    DATA/"co2_full_dashboards.json",
    DATA/"fedfunds_full_dashboards.json",
    DATA/"noaa_mlo_monthly_1990_2026_09.csv",
    DATA/"fred_fedfunds_2010_2026_09.csv",
)


def _hash(p:Path)->str:
    if not p.is_file():
        raise FileNotFoundError("Missing archived result, do not rerun experiment: "+str(p))
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _rows(path:Path)->list[dict]:
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _save(fig:plt.Figure,name:str)->list[str]:
    FIGURES.mkdir(parents=True,exist_ok=True)
    files=[]
    for ext in ("pdf","svg","png"):
        dest=FIGURES/(name+"."+ext)
        fig.savefig(dest,dpi=180,bbox_inches="tight",facecolor="white")
        files.append(str(dest.relative_to(ROOT)))
    plt.close(fig)
    return files


def _tex(name:str,body:list[str])->str:
    dst=HERE/name
    dst.write_text("\n".join(body)+"\n",encoding="utf-8")
    return str(dst.relative_to(ROOT))


def search_coordinates()->tuple[str,list[str]]:
    """All five criteria and both mu values; no averaged incompatible grids."""
    rows=_rows(BENCH/"windows_full_s_analysis"/"selected_s.csv")
    chosen=[r for r in rows if int(r["n"])==48 and int(r["d"])==2
            and float(r["mu"]) in (0,.15)]
    if len(chosen)!=10:
        raise ValueError(f"Expected 10 archived coordinate comparisons, got {len(chosen)}")
    chosen.sort(key=lambda r:(float(r["mu"]),METHODS.index(r["criterion"])))
    body=[
        r"\begin{tabular}{llrrrrr}",
        r"\toprule",
        r"Fixed $\mu$ & Criterion & $S_{\mathrm{native}}$ & Native $S$ & Mapped $\lambda$ & Log-$\lambda$ & $S_{\log\lambda}$ \\",
        r"\midrule",
    ]
    for r in chosen:
        body.append(
            f"{float(r['mu']):.2f} & {METHOD_NAMES[r['criterion']]} & "
            f"{float(r['native_s_S']):.3f} & "
            f"{float(r['native_s_ms']):.3f} & "
            f"{float(r['mapped_s_lambda_ms']):.3f} & "
            f"{float(r['native_log_lambda_ms']):.3f} & "
            f"{float(r['native_log_lambda_S']):.3f}" + r" \\"
        )
    body.extend([r"\bottomrule",r"\end{tabular}"])
    result=_tex("sncs_coordinate_methods_table.tex",body)
    apply()
    fig,axes=plt.subplots(1,2,figsize=(12,4.2),layout="constrained")
    colors={"native_s":"#0072B2","mapped_s_lambda":"#009E73",
            "native_log_lambda":"#D55E00"}
    for ax,mu in zip(axes,(0,.15)):
        subset=[r for r in chosen if np.isclose(float(r["mu"]),mu)]
        x=np.arange(5)
        for policy,key,label in (
            ("native_s","native_s_ms","Native S"),
            ("mapped_s_lambda","mapped_s_lambda_ms","Mapped S → λ"),
            ("native_log_lambda","native_log_lambda_ms","Log-λ: distinct grid"),
        ):
            ax.plot(x,[float(r[key]) for r in subset],
                    color=colors[policy],marker="o",
                    ls="--" if policy=="native_log_lambda" else "-",
                    label=label,lw=1.8)
        ax.set_xticks(x,[METHOD_NAMES[r["criterion"]] for r in subset])
        ax.set(title=f"Fixed reference mean μ={mu:g}",ylabel="Median full-search time (ms)")
        ax.grid(alpha=.22)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc="outside upper center",ncol=3,frameon=False)
    fig.suptitle("Same-grid native S versus pretranslated λ; log-λ uses different candidates",
                 fontsize=11,weight="bold")
    return result,_save(fig,"sncs_coordinate_methods")


def solver_by_order()->str:
    rows=_rows(VM/"solver"/"analysis"/"paired_comparisons.csv")
    # Changes in d and mu explicitly supported in independently replicated paired design.
    cases=((96,1,16,0.),(96,2,16,0.),(96,2,16,.15),
           (96,3,16,0.),(96,5,16,0.),
           (32,2,1,0.),(32,2,64,0.))
    body=[
        r"\begin{tabular}{rrrrrll}",
        r"\toprule",
        r"$n$ & $d$ & $M$ & $\mu$ & SVD/BChol & 95\% pointwise CI & Holm $p$ \\",
        r"\midrule",
    ]
    for n,d,m,mu in cases:
        matched=[r for r in rows if int(r["n"])==n and int(r["order"])==d
                 and int(r["evaluations"])==m and np.isclose(float(r["mu"]),mu)
                 and r["method_a"]=="svd" and r["method_b"]=="cholesky"]
        if len(matched)!=1:
            raise ValueError(f"Expected exactly one archived paired comparison {(n,d,m,mu)}")
        r=matched[0]
        body.append(
            f"{n} & {d} & {m} & {mu:.2f} & "
            f"{float(r['speedup_a_over_b']):.3f} & "
            f"[{float(r['ci95_low']):.3f}, {float(r['ci95_high']):.3f}] & "
            f"{float(r['p_holm_familywise']):.4g}" + r" \\"
        )
    body.extend([r"\bottomrule",r"\end{tabular}"])
    return _tex("sncs_solver_orders_table.tex",body)


def real_data_summary()->str:
    body=[
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Series & Criterion & $\lambda$ & $S$ & RMSE & MAE \\",
        r"\midrule",
    ]
    for label,slug in (("CO$_2$","co2_full"),("FEDFUNDS","fedfunds_full")):
        data,_=read_results(slug)
        for method in METHODS:
            r=data["records"]["zero"][f"d2_{method}"]
            body.append(
                f"{label} & {METHOD_NAMES[method]} & "
                f"{float(r['lambda']):.3g} & {float(r['s']):.3f} & "
                f"{float(r['rmse']):.3f} & {float(r['mae']):.3f}" + r" \\"
            )
        if slug=="co2_full":
            body.append(r"\midrule")
    body.extend([r"\bottomrule",r"\end{tabular}"])
    return _tex("sncs_realdata_table.tex",body)


def series_trends()->list[str]:
    """Reconstruct fits at previously saved penalties; NO parameter selection."""
    apply()
    fig,axes=plt.subplots(2,1,figsize=(11,7.2),layout="constrained")
    shown=("cv","aicc","mle","controlled")
    lines={"cv":"-","aicc":"--","mle":":","controlled":"-."}
    for ax,(slug,title,units,file,column) in zip(axes,SERIES):
        dates,y=load_series(DATA/file,column)
        cache,_=read_results(slug)
        model=TrendSmoother(len(y),order=2)
        ax.plot(dates,y,lw=1.1,color=OBSERVED,alpha=.75,label="Observed")
        for method in shown:
            result=cache["records"]["zero"][f"d2_{method}"]
            fit=model.fit(y,lambda_=float(result["lambda"]),
                          mu=float(result["mu"]))
            if not np.isclose(fit.smoothness,float(result["s"]),atol=2e-7):
                raise ArithmeticError(f"Saved S mismatch in {slug}/{method}")
            ax.plot(dates,fit.trend,lw=1.7,ls=lines[method],
                    color=METHOD_COLORS[method],
                    label=f"{METHOD_NAMES[method]}: S={result['s']:.2f}")
        ax.set(title=title,ylabel=units)
        ax.grid(alpha=.2)
        ax.legend(loc="best",frameon=False,ncol=3,fontsize=8)
    fig.suptitle("Observed monthly series and saved-parameter PLS trends (d=2, μ=0)",
                 fontsize=13,weight="bold")
    return _save(fig,"sncs_observed_trends")


def orders_trends()->list[str]:
    """Controlled S=.86 across four d, highlighting geometry differs."""
    apply()
    fig,axes=plt.subplots(2,1,figsize=(11,7),layout="constrained")
    for ax,(slug,title,units,file,column) in zip(axes,SERIES):
        dates,y=load_series(DATA/file,column)
        cache,_=read_results(slug)
        window=120 if slug=="co2_full" else 100
        ax.plot(dates[-window:],y[-window:],color=OBSERVED,lw=1,
                alpha=.75,label="Observed")
        for d in ORDERS:
            result=cache["records"]["zero"][f"d{d}_controlled"]
            model=TrendSmoother(len(y),order=d)
            fit=model.fit(y,lambda_=float(result["lambda"]),mu=0.)
            if not np.isclose(fit.smoothness,float(result["s"]),atol=2e-7):
                raise ArithmeticError(f"Controlled S mismatch in {slug}/d{d}")
            ax.plot(dates[-window:],fit.trend[-window:],lw=1.6,
                    color=ORDER_COLORS[d],label=f"d={d}",
                    marker=ORDER_MARKERS[d],markevery=max(1,window//12),ms=3)
        ax.set(title=title,ylabel=units)
        ax.grid(alpha=.2)
        ax.legend(loc="best",ncol=5,frameon=False,fontsize=8)
    fig.suptitle("Same controlled S=0.86, different difference-order trend geometries",
                 fontsize=13,weight="bold")
    return _save(fig,"sncs_orders_trends")


def smoothness_mapping()->list[str]:
    """Only read archived S ↔ λ lookups; no numerical inversions."""
    rows=_rows(BENCH/"full_s_reference"/"s_lambda_grid.csv")
    apply()
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout="constrained")
    for d in ORDERS:
        x=[r for r in rows if int(r["n"])==24 and int(r["d"])==d
           and np.isfinite(float(r["lambda_"])) and 0<float(r["S"])<1]
        x.sort(key=lambda r:float(r["S"]))
        if len(x)<12:
            raise ValueError("Expected archived S-to-lambda tail for each difference order")
        s=np.array([float(r["S"]) for r in x])
        l=np.array([float(r["lambda_"]) for r in x])
        axes[0].plot(s,np.log10(l),lw=1.65,color=ORDER_COLORS[d],
                     marker=ORDER_MARKERS[d],ms=3,label=f"d={d}")
        axes[1].plot(s,np.log10(l),lw=1.65,color=ORDER_COLORS[d],
                     marker=ORDER_MARKERS[d],ms=3,label=f"d={d}")
    axes[0].set(xlim=(.01,.99),xlabel="Normalized S",ylabel="log10(lambda)",
                title="Interior smoothness coordinate")
    axes[1].set(xlim=(.94,1.005),xlabel="Normalized S (near 1)",
                ylabel="log10(lambda)",title="Boundary-tail growth")
    for ax in axes: ax.grid(alpha=.2)
    axes[0].legend(frameon=False,ncol=2)
    fig.suptitle("Archived inverse mappings: the same S requires different λ across orders (n=24)",
                 fontsize=12,weight="bold")
    return _save(fig,"sncs_smoothness_mapping")


def render()->dict:
    before={str(p.relative_to(ROOT)):_hash(p) for p in SOURCE_PATHS}
    figures=[]
    table_coord,art=search_coordinates()
    figures+=art
    tables=[table_coord,solver_by_order(),real_data_summary()]
    figures+=series_trends()
    figures+=orders_trends()
    figures+=smoothness_mapping()
    after={str(p.relative_to(ROOT)):_hash(p) for p in SOURCE_PATHS}
    if before!=after:
        raise RuntimeError("Archived experiment changed during figure rendering")
    report={"operation":"render-only","source_sha256":before,"unchanged":True,
            "tables":tables,"figures":figures,
            "notes":(
                "Archived solver, mapping, selection and timing results only. "
                "PLS curves reconstructed deterministically at saved lambda and mu; "
                "no criterion optimization, root inversion or benchmark performed. "
                "Native S and mapped S-to-lambda share penalty candidates, "
                "whereas the independent log-lambda grid differs."
            )}
    (HERE/"sncs_expanded_render_manifest.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8"
    )
    print(f"Rendered {len(tables)} tables and {len(figures)} plot files "
          "with all 9 saved numerical inputs unchanged.",flush=True)
    return report


def main()->None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    render()


if __name__=="__main__":
    main()
