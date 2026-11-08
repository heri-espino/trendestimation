"""Paper C experiment002: small matched conventional trajectory forecast baselines.

Predeclared training-only spline smoothing and polynomial/Savitzky-Golay
continuation rules. NEVER uses a future observed position to choose parameters.
The five NGSIM segments contain only TWO distinct vehicle IDs.
No independent true jerk observation is available.

From repo root:
 python paper/ngsim-jerk-case-study/experiments/experiment002/run.py --output-dir <output>
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
from collections import defaultdict
from pathlib import Path
import sys

import numpy as np
from scipy import __version__ as scipy_version
from scipy.interpolate import UnivariateSpline
from scipy.signal import savgol_filter

CASE = Path(__file__).resolve().parents[2]
REPO = CASE.parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))

spec = importlib.util.spec_from_file_location("ngsim_exp002_case", CASE / "run_case.py")
assert spec is not None and spec.loader is not None
case = importlib.util.module_from_spec(spec)
spec.loader.exec_module(case)

METHODS = (
    "spline_cubic_taylor2",
    "spline_cubic_taylor3",
    "spline_cubic_local25",
    "savgol_21_taylor2",
    "savgol_21_taylor3",
    "raw_local_quad25",
    "raw_local_cubic25",
)


def estimate_sigma_training_only(y: np.ndarray) -> float:
    """Predeclared robust heuristic; the third differences contain real motion.

    For independent errors, var(D3 eps)=20*sigma^2. The estimator is
    only a smoothing-rule heuristic, NOT a NGSIM error estimate.
    """
    d3 = np.diff(np.asarray(y, dtype=float), n=3)
    median = np.median(d3)
    mad = np.median(np.abs(d3 - median))
    return float(np.clip(1.4826 * mad / math.sqrt(20.0), 0.01, 0.75))


def forecasts(train: np.ndarray, horizon: int) -> tuple[dict[str,np.ndarray], float]:
    y = np.asarray(train, dtype=float)
    if y.ndim != 1 or y.size < 30 or not np.all(np.isfinite(y)):
        raise ValueError("Expected >=30 finite position samples")
    if not isinstance(horizon, (int, np.integer)) or horizon <= 0:
        raise ValueError("Positive integer horizon required")

    dt = float(case.DT)
    t = np.arange(len(y), dtype=float) * dt
    t_last = t[-1]
    lag = np.arange(1, horizon + 1, dtype=float) * dt
    sigma = estimate_sigma_training_only(y)
    spline = UnivariateSpline(t, y, k=3, s=len(y)*sigma*sigma)
    z = spline(t)
    x0 = float(spline(t_last))
    v = float(spline.derivative(1)(t_last))
    a = float(spline.derivative(2)(t_last))
    j = float(spline.derivative(3)(t_last))

    smooth_sg = savgol_filter(y, 21, 3, mode="interp")
    derivatives = [
        float(savgol_filter(y, 21, 3, deriv=i, delta=dt, mode="interp")[-1])
        for i in range(1, 4)
    ]
    z0 = float(smooth_sg[-1])
    sg_v, sg_a, sg_j = derivatives

    outputs = {
        "spline_cubic_taylor2": x0+v*lag+a*lag*lag/2,
        "spline_cubic_taylor3": x0+v*lag+a*lag*lag/2+j*lag**3/6,
        "spline_cubic_local25": case.continuation(z, order=3, mu=0.0, horizon=horizon),
        "savgol_21_taylor2": z0+sg_v*lag+sg_a*lag*lag/2,
        "savgol_21_taylor3": z0+sg_v*lag+sg_a*lag*lag/2+sg_j*lag**3/6,
        "raw_local_quad25": case.polynomial_baseline(y, horizon, degree=2, window=25),
        "raw_local_cubic25": case.polynomial_baseline(y, horizon, degree=3, window=25),
    }
    for name, pred in outputs.items():
        if len(pred) != horizon or not np.all(np.isfinite(pred)):
            raise FloatingPointError(f"Nonfinite {name} forecast")
    assert tuple(outputs) == METHODS
    return outputs, sigma


def calculate() -> tuple[list[dict], list[dict], dict, str]:
    tracks, provenance = case.source_tracks()
    rows = []
    n = case.TRAIN_N
    for track, whole in sorted(tracks.items()):
        for origin in case.ORIGINS:
            train = whole[origin-n:origin]
            if len(train) != n:
                raise AssertionError("Frozen NGSIM window length changed")
            forecast, sigma = forecasts(train, max(case.HORIZONS))
            for horizon in case.HORIZONS:
                truth = whole[origin:origin+horizon]
                if len(truth) != horizon:
                    raise AssertionError("Missing NGSIM future holdout")
                for method in METHODS:
                    pred = forecast[method][:horizon]
                    delta = pred-truth
                    rows.append({
                        "track": int(track), "origin": int(origin),
                        "horizon": int(horizon), "method": method,
                        "noise_sigma_training_only_m": sigma,
                        "mse_m2": float(np.mean(delta**2)),
                        "mae_m": float(np.mean(np.abs(delta))),
                        "valid": True,
                    })
    if len(rows) != 5*3*3*len(METHODS):
        raise AssertionError("Unexpected baseline output count")
    groups = defaultdict(list)
    for row in rows:
        groups[(row["method"],row["horizon"])].append(row)
    summary = []
    for (method,horizon), values in sorted(groups.items()):
        if len(values) != 15:
            raise AssertionError("Expected 15 overlapping origins for each comparator")
        summary.append({
            "method": method, "horizon": horizon,
            "n_origins": len(values),
            "rmse_m": math.sqrt(sum(r["mse_m2"] for r in values)/len(values)),
            "mae_m": sum(r["mae_m"] for r in values)/len(values),
        })

    reference = json.loads((
        CASE / "experiments" / "experiment001" / "results" / "forecast_summary.json"
    ).read_text(encoding="utf-8"))
    gcv = [
        r for r in reference
        if r["criterion"] == "gcv" and r["horizon"] in case.HORIZONS
    ]
    if len(gcv) != 12:
        raise AssertionError("Archived experiment001 GCV rows differ")
    manuscript = [
        "# Experiment002 — conventional trajectory forecasts on frozen NGSIM pilot",
        "",
        "**Status:** completed descriptive matched benchmark; NOT independent vehicle-level validation.",
        "Five track segments originate from **two vehicle IDs**; the 15 origins overlap.",
        "No true jerk ground truth. All reported errors are observed future-position errors.",
        "",
        "## Training-only, predeclared methods",
        "",
        "- Cubic smoothing spline with estimated training-only noise scale; quadratic or cubic Taylor continuation.",
        "- Cubic smoothing spline followed by the same local-25 quadratic continuation as PLS.",
        "- Savitzky–Golay (window 21, degree 3) endpoint derivatives, quadratic or cubic Taylor continuation.",
        "- Ordinary local polynomial degree 2 or 3 on the last 25 raw positions.",
        "",
        "The spline smoothing target is s = n*clip(1.4826*MAD(D3 y)/sqrt(20),0.01,0.75)^2.",
        "This is a **fixed heuristic**, not tuning against future positions or a claimed observation noise variance.",
        "",
        "## RMSE by horizon (meters)",
        "",
        "| Method | 0.5 s | 1.0 s | 2.0 s |",
        "| --- | ---: | ---: | ---: |",
    ]
    allrows = {}
    for row in summary:
        allrows.setdefault(row["method"],{})[row["horizon"]] = row["rmse_m"]
    for item in gcv:
        name = "PLS_GCV_"+item["rule"]+"_"+item["mu_policy"]
        allrows.setdefault(name,{})[item["horizon"]] = item["rmse_m"]
    for name in sorted(allrows):
        vals=allrows[name]
        manuscript.append(
            f"| {name} | {vals[5]:.6f} | {vals[10]:.6f} | {vals[20]:.6f} |"
        )
    manuscript += [
        "",
        "## Limits and next steps",
        "",
        "This is a small, previously examined retrospective sample, with two unique vehicles and correlated windows.",
        "No independent statistical superiority or physically measured jerk is established.",
        "Compare on held-out vehicle IDs and known-jerk simulations, and explore robustness",
        "to spline smoothness and the size of the forecasting window before submitting Paper C.",
        "",
    ]
    manifest = {
        "experiment_id": "experiment002",
        "status": "descriptive_archived_ngsim_baseline_comparison",
        "source_doi": provenance["official_doi"],
        "data_subset_sha256": provenance["subset_sha256"],
        "n_tracks": len(tracks),
        "distinct_vehicle_ids": len({v["vehicle_id"] for v in provenance["selected"]}),
        "n_origins": len(tracks)*len(case.ORIGINS),
        "n_rows": len(rows),
        "n_summary_rows": len(summary),
        "n_train": n,
        "sample_dt_seconds": case.DT,
        "horizon_frames": list(case.HORIZONS),
        "methods": list(METHODS),
        "spline_k": 3,
        "spline_s_rule": "n*(clip(1.4826*MAD(D3 y)/sqrt(20),0.01,0.75))**2",
        "scipy_version": scipy_version,
        "numpy_version": np.__version__,
        "runner_name": os.environ.get("RUNNER_NAME","local"),
        "run_id": os.environ.get("GITHUB_RUN_ID",""),
        "qualifier": "retrospective 15 correlated origins; only 2 unique vehicle ids; no jerk truth",
    }
    return rows, summary, manifest, "\n".join(manuscript)+"\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    rows, summary, manifest, report = calculate()
    d = args.output_dir
    d.mkdir(parents=True,exist_ok=True)
    for name, value in [
        ("forecast_rows.json",rows),("forecast_summary.json",summary),
        ("run_manifest.json",manifest)
    ]:
        (d/name).write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (d/"RESULTS.md").write_text(report,encoding="utf-8")
    print(report)
    print("Saved",len(rows),"rows to",d)


if __name__=="__main__":
    main()
