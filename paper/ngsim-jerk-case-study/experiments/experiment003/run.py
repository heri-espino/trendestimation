"""Experiment003: fair GCV-selected cubic smoothing spline forecasts.

All spline smoothing penalties are automatically selected by SciPy generalized
cross-validation on each 80-position TRAINING window. No future observations
enter selection. Results are descriptive for 5 NGSIM segments (2 vehicle IDs).

From repository root:
  python paper/ngsim-jerk-case-study/experiments/experiment003/run.py --output-dir <dir>
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
from scipy.interpolate import make_smoothing_spline

CASE=Path(__file__).resolve().parents[2]
REPO=CASE.parents[1]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(REPO/"src"))
spec=importlib.util.spec_from_file_location("ngsim_exp003_case",CASE/"run_case.py")
assert spec is not None and spec.loader is not None
case=importlib.util.module_from_spec(spec)
spec.loader.exec_module(case)

METHODS=(
    "spline_gcv_taylor2",
    "spline_gcv_taylor3",
    "spline_gcv_local25",
    "spline_gcv_native",
)


def forecasts(train: np.ndarray, horizon: int) -> dict[str, np.ndarray]:
    y=np.asarray(train,dtype=float)
    if y.ndim!=1 or y.size<30 or not np.all(np.isfinite(y)):
        raise ValueError("Expected at least 30 finite training positions")
    if not isinstance(horizon,(int,np.integer)) or horizon<=0:
        raise ValueError("Horizon must be a positive integer")

    dt=float(case.DT)
    t=np.arange(len(y),dtype=float)*dt
    t_last=float(t[-1])
    lag=np.arange(1,horizon+1,dtype=float)*dt
    # Default lam=None invokes the documented in-sample GCV criterion.
    # It is NEVER selected against the future holdout positions.
    spline=make_smoothing_spline(t,y,lam=None)
    z=np.asarray(spline(t),dtype=float)
    x0=float(spline(t_last))
    velocity=float(spline.derivative(1)(t_last))
    acceleration=float(spline.derivative(2)(t_last))
    jerk=float(spline.derivative(3)(t_last))
    x2=x0+velocity*lag+acceleration*lag**2/2
    result={
        "spline_gcv_taylor2": x2,
        "spline_gcv_taylor3": x2+jerk*lag**3/6,
        "spline_gcv_local25": case.continuation(z,order=3,mu=0.0,horizon=horizon),
        "spline_gcv_native": np.asarray(spline(t_last+lag),dtype=float),
    }
    for method,pred in result.items():
        if pred.shape!=(horizon,) or not np.all(np.isfinite(pred)):
            raise FloatingPointError(f"Invalid spline GCV forecast for {method}")
    return result


def calculate() -> tuple[list[dict],list[dict],dict,str]:
    tracks,provenance=case.source_tracks()
    records=[]
    for track,whole in sorted(tracks.items()):
        for origin in case.ORIGINS:
            train=whole[origin-case.TRAIN_N:origin]
            pred=forecasts(train,max(case.HORIZONS))
            for h in case.HORIZONS:
                truth=whole[origin:origin+h]
                if len(truth)!=h:
                    raise AssertionError("Missing future holdout")
                for method in METHODS:
                    delta=pred[method][:h]-truth
                    records.append({
                        "track":int(track),"origin":int(origin),
                        "horizon":int(h),"method":method,
                        "mse_m2":float(np.mean(delta**2)),
                        "mae_m":float(np.mean(np.abs(delta))),
                        "valid":True,
                    })
    if len(records)!=5*3*3*len(METHODS):
        raise AssertionError("Expected 180 forecast records")
    groups=defaultdict(list)
    for row in records:
        groups[(row["method"],row["horizon"])].append(row)
    summaries=[]
    for (method,h),values in sorted(groups.items()):
        if len(values)!=15:
            raise AssertionError("Expected exactly fifteen overlapping origins")
        summaries.append({
            "method":method,"horizon":h,"n_origins":len(values),
            "rmse_m":math.sqrt(sum(r["mse_m2"] for r in values)/len(values)),
            "mae_m":sum(r["mae_m"] for r in values)/len(values),
        })

    def read(path:Path):
        return json.loads(path.read_text(encoding="utf-8"))

    previous=read(CASE/"experiments"/"experiment002"/"results"/"forecast_summary.json")
    pls=read(CASE/"experiments"/"experiment001"/"results"/"forecast_summary.json")
    selected=[r for r in pls if r["criterion"]=="gcv" and r["horizon"] in case.HORIZONS]
    if len(previous)!=21 or len(selected)!=12:
        raise AssertionError("Prior benchmark provenance mismatch")

    table={}
    for r in summaries+previous:
        table.setdefault(r["method"],{})[r["horizon"]]=r["rmse_m"]
    for r in selected:
        key="PLS_GCV_"+r["rule"]+"_"+r["mu_policy"]
        table.setdefault(key,{})[r["horizon"]]=r["rmse_m"]

    report=[
        "# Experiment003 — GCV-selected smoothing spline on frozen NGSIM",
        "",
        "**Status:** completed historical pilot only; 5 segments from 2 vehicle IDs.",
        "The SciPy cubic smoothing spline penalty is selected by GCV exclusively",
        "from the first 80 training positions. No future observation tunes it.",
        "All errors refer to recorded future positions, not measured physical jerk.",
        "",
        "## Mean position RMSE in meters over 15 overlapping origins",
        "",
        "| Method | 0.5 s | 1.0 s | 2.0 s |",
        "| --- | ---: | ---: | ---: |",
    ]
    for method in sorted(table):
        s=table[method]
        report.append(f"| {method} | {s[5]:.6f} | {s[10]:.6f} | {s[20]:.6f} |")
    report+=[
        "",
        "## Scientific limitations",
        "",
        "Four spline continuations share the same GCV-estimated historical spline.",
        "Natural spline boundary conditions can force nearly linear extrapolation",
        "or unstable higher-order polynomial extrapolation depending on data.",
        "This sample has only two distinct vehicle identifiers and overlapping origins.",
        "Any strong result needs many independent vehicles and simulated known-jerk truth.",
        "Neither a first-in-literature claim nor proof of physical jerk accuracy is supported.",
        "",
    ]
    manifest={
        "experiment_id":"experiment003",
        "status":"gcv_spline_retrospective_archived_ngsim_pilot",
        "source_doi":provenance["official_doi"],
        "data_subset_sha256":provenance["subset_sha256"],
        "n_tracks":len(tracks),
        "distinct_vehicle_ids":len({r["vehicle_id"] for r in provenance["selected"]}),
        "n_origins":len(tracks)*len(case.ORIGINS),
        "n_rows":len(records),
        "n_summary_rows":len(summaries),
        "n_train":case.TRAIN_N,
        "dt_seconds":case.DT,
        "horizon_frames":list(case.HORIZONS),
        "selector":"scipy.interpolate.make_smoothing_spline(lam=None): GCV on training only",
        "methods":list(METHODS),
        "scipy_version":scipy_version,
        "numpy_version":np.__version__,
        "runner_name":os.environ.get("RUNNER_NAME","local"),
        "run_id":os.environ.get("GITHUB_RUN_ID",""),
        "limitations":"two vehicle IDs and overlapping origins; jerk truth unavailable",
    }
    return records,summaries,manifest,"\n".join(report)+"\n"


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    opts=parser.parse_args()
    rows,summary,manifest,report=calculate()
    target=opts.output_dir
    target.mkdir(parents=True,exist_ok=True)
    for name,value in [
        ("forecast_rows.json",rows),
        ("forecast_summary.json",summary),
        ("run_manifest.json",manifest),
    ]:
        (target/name).write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (target/"RESULTS.md").write_text(report,encoding="utf-8")
    print(report)
    print("Saved",len(rows),"rows")


if __name__=="__main__":
    main()
