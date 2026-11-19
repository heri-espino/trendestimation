"""Derivative, selection, alpha and regime diagnostics for Experiment006.

Executed after the scoring run; reads persisted CSV instead of rerunning
any scientific model, and saves all reproducible derived tables.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path

import numpy as np


def _read(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write(path: Path, rows):
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite analysis: {path}")
    if not rows:
        raise ValueError("Cannot archive empty diagnostic table")
    with path.open("x", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def produce(root: Path, mode: str):
    selections = _read(root/"selections_rows.csv")
    jerk = _read(root/"jerk_rows.csv")
    cv = _read(root/"cv_rows.csv")
    forecasts = _read(root/"forecasts_rows.csv")
    if not selections or not jerk or not cv or not forecasts:
        raise ValueError("Missing complete method and forecast rows")

    groups = defaultdict(list)
    for row in selections:
        if row["status"] == "ok":
            groups[row["method"]].append(row)
    diagnostics = []
    for method, rows in sorted(groups.items()):
        smooth = np.asarray([float(r["smoothness"]) for r in rows])
        mu = np.asarray([float(r["reference_mu_discrete_m"]) for r in rows])
        boundary = Counter(r["selection_policy"] for r in rows)
        diagnostics.append({
            "method":method,"n_valid":len(rows),
            "n_lambda_zero_limit":boundary["zero_limit"],
            "n_lambda_infinity_limit":boundary["infinity_limit"],
            "n_lambda_finite":len(rows)-boundary["zero_limit"]-boundary["infinity_limit"],
            "mean_smoothness":float(smooth.mean()),
            "median_smoothness":float(np.median(smooth)),
            "p05_smoothness":float(np.quantile(smooth,.05)),
            "p95_smoothness":float(np.quantile(smooth,.95)),
            "mean_abs_reference_jerk_m_s3":float(np.mean(np.abs(mu)) / .1**3),
        })
    _write(root/"selection_diagnostics.csv", diagnostics)

    alpha_groups = defaultdict(list)
    for row in cv:
        if row["status"]=="ok":
            alpha_groups[(row["method"],int(row["horizon_frames"]))].append(
                float(row["selected_alpha"])
            )
    alpha_summary=[]
    for (name,h),values in sorted(alpha_groups.items()):
        arr=np.asarray(values)
        alpha_summary.append({
            "method":name,"horizon_frames":h,"n":len(arr),
            "n_alpha_zero":int(np.count_nonzero(arr==0)),
            "n_alpha_half":int(np.count_nonzero(arr==.5)),
            "n_alpha_one":int(np.count_nonzero(arr==1)),
            "mean_alpha":float(np.mean(arr)),
        })
    _write(root/"shrinkage_diagnostics.csv",alpha_summary)

    jerk_groups=defaultdict(list)
    for row in jerk:
        if row["status"]=="ok" and row["jerk_mse_m2_s6"] not in ("",None):
            h = row["horizon_frames"]
            jerk_groups[(row["method"],h if h else "all")].append(
                float(row["jerk_mse_m2_s6"])
            )
    jerk_summary=[]
    for (method,h),values in sorted(jerk_groups.items()):
        jerk_summary.append({
            "method":method,"horizon_frames":h,
            "n":len(values),"known_discrete_jerk_rmse_m_s3":
                float(math.sqrt(np.mean(values))),
        })
    if mode=="synthetic":
        _write(root/"known_jerk_summary.csv",jerk_summary)

    # Diagnose heterogeneity rather than collapsing into pooled averages alone.
    regime_groups=defaultdict(list)
    for row in forecasts:
        if row["status"]!="ok":
            continue
        regime = (row["stratum"].split("|")[0] if mode=="synthetic"
                  else row["site"])
        regime_groups[(regime,row["method"],int(row["horizon_frames"]))].append(
            float(row["mse_m2"])
        )
    per_regime=[]
    for (regime,method,h),values in sorted(regime_groups.items()):
        per_regime.append({
            "regime_or_site":regime,"method":method,
            "horizon_frames":h,"n":len(values),
            "future_position_rmse_m":float(math.sqrt(np.mean(values))),
        })
    _write(root/"regime_forecast_summary.csv",per_regime)

    lines=[
        f"# Experiment006 {mode}: selection and jerk diagnostics",
        "",
        f"**Models:** {len(diagnostics)}. **Inner-CV groups:** {len(alpha_summary)}.",
        f"**Historical jerk summaries:** {len(jerk_summary)}.",
        "",
        "## Smoothing selection and boundaries",
        "",
        "| Method | n | lambda→0 | lambda→infinity | Median S |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in diagnostics:
        lines.append(
            f"| {row['method']} | {row['n_valid']} "
            f"| {row['n_lambda_zero_limit']} | {row['n_lambda_infinity_limit']} "
            f"| {row['median_smoothness']:.4g} |"
        )
    if mode=="synthetic":
        lines += [
            "", "## True historical finite-difference jerk RMSE",
            "", "| Method | Horizon (when shrinkage varies) | RMSE (m/s³) |",
            "| --- | --- | ---: |",
        ]
        for row in sorted(jerk_summary,
                          key=lambda x:x["known_discrete_jerk_rmse_m_s3"]):
            lines.append(
                f"| {row['method']} | {row['horizon_frames']} "
                f"| {row['known_discrete_jerk_rmse_m_s3']:.6f} |"
            )
    lines += [
        "", "## Nested training-only forecast-shrinkage choices",
        "", "| Rule | Horizon | alpha=0 | alpha=.5 | alpha=1 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in alpha_summary:
        lines.append(
            f"| {row['method']} | {row['horizon_frames']}"
            f" | {row['n_alpha_zero']} | {row['n_alpha_half']}"
            f" | {row['n_alpha_one']} |"
        )
    lines += [
        "", "## Interpretation limits",
        "",
        "- Mean-adjusted REML is an *in-sample Gaussian* criterion, not a guarantee",
        "  of the smallest future prediction or known-jerk error.",
        "- Lambda=0 is a boundary covariance-model limit; historical trend",
        "  equals raw observations and has no smoothing. An observed frequency",
        "  of zero-boundary selections is substantive, not a numerical omission.",
        "- Exact 15-value grid REML excludes lambda=0 unless explicitly listed;",
        "  continuous REML checks both ends. Inspect both to isolate search effects.",
        "- Nested alpha uses past validation frames only; it changes the",
        "  extrapolation target and is not itself a restricted likelihood.",
        "- Monte Carlo uncertainty is conditional on the frozen synthetic DGP.",
        "- Real NGSIM has no measured true jerk and only five coarse session blocks.",
        "",
    ]
    (root/"DIAGNOSTICS.md").write_text("\n".join(lines),encoding="utf-8")
    return {"n_methods":len(diagnostics),"n_alpha_rows":len(alpha_summary),
            "n_known_jerk_summary":len(jerk_summary),
            "n_regime_summary":len(per_regime)}
