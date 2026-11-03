"""Four publication figures for CSDA Paper B.

Analytical curves are explicitly *illustrative normalized work counts*,
not measured performance or fitted scaling constants. The runtime
figure uses 48 real, frozen, single-worker Experiment010 observations.
The application figure uses the separate NGSIM real-vehicle manuscript's
immutable source data, preselected GCV candidate and training-only mean;
it does not search for a favorable result or extrapolate via native PLS.
All exports use the repository's pinned AwesomeFigures + CAS/TeX engine.

Run after copying the author's CAS class into the paper directory:
  python paper/csda-computational-costs/render_theory_figures.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from publication_style import (
    configure_publication, publication_export, finish_manifest
)

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parents[1]
FIG = PAPER / "figures"
DATA = PAPER / "data" / "experiment010_matched_three_methods.csv"
JERK = ROOT / "paper" / "ngsim-jerk-case-study"
NAMES = (
    "theory_regime_map", "theory_cost_curves",
    "matched_bic_timings", "ngsim_jerk_application"
)
NAVY = "#28495e"
BLUE = "#2867a0"
CYAN = "#339cba"
AMBER = "#bb7b48"
GRAY = "#7e909c"
METHODS = (
    ("spectral_svd", "Spectral SVD", BLUE),
    ("naive_inverse", "Dense inverse", GRAY),
    ("sparse_cholesky_banded_trace", "CHOLMOD hybrid", AMBER),
)
SOURCE_SHA = "f16f2bab6cfa37c6423c7f2d4554208efa9f683a"


def export(fig, name: str):
    publication_export(fig, name, FIG)


def normalized_work(n: np.ndarray, m: np.ndarray, *,
                    d: int = 3, r_series: int = 1,
                    criterion: str = "gcv"):
    """A transparently specified arithmetic proxy, NOT execution time.

    Equal unit coefficients for the dominant modeled terms; premapped
    penalties and streamed banded factors. The best method could change
    with library-level constants or numerical restrictions.
    """
    r = n - d
    spectral = n * r * r + r_series * n * r + m * r_series * r
    banded = n * d * d + m * (
        n * d * d + r_series * n * d + r_series * n)
    if criterion == "cv":
        # Candidate leverage shared across series, projections per series.
        spectral = spectral + m * (1 + r_series) * n * r
    elif criterion != "gcv":
        raise ValueError(criterion)
    return spectral, banded


def theoretical_landscape():
    n = np.geomspace(24, 4096, 125)
    m = np.geomspace(1, 1_000_000, 160)
    M, N = np.meshgrid(m, n)
    fig, axes = plt.subplots(1, 2, figsize=(8.1, 3.1), sharey=True)
    for ax, criterion, label in zip(
        axes, ("gcv", "cv"), ("Scalar GCV-style score", "Exact CV")
    ):
        ws, wb = normalized_work(N, M, criterion=criterion)
        ratio = np.log10(wb / ws)
        ax.contourf(M, N, ratio, levels=[-20, 0, 20],
                    colors=["#f4e8db", "#e4edf4"], alpha=.9)
        if float(np.min(ratio)) < 0 < float(np.max(ratio)):
            ax.contour(M, N, ratio, levels=[0], colors=[NAVY],
                       linewidths=1.3, linestyles="--")
        ax.text(.07, .91, label, transform=ax.transAxes,
                color=NAVY, weight="bold", fontsize=10)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set(xlabel="Number of evaluated smoothness values $M$")
        ax.grid(alpha=.10)
    axes[0].set_ylabel("Series length $n$")
    axes[0].text(.59, .12, "SVD work lower",
                 transform=axes[0].transAxes, color=NAVY, fontsize=8)
    axes[0].text(.05, .81, "Banded work lower",
                 transform=axes[0].transAxes, color="#89552f", fontsize=8)
    axes[1].text(.47, .15, "Banded work lower",
                 transform=axes[1].transAxes, color="#89552f", fontsize=8)
    fig.suptitle("Illustrative algorithmic work frontier ($d=3$, $R=1$)",
                 fontsize=12, y=.99)
    # Unit coefficients are disclosed in the LaTeX caption; avoid overflow.
    fig.tight_layout(rect=(0,.035,1,.92))
    export(fig, "theory_regime_map")


def amortized_curves():
    M = np.geomspace(1, 1_000_000, 270)
    fig, axes = plt.subplots(1, 2, figsize=(8.1, 3.2), sharey=True)
    for ax, criterion in zip(axes, ("gcv", "cv")):
        spectral, band = normalized_work(
            np.full_like(M, 64.), M, criterion=criterion)
        ax.loglog(M, spectral, color=BLUE, lw=2.0,
                  label="Full SVD + scores")
        ax.loglog(M, band, color=AMBER, lw=2.0,
                  label="Banded Cholesky + diagnostics")
        ax.grid(alpha=.18)
        ax.set(xlabel="Number of candidate penalties $M$",
               title=("Scalar GCV-style score" if criterion=="gcv"
                      else "Exact conditional CV"))
        if criterion == "gcv":
            n, d, r = 64., 3., 61.
            setup_svd=n*r*r+n*r
            setup_band=n*d*d
            marginal_svd=r
            marginal_band=n*d*d+n*d+n
            cross=(setup_svd-setup_band)/(marginal_band-marginal_svd)
            assert 100 < cross < 1000
            ax.axvline(cross, color=GRAY, ls=":", lw=1.1)
            ax.text(cross*1.4, 2.2e5, r"$M_\star$ (unit-cost)",
                    fontsize=8, color=NAVY)
    axes[0].set_ylabel("Illustrative arithmetic-work units (not seconds)")
    axes[0].legend(frameon=False, fontsize=7.5, loc="upper left")
    fig.suptitle("Amortized grid-search work ($n=64$, $d=3$, $R=1$)",
                 fontsize=12, y=.99)
    fig.tight_layout(rect=(0,.015,1,.92))
    export(fig, "theory_cost_curves")


def frozen_bic_records():
    with DATA.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 48, len(rows)
    counts = defaultdict(int)
    grouped = defaultdict(list)
    pair = defaultdict(dict)
    for row in rows:
        method = row["method"]
        assert method in dict((m, name) for m, name, _ in METHODS)
        assert (row["n"], row["d"], row["mu"],
                row["criterion"], row["grid_denominator"]) == (
                    "64", "1", "data", "bic", "100000")
        assert row["source_sha"] == SOURCE_SHA
        assert row["parallel_workers"] == row["blas_threads"] == "1"
        assert row["status"] == "ok", row
        counts[method] += 1
        key = (row["coordinate"], row["workload"],
               row["R"], row["repeat"])
        assert method not in pair[key]
        pair[key][method] = row
        grouped[(row["coordinate"], row["workload"], method)].append(
            float(row["total_cold_s"]))
    assert sorted(counts.values()) == [16, 16, 16]
    assert len(pair) == 16 and all(len(x)==3 for x in pair.values())
    for key, bundle in pair.items():
        sref = bundle["spectral_svd"]
        for method in ("naive_inverse", "sparse_cholesky_banded_trace"):
            candidate = bundle[method]
            assert abs(float(candidate["selected_s"]) -
                       float(sref["selected_s"])) < 1e-12
            diff = abs(float(candidate["selected_score"]) -
                       float(sref["selected_score"]))
            assert diff / max(1., abs(float(sref["selected_score"]))) < 1e-10
    assert all(len(values)==2 for values in grouped.values())
    return grouped


def matched_runtime_figure():
    grouped=frozen_bic_records()
    fig, axes = plt.subplots(1, 2, figsize=(8.05,3.10))
    scenarios = (
        ("one_s_one_series", "one_s_multiple_series"),
        ("grid_one_series", "grid_multiple_series"),
    )
    for ax, kinds, scale, label in zip(
        axes, scenarios, (1000., 1.), (
            "One smoothness value (milliseconds)",
            "100,000 values (seconds)",
        )
    ):
        x=np.arange(2)
        width=.23
        for j,(method, display, color) in enumerate(METHODS):
            values = [
                np.median(grouped[("mapped_lambda",kind,method)])*scale
                for kind in kinds
            ]
            ax.bar(x+(j-1)*width, values, width=.205,
                   color=color, label=display)
            for px, val in zip(x+(j-1)*width,values):
                ax.text(px, val*1.015, f"{val:.2f}",
                        ha="center", va="bottom", fontsize=6.6)
        ax.set_xticks(x, ["$R=1$","$R=2$"])
        ax.set(xlabel="Independent series $R$",
               ylabel=label)
        ax.set_ylim(0,max(np.median(grouped[("mapped_lambda", k, meth)])*
                           scale for k in kinds for meth,_,_ in METHODS)*1.23)
        ax.grid(axis="y",alpha=.14)
    # Place shared legend above, outside the bars and value annotations.
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, fontsize=7.5,
               ncol=3, loc="upper center", bbox_to_anchor=(.52,.92))
    fig.suptitle("Real matched one-worker BIC pipeline measurements ($n=64$, $d=1$)",
                 fontsize=11.5,y=.995)
    fig.tight_layout(rect=(0,.02,1,.80))
    export(fig,"matched_bic_timings")


def jerk_application():
    # The separate third manuscript is the authoritative scientific source:
    # no synthetic data, no re-selection, no future observations during fit.
    sys.path.insert(0, str(JERK))
    from run_case import source_tracks, continuation, DT, TRAIN_N
    from trendestimation import TrendSmoother
    tracks, prov = source_tracks()
    raw=(JERK/"data"/"ngsim_us101_selected_raw_positions.csv").read_bytes()
    source_sha=hashlib.sha256(raw).hexdigest()
    assert source_sha == prov["subset_sha256"] or hashlib.sha256(
        raw.replace(b"\r\n",b"\n").replace(b"\n",b"\r\n")
    ).hexdigest()==prov["subset_sha256"]
    with (JERK/"results"/"selection_rows.json").open() as f:
        selection=json.load(f)
    sample=next(row for row in selection if
        row.get("track")==1 and row.get("origin")==185 and
        row.get("d")==3 and row.get("criterion")=="gcv" and
        row.get("mu_policy")=="sample" and row.get("status")=="ok")
    n=TRAIN_N
    train=np.asarray(tracks[1][185-n:185],dtype=float)
    observed=np.asarray(tracks[1][185:185+20],dtype=float)
    mu=float(np.mean(np.diff(train,n=3)))
    assert abs(mu-float(sample["mu"]))<1e-10
    assert sample["S"] == .4
    smoother=TrendSmoother(n,order=3)
    fitted=smoother.fit(train,lambda_=float(sample["lambda"]),mu=mu)
    future=continuation(fitted.trend,3,mu,20)
    assert np.all(np.isfinite(future))
    dt=float(DT)
    t_train=np.arange(-n+1,1)*dt
    t_future=np.arange(1,21)*dt
    fig=plt.figure(figsize=(8.2,4.6))
    gs=fig.add_gridspec(2,2,height_ratios=(1.15,.9),
                        hspace=.48,wspace=.24)
    a=fig.add_subplot(gs[0,:])
    b=fig.add_subplot(gs[1,0])
    c=fig.add_subplot(gs[1,1])
    a.scatter(t_train[-45:],train[-45:],s=10,
              color=GRAY,alpha=.75,label="Measured training position")
    a.plot(t_train[-45:],fitted.trend[-45:],color=BLUE,lw=1.8,
           label=r"PLS trend ($d=3$, $\widehat\mu$)")
    a.plot(t_future,observed,color=NAVY,lw=2,
           label="Measured held-out future")
    a.plot(t_future,future,color=AMBER,lw=1.9,ls="--",
           label="Local polynomial continuation")
    a.axvline(0,color=GRAY,ls=":",lw=1.0)
    a.set(xlabel="Time relative to forecast origin (s)",
          ylabel="Longitudinal position (m)")
    a.legend(frameon=False,fontsize=7,ncol=2,loc="upper left")
    jerk_t=(np.arange(n-3)+1.5)*dt
    raw_jerk=np.diff(train,n=3)/(dt**3)
    smooth_jerk=np.diff(fitted.trend,n=3)/(dt**3)
    b.plot(jerk_t,raw_jerk,color=GRAY,lw=.85)
    c.plot(jerk_t,smooth_jerk,color=BLUE,lw=1.55)
    c.axhline(mu/dt**3,ls=":",color=AMBER,lw=1)
    b.set(xlabel="Training window (s)",
          ylabel=r"Raw $\Delta^3 y/\Delta t^3$ ($m/s^3$)",
          title="Noisy third difference")
    c.set(xlabel="Training window (s)",
          ylabel=r"Trend $\Delta^3\tau/\Delta t^3$ ($m/s^3$)",
          title="Regularized third difference")
    fig.suptitle("Real NGSIM US-101 track, training-only jerk-mean plug-in",
                 fontsize=11.5,y=.99)
    fig.tight_layout(rect=(0,0,1,.94))
    export(fig,"ngsim_jerk_application")
    return {
        "provenance_reference": "paper/ngsim-jerk-case-study/data/provenance.json",
        "track":1, "origin":185, "n_train":n, "frames_holdout":20,
        "dt_s":dt, "d":3, "mu_policy":"data",
        "mu_from_training":mu, "criterion":"GCV",
        "selected_S":sample["S"], "lambda":sample["lambda"],
        "forecast_method":"local degree-2 after removing cubic particular solution",
        "is_intrinsic_PLS_forecast":False,
        "ground_truth_jerk_available":False,
    }


def main():
    FIG.mkdir(parents=True,exist_ok=True)
    configure_publication(PAPER)
    theoretical_landscape()
    amortized_curves()
    matched_runtime_figure()
    application=jerk_application()
    finish_manifest(
        PAPER, FIG, names=NAMES,
        manifest_name="theory_awesomefigures_manifest.json",
        source_data=("closed-form unit-cost work model (not timings); "
                     "single-worker archived Experiment010 raw outcomes; "
                     "real FHWA NGSIM US-101 observations / frozen GCV selection"),
    )
    (PAPER/"theory_figure_sources.json").write_text(
        json.dumps({
            "analytic_figures_not_measured_times":
                ["theory_regime_map","theory_cost_curves"],
            "empirical_figure":"matched_bic_timings",
            "benchmark_csv":str(DATA.relative_to(ROOT)),
            "benchmark_sha":SOURCE_SHA,
            "benchmark_workers":1,
            "benchmark_records":48,
            "application_figure":"ngsim_jerk_application",
            "application":application,
        },indent=2)+"\n",encoding="utf-8")
    print("All four research figure families rendered reproducibly.")


if __name__=="__main__":
    main()
