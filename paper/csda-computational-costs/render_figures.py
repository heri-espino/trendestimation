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
    n, d, mu, R = 48, 2, 0., 1
    policies = ("native_s", "mapped_s_lambda", "native_log_lambda")
    tags = ("Native S", "Premapped S", "Different log-$\\lambda$")
    values = []
    for policy in policies:
        vals = [
            1000*median_valid(buckets,d,c,"svd",R,"shared",policy,"total_standalone_s")
            for c in CRITERIA
        ]
        assert all(math.isfinite(x) for x in vals), (policy, vals)
        values.append(vals)
    fig, ax = plt.subplots(figsize=(8.2, 3.25))
    x = np.arange(5); width = .23
    for k, (name, color) in enumerate(zip(tags, (BLUE,CYAN,COLORS[4]))):
        ax.bar(x+(k-1)*width, values[k], width, label=name, color=color)
    ax.set_xticks(x, ["CV", "GCV", "AICc", "BIC*", "ML"])
    ax.set_yscale("log")
    ax.set_ylim(.3, 5.5)
    ax.set(xlabel="Selection criterion",
           ylabel="Total elapsed time (ms)",
           title="One complete 17-point search ($n=48,d=2$)")
    ax.legend(frameon=False, ncol=3, loc="upper center", fontsize=7)
    OUT["criterion_coordinate_milliseconds"] = {
        tags[k]: dict(zip(CRITERIA, values[k])) for k in range(3)
    }
    # Shared mapping is paid exactly once, not once per criterion:
    mapping = read(RAW / "search_grid_preparation.csv")
    once = next(1000*float(x["map_once_s"]) for x in mapping
                if x["n"] == "48" and x["d"] == "2")
    backend = [
        1000*median_valid(
            buckets,d,c,"svd",1,"shared","mapped_s_lambda","total_backend_only_s"
        )
        for c in CRITERIA
    ]
    native = sum(values[0])
    mapped = once + sum(backend)
    assert abs(native-11.234) < .02, native
    assert abs(mapped-3.980) < .02, mapped
    OUT["five_criterion_joint"] = {
        "native_s_ms":native,
        "premapped_once_ms":mapped,
        "speedup":native/mapped,
        "mapping_once_ms":once,
        "matched_candidate_count":17,
    }
    save(fig, "criterion_coordinates")


def workload_scaling(buckets):
    policies = [
        (1, "single_mapped_s_lambda", "Single $s=0.5$"),
        (1, "mapped_s_lambda", "17-point grid"),
        (8, "mapped_s_lambda", "Eight grids"),
    ]
    fig, ax = plt.subplots(figsize=(8.6, 3.45))
    counts = 0
    for j, (method, label) in enumerate(METHODS):
        y = [
            1000*median_valid(
                buckets,1,"gcv",method,R,"shared",policy,
                "total_standalone_s",
            )
            for R, policy, _ in policies
        ]
        if all(np.isfinite(y)):
            ax.plot(np.arange(3), y,
                    marker=("o","s","^","D")[j%4],
                    ls=("-","--","-.")[j%3], color=COLORS[j],
                    lw=1.4, ms=4, label=label)
            counts += 1
    if counts < 3:
        raise RuntimeError("Insufficient complete numerical validity for plot")
    ax.set_yscale("log")
    ax.set_xticks(range(3), [p[2] for p in policies])
    ax.set(ylabel="Total time (ms, log scale)",
           title="GCV: one score, one grid and repeated searches")
    ax.legend(frameon=False, ncol=4, fontsize=7, loc="upper center")
    OUT["workload_valid_backends"] = counts
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
    rows=read(BENCH / "solver_study_runs" / "pilot-01" /
              "analysis" / "paired_comparisons.csv")
    fig,ax=plt.subplots(figsize=(8.1,3.25))
    out = {}
    for j,M in enumerate((1,16,64)):
        vals={}
        for r in rows:
            if (int(r["order"])==2 and r["mu"]=="0.0" and
                r["method_a"]=="svd" and r["method_b"]=="cholesky" and
                int(r["evaluations"])==M and int(r["n"]) in (32,96,192)):
                vals[int(r["n"])]=float(r["speedup_a_over_b"])
        assert set(vals)=={32,96,192},(M,vals)
        x=sorted(vals)
        ax.plot(x,[vals[v] for v in x],marker=("o","s","^")[j],lw=1.6,
                color=COLORS[j],label=f"$M={M}$")
        out[str(M)]=vals
    ax.axhline(1,color="#878d93",ls=":",lw=.9)
    ax.set_yscale("log")
    ax.set_xticks([32,96,192])
    ax.set(xlabel="Series length $n$",
           ylabel="SVD / banded Cholesky total time",
           title="Full fitted trends: 20 paired seeds ($d=2$)")
    ax.legend(ncol=3,fontsize=7,frameon=False)
    OUT["paired_solver_ratios"] = out
    save(fig,"solver_crossover")


def main():
    configure_publication(PAPER)
    buckets = raw_matrix()
    coordinate_map()
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
