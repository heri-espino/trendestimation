"""Rebuild computational CSDA figures from immutable benchmark CSV archives.

No synthetic timing data, reconstructed experiment, or benchmark re-execution.
Uses the same CAS/TeX-aware AwesomeFigures renderer as the accuracy paper.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from publication_style import (
    configure_publication, publication_export, finish_manifest,
)

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parents[1]
BENCH = ROOT / "paper" / "benchmarks"
RAW = BENCH / "results" / "full_s_search_modes"
FIG = PAPER / "figures"
FIG.mkdir(exist_ok=True)
BLUE = "#2867a0"
CYAN = "#3697bd"
COLORS = ["#18334c", "#2867a0", "#3697bd", "#5c89a6",
          "#7c6b91", "#ac784d", "#7b8794"]
METHODS = (
    ("dense_fresh", "Dense fresh"),
    ("dense_cached", "Dense cached"),
    ("general_banded", "General banded"),
    ("dense_cholesky", "Dense Cholesky"),
    ("banded_cholesky", "Banded Cholesky"),
    ("eigh", "Eigh"),
    ("svd", "SVD"),
)
CRITERIA = ("cv", "gcv", "aicc", "bic", "mle")
OUT = {}


def read(path):
    if not path.is_file():
        raise FileNotFoundError(f"Missing measured source: {path}")
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def save(fig, name):
    publication_export(fig, name, FIG)


def raw_matrix():
    rows = read(RAW / "search_mode_timings.csv")
    assert len(rows) == 80640, len(rows)
    buckets = defaultdict(list)
    for row in rows:
        if int(row["n"]) != 48 or float(row["mu"]) != 0.:
            continue
        key = (
            int(row["d"]), row["criterion"], row["method"],
            int(row["R"]), row["reuse_mode"], row["policy"],
        )
        buckets[key].append(row)
    assert all(len(r) == 2 for r in buckets.values())
    OUT["windows_source_rows"] = 80640
    OUT["windows_matched_cells"] = 40320
    OUT["windows_filters"] = "n=48, fixed mu=0; shared or cold; two seeds"
    return buckets


def median_valid(buckets, d, criterion, method, R, reuse, policy, field):
    values = buckets.get((d, criterion, method, R, reuse, policy), [])
    if len(values) != 2 or any(x["success"] != "True" for x in values):
        return float("nan")
    return statistics.median(float(x[field]) for x in values)


def coordinate_map():
    n = 48
    penalties = np.geomspace(1e-6, 1e18, 500)
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    for j, d in enumerate(range(1, 7)):
        D = np.diff(np.eye(n), n=d, axis=0)
        sig = np.linalg.svd(D, compute_uv=False)
        z = np.log(penalties[:, None]) + 2*np.log(sig)[None, :]
        vals = np.mean(1.0 / (1.0 + np.exp(-np.clip(z, -700, 700))), axis=1)
        ax.plot(penalties, vals, lw=1.5, label=f"$d={d}$", color=COLORS[j])
    ax.set_xscale("log")
    ax.set_ylim(-.02, 1.03)
    ax.set(xlabel="Internal penalty $\\lambda$",
           ylabel="Smoothness $S_d(\\lambda)$",
           title="Shared smoothness scale")
    ax.legend(frameon=False, ncol=3, fontsize=7)
    save(fig, "coordinate_map")


def criterion_coordinates(buckets):
    """Two STRICTLY matched ways to evaluate the same user-facing S grid."""
    n, d, mu, R = 48, 3, 0., 1
    policies = ("native_s", "mapped_s_lambda")
    tags = ("Repeated S inversion", "One cached S grid")
    values = []
    for policy in policies:
        vals = [
            1000*median_valid(buckets, d, c, "svd", R, "shared",
                              policy, "total_standalone_s")
            for c in CRITERIA
        ]
        assert all(math.isfinite(x) for x in vals), (policy, vals)
        values.append(vals)
    fig, ax = plt.subplots(figsize=(8.2, 3.25))
    x = np.arange(5); width = .34
    for k, (name, color) in enumerate(zip(tags, (BLUE, CYAN))):
        ax.bar(x+(k-.5)*width, values[k], width, label=name, color=color)
    ax.set_xticks(x, ["CV", "GCV", "AICc", "BIC*", "ML"])
    ax.set_ylim(0, max(max(v) for v in values)*1.3)
    ax.set(xlabel="Criterion (same 17 S candidates; exact endpoints 0 and 1)",
           ylabel="Total measured time (ms)",
           title="d=3: identical S-grid, different reuse strategies")
    ax.legend(frameon=False, ncol=2, loc="upper right", fontsize=8)
    OUT["criterion_coordinate_milliseconds"] = {
        tags[k]: dict(zip(CRITERIA, values[k])) for k in range(2)
    }

    mapping = read(RAW / "search_grid_preparation.csv")
    once = next(1000*float(v["map_once_s"]) for v in mapping
                if v["n"] == str(n) and v["d"] == str(d))
    backend = [
        1000*median_valid(
            buckets, d, c, "svd", R, "shared", "mapped_s_lambda",
            "total_backend_only_s")
        for c in CRITERIA
    ]
    assert all(math.isfinite(x) for x in backend)
    native = sum(values[0])
    mapped = once + sum(backend)
    assert native > 0 and mapped > 0
    # Validate that these two policies actually choose exactly the
    # SAME search candidate; don't assume coordinate agreement.
    selected = {}
    for c in CRITERIA:
        a = median_valid(buckets, d, c, "svd", R, "shared",
                         "native_s", "selected_s")
        b = median_valid(buckets, d, c, "svd", R, "shared",
                         "mapped_s_lambda", "selected_s")
        assert math.isfinite(a) and abs(a-b) < 1e-12, (c,a,b)
        selected[c] = a
    OUT["five_criterion_joint"] = {
        "n": n, "d": d, "mu": mu, "R": R,
        "native_s_ms": native,
        "premapped_once_ms": mapped,
        "speedup": native/mapped,
        "mapping_once_ms": once,
        "matched_candidate_count": 17,
        "selected_s": selected,
    }
    # Keep old d=2 figure's numerical statement as an explicitly
    # separate, historical comparison, NOT a d=3 measurement.
    d2_native = sum(
        1000*median_valid(buckets,2,c,"svd",1,"shared",
                          "native_s","total_standalone_s")
        for c in CRITERIA)
    d2_once = next(1000*float(v["map_once_s"]) for v in mapping
                   if v["n"]=="48" and v["d"]=="2")
    d2_backend = sum(
        1000*median_valid(buckets,2,c,"svd",1,"shared",
                          "mapped_s_lambda","total_backend_only_s")
        for c in CRITERIA)
    assert abs(d2_native-11.234) < .02, d2_native
    assert abs(d2_once+d2_backend-3.980) < .02
    OUT["historical_d2_comparator"] = {
        "n":48,"d":2,"mu":0.,"R":1,
        "native_s_ms":d2_native,
        "premapped_once_ms":d2_once+d2_backend,
        "speedup":d2_native/(d2_once+d2_backend),
    }
    # Generate the paper's d=3 table directly from measured raw records.
    lines = [
        "% AUTO-GENERATED FROM ARCHIVED WINDOWS DATA; DO NOT EDIT",
        r"\begin{table*}[t]",
        r"\caption{Five completed 17-point selection searches for $d=3$, $n=48$, fixed $\mu=0$, SVD, $R=1$. Values are two-seed medians in milliseconds. Both policies evaluate the identical full $S\in[0,1]$ grid; premapped standalone time includes conversion once per criterion.}",
        r"\label{tab:criteria}\centering",
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"Criterion & Repeated $S$ inversion & Premapped $S$ grid \\",
        r"\midrule",
    ]
    for i,c in enumerate(CRITERIA):
        title = {"cv":"CV","gcv":"GCV","aicc":"AICc",
                 "bic":"Residual BIC","mle":"Profiled Gaussian ML"}[c]
        lines.append(f"{title} & {values[0][i]:.3f} & {values[1][i]:.3f} \\\\")
    lines.extend([r"\bottomrule",r"\end{tabular}",r"\end{table*}"])
    (PAPER/"sections"/"generated_d3_timings.tex").write_text(
        "\n".join(lines)+"\n", encoding="utf8")
    save(fig,"criterion_coordinates")


def workload_scaling(buckets):
    """Show valid results only; missing or invalid grids cannot be winners."""
    policies = [
        (1, "single_mapped_s_lambda", "Single $s=0.5$"),
        (1, "mapped_s_lambda", "17-point grid"),
        (8, "mapped_s_lambda", "Eight grids"),
    ]
    fig, ax = plt.subplots(figsize=(8.6, 3.45))
    valid_counts = [0,0,0]
    method_validity = {}
    for j, (method, label) in enumerate(METHODS):
        y = np.asarray([
            1000*median_valid(
                buckets,3,"gcv",method,R,"shared",policy,
                "total_standalone_s",
            )
            for R, policy, _ in policies
        ], dtype=float)
        valid = np.isfinite(y) & (y > 0)
        for i,is_valid in enumerate(valid):
            valid_counts[i] += int(is_valid)
        method_validity[method] = {
            "valid": [bool(v) for v in valid],
            "milliseconds": [float(v) if np.isfinite(v) else None for v in y],
        }
        if np.any(valid):
            # Do NOT join a line across an unmeasured/invalid workload.
            ax.plot(np.arange(3), y,
                    marker=("o","s","^","D")[j%4],
                    ls=("-","--","-.")[j%3], color=COLORS[j],
                    lw=1.4, ms=4, label=label)
    if not all(count > 0 for count in valid_counts):
        raise RuntimeError(
            "At least one d=3 workload lacks any numerically valid backend: "
            +str(valid_counts)
        )
    ax.set_yscale("log")
    ax.set_xticks(range(3), [p[2] for p in policies])
    ax.set(ylabel="Valid complete-workload time (ms, log scale)",
           title="d=3 GCV: score, full grid, and reused grids")
    ax.legend(frameon=False, ncol=4, fontsize=7, loc="upper center")
    OUT["workload_valid_backends_by_workload"] = valid_counts
    OUT["workload_backend_validity"] = method_validity
    save(fig, "workload_scaling")


def reuse_by_d(buckets):
    fig, ax = plt.subplots(figsize=(8.2, 3.3))
    any_finite = False
    rows = {}
    for j, criterion in enumerate(CRITERIA):
        ratios = []
        for d in range(1,6):
            shared = median_valid(
                buckets,d,criterion,"svd",8,"shared",
                "mapped_s_lambda","total_backend_only_s")
            cold = median_valid(
                buckets,d,criterion,"svd",8,"cold",
                "mapped_s_lambda","total_backend_only_s")
            ratio = cold/shared if (
                math.isfinite(cold) and math.isfinite(shared) and shared>0
            ) else float("nan")
            ratios.append(ratio)
        rows[criterion] = ratios
        if any(math.isfinite(v) for v in ratios):
            any_finite = True
            ax.plot(range(1,6),ratios,marker=("o","s","^","D","v")[j],
                    color=COLORS[j], lw=1.65, ms=4.2,
                    label=criterion.upper() if criterion!="aicc" else "AICc")
    if not any_finite:
        raise RuntimeError("No matched cold/shared valid pairs")
    ax.axhline(1,color="#878d93",ls=":",lw=.9)
    ax.set_xticks(range(1,6))
    ax.set(xlabel="Difference order $d$",
           ylabel="Cold / shared backend-only time",
           title="Eight reused full grids ($n=48$, SVD)")
    ax.legend(ncol=5,fontsize=7,frameon=False,loc="upper center")
    OUT["reuse_ratios"] = rows
    save(fig, "reuse_by_d")


def solver_crossover():
    """Compare measured higher-order full-curve costs where paired evidence exists."""
    rows=read(BENCH / "solver_study_runs" / "pilot-01" /
              "analysis" / "paired_comparisons.csv")
    orders=(1,2,3,5)
    vals={}
    for r in rows:
        if (int(r["n"])==96 and r["mu"]=="0.0" and
            r["method_a"]=="svd" and r["method_b"]=="cholesky" and
            int(r["evaluations"])==16 and int(r["order"]) in orders):
            vals[int(r["order"])]=float(r["speedup_a_over_b"])
    assert set(vals)==set(orders),vals
    fig,ax=plt.subplots(figsize=(8.1,3.25))
    x=sorted(vals)
    ax.plot(x,[vals[k] for k in x],marker="o",lw=1.8,
            color=BLUE,ms=5.0)
    ax.axhline(1,color="#878d93",ls=":",lw=.95)
    ax.set_yscale("log")
    ax.set_xticks(list(orders))
    ax.set(xlabel="Difference order d (d=4 not archived in this paired study)",
           ylabel="SVD / banded Cholesky total time",
           title="16 full curves, n=96, 20 paired seeds")
    OUT["paired_solver_ratios_d"] = {
        str(d): vals[d] for d in orders
    }
    save(fig,"solver_crossover")


def derivative_interpretation():
    """Deterministic physical-position illustration; not runtime data.

    At the S=1 limit, fixed D_d tau=mu*1. When mu=0 this is a
    polynomial of degree at most d-1; for mu != 0 it is degree d.
    """
    n=48
    t=np.linspace(0,1,n)
    y=.22+1.25*t-1.9*t*t+1.5*t**3+.11*np.sin(10*np.pi*t)
    def project(d,mu=0.):
        k=np.arange(n,dtype=float)
        # binomial polynomial scaled to the desired time coordinate
        import scipy.special
        particular=mu*scipy.special.binom(k,d)
        A=np.column_stack([t**j for j in range(d)])
        coeff=np.linalg.lstsq(A,y-particular,rcond=None)[0]
        return particular+A@coeff
    # For y's 1.5*t^3 component, the exact discrete third difference is:
    mu3=1.5*6.0/(n-1)**3
    fig,(ax,ax2)=plt.subplots(1,2,figsize=(8.4,3.3))
    for a in (ax,ax2):
        a.plot(t,y,color="#8e9ba6",lw=1.0,alpha=.65,label="Observed position")
        a.set(xlabel="Equally spaced time",ylabel="Position")
    for j,d in enumerate((1,2,3,4)):
        ax.plot(t,project(d),color=COLORS[j],lw=1.5,
                label=f"$d={d}$")
    ax.set_title("S=1, zero mean differences")
    ax.legend(ncol=2,frameon=False,fontsize=7)
    ax2.plot(t,project(3,0.),color=BLUE,lw=1.8,label="$d=3, \\mu=0$ (quadratic)")
    ax2.plot(t,project(3,mu3),color=CYAN,lw=1.8,ls="--",
             label="$d=3, \\mu\\ne0$ (cubic)")
    ax2.set_title("Third differences: quadratic vs cubic")
    ax2.legend(frameon=False,fontsize=7)
    OUT["derivative_illustration"]={
        "d3_mu_fixed":mu3,
        "role":"deterministic algebraic illustration (not timed)",
        "time_step":1.0/(n-1),
        "physical_meaning":"third finite difference approximates jerk times step cubed"
    }
    save(fig,"derivative_orders")


def main():
    configure_publication(PAPER)
    buckets = raw_matrix()
    coordinate_map()
    derivative_interpretation()
    criterion_coordinates(buckets)
    workload_scaling(buckets)
    reuse_by_d(buckets)
    solver_crossover()
    finish_manifest(PAPER,FIG)
    sources=[
        RAW/"search_mode_timings.csv",
        RAW/"search_grid_preparation.csv",
        RAW/"environment.json",
        BENCH/"solver_study_runs"/"pilot-01"/"analysis"/"paired_comparisons.csv",
    ]
    OUT["source_sha256"]={
        str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sources
    }
    (PAPER/"timing_figure_data.json").write_text(
        json.dumps(OUT,indent=2,sort_keys=True,allow_nan=True)+"\n",
        encoding="utf8")
    print("Computed archived-only statistics",json.dumps(
        OUT["five_criterion_joint"],indent=2),flush=True)


if __name__=="__main__":
    main()
