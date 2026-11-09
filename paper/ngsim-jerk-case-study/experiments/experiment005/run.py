"""Paper C Experiment005: reproducible known-jerk simulation experiment.

Real NGSIM results (experiment004) remain archived and untouched.
Only this isolated directory contains synthetic data and known truth.

Usage:
    python run.py --stage pilot --output-dir C:/.../experiment005/run-123/pilot
    python run.py --stage confirm --output-dir C:/.../experiment005/run-123/confirm
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import sys
import time

import numpy as np
from scipy import __version__ as scipy_version
from scipy.interpolate import make_smoothing_spline
from scipy.signal import savgol_filter

PAPER = Path(__file__).resolve().parents[2]
REPO = PAPER.parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))
from trendestimation import TrendSmoother, select_lambda  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "paper_c_exp005_source", PAPER / "run_case.py"
)
assert _spec is not None and _spec.loader is not None
_case = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_case)

CONFIG_FILE = HERE / "config.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def step_jerk_trajectory(
    t: np.ndarray, base_jerk: float, changes: list[tuple[float, float]],
    initial_velocity: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Integrate jerk steps analytically using positive-part cubics."""
    position = initial_velocity * t + base_jerk * t**3 / 6.0
    velocity = initial_velocity + base_jerk * t**2 / 2.0
    acceleration = base_jerk * t
    jerk = np.full(t.shape, base_jerk, dtype=float)
    for switch, delta in changes:
        u = np.maximum(t - switch, 0.0)
        position += delta * u**3 / 6.0
        velocity += delta * u**2 / 2.0
        acceleration += delta * u
        jerk += delta * (t >= switch)
    return position, velocity, acceleration, jerk


def truth(regime: str, t: np.ndarray, config: dict):
    """Provide exactly differentiable clean x,v,a,j in SI units."""
    v0 = float(config["true_movement"]["baseline_initial_speed_m_s"])
    amps = config["true_movement"]["jerk_amplitudes"]
    if regime == "constant_zero":
        result = step_jerk_trajectory(t, 0.0, [], v0)
    elif regime == "constant_positive":
        result = step_jerk_trajectory(t, float(amps["constant_positive"]), [], v0)
    elif regime == "constant_negative":
        result = step_jerk_trajectory(t, float(amps["constant_negative"]), [], v0)
    elif regime == "sign_reversal":
        before = float(amps["sign_reversal_before"])
        after = float(amps["sign_reversal_after"])
        result = step_jerk_trajectory(
            t, before, [(float(amps["sign_reversal_time_s"]), after - before)], v0,
        )
    elif regime == "braking_pulse":
        pulse = float(amps["braking_pulse"])
        result = step_jerk_trajectory(t, 0.0, [
            (float(amps["braking_start_s"]), pulse),
            (float(amps["braking_end_s"]), -pulse),
        ], v0)
    elif regime == "sinusoidal":
        amplitude = float(amps["sinusoidal_amplitude"])
        omega = 2.0 * np.pi / float(amps["sinusoidal_period_s"])
        position = (
            v0 * t + amplitude * t**2 / (2.0 * omega)
            + amplitude * (np.cos(omega*t) - 1.0) / omega**3
        )
        velocity = v0 + amplitude * t / omega - amplitude * np.sin(omega*t) / omega**2
        acceleration = amplitude * (1.0 - np.cos(omega*t)) / omega
        jerk = amplitude * np.sin(omega*t)
        result = position, velocity, acceleration, jerk
    else:
        raise ValueError("Unregistered jerk regime: " + regime)
    return tuple(np.asarray(row, dtype=float) for row in result)


def observations(
    x: np.ndarray, *, sigma: float, noise_type: str,
    rng: np.random.Generator, train_n: int, config: dict,
    trial_index: int,
) -> np.ndarray:
    """Generate full noisy observation stream; training uses only first n."""
    rho = float(config["noise"]["ar1_rho"])
    if noise_type == "ar1_rho065":
        z = rng.standard_normal(len(x))
        errors = np.empty(len(x), dtype=float)
        errors[0] = sigma * z[0]
        for i in range(1, len(x)):
            errors[i] = rho * errors[i-1] + sigma * math.sqrt(1-rho*rho) * z[i]
    elif noise_type in ("iid_gaussian", "last_train_outlier"):
        errors = rng.normal(0.0, sigma, size=len(x))
        if noise_type == "last_train_outlier":
            sign = 1.0 if trial_index % 2 == 0 else -1.0
            errors[train_n-1] += (
                sign * float(config["noise"]["outlier_multiples_of_sigma"]) * sigma
            )
    else:
        raise ValueError("Unrecognized noise model: " + noise_type)
    return np.asarray(x + errors, dtype=float)


def mu_policies(y: np.ndarray, clean: np.ndarray, dt: float) -> dict[str, float]:
    """Zero, data-only estimates and labelled UNAVAILABLE real-data oracle."""
    n = len(y)
    times = dt * np.arange(n, dtype=float)

    def cubic(window: int) -> float:
        fit = np.polynomial.Polynomial.fit(
            times[-window:], y[-window:], deg=3
        ).convert()
        # cubic coefficient has units m/s^3; D3 third-difference mean is m.
        return float(6.0 * fit.coef[3] * dt**3)

    return {
        "zero": 0.0,
        "sample": float(np.mean(np.diff(y, n=3))),
        "ols_global": cubic(n),
        "ols_tail25": cubic(25),
        "oracle": float(np.mean(np.diff(clean, n=3))),
    }


def forecasts_of_trend(trend: np.ndarray, mu: float, horizon: int):
    return {
        "guerrero_last3": _case.continuation_guerrero_d3(
            trend, mu, horizon
        ),
        "local25": _case.continuation(trend, order=3, mu=mu, horizon=horizon),
    }


def other_methods(y: np.ndarray, dt: float, horizon: int):
    """Comparable in-sample smoothing and predeclared extrapolators."""
    n = len(y)
    times = np.arange(n, dtype=float) * dt
    future = times[-1] + dt * np.arange(1, horizon+1, dtype=float)
    lag = future - times[-1]
    smooth = make_smoothing_spline(times, y, lam=None)  # training-only GCV
    spline_fit = np.asarray(smooth(times), dtype=float)
    predicted_spline = (
        float(smooth(times[-1]))
        + float(smooth.derivative(1)(times[-1])) * lag
        + 0.5 * float(smooth.derivative(2)(times[-1])) * lag**2
    )
    sg_fit = savgol_filter(y, window_length=21, polyorder=3, mode="interp")
    sg_vel = float(savgol_filter(y, 21, 3, deriv=1, delta=dt, mode="interp")[-1])
    sg_acc = float(savgol_filter(y, 21, 3, deriv=2, delta=dt, mode="interp")[-1])
    predicted_sg = sg_fit[-1] + sg_vel*lag + 0.5*sg_acc*lag**2
    predicted_raw_quad = _case.polynomial_baseline(
        y, horizon, degree=2, window=25
    )
    return {
        "spline_gcv_taylor2": (spline_fit, predicted_spline),
        "savgol21_taylor2": (sg_fit, predicted_sg),
        "raw_local_quad25": (None, predicted_raw_quad),
    }


def stable_seed(stage: str, regime: str, sigma: float, noise: str, rep: int) -> int:
    """Independent, reproducible seeds with disjoint pilot/confirm namespaces."""
    message = f"exp005|20261108|{stage}|{regime}|{sigma:.10g}|{noise}|{rep}".encode()
    return int.from_bytes(hashlib.sha256(message).digest()[:8], "little")


def rows_for_stage(config: dict, stage: str) -> list[dict]:
    cfg = config["experiments"][stage]
    regimes = config["true_movement"]["regimes"] if cfg["regimes"] == "all" else cfg["regimes"]
    cases = []
    for regime in regimes:
        for sigma in cfg["sigma_m"]:
            for noise in cfg["noise_types"]:
                for rep in range(int(cfg["reps_per_cell"])):
                    cases.append({
                        "regime": regime, "sigma_m": float(sigma),
                        "noise_model": noise, "rep": rep, "stage": stage,
                        "seed": stable_seed(stage, regime, float(sigma), noise, rep),
                        "scenario_key": f"{regime}|{sigma:.6g}|{noise}",
                    })
    if len(cases) != int(cfg["expected_trials"]):
        raise AssertionError("Saved design's expected-trial count disagrees with grid")
    return cases


def _append_csv(writer, fields, attrs, name, status, **values):
    record = {field: "" for field in fields}
    record.update(attrs)
    record.update({"method": name, "status": status})
    record.update(values)
    writer.writerow(record)


def simulate(config: dict, stage: str, output: Path):
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite an existing experiment run: {output}")
    if stage not in config["experiments"]:
        raise ValueError("Unknown simulation stage: " + stage)
    started = time.perf_counter()
    dt = float(config["sampling_interval_s"])
    n = int(config["train_frames"])
    horizons = tuple(int(h) for h in config["forecast_horizons_frames"])
    horizon = max(horizons)
    t = np.arange(n+horizon, dtype=float)*dt
    cases = rows_for_stage(config, stage)
    grid = tuple(float(s) for s in config["policies"]["smoothness_grid"])
    smoother = TrendSmoother(n, order=3)
    penalties = tuple(float(smoother.lambda_for_smoothness(s)) for s in grid)
    fixed_lambda = float(smoother.lambda_for_smoothness(
        float(config["policies"]["fixed_S_ablation"])
    ))
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(CONFIG_FILE, output / "config.json")
    files = {
        "forecasts": "forecast_rows.csv",
        "fits": "jerk_rows.csv",
        "selections": "selection_rows.csv",
        "ablation": "ablation_rows.csv",
    }
    paths = {key: output / name for key, name in files.items()}
    schemas = {
        "forecasts": [
            "trial_id","scenario_key","regime","sigma_m","noise_model","rep","seed",
            "horizon_frames","method","status","mse_m2","mae_m","final_error_m","reason",
        ],
        "fits": [
            "trial_id","scenario_key","regime","sigma_m","noise_model","rep","seed",
            "method","status","historical_position_mse_m2","jerk_mse_m2_s6",
            "tail_jerk_mse_m2_s6","reference_mu_m","true_training_mu_m","reason",
        ],
        "selections": [
            "trial_id","scenario_key","regime","sigma_m","noise_model","rep","seed",
            "method","status","criterion","mu_policy","mu_m","true_mu_m",
            "selected_S","selected_lambda","criterion_score","reason",
        ],
        "ablation": [
            "trial_id","scenario_key","regime","sigma_m","noise_model","rep","seed",
            "horizon_frames","mu_source","rule","fit_policy","forecast_policy",
            "fixed_S","mu_reference_m","mse_m2","status","reason",
        ],
    }
    handles = {}
    writers = {}
    for key, path in paths.items():
        handle = path.open("x", newline="", encoding="utf-8")
        handles[key] = handle
        writer = csv.DictWriter(handle, fieldnames=schemas[key], extrasaction="raise")
        writer.writeheader()
        writers[key] = writer
    trajectory_path = output / "trajectories.jsonl.gz"
    clean_by_regime = {
        regime: truth(regime, t, config)
        for regime in config["true_movement"]["regimes"]
    }
    counts = Counter()
    errors = Counter()
    try:
        with gzip.open(trajectory_path, "xt", encoding="utf-8") as trace:
            for index, case in enumerate(cases):
                attrs = {"trial_id": f"{stage}_{index:06d}",
                         **{key: case[key] for key in (
                             "scenario_key","regime","sigma_m",
                             "noise_model","rep","seed"
                         )}}
                clean_x, clean_v, clean_a, clean_j = clean_by_regime[case["regime"]]
                generated = observations(
                    clean_x, sigma=case["sigma_m"],
                    noise_type=case["noise_model"],
                    rng=np.random.default_rng(case["seed"]),
                    train_n=n, config=config, trial_index=case["rep"],
                )
                trace.write(json.dumps({
                    **attrs,
                    "time_seconds": t.tolist(),
                    "clean_position_m": clean_x.tolist(),
                    "clean_velocity_m_s": clean_v.tolist(),
                    "clean_acceleration_m_s2": clean_a.tolist(),
                    "true_instantaneous_jerk_m_s3": clean_j.tolist(),
                    "observed_noisy_position_m": generated.tolist(),
                    "observations_used_to_fit": n,
                    "future_predictions_scored_against": "clean_position_m",
                }, allow_nan=False) + "\n")
                observed = generated[:n]
                truth_train = clean_x[:n]
                mu_ref = mu_policies(observed, truth_train, dt)
                true_discrete_jerk = np.diff(truth_train, n=3) / dt**3

                def record_fit(method: str, fitted: np.ndarray, mu: float):
                    error = (fitted - truth_train)
                    jerk_delta = (
                        np.diff(fitted, n=3) / dt**3 - true_discrete_jerk
                    )
                    _append_csv(writers["fits"], schemas["fits"], attrs,
                                method, "ok",
                                historical_position_mse_m2=float(np.mean(error**2)),
                                jerk_mse_m2_s6=float(np.mean(jerk_delta**2)),
                                tail_jerk_mse_m2_s6=float(np.mean(jerk_delta[-25:]**2)),
                                reference_mu_m=float(mu),
                                true_training_mu_m=mu_ref["oracle"])
                    counts["fits_ok"] += 1

                def record_future(method: str, prediction: np.ndarray):
                    if prediction.shape != (horizon,) or not np.all(np.isfinite(prediction)):
                        raise FloatingPointError(f"Invalid prediction for {method}")
                    for h in horizons:
                        err = prediction[:h] - clean_x[n:n+h]
                        _append_csv(writers["forecasts"], schemas["forecasts"],
                                    {**attrs, "horizon_frames": h}, method, "ok",
                                    mse_m2=float(np.mean(err**2)),
                                    mae_m=float(np.mean(np.abs(err))),
                                    final_error_m=float(err[-1]))
                        counts["forecasts_ok"] += 1

                def record_invalid(method: str, error: Exception, *, forecast=True, fit=True):
                    reason = f"{type(error).__name__}: {error}"[:300]
                    errors[reason] += 1
                    if fit:
                        _append_csv(writers["fits"], schemas["fits"], attrs,
                                    method, "invalid", reason=reason)
                        counts["fits_invalid"] += 1
                    if forecast:
                        for h in horizons:
                            _append_csv(writers["forecasts"], schemas["forecasts"],
                                        {**attrs, "horizon_frames":h},
                                        method, "invalid", reason=reason)
                            counts["forecasts_invalid"] += 1

                for policy, mu in mu_ref.items():
                    for criterion in config["policies"]["lambda_selection"]:
                        selector_name = f"pls_{criterion}_{policy}"
                        try:
                            choice = select_lambda(
                                smoother, observed, mu=mu,
                                criterion=criterion, grid=penalties,
                                method="grid",
                            )
                            fitted = np.asarray(smoother.fit(
                                observed, lambda_=choice.lambda_, mu=mu
                            ).trend, dtype=float)
                            _append_csv(writers["selections"], schemas["selections"], attrs,
                                        selector_name, "ok", criterion=criterion,
                                        mu_policy=policy, mu_m=mu,
                                        true_mu_m=mu_ref["oracle"],
                                        selected_S=choice.smoothness,
                                        selected_lambda=choice.lambda_,
                                        criterion_score=choice.score)
                            counts["selections_ok"] += 1
                            record_fit(selector_name, fitted, mu)
                            for rule, predicted in forecasts_of_trend(
                                fitted, mu, horizon
                            ).items():
                                record_future(f"{selector_name}_{rule}", predicted)
                        except (ValueError, ArithmeticError, np.linalg.LinAlgError) as exc:
                            reason = f"{type(exc).__name__}: {exc}"[:300]
                            errors[reason] += 1
                            _append_csv(writers["selections"], schemas["selections"],
                                        attrs, selector_name, "invalid",
                                        criterion=criterion, mu_policy=policy,
                                        mu_m=mu, true_mu_m=mu_ref["oracle"], reason=reason)
                            counts["selections_invalid"] += 1
                            record_invalid(selector_name, exc, forecast=False)
                            for rule in config["policies"]["forecast_rules"]:
                                record_invalid(
                                    f"{selector_name}_{rule}", exc, fit=False
                                )
                try:
                    for name, (smooth_positions, forecast) in other_methods(
                        observed, dt, horizon
                    ).items():
                        if smooth_positions is not None:
                            record_fit(name, smooth_positions, 0.0)
                        record_future(name, np.asarray(forecast, dtype=float))
                except (ValueError, ArithmeticError, np.linalg.LinAlgError) as exc:
                    # A failed control is documented, not replaced by another.
                    for name in ("spline_gcv_taylor2", "savgol21_taylor2",
                                 "raw_local_quad25"):
                        record_invalid(name, exc, forecast=True,
                                       fit=name!="raw_local_quad25")

                # Fixed-S crossed reference design separates the effect of
                # historical fit mu from that of future continuation mu.
                for source in config["policies"]["ablation_mu_sources"]:
                    reference = float(mu_ref[source])
                    for rule in config["policies"]["forecast_rules"]:
                        try:
                            fits = {
                                "zero": smoother.fit(
                                    observed, lambda_=fixed_lambda, mu=0.0
                                ).trend,
                                "reference": smoother.fit(
                                    observed, lambda_=fixed_lambda, mu=reference
                                ).trend,
                            }
                            predictions = {}
                            for fit_pol, tr in fits.items():
                                for future_pol, fmu in (
                                    ("zero", 0.0), ("reference", reference)
                                ):
                                    predictions[(fit_pol, future_pol)] = (
                                        forecasts_of_trend(tr, fmu, horizon)[rule]
                                    )
                            interaction = (
                                predictions["reference","reference"]
                                - predictions["reference","zero"]
                                - predictions["zero","reference"]
                                + predictions["zero","zero"]
                            )
                            if np.max(np.abs(interaction)) > 1e-7:
                                raise AssertionError("Fixed-S crossed forecast nonlinearity")
                            for (fp, cp), pred in predictions.items():
                                for h in horizons:
                                    err = pred[:h] - clean_x[n:n+h]
                                    _append_csv(writers["ablation"], schemas["ablation"],
                                                {**attrs, "horizon_frames":h},
                                                f"ablation_{source}_{rule}_{fp}_{cp}",
                                                "ok", mu_source=source, rule=rule,
                                                fit_policy=fp, forecast_policy=cp,
                                                fixed_S=config["policies"]["fixed_S_ablation"],
                                                mu_reference_m=reference,
                                                mse_m2=float(np.mean(err**2)))
                                    counts["ablation_ok"] += 1
                        except (ValueError, ArithmeticError, np.linalg.LinAlgError,
                                AssertionError) as exc:
                            reason = f"{type(exc).__name__}: {exc}"[:300]
                            errors[reason] += 1
                            for fp in ("zero", "reference"):
                                for cp in ("zero", "reference"):
                                    for h in horizons:
                                        _append_csv(writers["ablation"], schemas["ablation"],
                                                    {**attrs,"horizon_frames":h},
                                                    f"ablation_{source}_{rule}_{fp}_{cp}",
                                                    "invalid", mu_source=source,rule=rule,
                                                    fit_policy=fp, forecast_policy=cp,
                                                    fixed_S=config["policies"]["fixed_S_ablation"],
                                                    mu_reference_m=reference,reason=reason)
                                        counts["ablation_invalid"] += 1

                counts["trials"] += 1
                if (index + 1) % 25 == 0 or index + 1 == len(cases):
                    print(f"{stage}: {index+1}/{len(cases)} known-truth trials", flush=True)
                    for handle in handles.values():
                        handle.flush()
    finally:
        for handle in handles.values():
            handle.close()
    elapsed = time.perf_counter() - started
    return {"counts":dict(counts),"errors":dict(errors),"seconds":elapsed,
            "n_trials":len(cases),"design":cases,"config_sha256":sha256(CONFIG_FILE)}


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8",newline="") as handle:
        return list(csv.DictReader(handle))


def reduce_results(output: Path, config: dict, info: dict, stage: str):
    """Preserve every trial; compute scenario-conditional Monte Carlo summaries."""
    forecast = load_csv(output / "forecast_rows.csv")
    fitted = load_csv(output / "jerk_rows.csv")
    ablation = load_csv(output / "ablation_rows.csv")
    grouped = defaultdict(list)
    for row in forecast:
        if row["status"] == "ok":
            grouped[(row["method"],row["horizon_frames"],row["scenario_key"])].append(
                float(row["mse_m2"])
            )
    groupfit = defaultdict(list)
    for row in fitted:
        if row["status"] == "ok":
            groupfit[(row["method"],row["scenario_key"])].append(
                float(row["jerk_mse_m2_s6"])
            )
    recs = []
    for (method,hor,scenario),s in sorted(grouped.items()):
        recs.append({
            "scenario_key":scenario,"method":method,"horizon_frames":int(hor),
            "n_valid_trials":len(s),"forecast_rmse_m":float(np.sqrt(np.mean(s))),
        })
    fsum = []
    for (method,scenario),s in sorted(groupfit.items()):
        fsum.append({
            "scenario_key":scenario,"method":method,
            "n_valid_trials":len(s),"historical_jerk_rmse_m_s3":float(np.sqrt(np.mean(s))),
        })
    all_scenario = sorted(set(r["scenario_key"] for r in forecast))
    all_methods = sorted(set(r["method"] for r in forecast))
    hor = list(config["forecast_horizons_frames"])
    pool = {}
    for m in all_methods:
        for h in hor:
            samples = [float(row["mse_m2"]) for row in forecast
                       if row["status"]=="ok" and row["method"]==m
                       and int(row["horizon_frames"])==h]
            pool[(m,h)] = {
                "method":m, "horizon_frames":h,
                "n_valid_trials":len(samples),
                "forecast_rmse_m":float(np.sqrt(np.mean(samples))) if samples else None,
            }
    jerk_pool = {}
    for m in sorted(set(r["method"] for r in fitted)):
        samples = [float(r["jerk_mse_m2_s6"]) for r in fitted
                   if r["status"]=="ok" and r["method"]==m]
        jerk_pool[m] = {
            "method":m,"n_valid_trials":len(samples),
            "jerk_rmse_m_s3":float(np.sqrt(np.mean(samples))) if samples else None
        }

    # Deterministically seeded paired Monte Carlo bootstrap by scenario,
    # not by frame, with each independent trial represented once.
    bykey = {
        (r["trial_id"],r["method"],int(r["horizon_frames"])): r
        for r in forecast
    }
    baseline="spline_gcv_taylor2"
    paired = []
    rng=np.random.default_rng(int(config["statistics"]["bootstrap_seed"]))
    repeats=int(config["statistics"]["bootstrap_repetitions"])
    for h in hor:
        for method in all_methods:
            if method==baseline:
                continue
            stratum = []
            for scenario in all_scenario:
                vals=[]
                for trial in info["design"]:
                    if trial["scenario_key"] != scenario:
                        continue
                    tid=f"{stage}_{info['design'].index(trial):06d}"
                    a=bykey.get((tid,method,int(h)))
                    b=bykey.get((tid,baseline,int(h)))
                    if a is not None and b is not None and a["status"]=="ok" and b["status"]=="ok":
                        vals.append(float(a["mse_m2"])-float(b["mse_m2"]))
                if vals:
                    stratum.append(np.asarray(vals,dtype=float))
            n=sum(len(v) for v in stratum)
            if n<12:
                paired.append({"method":method,"reference":baseline,
                               "horizon_frames":h,"n_paired":n,
                               "mean_delta_mse_m2":None,"lo_95":None,"hi_95":None})
                continue
            draws=np.empty(repeats)
            for i in range(repeats):
                draws[i]=sum(
                    float(a[rng.integers(0,len(a),size=len(a))].sum())
                    for a in stratum
                ) / n
            values=np.concatenate(stratum)
            lo,hi=np.quantile(draws,[0.025,0.975])
            paired.append({
                "method":method,"reference":baseline,"horizon_frames":h,
                "n_paired":n,"mean_delta_mse_m2":float(np.mean(values)),
                "lo_95":float(lo),"hi_95":float(hi),
                "fraction_trials_better":float(np.mean(values<0)),
                "inference":"scenario-stratified paired Monte Carlo bootstrap",
            })

    def dump(name,records):
        (output/name).write_text(json.dumps(records,indent=2,allow_nan=False)+"\n",
                                 encoding="utf-8")
    dump("scenario_forecast_summary.json",recs)
    dump("scenario_jerk_summary.json",fsum)
    dump("pooled_forecast_summary.json",list(pool.values()))
    dump("pooled_jerk_summary.json",list(jerk_pool.values()))
    dump("paired_bootstrap.json",paired)

    ranked=sorted(
        (v for v in pool.values() if v["forecast_rmse_m"] is not None),
        key=lambda r:(r["horizon_frames"],r["forecast_rmse_m"])
    )
    ranked_jerk=sorted(
        (v for v in jerk_pool.values() if v["jerk_rmse_m_s3"] is not None),
        key=lambda r:r["jerk_rmse_m_s3"]
    )
    text=[
        f"# Experiment005 {stage} — known jerk, controlled position observations",
        "",
        f"**Trials:** {info['n_trials']} independent seeded synthetic series.",
        f"**Duration:** {info['seconds']:.1f} seconds on {os.environ.get('RUNNER_NAME','local')}.",
        "**Reference truth:** exact analytic trajectories and discrete third differences;",
        "future forecasts evaluated against clean **known** positions.",
        "",
        "## Pooled future clean-position RMSE (meters)",
        "",
        "| Horizon | Method | RMSE (m) |",
        "| --- | --- | ---: |",
    ]
    for row in ranked:
        text.append(f"| {row['horizon_frames']} frames | {row['method']} | {row['forecast_rmse_m']:.6f} |")
    text += ["","## Historical known-discrete-jerk RMSE (m/s³)","","| Method | RMSE |","| --- | ---: |"]
    for row in ranked_jerk:
        text.append(f"| {row['method']} | {row['jerk_rmse_m_s3']:.6f} |")
    text += [
        "", "## Interpretation and limitations", "",
        "- Scenarios, noise and policy families were frozen in config.json.",
        "- Future-position target is **clean simulated position**, not a recorded video position.",
        "- Primary jerk target is exactly D3(true position)/dt³, aligned to the PLS finite-difference operator.",
        "- The oracle mu is available ONLY in synthetic trials and may not be used on real NGSIM.",
        "- The pooled mixture weights are constructed by design; results are not traffic-population inference.",
        "- Paired bootstrap intervals condition on this artificial generating process; competing methods/horizons were not multiplicity-adjusted.",
        "- Changing the mu fit generally changes the selected lambda; fixed-S crossings in ablation_rows.csv isolate the fit and continuation effects.",
        "- Retain all failure rows, full known/noisy trajectories and immutable run metadata.",
        "",
    ]
    (output/"RESULTS.md").write_text("\n".join(text),encoding="utf-8")
    return {"forecast_methods":len(all_methods),"jerk_methods":len(jerk_pool),
            "n_forecast_rows":len(forecast),"n_jerk_rows":len(fitted),
            "n_ablation_rows":len(ablation),
            "pairwise_comparisons":len(paired)}


def plot_results(output: Path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return {"created":False,"error":"matplotlib not installed"}
    records=json.loads((output/"pooled_forecast_summary.json").read_text())
    focus={
        "pls_gcv_zero_guerrero_last3","pls_mle_zero_guerrero_last3",
        "pls_gcv_sample_guerrero_last3","pls_mle_ols_global_guerrero_last3",
        "pls_gcv_oracle_guerrero_last3","spline_gcv_taylor2","savgol21_taylor2",
    }
    bymethod=defaultdict(dict)
    for row in records:
        if row["method"] in focus:
            bymethod[row["method"]][row["horizon_frames"]]=row["forecast_rmse_m"]
    fig, ax=plt.subplots(figsize=(9,5))
    for name, vals in sorted(bymethod.items()):
        if all(v is not None for v in vals.values()):
            ax.plot(sorted(vals), [vals[k] for k in sorted(vals)], marker="o", label=name)
    ax.set(xlabel="Forecast horizon (frames, 10 Hz)",
           ylabel="Known-clean future position RMSE (m)",
           title="Paper C Experiment005 — simulation forecast comparison")
    ax.grid(alpha=0.2);ax.legend(fontsize=7,loc="upper left")
    fig.tight_layout()
    (output/"figures").mkdir(exist_ok=True)
    fig.savefig(output/"figures"/"forecast_rmse.png",dpi=190)
    plt.close(fig)
    return {"created":True,"files":["figures/forecast_rmse.png"]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage",choices=("pilot","confirm"),required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    arguments=parser.parse_args()
    config=json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    start=datetime.now(timezone.utc).isoformat()
    destination=arguments.output_dir.resolve()
    info=simulate(config,arguments.stage,destination)
    aggregate=reduce_results(destination,config,info,arguments.stage)
    plots=plot_results(destination)
    manifest={
        "schema":1,"status":"completed_synthetic_known_jerk",
        "experiment":"experiment005","stage":arguments.stage,
        "started_utc":start,"completed_utc":datetime.now(timezone.utc).isoformat(),
        "source_repository_sha":os.environ.get("GITHUB_SHA","manual"),
        "runner_name":os.environ.get("RUNNER_NAME","manual"),
        "workflow_id":os.environ.get("GITHUB_RUN_ID",""),
        "persistent_run_output":str(destination),
        "config_sha256":info["config_sha256"],
        "synthetic_trial_count":info["n_trials"],
        "counts":info["counts"],"errors":info["errors"],
        "elapsed_wall_seconds":info["seconds"],
        "aggregates":aggregate,"figures":plots,
        "numpy_version":np.__version__,"scipy_version":scipy_version,
        "real_ngsim_data_used":False,"jerk_truth_observed":True,
        "reference_mean_oracle_is_synthetic_only":True,
    }
    (destination/"run_manifest.json").write_text(
        json.dumps(manifest,indent=2,allow_nan=False)+"\n",encoding="utf-8"
    )
    print((destination/"RESULTS.md").read_text(encoding="utf-8")[:12000],flush=True)
    print(f"Experiment005 {arguments.stage} saved to {destination}",flush=True)


if __name__=="__main__":
    main()
