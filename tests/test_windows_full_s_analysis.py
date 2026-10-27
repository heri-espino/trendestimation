"""Guard the author's original 80,640-cell Windows results against loss."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "paper" / "benchmarks"))
from report_windows_full_s import load, summarize, check_parity  # noqa: E402


def test_windows_full_results_complete_and_distinct_from_linux():
    raw, prep, env = load()
    assert len(raw) == 80640
    assert len(prep) == 12
    assert env["platform"].startswith("Windows")
    assert env["seeds"] == [20261026, 20261027]
    assert env["n"] == [24, 48]
    assert env["d"] == list(range(6))
    assert env["R"] == [1, 3, 8]
    assert env["blas_threads"] == 1
    assert (PROJECT / "paper/benchmarks/full_s_search_reference/"
            "search_mode_timings.csv").exists()


def test_two_seeds_per_cell_and_identical_matched_s_lambda_grid():
    raw, _, _ = load()
    rows, pairs = summarize(raw)
    assert len(rows) == 40320
    assert len(pairs) == 40320
    assert all(row["seed_count"] == 2 for row in rows)
    parity = check_parity(pairs)
    assert parity["matched_valid_seed_pairs"] > 0
    assert parity["maximum_selected_s_disagreement"] <= 1e-6


def test_springer_and_sphinx_sources_include_windows_full_evidence():
    assert r"\input{sections/windows_full_s_results}" in (
        PROJECT / "paper/main.tex").read_text(encoding="utf-8")
    assert "windows_full_s_results" in (
        PROJECT / "docs/index.rst").read_text(encoding="utf-8")
    assert (PROJECT / "paper/sections/windows_full_s_results.tex").exists()
    assert (PROJECT / "docs/windows_full_s_results.rst").exists()
