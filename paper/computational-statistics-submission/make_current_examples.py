#!/usr/bin/env python3
"""Generate real-data PLS comparisons for the Springer submission.

Usage from repo root:
  python paper/computational-statistics-submission/make_current_examples.py
  python paper/computational-statistics-submission/make_current_examples.py --fetch-fred

Output PDFs/SVGs/PNGs, a selection table, and JSON/CSV audit trails.
No artificial observations or data-filling of missing monthly values.
The frozen NOAA slice ends 2026-09; FRED's UNRATE snapshot must have
an explicit observed last month. Forecast paths are local-polynomial
extrapolations of smoothed endpoints, NOT calibrated forecast models.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.request
from datetime import date
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from trendestimation import TrendSmoother, select_lambda

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
DATA = ROOT / "data"
FIG = ROOT / "figures"
ORDERS = (1, 2, 3, 4)
METHODS = ("cv", "gcv", "aicc", "bic", "controlled")
CONTROLLED_S = .86
TARGET_S = np.linspace(.10, .98, 29)
HORIZON = 12
HOLDOUT = 12
DATE_CUTOFF = date(2026, 9, 1)
FRED_SOURCE = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE"
NOAA_SOURCE = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"

def fetch_fred() -> Path:
    """Download fresh observations into a pinned snapshot (explicit opt-in)."""
    dest = DATA / "fred_unrate_2010_2026_09.csv"
    request = urllib.request.Request(
        FRED_SOURCE, headers={"User-Agent": "trendestimation-research/1.0",
                              "Accept": "text/csv"})
    with urllib.request.urlopen(request, timeout=35) as response:
        raw = response.read(400_000).decode("utf-8-sig")
    lines = list(csv.DictReader(raw.splitlines()))
    if not lines or "observation_date" not in lines[0] and "DATE" not in lines[0]:
        raise ValueError("Unexpected FRED UNRATE CSV format")
    col = "observation_date" if "observation_date" in lines[0] else "DATE"
    rows = []
    for item in lines:
        period = date.fromisoformat(item[col])
        if date(2010, 1, 1) <= period <= DATE_CUTOFF:
            value = float(item["UNRATE"])
            if not np.isfinite(value):
                raise ValueError("Missing FRED observation; refuse imputation")
            rows.append((period, value))
    if not rows or rows[-1][0] != DATE_CUTOFF:
        raise ValueError(f"FRED snapshot not through Sep 2026; last={rows[-1][0] if rows else None}")
    DATA.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(("month", "value"))
        writer.writerows((d.isoformat()[:7], f"{value:.8g}") for d, value in rows)
    return dest


def load_series(path: Path, field: str) -> tuple[list[date], np.ndarray]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(row for row in handle if not row.startswith("#")))
    if not rows or any(set(row) != {"month", field} for row in rows):
        raise ValueError(f"Unexpected data columns at {path}")
    dates = [date.fromisoformat(row["month"] + "-01") for row in rows]
    y = np.array([float(row[field]) for row in rows])
    if not np.all(np.isfinite(y)) or len(y) < 55 or dates[-1] != DATE_CUTOFF:
        raise ValueError(f"Nonfinite / short / out-of-date series: {path}")
    indices = np.array([m.year*12 + m.month for m in dates])
    if np.any(np.diff(indices) != 1):
        raise ValueError("Monthly series must be contiguous; no interpolation")
    return dates, y


def extrapolate_tail(trend: np.ndarray, d: int, horizon: int) -> np.ndarray:
    """Explicit degree-(d-1) tail polynomial extension; no future fitting.

    The regression window is at least 24 observations and extends to at
    most 36. The polynomial is centered and evaluated in months; a cap
    of 2 avoids cubic/quartic explosion for higher difference orders.
    """
    degree = min(d-1, 2)
    window = min(len(trend), 36)
    t = np.arange(-window+1, 1, dtype=float)
    future = np.arange(1, horizon+1, dtype=float)
    scale = float(max(1, window-1))
    basis = np.vander(t / scale, N=degree+1, increasing=True)
    coefficients = np.linalg.lstsq(basis, trend[-window:], rcond=None)[0]
    predicted = np.vander(future/scale, N=degree+1, increasing=True) @ coefficients
    if not np.all(np.isfinite(predicted)):
        raise ArithmeticError("Nonfinite extrapolated trend")
    return predicted


def estimate_candidates(y: np.ndarray, d: int) -> tuple[TrendSmoother, dict]:
    model = TrendSmoother(len(y), order=d)
    # A single comparable smoothness grid is inverted once, then the
    # same penalized fits are evaluated by every published criterion.
    penalties = np.array([model.lambda_for_smoothness(float(s))
                          for s in TARGET_S], dtype=float)
    out = {}
    for criterion in METHODS[:4]:
        start = perf_counter()
        sel = select_lambda(model, y, criterion=criterion, mu=0.0,
                            search_space="lambda", grid=penalties)
        out[criterion] = {
            "lambda": float(sel.lambda_),
            "s": float(sel.smoothness),
            "criterion_score": float(sel.score),
            "selection_ms_excluding_shared_svd_and_grid": 1000*(perf_counter()-start),
            "candidate_count": len(penalties),
        }
    lam = float(model.lambda_for_smoothness(CONTROLLED_S))
    out["controlled"] = {"lambda": lam, "s": float(model.smoothness(lam)),
                         "criterion_score": None,
                         "selection_ms_excluding_shared_svd_and_grid": None,
                         "candidate_count": None}
    return model, out


def plot_panel(title: str, dates: list[date], y: np.ndarray,
               fits: dict[tuple[int, str], np.ndarray], prefix: str) -> None:
    fig, ax = plt.subplots(2, 2, figsize=(12, 7.8), sharex=True)
    x = np.array(dates)
    cs = {1:"#1d4ed8",2:"#0891b2",3:"#a855f7",4:"#e17a32"}
    for i, criterion in enumerate(("cv", "gcv", "aicc", "bic")):
        axis = ax.flat[i]
        axis.plot(x, y, color="#a0a7b3", lw=.85, label="Observed")
        for d in ORDERS:
            axis.plot(x, fits[(d, criterion)], lw=1.65,
                      color=cs[d], label=f"d={d}")
        axis.set_title(f"{criterion.upper()}: difference-order comparison")
        axis.grid(alpha=.18)
    ax[0,0].legend(frameon=False, ncol=5, fontsize=8, loc="upper left")
    for axis in ax[1]:
        axis.tick_params(axis="x", rotation=20)
    fig.suptitle(title + " — four classical selectors", fontweight="bold")
    fig.tight_layout()
    save(fig, prefix+"_criteria")


def save(fig: plt.Figure, name: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    for extension in ("pdf","svg","png"):
        fig.savefig(FIG/f"{name}.{extension}", dpi=165, bbox_inches="tight")
    plt.close(fig)


def evaluate(name: str, dates: list[date], observations: np.ndarray,
             *, recent_months: int | None = None) -> dict:
    if recent_months:
        dates, observations = dates[-recent_months:], observations[-recent_months:]
    n = len(observations)
    tag = ("co2_recent" if recent_months else "co2_full") if "CO2" in name else "unrate_full"
    print(f"[paper] {tag}: n={n}, last={dates[-1]}", flush=True)
    fitted: dict[tuple[int,str], np.ndarray] = {}
    selected = {}
    forward = {}
    heldout = {}
    for d in ORDERS:
        model, info = estimate_candidates(observations, d)
        for criterion in METHODS:
            params = info[criterion]
            trend = model.fit(observations, lambda_=params["lambda"], mu=0.0).trend
            fitted[(d, criterion)] = trend
            params["final_trend"] = float(trend[-1])
            params["training_rmse"] = float(np.sqrt(np.mean((trend-observations)**2)))
            if criterion == "controlled":
                forward[str(d)] = extrapolate_tail(trend, d, HORIZON).tolist()
            selected[(d,criterion)] = params

        # Genuine holdout experiment: no part of the last 12 months is
        # used to choose lambda, smooth, or extrapolate from the training
        # origin. Historical 12-month losses are diagnostics, not a proof
        # of forecasting validity.
        hist = observations[:-HOLDOUT]
        train_model, train_info = estimate_candidates(hist, d)
        for criterion in ("cv","gcv","aicc","bic","controlled"):
            h_lambda = train_info[criterion]["lambda"]
            trained = train_model.fit(hist, lambda_=h_lambda, mu=0).trend
            pred = extrapolate_tail(trained,d,HOLDOUT)
            heldout[(d,criterion)] = {
                "mae": float(np.mean(np.abs(pred-observations[-HOLDOUT:]))),
                "rmse": float(np.sqrt(np.mean((pred-observations[-HOLDOUT:])**2))),
                "forecast": pred.tolist(),
            }

    plot_panel(name, dates, observations, fitted, tag)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    x = np.array(dates)
    ax.plot(x, observations, color="#9ca3af", label="Observed", lw=1.0)
    for d, color in zip(ORDERS, ("#205fd4","#138b94","#9d57c8","#cf8427")):
        ax.plot(x, fitted[(d, "controlled")], color=color, lw=1.55,
                label=f"PLS d={d}, S={CONTROLLED_S}")
    ax.set_title(f"{name}: common normalized smoothness, different d")
    ax.legend(ncol=3, fontsize=8, frameon=False)
    ax.grid(alpha=.22)
    save(fig, tag+"_controlled_orders")

    # Both optimization coordinates are reported in data exports.
    fig, axes = plt.subplots(1,2,figsize=(11.5,4.5))
    markers={"cv":"o","gcv":"s","aicc":"D","bic":"^","controlled":"X"}
    for crit in METHODS:
        ds=np.array(ORDERS)
        axes[0].plot(ds,[selected[(d,crit)]["s"] for d in ORDERS],
                     marker=markers[crit], label=crit.upper())
        axes[1].plot(ds,[selected[(d,crit)]["lambda"] for d in ORDERS],
                     marker=markers[crit], label=crit.upper())
    axes[0].set(xlabel="Difference order d", ylabel="Normalized smoothness S",
                title="Selected S, fixed mu=0")
    axes[1].set(xlabel="Difference order d", ylabel="Penalty lambda (log scale)",
                title="Equivalent selected lambda, fixed mu=0")
    axes[1].set_yscale("log")
    for axis in axes:
        axis.set_xticks(ORDERS);axis.grid(alpha=.25)
    axes[0].legend(ncol=3, fontsize=8, frameon=False)
    fig.suptitle(name+" — same fitted configuration, two coordinates",fontweight="bold")
    fig.tight_layout()
    save(fig, tag+"_selected_coordinates")

    # Extrapolation from all data: keep unobserved months SEPARATE.
    # Actual future truth does not exist yet; no bands are invented.
    future_dates=[]
    for step in range(1, HORIZON+1):
        k=dates[-1].year*12+dates[-1].month+step-1
        future_dates.append(date(k//12,(k%12)+1,1))
    fig, ax=plt.subplots(figsize=(11.4,5.0))
    visible=min(n,84)
    ax.plot(dates[-visible:], observations[-visible:], c="#9ca3af",
            label="Observed historical", lw=1.1)
    for d,c in zip(ORDERS,("#205fd4","#138b94","#9d57c8","#cf8427")):
        ax.plot(dates[-visible:], fitted[(d,"controlled")][-visible:],
                color=c, lw=1.8, label=f"d={d} fitted")
        ax.plot([dates[-1], *future_dates],
                [fitted[(d,"controlled")][-1], *forward[str(d)]],
                color=c, ls="--", lw=1.65, alpha=.85)
    ax.axvline(dates[-1], color="#444", ls=":", lw=1.0)
    ax.text(dates[-1], ax.get_ylim()[1], " observed cutoff",
            ha="left",va="top",fontsize=8)
    ax.set_title(name+": future LOCAL POLYNOMIAL extension; not a validated forecast")
    ax.legend(ncol=3,fontsize=8,frameon=False)
    ax.grid(alpha=.2)
    fig.tight_layout()
    save(fig,tag+"_future_extrapolations")

    # Honest fixed-origin holdout backtest over 12 historical months.
    fig, ax=plt.subplots(figsize=(11.5,4.5))
    xx=dates[-HOLDOUT:]
    ax.plot(xx,observations[-HOLDOUT:],c="#161616",marker="o",lw=1.2,label="Held-out observed")
    for d,c in zip(ORDERS,("#205fd4","#138b94","#9d57c8","#cf8427")):
        ax.plot(xx,heldout[(d,"controlled")]["forecast"],
                c=c,ls="--",label=f"d={d} predicted at origin")
    ax.set_title(name+": 12-month single-origin holdout (S=0.86)")
    ax.grid(alpha=.2)
    ax.legend(fontsize=8,ncol=3,frameon=False)
    fig.tight_layout()
    save(fig,tag+"_heldout_backtest")

    summary={
        "dataset": name, "n": n, "first": str(dates[0]), "last": str(dates[-1]),
        "mu":0.0, "order":list(ORDERS), "methods":list(METHODS),
        "controlled_s":CONTROLLED_S,"grid_s":TARGET_S.tolist(),
        "future_start":str(future_dates[0]), "future_end":str(future_dates[-1]),
        "extrapolation_degree_rule":"min(d-1,2), regression on last <=36 fitted months",
        "future_paths":forward,
        "selection":{f"d{d}_{c}":v for (d,c),v in selected.items()},
        "holdout":{f"d{d}_{c}":v for (d,c),v in heldout.items()},
        "scope":"PLS trend extrapolation, not seasonal forecast or prediction intervals",
    }
    with (DATA/f"{tag}_results.json").open("w",encoding="utf-8") as h:
        json.dump(summary,h,indent=2)
    return summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fetch-fred", action="store_true",
                    help="Replace pinned FRED UNRATE snapshot with new source data")
    args=ap.parse_args()
    if args.fetch_fred:
        print("[paper] FRED downloaded:",fetch_fred())
    DATA.mkdir(exist_ok=True)
    co2_file=DATA/"noaa_mlo_monthly_1990_2026_09.csv"
    fred_file=DATA/"fred_unrate_2010_2026_09.csv"
    noaa_x,noaa_y=load_series(co2_file, "average_ppm")
    fred_x,fred_y=load_series(fred_file, "value")
    if len(noaa_y)!=441 or abs(noaa_y[-1]-426.07)>1e-9:
        raise ValueError("NOAA 441-month cutoff or value differs")
    if len(fred_y)!=201 or abs(fred_y[-1]-4.2)>1e-9:
        raise ValueError("FRED UNRATE 201-month Sep 2026 cutoff or value differs")
    out=[
        evaluate("NOAA Mauna Loa CO2 (ppm)", noaa_x,noaa_y),
        evaluate("NOAA Mauna Loa CO2 (ppm)", noaa_x,noaa_y,recent_months=120),
        evaluate("FRED US unemployment rate (percent, SA)", fred_x,fred_y),
    ]
    # Compact paper LaTeX table: order d=2 from all three empirical designs.
    lines=[
        r"\begin{tabular}{llrrr}\toprule",
        r"Dataset & Selector & $\lambda$ & $S$ & holdout RMSE\\\midrule",
    ]
    for report,display in zip(out,("CO$_2$ (1990--2026)",
                                   "CO$_2$ (recent 120 months)","Unemployment (2010--2026)")):
        for criterion in METHODS:
            s=report["selection"][f"d2_{criterion}"]
            loss=report["holdout"][f"d2_{criterion}"]["rmse"]
            lines.append(f"{display} & {criterion.upper()} & "
                         f"{s['lambda']:.4g} & {s['s']:.3f} & {loss:.3f}"+r"\\")
    lines.append(r"\bottomrule\end{tabular}")
    (ROOT/"current_examples_table.tex").write_text(
        "\n".join(lines)+"\n",encoding="utf-8")
    provenance={
        "generated_utc":"not stamped; reproducible pinned source data",
        "sources":[
            {"dataset":"NOAA Mauna Loa CO2 monthly mean","url":NOAA_SOURCE,
             "file":str(co2_file.relative_to(ROOT)),"n":441,
             "last":"2026-09","last_value":426.07,
             "publisher_revisions_possible":True},
            {"dataset":"BLS unemployment rate UNRATE via FRED",
             "url":"https://fred.stlouisfed.org/series/UNRATE",
             "csv_url":FRED_SOURCE,
             "file":str(fred_file.relative_to(ROOT)),"n":201,
             "last":"2026-09","last_value":4.2,
             "publisher_revisions_possible":True}
        ],
        "files_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (co2_file,fred_file)},
        "cases":[{"dataset":r["dataset"],"n":r["n"],
                  "start":r["first"],"end":r["last"]} for r in out],
        "limits":"Forecast paths are descriptive extrapolations; local polynomial order capped at 2. Single-origin 12-month holdout is not a statistically sufficient rolling-origin comparison. Selection scores are in-sample, no causal or climate forecasting inference.",
    }
    (DATA/"provenance.json").write_text(json.dumps(provenance,indent=2)+"\n",
                                        encoding="utf-8")
    print("[paper] Created figures, table, json; source checks passed",flush=True)


if __name__=="__main__":
    main()
