"""Experiment001: matched d=3 PLS continuation rules on archived NGSIM.

Uses the *same historical fits and archived in-sample selections* as Paper C.
Does not rerun hyperparameter optimization, redownload raw trajectories, or
overwrite the original case-study's results.

Run from repository root:
    python paper/ngsim-jerk-case-study/experiments/experiment001/run.py
    python paper/ngsim-jerk-case-study/experiments/experiment001/run.py --verify

The saved rows are a small descriptive historical pilot, NOT an independent
vehicle-level benchmark or a test of ground-truth physical jerk.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

CASE = Path(__file__).resolve().parents[2]
REPO = CASE.parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))

spec = importlib.util.spec_from_file_location("ngsim_case_exp001", CASE / "run_case.py")
assert spec is not None and spec.loader is not None
case = importlib.util.module_from_spec(spec)
spec.loader.exec_module(case)
from trendestimation import TrendSmoother


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _close(a: float, b: float, *, atol: float = 2e-6, rtol: float = 1e-8) -> bool:
    return math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol)


def calculate() -> tuple[list[dict], list[dict], dict]:
    tracks, provenance = case.source_tracks()
    selections = _load(CASE / "results" / "selection_rows.json")
    archived = _load(CASE / "results" / "forecast_rows.json")

    # Archive contains selections for other d, too. Never reselect on holdouts.
    selected = [r for r in selections if r["d"] == 3 and r["status"] == "ok"]
    if len(selected) != 5 * 3 * 2 * 5:
        raise AssertionError("Unexpected number of frozen d=3 selections")

    historical = {
        (int(r["track"]), int(r["origin"]), str(r["mu_policy"]),
         str(r["criterion"]), int(r["horizon"])): float(r["mse"])
        for r in archived if r["order"] == 3 and r["method"].startswith("PLS_")
    }
    if len(historical) != len(selected) * len(case.HORIZONS):
        raise AssertionError("Existing d=3 forecast reference rows changed")

    solver = TrendSmoother(case.TRAIN_N, order=3)
    rows: list[dict] = []
    max_baseline_mse_discrepancy = 0.0
    for record in selected:
        track, origin = int(record["track"]), int(record["origin"])
        policy, criterion = str(record["mu_policy"]), str(record["criterion"])
        y = tracks[track]
        train = y[origin-case.TRAIN_N:origin]
        mu, lam = float(record["mu"]), float(record["lambda"])
        if len(train) != case.TRAIN_N or not np.isfinite(lam):
            raise AssertionError("Training length/selected finite lambda changed")
        expected_mu = (
            0.0 if policy == "zero" else float(np.mean(np.diff(train, n=3)))
        )
        if not _close(mu, expected_mu, atol=1e-10):
            raise AssertionError("A selection uses mismatched training-only mu")
        trend = solver.fit(train, lambda_=lam, mu=mu).trend

        for h in case.HORIZONS:
            truth = y[origin:origin+h]
            predictions = {
                "local25": case.continuation(trend, 3, mu, h),
                "guerrero_last3": case.continuation_guerrero_d3(trend, mu, h),
            }
            for rule, pred in predictions.items():
                if len(pred) != h or not np.all(np.isfinite(pred)):
                    raise AssertionError(f"Invalid forecast {track=} {rule=} {h=}")
                mse = float(np.mean((pred-truth)**2))
                mae = float(np.mean(np.abs(pred-truth)))
                if rule == "local25":
                    old = historical[(track, origin, policy, criterion, h)]
                    max_baseline_mse_discrepancy = max(
                        max_baseline_mse_discrepancy, abs(old-mse)
                    )
                    if not _close(old, mse):
                        raise AssertionError(
                            "Old local25 forecast cannot be reproduced; "
                            f"{track=} {origin=} {policy=} {criterion=} {h=} "
                            f"old={old} new={mse}"
                        )
                rows.append({
                    "track": track, "origin": origin, "horizon": int(h),
                    "criterion": criterion, "mu_policy": policy,
                    "S": float(record["S"]), "lambda": lam,
                    "mu": mu, "rule": rule,
                    "mse": mse, "mae": mae, "valid": True,
                })

    summary = []
    groups = defaultdict(list)
    for r in rows:
        groups[(r["rule"], r["mu_policy"], r["criterion"], r["horizon"])].append(r)
    for rule, policy, criterion, horizon in sorted(groups):
        items = groups[(rule, policy, criterion, horizon)]
        if len(items) != 15:
            raise AssertionError("Expected exactly 15 overlapping origins")
        summary.append({
            "rule": rule, "mu_policy": policy,
            "criterion": criterion, "horizon": horizon,
            "n_evaluated": len(items),
            "rmse_m": float(np.sqrt(np.mean([r["mse"] for r in items]))),
            "mae_m": float(np.mean([r["mae"] for r in items])),
        })

    manifest = {
        "experiment_id": "experiment001",
        "status": "computed_archived_trajectory_pilot",
        "data_doi": provenance["official_doi"],
        "source_subset_sha256": provenance["subset_sha256"],
        "n_tracks": len(tracks),
        "distinct_vehicle_ids": len({
            item["vehicle_id"] for item in provenance["selected"]
        }),
        "n_origins": len(tracks)*len(case.ORIGINS),
        "n_fitted_selected_trends": len(selected),
        "n_forecast_rows": len(rows),
        "n_summary_rows": len(summary),
        "difference_order": 3,
        "sample_seconds": case.DT,
        "training_points": case.TRAIN_N,
        "horizon_frames": list(case.HORIZONS),
        "selection_policy": "reuse_archived_selected_lambdas_and_mu",
        "forecast_rules": ["local25", "guerrero_last3"],
        "max_existing_local25_mse_discrepancy": max_baseline_mse_discrepancy,
        "status_note": (
            "Historical descriptive comparison; five track segments, "
            "not five independent vehicle identities; no jerk truth."
        ),
        "reproduction_command": (
            "python paper/ngsim-jerk-case-study/experiments/experiment001/run.py --verify"
        ),
    }
    if len(rows) != 900 or len(summary) != 60:
        raise AssertionError("Incomplete experiment001 output")
    return rows, summary, manifest


def verify_file(actual, path: Path, name: str):
    expected = _load(path)
    if isinstance(actual, list):
        if len(actual) != len(expected):
            raise AssertionError(f"{name}: row count changed")
        for i, (item, original) in enumerate(zip(actual, expected)):
            if set(item) != set(original):
                raise AssertionError(f"{name}: schema mismatch at row {i}")
            for key, val in item.items():
                ref = original[key]
                if isinstance(val, (float, int)) and not isinstance(val, bool):
                    if not _close(val, ref, atol=2e-6):
                        raise AssertionError(
                            f"{name}: row {i} key {key} got {val}, expected {ref}"
                        )
                elif val != ref:
                    raise AssertionError(
                        f"{name}: row {i} key {key} got {val}, expected {ref}"
                    )
    else:
        if set(actual) != set(expected):
            raise AssertionError(f"{name}: manifest schema mismatch")
        for key, val in actual.items():
            ref = expected[key]
            if isinstance(val, (float, int)) and not isinstance(val, bool):
                if not _close(val, ref, atol=2e-6):
                    raise AssertionError(f"{name}: mismatch at {key}")
            elif val != ref:
                raise AssertionError(f"{name}: mismatch at {key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify", action="store_true",
        help="verify checked-in outputs without overwriting results"
    )
    args = parser.parse_args()
    rows, summary, manifest = calculate()
    result_dir = HERE / "results"
    data = {
        "forecast_rows.json": rows,
        "forecast_summary.json": summary,
        "run_manifest.json": manifest,
    }
    if args.verify:
        for name, result in data.items():
            verify_file(result, result_dir / name, name)
        print("Verified all saved experiment001 rows and prior local25 forecasts.")
    else:
        result_dir.mkdir(parents=True, exist_ok=True)
        for name, result in data.items():
            (result_dir / name).write_text(
                json.dumps(result, indent=2, allow_nan=False) + "\n",
                encoding="utf-8",
            )
        print(
            "Saved", len(rows), "forecast rows and", len(summary),
            "summaries; matched original local25 MSE to",
            manifest["max_existing_local25_mse_discrepancy"],
        )


if __name__ == "__main__":
    main()
