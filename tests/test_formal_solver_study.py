"""Tests of the blocked design, statistical calculations and file exports."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from benchmarks.analyze_formal_solver_study import (
    bootstrap_log_ratio_ci,
    holm_adjust,
    signflip_pvalue,
    summarize,
    validate_and_aggregate,
)

ROOT = Path(__file__).resolve().parents[1]


def synthetic_blocks(seeds=6, repeats=3):
    rows = []
    metadata = {
        "protocol_version": "paired_solver_study_v1",
        "preset": "test",
        "independent_seeds": seeds,
        "timing_blocks_per_seed": repeats,
        "workload_cases": [
            {"case_id": 0, "n": 24, "order": 2, "evaluations": 8, "mu": 0.0},
        ],
    }
    for seed in range(seeds):
        for block in range(repeats):
            for method, multiple in [
                ("svd", 10), ("eigh", 8), ("cholesky", 2),
            ]:
                timing = multiple * 1_000_000 + seed * 10_000 + block * 100
                rows.append({
                    "case_id": 0, "seed_index": seed, "block": block,
                    "method": method,
                    "end_to_end_ns": timing,
                    "setup_ns": timing / 3,
                    "batch_ns": timing * 2 / 3,
                    "single_amortized_ns": timing / 10,
                })
    return rows, metadata


def test_paired_signflip_exact_extremal_and_null():
    rng = np.random.default_rng(12)
    # All observations favor the same method: exact two-sided 2/2^6.
    p, test = signflip_pvalue(np.ones(6), rng, 1000)
    assert p == pytest.approx(2 / 64)
    assert test == "exact_signflip"
    p0, _ = signflip_pvalue(np.zeros(6), rng, 1000)
    assert p0 == 1.0


def test_holm_adjustment_preserves_order_and_monotonicity():
    assert holm_adjust([0.03, 0.01, 0.4]) == pytest.approx([0.06, 0.03, 0.4])
    assert holm_adjust([]) == []


def test_bootstrap_exact_ratio_data():
    ci = bootstrap_log_ratio_ci(
        np.log(np.full(12, 3.0)), np.random.default_rng(3), 150, .05,
    )
    assert ci[0] == pytest.approx(3.0)
    assert ci[1] == pytest.approx(3.0)


def test_seed_is_inferential_unit_not_timing_block():
    rows, metadata = synthetic_blocks()
    grouped = validate_and_aggregate(rows, metadata)
    assert len(grouped) == 6 * 3
    timing, pairs = summarize(
        grouped, metadata, seed=22, bootstrap=200, permutations=200,
    )
    assert len(timing) == 3 * 4
    assert len(pairs) == 3
    assert all(pair["independent_seeds"] == 6 for pair in pairs)
    direct = next(p for p in pairs if (p["method_a"], p["method_b"]) == (
        "svd", "cholesky",
    ))
    assert direct["speedup_a_over_b"] > 4.8
    assert direct["ci95_low"] > 4.0
    assert direct["test_kind"] == "exact_signflip"


def test_missing_and_duplicate_blocks_are_rejected():
    rows, metadata = synthetic_blocks()
    with pytest.raises(ValueError, match="Duplicate"):
        validate_and_aggregate(rows + [dict(rows[0])], metadata)
    with pytest.raises(ValueError, match="Incomplete"):
        validate_and_aggregate(rows[:-1], metadata)


def test_insufficient_independent_seeds_does_not_claim_significance():
    rows, metadata = synthetic_blocks(seeds=2, repeats=8)
    grouped = validate_and_aggregate(rows, metadata)
    _, comparisons = summarize(
        grouped, metadata, bootstrap=100, permutations=100,
    )
    assert all(r["p_two_sided_unadjusted"] is None for r in comparisons)
    assert all(r["significant_holm"] is None for r in comparisons)


def test_formal_study_smoke_end_to_end_exports(tmp_path):
    raw_dir = tmp_path / "formal-study"
    run = subprocess.run(
        [sys.executable, "benchmarks/formal_solver_study.py",
         "--preset", "smoke", "--seeds", "2", "--repeats", "1",
         "--single-calls", "2", "--threads", "1",
         "--output-dir", str(raw_dir)],
        cwd=ROOT, text=True, capture_output=True, timeout=90, check=False,
    )
    assert run.returncode == 0, run.stderr[-4000:]
    metadata = json.loads(
        (raw_dir / "study_metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["primary_metric"] == "end_to_end_ns"
    assert len(metadata["workload_cases"]) == 3
    with (raw_dir / "raw_measurements.csv").open(newline="") as f:
        raw = list(csv.DictReader(f))
    assert len(raw) == 3 * 2 * 1 * 3
    with (raw_dir / "numerical_accuracy.csv").open(newline="") as f:
        accuracy = list(csv.DictReader(f))
    assert len(accuracy) == 3 * 2 * 3
    assert max(float(x["max_abs_error_vs_svd"]) for x in accuracy) < 1e-6

    analysis = subprocess.run(
        [sys.executable, "benchmarks/analyze_formal_solver_study.py",
         "--input-dir", str(raw_dir), "--no-plots",
         "--bootstrap", "100", "--permutations", "100"],
        cwd=ROOT, text=True, capture_output=True, timeout=90, check=False,
    )
    assert analysis.returncode == 0, analysis.stderr[-4000:]
    folder = raw_dir / "analysis"
    for required in (
        "paired_comparisons.csv", "timing_summary.csv",
        "results.md", "paper_solver_timings.tex",
        "paper_solver_speedups.tex", "analysis_manifest.json",
    ):
        assert (folder / required).is_file(), required
    with (folder / "paired_comparisons.csv").open(newline="") as f:
        comparisons = list(csv.DictReader(f))
    assert len(comparisons) == 3 * 3
    assert all(r["p_holm_familywise"] == "" for r in comparisons)
