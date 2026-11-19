"""Experiment004 — ONLY REAL NGSIM position forecast comparisons.

Compare third-difference PLS + (GCV or profiled Gaussian marginal MLE)
under zero/data-derived means and two extrapolators against:
  - training-only GCV natural cubic smoothing spline, Taylor quadratic;
  - training-only Savitzky-Golay endpoint quadratic Taylor;
  - training-only local quadratic raw-position extrapolation.

One predeclared origin per recorded contiguous trajectory episode.
Store all result rows on the VM. Summary and file inventory are mirrored
to a GitHub results-only branch by the self-hosted workflow.

Run: python evaluate.py --data-dir <run/data> --output-dir <run/results>
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import sys

import numpy as np
from scipy import __version__ as scipy_version
from scipy.interpolate import make_smoothing_spline
from scipy.signal import savgol_filter

CASE = Path(__file__).resolve().parents[2]
REPO = CASE.parents[1]
sys.path.insert(0, str(REPO / "src"))
from trendestimation import TrendSmoother, score_lambda  # noqa: E402

spec = importlib.util.spec_from_file_location("paper_c_ngsim_case4", CASE / "run_case.py")
assert spec is not None and spec.loader is not None
case = importlib.util.module_from_spec(spec)
spec.loader.exec_module(case)

S_GRID = (0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
          0.95, 0.975, 0.99, 0.995, 1.0)
METHODS = (
    "pls_gcv_zero_last3", "pls_gcv_zero_local25",
    "pls_gcv_sample_last3", "pls_gcv_sample_local25",
    "pls_mle_zero_last3", "pls_mle_zero_local25",
    "pls_mle_sample_last3", "pls_mle_sample_local25",
    "spline_gcv_taylor2", "savgol_21_taylor2", "raw_local_quad25",
)
HORIZONS = (5, 10, 20)
TRAIN_N = 80
ORIGIN = 100
DT = 0.1
BOOTSTRAP_REPS = 2000
BOOTSTRAP_SEED = 20261108
REFERENCE = "spline_gcv_taylor2"


def sha256(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def load_episodes(data_dir: Path) -> tuple[list[dict], dict]:
    source = data_dir / "selected_positions.csv"
    manifest_path = data_dir / "download_manifest.json"
    catalog_path = data_dir / "episode_catalog.json"
    for path in (source, manifest_path, catalog_path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing genuine NGSIM input: {path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["selected_positions_csv_sha256"] != sha256(source):
        raise ValueError("Downloaded NGSIM episode checksum mismatch")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    grouped = defaultdict(list)
    with source.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            grouped[row["episode_id"]].append((
                int(row["timestamp_ms"]), int(row["frame_id"]),
                float(row["longitudinal_m"]),
            ))
    episodes = []
    for item in catalog:
        group = grouped[item["episode_id"]]
        timestamps = np.asarray([x[0] for x in group], dtype=np.int64)
        frames = np.asarray([x[1] for x in group], dtype=np.int64)
        positions = np.asarray([x[2] for x in group], dtype=float)
        if (
            len(group) != item["n_frames"] or len(group) < ORIGIN + max(HORIZONS)
            or not np.all(np.diff(timestamps) == 100)
            or not np.all(np.diff(frames) == 1)
            or not np.all(np.isfinite(positions))
        ):
            raise ValueError(f"Invalid source sequence {item['episode_id']}")
        episodes.append({
            "episode_id": item["episode_id"],
            "site": item["site"],
            "session_proxy": item["session_proxy"],
            "vehicle_id": item["vehicle_id"],
            "y": positions - positions[0],
        })
    if len(episodes) != manifest["episode_count"] or len(episodes) < 12:
        raise ValueError("Insufficient independent episodes or catalog mismatch")
    return episodes, manifest


def _fit_methods(
    train: np.ndarray, *, smoother: TrendSmoother, penalties: tuple[float, ...],
) -> tuple[dict[str, np.ndarray], list[dict], dict[str, str]]:
    """Return 20-step forecasts, training-only selections and failure reasons."""
    predictions = {}
    selection_rows = []
    errors = {}
    mu_sample = float(np.mean(np.diff(train, n=3)))
    for criterion in ("gcv", "mle"):
        for policy, mu in (("zero", 0.0), ("sample", mu_sample)):
            key = f"pls_{criterion}_{policy}"
            try:
                scores = np.asarray([
                    score_lambda(
                        smoother, train, lambda_=lam, criterion=criterion,
                        mu=mu,
                    )
                    for lam in penalties
                ], dtype=float)
                if not np.any(np.isfinite(scores)):
                    raise ValueError("No finite training-only selection scores")
                idx = int(np.argmin(scores))
                selected = float(penalties[idx])
                fit = smoother.fit(train, lambda_=selected, mu=mu)
                predictions[key + "_last3"] = case.continuation_guerrero_d3(
                    fit.trend, mu, max(HORIZONS)
                )
                predictions[key + "_local25"] = case.continuation(
                    fit.trend, order=3, mu=mu, horizon=max(HORIZONS)
                )
                selection_rows.append({
                    "method_family": key, "criterion": criterion, "mu_policy": policy,
                    "mu_discrete_m": mu, "mu_reference_m_s3": mu / (DT ** 3),
                    "selected_S": S_GRID[idx], "selected_lambda": selected,
                    "criterion_score": float(scores[idx]), "status": "ok",
                })
            except (ValueError, ArithmeticError, np.linalg.LinAlgError) as exc:
                errors[key + "_last3"] = type(exc).__name__ + ": " + str(exc)[:250]
                errors[key + "_local25"] = type(exc).__name__ + ": " + str(exc)[:250]
                selection_rows.append({
                    "method_family": key, "criterion": criterion, "mu_policy": policy,
                    "mu_discrete_m": mu, "mu_reference_m_s3": mu / (DT ** 3),
                    "selected_S": "", "selected_lambda": "", "criterion_score": "",
                    "status": "invalid",
                })

    try:
        times = np.arange(TRAIN_N, dtype=float) * DT
        spline = make_smoothing_spline(times, train, lam=None)
        lag = np.arange(1, max(HORIZONS) + 1, dtype=float) * DT
        predictions["spline_gcv_taylor2"] = (
            float(spline(times[-1]))
            + float(spline.derivative(1)(times[-1])) * lag
            + 0.5 * float(spline.derivative(2)(times[-1])) * lag**2
        )
    except (ValueError, ArithmeticError, np.linalg.LinAlgError) as exc:
        errors["spline_gcv_taylor2"] = type(exc).__name__ + ": " + str(exc)[:250]
    try:
        smooth = savgol_filter(train, window_length=21, polyorder=3, mode="interp")
        vel = float(savgol_filter(
            train, 21, 3, deriv=1, delta=DT, mode="interp"
        )[-1])
        acc = float(savgol_filter(
            train, 21, 3, deriv=2, delta=DT, mode="interp"
        )[-1])
        lag = np.arange(1, max(HORIZONS) + 1, dtype=float) * DT
        predictions["savgol_21_taylor2"] = smooth[-1] + vel*lag + 0.5*acc*lag**2
    except (ValueError, ArithmeticError) as exc:
        errors["savgol_21_taylor2"] = type(exc).__name__ + ": " + str(exc)[:250]
    try:
        predictions["raw_local_quad25"] = case.polynomial_baseline(
            train, max(HORIZONS), degree=2, window=25
        )
    except (ValueError, ArithmeticError) as exc:
        errors["raw_local_quad25"] = type(exc).__name__ + ": " + str(exc)[:250]

    for name in METHODS:
        pred = predictions.get(name)
        if pred is not None and (
            pred.shape != (max(HORIZONS),)
            or not np.all(np.isfinite(pred))
        ):
            del predictions[name]
            errors[name] = "Forecast returned nonfinite or malformed positions"
    return predictions, selection_rows, errors


def calculate(
    episodes: list[dict],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    smoother = TrendSmoother(TRAIN_N, order=3)
    penalties = tuple(float(smoother.lambda_for_smoothness(s)) for s in S_GRID)
    records, selections = [], []
    for index, episode in enumerate(episodes, 1):
        y = episode["y"]
        train = np.asarray(y[ORIGIN - TRAIN_N:ORIGIN], dtype=float)
        forecasts, selected, errors = _fit_methods(
            train, smoother=smoother, penalties=penalties,
        )
        for row in selected:
            selections.append({
                "episode_id": episode["episode_id"], "site": episode["site"], **row,
            })
        for method in METHODS:
            pred = forecasts.get(method)
            for h in HORIZONS:
                if pred is not None:
                    deviation = np.asarray(pred[:h] - y[ORIGIN:ORIGIN + h])
                    mse = float(np.mean(deviation ** 2))
                    mae = float(np.mean(np.abs(deviation)))
                    fde = float(abs(deviation[-1]))
                    valid = bool(np.isfinite(mse) and np.isfinite(mae))
                else:
                    mse = mae = fde = float("nan")
                    valid = False
                records.append({
                    "episode_id": episode["episode_id"], "site": episode["site"],
                    "session_proxy": episode["session_proxy"],
                    "vehicle_id": episode["vehicle_id"],
                    "origin": ORIGIN, "method": method, "horizon_frames": h,
                    "mse_m2": mse if valid else "", "mae_m": mae if valid else "",
                    "fde_m": fde if valid else "",
                    "status": "ok" if valid else "invalid",
                    "reason": "" if valid else errors.get(method, "Nonfinite error"),
                })
        if index % 25 == 0:
            print(f"Scored {index}/{len(episodes)} REAL episodes", flush=True)
    summaries, inference = summarize(records, episodes)
    return records, selections, summaries, inference


def summarize(
    records: list[dict], episodes: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Real-position RMSE and exploratory paired episode bootstrap, not jerk truth."""
    by_key = {(r["episode_id"], r["method"], r["horizon_frames"]): r for r in records}
    sites = sorted(set(e["site"] for e in episodes))
    summary = []
    paired = []
    for site in ("all", *sites):
        subset = [e for e in episodes if site == "all" or e["site"] == site]
        for h in HORIZONS:
            for method in METHODS:
                samples = [
                    by_key[(e["episode_id"], method, h)]
                    for e in subset
                ]
                good = [r for r in samples if r["status"] == "ok"]
                summary.append({
                    "site": site, "horizon_frames": h, "method": method,
                    "n_episode_candidates": len(samples),
                    "n_valid": len(good),
                    "n_invalid": len(samples) - len(good),
                    "rmse_m": float(np.sqrt(np.mean([r["mse_m2"] for r in good])))
                    if good else "",
                    "mae_m": float(np.mean([r["mae_m"] for r in good]))
                    if good else "",
                    "fde_m": float(np.mean([r["fde_m"] for r in good]))
                    if good else "",
                })
    # CI on paired episode mean squared-error differences against the spline.
    # Resample within locations. This is conditional/descriptive; simultaneous
    # vehicles share scene conditions and session clusters remain dependent.
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    for h in HORIZONS:
        for method in METHODS:
            if method == REFERENCE:
                continue
            per_site = []
            for site in sites:
                pairs = []
                for e in episodes:
                    if e["site"] != site:
                        continue
                    a = by_key[(e["episode_id"], method, h)]
                    b = by_key[(e["episode_id"], REFERENCE, h)]
                    if a["status"] == "ok" and b["status"] == "ok":
                        pairs.append(float(a["mse_m2"] - b["mse_m2"]))
                if pairs:
                    per_site.append(np.asarray(pairs, dtype=float))
            n = sum(len(s) for s in per_site)
            if n < 12:
                paired.append({
                    "method": method, "reference": REFERENCE,
                    "horizon_frames": h, "n_paired": n,
                    "status": "insufficient_paired_episodes",
                })
                continue
            bootstrap = np.zeros(BOOTSTRAP_REPS, dtype=float)
            for i in range(BOOTSTRAP_REPS):
                parts = [
                    s[rng.integers(0, len(s), size=len(s))]
                    for s in per_site
                ]
                bootstrap[i] = float(np.sum([p.sum() for p in parts]) / n)
            all_deltas = np.concatenate(per_site)
            low, high = np.quantile(bootstrap, [0.025, 0.975])
            paired.append({
                "method": method, "reference": REFERENCE,
                "horizon_frames": h, "n_paired": n,
                "mean_delta_mse_m2": float(np.mean(all_deltas)),
                "ci_95_low_m2": float(low),
                "ci_95_high_m2": float(high),
                "fraction_episodes_better": float(np.mean(all_deltas < 0)),
                "status": "exploratory_stratified_episode_bootstrap",
            })
    return summary, paired


def csv_write(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"Refusing to save empty table: {path}")
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite experiment output: {path}")
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def report(summary: list[dict], paired: list[dict], manifest: dict) -> str:
    rows = [
        "# Experiment004 — expanded REAL NGSIM GCV/ML + spline forecasts",
        "",
        "**Status:** " + manifest["status"],
        "",
        "No simulated positions or jerk were created. All outcomes compare "
        "forecasts with recorded future NGSIM positions.",
        "",
        f"Downloaded eligible trajectory episodes: **{manifest['n_episodes']}**.",
        "These are episode units, **not verified unique physical vehicles**.",
        "One predeclared origin per episode; each sample is an overlapping "
        "horizon of the same episode.",
        "",
        "## RMSE of future observed position (meters), all sites",
        "",
        "| Method | 0.5 s | 1 s | 2 s |",
        "| --- | ---: | ---: | ---: |",
    ]
    by_key = {(r["method"], r["horizon_frames"]): r
              for r in summary if r["site"] == "all"}
    for name in METHODS:
        line = [name]
        for h in HORIZONS:
            row = by_key[(name, h)]
            value = row["rmse_m"]
            line.append(f"{value:.6f}" if isinstance(value, float) else "NA")
        rows.append("| " + " | ".join(line) + " |")
    rows += [
        "", "## Paired exploratory inference (method minus GCV spline)",
        "",
        "Negative ΔMSE favors the named method. Stratified bootstrap resamples",
        "**trajectory episodes**, not individual forecast steps. Dependence",
        "within recording sessions remains, so these intervals are **exploratory**.",
        "No multiple-testing correction or claim of population significance.",
        "",
        "| Method | Horizon | n paired | ΔMSE (m²) | 95% bootstrap interval (m²) |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in paired:
        if row["status"] != "exploratory_stratified_episode_bootstrap":
            rows.append(
                f"| {row['method']} | {row['horizon_frames']} | {row['n_paired']} "
                "| NA | insufficient data |"
            )
            continue
        rows.append(
            f"| {row['method']} | {row['horizon_frames']} "
            f"| {row['n_paired']} | {row['mean_delta_mse_m2']:.5f} "
            f"| [{row['ci_95_low_m2']:.5f}, {row['ci_95_high_m2']:.5f}] |"
        )
    rows += [
        "",
        "## Method interpretation and unavoidable limitations",
        "",
        "- PLS MLE means **profiled Gaussian marginal-likelihood selection**",
        "  in this repository, a REML-style criterion, NOT an assertion of",
        "  exact joint Guerrero likelihood MLE for (lambda, mu, sigma²).",
        "- Training-derived mu is conditional; its estimation is not refit",
        "  for every held-out leave-one-out sample.",
        "- NGSIM Vehicle_ID can repeat. Recorded episodes are defined by",
        "  location, ID, start time and frame/time continuity; repeated",
        "  drivers across episodes or shared scenes can induce dependence.",
        "- Ground-truth physical jerk is NOT observed; this experiment",
        "  supports only statistical analysis of recorded-position forecasts.",
        "- If the data-selection screen favors typical motions or the first",
        "  IDs, sampling need not represent the full traffic population.",
        "- Complete raw source pages, selected trajectories, all model rows,",
        "  environment and file inventory are retained in the persistent VM",
        "  directory listed in the run manifest. Their exact hashes are",
        "  recorded so another agent can audit them.",
        "",
    ]
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_dir.resolve()
    if root.exists():
        raise FileExistsError(f"Refusing to overwrite existing run results: {root}")
    episodes, download_manifest = load_episodes(args.data_dir.resolve())
    rows, selections, summaries, paired = calculate(episodes)
    root.mkdir(parents=True, exist_ok=False)
    csv_write(root / "forecast_rows.csv", rows)
    csv_write(root / "selection_rows.csv", selections)
    csv_write(root / "summary.csv", summaries)
    csv_write(root / "paired_bootstrap.csv", paired)
    manifest = {
        "schema": 1, "experiment_id": "experiment004",
        "status": "completed_real_ngsim_expanded",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "persistent_vm_results_dir": str(root),
        "persistent_vm_data_dir": str(args.data_dir.resolve()),
        "n_episodes": len(episodes), "by_site": {
            site: sum(e["site"] == site for e in episodes)
            for site in sorted(set(e["site"] for e in episodes))
        },
        "n_forecast_rows": len(rows), "n_selections": len(selections),
        "n_summary_rows": len(summaries), "n_paired_comparisons": len(paired),
        "run_status_counts": dict(__import__("collections").Counter(r["status"] for r in rows)),
        "download_manifest_sha256": sha256(args.data_dir / "download_manifest.json"),
        "selected_positions_sha256": download_manifest["selected_positions_csv_sha256"],
        "source_dataset_doi": download_manifest["official_doi"],
        "source_repository_sha": os.environ.get("GITHUB_SHA", "manual"),
        "selection_criteria": ["gcv", "mle"],
        "mle_definition": "profiled Gaussian marginal likelihood; mu conditional, not joint MLE",
        "smoothing_grid": list(S_GRID),
        "reference_mean_policies": ["zero", "sample"],
        "forecast_rules": ["last3", "local25", "GCV spline Taylor2",
                           "Savitzky-Golay Taylor2", "raw quadratic25"],
        "forecast_horizons_frames": list(HORIZONS), "training_frames": TRAIN_N,
        "origin_frame": ORIGIN, "dt_seconds": DT,
        "bootstrap_seed": BOOTSTRAP_SEED, "bootstrap_reps": BOOTSTRAP_REPS,
        "numpy_version": np.__version__, "scipy_version": scipy_version,
        "runner_name": os.environ.get("RUNNER_NAME", "manual"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "primary_outcome": "recorded_future_position_mse_m2",
        "jerk_ground_truth": False,
    }
    (root / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    text = report(summaries, paired, manifest)
    (root / "RESULTS.md").write_text(text, encoding="utf-8")
    print(text, flush=True)
    print(f"Saved complete run to: {root}", flush=True)


if __name__ == "__main__":
    main()
