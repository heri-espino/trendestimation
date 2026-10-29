"""Experiment005: compute eligible-only accuracy/runtime frontiers from saved CSVs.

This script never reruns benchmarks or invents data. It preserves all failure
counts, uses median CPU durations within defined design cells, and writes
a machine-readable analysis. Optional AwesomeFigures vector plots use
the saved data, not a recomputed model.

Usage:
    python paper/benchmarks/experiment005/analyze.py --run <run-directory>
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


def read_rows(path):
    with path.open(newline="",encoding="utf8") as f:
        return list(csv.DictReader(f))


def numeric(row,name):
    try:
        x=float(row[name])
        return x if math.isfinite(x) else None
    except (ValueError,TypeError,KeyError):
        return None


def pareto(groups,xkey,ykey):
    """Find admissible nondominated points (both objectives minimized)."""
    valid=[x for x in groups if x["eligible"] and
           math.isfinite(x[xkey]) and math.isfinite(x[ykey])]
    return [
        x for x in valid if not any(
            (other[xkey]<=x[xkey] and other[ykey]<=x[ykey]) and
            (other[xkey]<x[xkey] or other[ykey]<x[ykey])
            for other in valid if other is not x
        )
    ]


def summarize(path):
    fit=read_rows(path/"fit_accuracy_timing.csv")
    sel=read_rows(path/"selection_accuracy_timing.csv")
    result={"source_run":path.name,
            "definitions":{
                "numerical_error":"relative L2 versus frozen-penalty independent multiprecision trend",
                "statistical_error":"RMSE to known latent historical trend, not forecast error",
                "time":"same-run CPU wall-clock timing; fits are medians of repeated measurements",
                "eligible":"ALL original rows in group have status ok, with verified entire criterion grid",
                "uncertainty":"pilot has too few independent seeds for uncertainty claims"
            },
            "fit_groups":[],"selection_groups":[],"fit_frontiers":[],
            "selection_frontiers":[]}
    by_fit=defaultdict(list)
    for row in fit:
        key=(int(row["n"]),int(row["d"]),row["shape"],row["noise"],
             row["mu_policy"],row["method"])
        by_fit[key].append(row)
    for key,rows in sorted(by_fit.items()):
        err=[numeric(r,"relative_l2_numerical_error") for r in rows]
        times=[numeric(r,"fit_median_seconds") for r in rows]
        truth=[numeric(r,"true_trend_rmse") for r in rows]
        good=all(r["status"]=="ok" for r in rows)
        clean=lambda a:[x for x in a if x is not None]
        result["fit_groups"].append(dict(
            n=key[0],d=key[1],shape=key[2],noise=key[3],
            mu_policy=key[4],method=key[5],observations=len(rows),
            failures=sum(r["status"]!="ok" for r in rows),
            eligible=bool(good and len(clean(err))==len(rows)),
            median_numerical_error=statistics.median(clean(err)) if clean(err) else None,
            max_numerical_error=max(clean(err)) if clean(err) else None,
            median_fitting_ms=1000*statistics.median(clean(times)) if clean(times) else None,
            median_statistical_rmse=statistics.median(clean(truth)) if clean(truth) else None
        ))
    by_select=defaultdict(list)
    for row in sel:
        key=(int(row["n"]),int(row["d"]),row["shape"],row["noise"],
             row["mu_policy"],row["criterion"],row["backend"],row["policy"])
        by_select[key].append(row)
    for key,rows in sorted(by_select.items()):
        t=[numeric(r,"warm_selection_fit_seconds") for r in rows]
        error=[numeric(r,"numerical_relative_l2_error") for r in rows]
        rmse=[numeric(r,"true_trend_rmse") for r in rows]
        good=all(r["status"]=="ok" and
                 r["complete_grid_valid"]=="True" for r in rows)
        clean=lambda a:[x for x in a if x is not None]
        result["selection_groups"].append(dict(
            n=key[0],d=key[1],shape=key[2],noise=key[3],
            mu_policy=key[4],criterion=key[5],backend=key[6],
            policy=key[7],observations=len(rows),
            failures=sum(r["status"]!="ok" for r in rows),
            eligible=bool(good and len(clean(error))==len(rows)
                          and len(clean(rmse))==len(rows)),
            median_numerical_error=statistics.median(clean(error)) if clean(error) else None,
            median_time_ms=1000*statistics.median(clean(t)) if clean(t) else None,
            median_latent_rmse=statistics.median(clean(rmse)) if clean(rmse) else None,
            median_oracle_gap=statistics.median(
                clean([numeric(r,"excess_oracle_rmse") for r in rows]))
                if any(numeric(r,"excess_oracle_rmse") is not None for r in rows) else None
        ))
    # Never pool distinct n,d or DGP; compare methods within matched groups.
    fit_sets=defaultdict(list)
    for x in result["fit_groups"]:
        fit_sets[tuple(x[k] for k in ("n","d","shape","noise","mu_policy"))].append(x)
    for key,groups in fit_sets.items():
        eligible=pareto(
            [{**g,"time":g["median_fitting_ms"] or math.inf,
              "err":g["max_numerical_error"] if g["max_numerical_error"] is not None else math.inf}
             for g in groups],
            "time","err")
        for e in eligible:
            result["fit_frontiers"].append({k:e[k] for k in (
                "n","d","shape","noise","mu_policy","method",
                "median_fitting_ms","max_numerical_error")})
    sel_sets=defaultdict(list)
    for x in result["selection_groups"]:
        sel_sets[tuple(x[k] for k in (
            "n","d","shape","noise","mu_policy","criterion"))].append(x)
    for key,groups in sel_sets.items():
        eligible=pareto(
            [{**g,"time":g["median_time_ms"] or math.inf,
              "rmse":g["median_latent_rmse"] if g["median_latent_rmse"] is not None else math.inf}
             for g in groups],"time","rmse")
        for e in eligible:
            result["selection_frontiers"].append({
                k:e[k] for k in ("n","d","shape","noise",
                               "mu_policy","criterion","backend","policy",
                               "median_time_ms","median_latent_rmse")})
    return result


def figures(summary,run):
    """Optional AwesomeFigures vector scatter; no LaTeX dependency."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import awesomefigures as af
    except ImportError:
        return False
    af.set_style("elegante",palette="okabe-ito",font="DejaVu Sans",
                 use_tex=False,rasterize=True)
    out=run/"figures"
    out.mkdir(exist_ok=True)
    # Accuracy-time on precisely the same frozen-S fit cases.
    for d in sorted({r["d"] for r in summary["fit_groups"]}):
        # Keep each DGP distinct: pilot plots use smooth/iid, fixed mu=0.
        points=[r for r in summary["fit_groups"]
                if r["d"]==d and r["shape"]=="smooth" and
                r["noise"]=="iid" and r["mu_policy"]=="fixed_zero"]
        if not points:continue
        fig,ax=plt.subplots(figsize=(6.4,4))
        for r in points:
            x=r["median_fitting_ms"];y=r["max_numerical_error"]
            if x is None or y is None or x<=0:continue
            ax.scatter(x,max(y,1e-18),s=47,marker="o" if r["eligible"] else "x",
                       label=r["method"])
        ax.set(xscale="log",yscale="log",
               xlabel="Median complete fit (ms)",
               ylabel="Maximum numerical relative L2 error",
               title=f"Experiment005: frozen-S paired fit, d={d}")
        ax.legend(fontsize=6,ncol=2,frameon=False)
        fig.tight_layout()
        fig.savefig(out/f"fit_numerical_vs_time_d{d}.pdf")
        fig.savefig(out/f"fit_numerical_vs_time_d{d}.svg")
        plt.close(fig)
    return True


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run",required=True,type=Path)
    a=p.parse_args()
    if not a.run.is_dir():p.error("Run directory not found")
    report=summarize(a.run)
    figures(report,a.run)
    dest=a.run/"analysis.json"
    dest.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps({"fit_groups":len(report["fit_groups"]),
                      "selection_groups":len(report["selection_groups"]),
                      "fit_frontier_rows":len(report["fit_frontiers"]),
                      "selection_frontier_rows":len(report["selection_frontiers"])},indent=2))


if __name__=="__main__":
    main()
