"""Check the opt-in benchmark and plot-data export contracts."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_solver_backend_benchmark_smoke_produces_verifiable_json(tmp_path):
    output = tmp_path / "measurements.json"
    command = [
        sys.executable, "benchmarks/compare_solver_backends.py",
        "--preset", "smoke", "--repeats", "1", "--threads", "1",
        "--output", str(output),
    ]
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True,
        timeout=60, check=False,
    )
    assert completed.returncode == 0, completed.stderr[-3000:]
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["kind"] == "matched_full_trend_reconstruction"
    assert len(report["rows"]) == 9
    assert {row["method"] for row in report["rows"]} == {
        "svd", "eigh", "cholesky",
    }
    for row in report["rows"]:
        assert row["max_abs_error_vs_svd"] < 1e-6
        assert row["setup_seconds_median"] >= 0
        assert row["setup_plus_batched_seconds_median"] >= 0
        assert row["stored_bytes_median"] > 0
