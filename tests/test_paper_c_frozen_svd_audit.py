"""Frozen Experiment008 outcomes are audited, never refitted."""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "ngsim-jerk-case-study" / "visuals" / "audit_frozen_svd_comparison.py"
spec = importlib.util.spec_from_file_location("frozen_svd_review", SOURCE)
assert spec and spec.loader
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def synthetic_rows(path: Path):
    out = []
    for cell in ("a", "b"):
        for j in (0, 1):
            sid = f"{cell}-{j}"
            for method in audit.METHODS:
                loss = (j + 1) ** 2
                if method == "tsvd_matched_edf":
                    loss += 1.5
                elif method == "tsvd_gcv_cubic_ols":
                    loss += 3.0
                row = {
                    "sample_id": sid, "site": "simulation", "stratum": cell,
                    "method": method, "n_training": 80, "reference_mu_discrete_m": 0,
                    "lambda": "", "rank_retained": (
                        75 if method == "tsvd_gcv_cubic_ols" else
                        (0 if method == "tsvd_matched_edf" else "")
                    ),
                    "effective_df": (
                        3 if method == "tsvd_matched_edf" else
                        (3.4 if method == "pls_profileml_cubic_ols" else "")
                    ),
                    "S_equiv": "", "historical_position_mse_m2": 0,
                    "historical_jerk_mse_m2_s6": loss, "status": "ok",
                }
                out.append(row)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)


def test_frozen_jerk_audit_is_deterministic_and_paired(tmp_path):
    source = tmp_path / "fitted_rows.csv"
    synthetic_rows(source)
    a = audit.analyze(source, expected_episodes=4,
                      expected_strata=2, resamples=1000, seed=333)
    b = audit.analyze(source, expected_episodes=4,
                      expected_strata=2, resamples=1000, seed=333)
    assert a == b
    assert a["n_paired_trajectories"] == 4
    assert a["n_design_cells"] == 2
    assert a["near_interpolating_rank_75_76_count"] == 4
    assert a["nominal_edf_matched_tsvd_minus_pls_rmse_m_per_s3"] > 0
    lo, hi = a["stratified_paired_bootstrap"]["rmse_difference_95pct_interval_m_per_s3"]
    assert 0 < lo <= hi
    assert a["source_sha256"] == audit.checksum(source)


def test_frozen_audit_rejects_missing_paired_rows(tmp_path):
    source = tmp_path / "fitted_rows.csv"
    synthetic_rows(source)
    lines = source.read_text(encoding="utf-8").splitlines()
    source.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing or unexpected"):
        audit.analyze(source, expected_episodes=4, expected_strata=2, resamples=1000)


def test_frozen_audit_rejects_corrupted_data(tmp_path):
    source = tmp_path / "fitted_rows.csv"
    synthetic_rows(source)
    content = source.read_text(encoding="utf-8")
    corrupted = content.replace(",2.0,ok", ",nan,ok")
    if corrupted == content:
        corrupted = content.replace(",1,ok", ",nan,ok")
    source.write_text(corrupted, encoding="utf-8")
    with pytest.raises(ValueError):
        audit.analyze(source, expected_episodes=4, expected_strata=2, resamples=1000)
