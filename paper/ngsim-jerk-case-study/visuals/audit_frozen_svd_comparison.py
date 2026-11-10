"""Read-only secondary audit of immutable Experiment008 fitted-outcome rows.

This script does NOT load/recreate clean/noisy trajectories, refit any PLS,
run a parameter search, change the experimental protocol, or claim a new
experiment. It verifies the historical TSVD-GCV high-rank failure and computes
an explicitly conditional, balanced-stratum paired bootstrap for the PLS
versus nominal-EDF-matched TSVD *historical discrete-jerk* RMSE contrast.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

METHODS = (
    "pls_profileml_cubic_ols",
    "tsvd_matched_edf",
    "tsvd_gcv_cubic_ols",
    "cubic_spline_gcv",
    "savitzky_golay_21_3",
)
REFERENCE = {
    "pls_profileml_cubic_ols": 2.4412570862016945,
    "tsvd_matched_edf": 2.9416214671451617,
    "tsvd_gcv_cubic_ols": 250.71810360983292,
}


def checksum(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for part in iter(lambda: f.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


def read_rows(path: Path, expected_episodes: int, expected_strata: int) -> dict:
    """Check each paired row, without changing old source or estimator choice."""
    groups = defaultdict(dict)
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {
            "sample_id", "site", "stratum", "method", "rank_retained",
            "effective_df", "historical_jerk_mse_m2_s6", "status",
        }
        if not required.issubset(reader.fieldnames or ()):
            raise ValueError("Missing Experiment008 frozen-data fields")
        count = 0
        for row in reader:
            sid, method = row["sample_id"], row["method"]
            if method not in METHODS or row["status"] != "ok":
                raise ValueError("Unexpected historical smoother row")
            if not sid or method in groups[sid]:
                raise ValueError("Duplicate or missing sample/method identity")
            if row["site"] != "simulation":
                raise ValueError("Expected only archived synthetic known truth")
            loss = float(row["historical_jerk_mse_m2_s6"])
            if not np.isfinite(loss) or loss < 0:
                raise ValueError("Invalid recorded historical-jerk MSE")
            rank = int(row["rank_retained"]) if row["rank_retained"] else None
            df = float(row["effective_df"]) if row["effective_df"] else None
            groups[sid][method] = {
                "loss": loss, "stratum": row["stratum"], "rank": rank, "edf": df
            }
            count += 1
    if len(groups) != expected_episodes or count != expected_episodes * len(METHODS):
        raise ValueError("Archive has missing or unexpected episodes/fits")
    strata = defaultdict(list)
    for sid in sorted(groups):
        d = groups[sid]
        if set(d) != set(METHODS):
            raise ValueError(f"Incomplete paired historical methods: {sid}")
        distinct_strata = {d[m]["stratum"] for m in METHODS}
        if len(distinct_strata) != 1:
            raise ValueError("Mismatched stratum across paired methods")
        strata[next(iter(distinct_strata))].append(sid)
        ref_df = d["pls_profileml_cubic_ols"]["edf"]
        hard_df = d["tsvd_matched_edf"]["edf"]
        if ref_df is None or hard_df is None or abs(hard_df - ref_df) > 0.5000001:
            raise ValueError("Stored nominal-EDF rank matching is inconsistent")
    if len(strata) != expected_strata:
        raise ValueError("Incorrect number of balanced design strata")
    expected_per_cell = expected_episodes // expected_strata
    if expected_per_cell * expected_strata != expected_episodes:
        raise ValueError("Expected cases must divide evenly across strata")
    if set(map(len, strata.values())) != {expected_per_cell}:
        raise ValueError("Stratum is unbalanced; do not apply balanced bootstrap")
    return {"rows": groups, "strata": strata, "n": len(groups)}


def analyze(
    source: Path, expected_episodes: int = 1296, expected_strata: int = 54,
    resamples: int = 5000, seed: int = 30133,
) -> dict:
    if resamples < 1000:
        raise ValueError("Use at least 1000 Monte Carlo bootstrap replicates")
    data = read_rows(source, expected_episodes, expected_strata)
    groups, strata, n = data["rows"], data["strata"], data["n"]
    mses = {
        m: np.array([groups[sid][m]["loss"] for sid in sorted(groups)])
        for m in METHODS
    }
    rmse = {m: float(np.sqrt(np.mean(loss))) for m, loss in mses.items()}
    if n == 1296 and expected_strata == 54:
        for m, target in REFERENCE.items():
            if abs(rmse[m] - target) > 2e-8:
                raise ValueError("Archived numerical checksum differs from confirmed ledger")

    ranks = Counter(
        groups[sid]["tsvd_gcv_cubic_ols"]["rank"] for sid in groups
    )
    if None in ranks or min(ranks) < 0 or max(ranks) > 76:
        raise ValueError("Invalid historical TSVD-GCV rank")
    flagged = [
        sid for sid in groups if groups[sid]["tsvd_gcv_cubic_ols"]["rank"] in (75, 76)
    ]
    all_gcv = sum(groups[sid]["tsvd_gcv_cubic_ols"]["loss"] for sid in groups)
    bad_gcv = sum(groups[sid]["tsvd_gcv_cubic_ols"]["loss"] for sid in flagged)
    frac = bad_gcv / all_gcv
    if n == 1296 and expected_strata == 54:
        if len(flagged) != 145 or abs(frac - 0.7894650568496807) > 1e-10:
            raise ValueError("Archived high-rank/error decomposition was not reproduced")

    rng = np.random.default_rng(seed)
    # Resample complete paired *trajectory* outcomes within each of the
    # predeclared 54 factorial cells, fixing original cell composition.
    # This is descriptive Monte Carlo uncertainty, conditional on the
    # original designed mixture; it is not uncertainty over NGSIM drivers.
    means = np.zeros((resamples, 2), dtype=float)
    for cell in sorted(strata):
        ids = sorted(strata[cell])
        losses = np.array([
            [groups[sid][METHODS[0]]["loss"], groups[sid][METHODS[1]]["loss"]]
            for sid in ids
        ])
        sampled = losses[
            rng.integers(0, len(ids), size=(resamples, len(ids)))
        ]
        means += np.sum(sampled, axis=1) / n
    root_means = np.sqrt(means)
    # Positive means nominally matched TSVD has larger pooled jerk RMSE.
    difference = root_means[:, 1] - root_means[:, 0]
    ratio = root_means[:, 1] / root_means[:, 0]
    low, high = np.quantile(difference, [0.025, 0.975])
    ratio_low, ratio_high = np.quantile(ratio, [0.025, 0.975])
    point_diff = rmse[METHODS[1]] - rmse[METHODS[0]]
    return {
        "status": "verified",
        "source_sha256": checksum(source),
        "source_name": source.name,
        "n_paired_trajectories": n,
        "n_methods": len(METHODS),
        "n_design_cells": len(strata),
        "n_per_design_cell": n // len(strata),
        "historical_discrete_jerk_rmse_m_per_s3": rmse,
        "rank_distribution_tsvd_conditional_gcv": dict(sorted(ranks.items())),
        "near_interpolating_rank_75_76_count": len(flagged),
        "near_interpolating_rank_75_76_error_share": float(frac),
        "nominal_edf_matched_tsvd_minus_pls_rmse_m_per_s3": float(point_diff),
        "stratified_paired_bootstrap": {
            "resamples": resamples, "seed": seed,
            "unit": "full paired synthetic trajectory",
            "stratification": "54 predeclared regime/noise/error cells",
            "conditional_on": "fixed balanced synthetic design, not NGSIM population",
            "rmse_difference_95pct_interval_m_per_s3": [float(low), float(high)],
            "rmse_ratio_tsvd_to_pls": rmse[METHODS[1]] / rmse[METHODS[0]],
            "rmse_ratio_95pct_interval": [float(ratio_low), float(ratio_high)],
        },
        "caveat": (
            "This reads the original fitted rows only; it does not retune "
            "conditional TSVD-GCV or convert nominal EDF to exact full-fit EDF."
        )
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fitted-rows", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--resamples", type=int, default=5000)
    p.add_argument("--seed", type=int, default=30133)
    opts = p.parse_args()
    if opts.output.exists():
        raise FileExistsError("Read-only audit must not overwrite prior output")
    result = analyze(opts.fitted_rows, resamples=opts.resamples, seed=opts.seed)
    opts.output.parent.mkdir(parents=True, exist_ok=True)
    opts.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
