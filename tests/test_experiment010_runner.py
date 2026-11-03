"""Contract tests for Experiment010 all-method, smoothness-first timings."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE / "paper" / "benchmarks" / "experiment010" / "run_batches.py"
SPEC = importlib.util.spec_from_file_location("experiment010_runner", BENCH)
assert SPEC and SPEC.loader
RUN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUN)


def test_all_existing_full_criterion_methods_included():
    assert len(RUN.METHODS_ALL) == 10
    assert "guarded_svd_cholesky" in RUN.METHODS_ALL
    assert "sparse_cholesky_banded_trace" in RUN.METHODS_ALL
    assert "pcg_fft_banded_trace" in RUN.METHODS_ALL
    assert "pcg_dst_banded_trace" in RUN.METHODS_ALL
    assert "pcg_jacobi_banded_trace" in RUN.METHODS_ALL


def test_manifest_factors_cross_reference_means_not_confounded():
    assert RUN.MEANS == ("0", "data", "0.15")
    assert len(RUN.configurations("smoke")) == 3
    assert len(RUN.configurations("pilot")) == 2 * 6 * 5 * 3
    assert len(RUN.configurations("comprehensive")) == 7 * 6 * 3 * 2 * 5 * 4
    for candidate in RUN.configurations("pilot"):
        assert candidate["mu"] in RUN.MEANS
    assert len(RUN.attempts("smoke")) == 3 * 10
    assert len({x[0] for x in RUN.attempts("smoke")}) == 3
    assert all(x[1]["criterion"] == "gcv"
               for x in RUN.attempts("smoke"))


def test_shards_are_disjoint_and_exhaustive():
    whole = {(key, method) for key, _, method in RUN.attempts("pilot")}
    a = {(key, method) for key, _, method in RUN.attempts("pilot", 0, 3)}
    b = {(key, method) for key, _, method in RUN.attempts("pilot", 1, 3)}
    c = {(key, method) for key, _, method in RUN.attempts("pilot", 2, 3)}
    assert not a.intersection(b) and not a.intersection(c)
    assert not b.intersection(c)
    assert whole == a | b | c


def test_dense_resource_mask_does_not_report_synthetic_times():
    status = RUN.memory_budget_status(
        131072, 6, "naive_inverse", 100, 2 * 1024**3, 1e14,
        "one_s_one_series", 1, 1)
    assert status == "infeasible_dense_memory"


def test_parity_marks_unverified_and_does_not_assert_precision(tmp_path):
    case_id = "small"
    root = tmp_path / "slices" / case_id
    outcomes = []
    for method, score in [("spectral_svd", 0.5),
                          ("banded_cholesky", 0.5 + 1e-10),
                          ("sparse_lu_banded_trace", 0.6)]:
        folder = root / method
        folder.mkdir(parents=True)
        with (folder / "raw_times.csv").open(
                "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "workload", "coordinate", "repeat", "method", "status",
                "selected_score", "M", "R", "evaluations",
                "criterion", "mu", "total_cold_s", "total_warm_s"])
            writer.writeheader()
            writer.writerow(dict(
                workload="one_s_one_series", coordinate="direct_s",
                repeat=0, method=method, status="ok",
                selected_score=score, M=1, R=1, evaluations=1,
                criterion="gcv", mu="0",
                total_cold_s=0.001, total_warm_s=0.0005))
        outcomes.append({
            "case_id": case_id, "status": "completed_with_csv",
            "folder": str(folder.relative_to(tmp_path))})
    counts = RUN.aggregate(tmp_path, outcomes)
    assert counts["parity_rows"] == 3
    assert counts["parity_row_status_counts"] == {
        "score_parity_only_not_precision_certified": 2,
        "score_disagreement": 1,
    }
    with (tmp_path / "score_parity_not_certification.csv").open(
            newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert {r["status"] for r in rows} == {
        "score_parity_only_not_precision_certified",
        "score_disagreement",
    }
