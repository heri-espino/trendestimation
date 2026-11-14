"""Contract tests for observational Paper C experiment004.

Tiny deterministic arrays used here are only software tests; experiment004
itself never generates or scores simulated vehicle trajectories.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "paper" / "ngsim-jerk-case-study" / "experiments" / "experiment004"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


fetch = module("paper_c4_fetch", EXPERIMENT / "fetch_real_ngsim.py")
evaluate = module("paper_c4_evaluate", EXPERIMENT / "evaluate.py")
inventory = module("paper_c4_inventory", EXPERIMENT / "inventory.py")


def test_download_query_is_bounded_and_site_specific():
    url = fetch.query_url("i-80", offset=20000, page_size=20000, max_vehicle_id=500)
    parameters = parse_qs(urlparse(url).query)
    assert parameters["$limit"] == ["20000"]
    assert parameters["$offset"] == ["20000"]
    assert "location = 'i-80'" in parameters["$where"][0]
    assert "vehicle_id <= 500" in parameters["$where"][0]
    with pytest.raises(ValueError):
        fetch.query_url("unknown", 0, 20, 500)


def test_episode_split_follows_frame_and_clock_and_vehicle_id():
    # Includes reused ID at a distant time and discontinuous frame ID.
    rows = [
        (1, 1000, 1, 0.0, 0.0), (1, 1100, 2, 0.1, 0.0),
        (1, 5000, 1, 1.0, 0.0), (1, 5100, 2, 1.1, 0.0),
        (2, 6000, 1, 0.0, 0.0),
        (1, 1200, 5, 0.2, 0.0),
    ]
    episodes = fetch.split_episodes(rows)
    assert [len(e) for e in episodes] == [2, 1, 2, 1]


def test_quality_screen_does_not_use_future_positions():
    # A positive-speed input has one prescribed historical origin.
    prefix = [(1, i * 100, i, 0.3 * i, 0.0) for i in range(100)]
    future_a = [(1, i * 100, i, 30.0 + i, 0.0) for i in range(100, 140)]
    future_b = [(1, i * 100, i, -1000.0 * i, 0.0) for i in range(100, 140)]
    a = fetch.eligible(prefix + future_a, origin=100, min_frames=140)
    b = fetch.eligible(prefix + future_b, origin=100, min_frames=140)
    assert a == b and a[0]


def test_mle_is_distinct_from_gcv_and_all_methods_have_forecasts():
    from trendestimation import TrendSmoother
    t = np.arange(80, dtype=float) * 0.1
    positions = 10 + 1.5 * t + 0.2 * np.sin(t * 2)
    smoother = TrendSmoother(80, order=3)
    penalties = tuple(smoother.lambda_for_smoothness(s) for s in evaluate.S_GRID)
    forecasts, choices, errors = evaluate._fit_methods(
        positions, smoother=smoother, penalties=penalties
    )
    assert len(choices) == 4
    assert {r["criterion"] for r in choices} == {"gcv", "mle"}
    assert {r["mu_policy"] for r in choices} == {"zero", "sample"}
    assert not errors
    assert set(forecasts) == set(evaluate.METHODS)
    assert all(np.isfinite(p).all() and p.shape == (20,) for p in forecasts.values())


def test_inventory_records_complete_paths_and_bytes(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "results").mkdir()
    (tmp_path / "data" / "raw.csv").write_text("real-data-placeholder", encoding="utf-8")
    (tmp_path / "results" / "a.json").write_text("{}", encoding="utf-8")
    audit = inventory.create_inventory(
        tmp_path, status="software_test", output=tmp_path / "file_inventory.json"
    )
    assert audit["total_files_excluding_this_inventory"] == 2
    assert set(audit["directory_paths_relative_to_root"]) >= {"data", "results"}
    assert "data/raw.csv" in [r["relative_path"] for r in audit["files"]]
    assert all(len(r["sha256"]) == 64 for r in audit["files"])


def test_inference_is_paired_at_episode_level_not_position_level():
    episodes = [
        {"episode_id": f"{site}_v_{i}", "site": site}
        for site in ("us-101", "i-80") for i in range(10)
    ]
    records = []
    for e in episodes:
        for method in evaluate.METHODS:
            for h in evaluate.HORIZONS:
                base = 1.5 if method == evaluate.REFERENCE else 1.0
                records.append({
                    "episode_id": e["episode_id"], "method": method,
                    "horizon_frames": h, "status": "ok",
                    "mse_m2": base, "mae_m": base, "fde_m": base,
                })
    summaries, paired = evaluate.summarize(records, episodes)
    assert len(summaries) == 3 * 3 * len(evaluate.METHODS)
    assert len(paired) == len(evaluate.HORIZONS) * (len(evaluate.METHODS) - 1)
    good = [r for r in paired if r["status"] == "exploratory_stratified_episode_bootstrap"]
    assert all(r["n_paired"] == 20 for r in good)
    assert all(r["ci_95_high_m2"] < 0 for r in good)
