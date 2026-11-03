"""Contract tests for parallel, uncapped, independently archived methods."""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]
DIR = REPO / "paper" / "benchmarks" / "experiment010"
if str(DIR) not in sys.path:
    sys.path.insert(0, str(DIR))
SPEC = importlib.util.spec_from_file_location(
    "experiment010_parallel_tests_module", DIR / "run_parallel.py")
assert SPEC and SPEC.loader
PAR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PAR)


def test_parallel_two_workers_run_concurrently_and_checkpoint(tmp_path, monkeypatch):
    barrier = threading.Barrier(2)
    seen = []
    lock = threading.Lock()

    def fake_run_one(item, output, *, repeats, series_count,
                     max_dense_bytes, seed):
        key, cfg, method = item
        with lock:
            seen.append(method)
        barrier.wait(timeout=5)  # Would fail in a sequential runner.
        folder = Path("slices") / key / method
        dest = output / folder
        dest.mkdir(parents=True)
        with (dest / "raw_times.csv").open(
                "w", newline="", encoding="utf-8") as handle:
            fields = ["method", "workload", "coordinate", "repeat", "status",
                      "selected_score", "M", "R", "evaluations",
                      "criterion", "mu", "total_cold_s", "total_warm_s"]
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerow(dict(
                method=method, workload="one_s_one_series",
                coordinate="mapped_lambda", repeat=0, status="ok",
                selected_score=0.3, M=1, R=1, evaluations=1,
                criterion=cfg["criterion"], mu=cfg["mu"],
                total_cold_s=0.1, total_warm_s=0.08))
        return dict(case_id=key, configuration=cfg, method=method,
                    status="completed_with_csv", folder=str(folder),
                    elapsed_s=0.2, reason="", measured_rows=1)

    monkeypatch.setattr(PAR, "run_one", fake_run_one)
    monkeypatch.setattr(PAR.B, "source_sha", lambda: "frozen-test-sha")
    output = tmp_path / "parallel"
    summary = PAR.execute_parallel(
        output, shard_index=0, shard_count=64, start_attempt=0,
        max_method_attempts=2, workers=2,
        max_dense_bytes=2 * 1024**3,
        total_parallel_dense_bytes=4 * 1024**3,
        repeats=2, series_count=2)
    assert len(seen) == 2 and len(set(seen)) == 2
    assert summary["actual_attempted"] == 2
    assert summary["completed_method_slices"] == 2
    assert summary["successful_raw_timing_rows"] == 2
    assert summary["next_attempt_offset"] == 2
    with (output / "method_attempts.csv").open(
            newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    assert len(records) == 2
    assert [r["status"] for r in records] == ["completed_with_csv"] * 2
    metadata = json.loads((output / "run_metadata.json").read_text())
    assert metadata["mode"] == "parallel_uncapped"
    assert metadata["workers"] == 2
    assert metadata["per_method_seconds"] is None


def test_parallel_workers_cannot_exceed_declared_dense_reservation(tmp_path):
    with pytest.raises(ValueError, match="reservation"):
        PAR.execute_parallel(
            tmp_path / "denied", shard_index=0, shard_count=16,
            workers=16, max_dense_bytes=2 * 1024**3,
            total_parallel_dense_bytes=16 * 1024**3)
    assert not (tmp_path / "denied").exists()


def test_child_invocation_has_no_runtime_timeout_and_keeps_error_status(
        tmp_path, monkeypatch):
    item = PAR.B.attempts("smoke")[0]
    observed = []

    def fake_run(cmd, **kwargs):
        observed.append((cmd, kwargs))
        dest = Path(cmd[cmd.index("--output") + 1])
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "raw_times.csv").write_text(
            "status\\n" + "numerical_failed\\n", encoding="utf-8")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(PAR.subprocess, "run", fake_run)
    result = PAR.run_one(item, tmp_path, repeats=2, series_count=2,
                         max_dense_bytes=2 * 1024**3, seed=20261102)
    assert result["status"] == "completed_with_csv"
    assert result["measured_rows"] == 0
    assert len(observed) == 1
    args, kwargs = observed[0]
    assert "--allow-unbounded-runtime" in args
    assert args[args.index("--max-work") + 1] == "inf"
    assert "timeout" not in kwargs
    assert kwargs["stderr"] is PAR.subprocess.STDOUT
    log = tmp_path / "slices" / item[0] / (item[2] + ".log")
    assert log.exists()
