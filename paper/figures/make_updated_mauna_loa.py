"""Reproduce the 1990--September 2026 Mauna Loa controlled-smoothness example.

Source: frozen NOAA GML-derived published monthly mean observations (ppm).
The repository pins the values and their vintage in noaa_mlo_monthly_1990_2026_09.csv;
this script does not download moving external data or extrapolate October 2026.

Run from repository root:
    python paper/figures/make_updated_mauna_loa.py

Outputs:
    paper/figures/mauna_loa_1990_2026_09.dat
    paper/real_data_2026_summary.json

An independent legacy 1990--1999 experiment remains unchanged.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np

from trendestimation import TrendSmoother

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = HERE / "noaa_mlo_monthly_1990_2026_09.csv"
OUTPUT = HERE / "mauna_loa_1990_2026_09.dat"
SUMMARY = ROOT / "real_data_2026_summary.json"
ORDERS = (2, 3, 4, 5)
SMOOTHNESS = 0.86


def load_observations(path: Path = SOURCE) -> tuple[list[date], np.ndarray]:
    """Validate the complete, ordered, frozen monthly NOAA-derived slice."""
    rows = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        data = (line for line in handle if not line.startswith("#"))
        for row in csv.DictReader(data):
            if set(row) != {"month", "average_ppm"}:
                raise ValueError("Unexpected columns in frozen NOAA snapshot.")
            try:
                month = date.fromisoformat(row["month"] + "-01")
                ppm = float(row["average_ppm"])
            except (ValueError, TypeError) as exc:
                raise ValueError("Invalid frozen NOAA monthly value.") from exc
            if not np.isfinite(ppm) or not 200.0 < ppm < 600.0:
                raise ValueError("Missing, imputed-as-sentinel or implausible ppm.")
            rows.append((month, ppm))

    dates = [row[0] for row in rows]
    if len(dates) != 441 or dates[0] != date(1990, 1, 1) or dates[-1] != date(2026, 9, 1):
        raise ValueError("Expected exactly 441 months from Jan 1990 through Sep 2026.")
    serial = np.array([d.year * 12 + d.month for d in dates], dtype=np.int64)
    if not np.all(np.diff(serial) == 1):
        raise ValueError("NOAA months must be contiguous, without duplicates.")
    observations = np.array([row[1] for row in rows], dtype=float)
    if not np.isclose(observations[-1], 426.07, rtol=0, atol=1e-12):
        raise ValueError("Pinned September 2026 NOAA value has changed.")
    return dates, observations


def generate(*, validate_only: bool = False) -> dict:
    dates, observed = load_observations()
    checksum = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    n = len(observed)
    report = {
        "dataset": "NOAA GML Mauna Loa monthly mean CO2 (ppm), frozen derived slice",
        "snapshot_file": str(SOURCE.relative_to(ROOT.parent)),
        "snapshot_sha256": checksum,
        "data_vintage": "2026-10-09",
        "accessed": "2026-10-25",
        "period": "1990-01 to 2026-09",
        "n_months": n,
        "latest_observed_ppm": float(observed[-1]),
        "source_noaa_url": "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv",
        "source_note": (
            "1990-01..2026-08 NOAA average via datasets/co2-ppm public mirror; "
            "2026-09 426.07 verified from NOAA October 9 release. "
            "Different source and aggregation from legacy statsmodels weekly dataset."
        ),
        "normalized_target_smoothness": SMOOTHNESS,
        "fixed_mu": 0.0,
        "orders": list(ORDERS),
        "limits": (
            "Two-sided descriptive PLS fits; no held-out forecasts, "
            "seasonal adjustment, uncertainty intervals, or new measured-data claim."
        ),
    }
    if validate_only:
        return report

    profiles = {}
    parameters = {}
    for d in ORDERS:
        smoother = TrendSmoother(n, order=d)
        penalty = smoother.lambda_for_smoothness(SMOOTHNESS)
        fit = smoother.fit(observed, lambda_=penalty, mu=0.0)
        if not np.isclose(fit.smoothness, SMOOTHNESS, rtol=0, atol=2e-9):
            raise ArithmeticError("Smoothness inversion did not attain the target.")
        if not np.all(np.isfinite(fit.trend)):
            raise ArithmeticError("PLS returned a nonfinite trend.")
        profiles[d] = fit.trend
        parameters[str(d)] = {
            "lambda": float(penalty),
            "smoothness": float(fit.smoothness),
            "edf_conditional": float(fit.edf_conditional),
            "residual_rmse_ppm": float(np.sqrt(np.mean(fit.residual**2))),
            "final_fitted_trend_ppm": float(fit.trend[-1]),
        }

    # Same column contract as legacy real-data .dat for AwesomeFigures.
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("year observed d2 d3 d4 d5\n")
        for i, month in enumerate(dates):
            year = month.year + (month.month - 1) / 12.0
            values = [year, observed[i]] + [profiles[d][i] for d in ORDERS]
            handle.write(" ".join(f"{v:.12g}" for v in values) + "\n")

    report["by_order"] = parameters
    SUMMARY.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true",
                        help="Validate pinned NOAA dates/values without fitting.")
    args = parser.parse_args()
    print(json.dumps(generate(validate_only=args.validate_only), indent=2))


if __name__ == "__main__":
    main()
