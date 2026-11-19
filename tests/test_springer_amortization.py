"""Source-only QA for the two Springer measurement extensions.

These tests use synthetic *test fixture* values, never journal observations.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
EX11 = ROOT / "paper/benchmarks/experiment011"
EX12 = ROOT / "paper/benchmarks/experiment012"
sys.path.insert(0, str(EX11))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extension = load_module(EX11 / "complete_100_seeds.py", "springer_extension")
amort = load_module(EX12 / "run.py", "springer_amortization")
figures = load_module(EX12 / "render.py", "springer_amortization_render")


def test_extension_preserves_all_97_old_indices_and_adds_exactly_three() -> None:
    design = {"cases": [
        {"id": "c1", "planned_blocks": 1},
        {"id": "c2", "planned_blocks": 3},
    ]}
    jobs = extension.extension_jobs(design)
    extension.validate_jobs(design, jobs)
    assert len(jobs) == 6
    assert {i for i, *_ in jobs} == {97, 98, 99}
    assert {i + 3 for i, *_ in jobs} == {100, 101, 102}
    assert jobs[0][1] == 1_000_000_000 + 97 * 1_000_000
    # Legacy seed stream has a distinct and nonoverlapping index family.
    assert not set(range(3, 100)) & {i + 3 for i, *_ in jobs}


def test_incremental_plan_is_bounded_and_homogeneous() -> None:
    p = amort.plan(64, 3, "gcv", 100, (1, 10, 100, 1000))
    assert p["seeds"] == 100 and p["methods"] == list(amort.METHODS)
    assert p["coordinate"] == "direct_lambda"
    assert p["blas_threads"] == 1
    assert amort.seed_for(0, 64, 3) != amort.seed_for(1, 64, 3)
    assert len(amort.lambda_grid(1000)) == 1000
    with pytest.raises(ValueError):
        amort.plan(64, 3, "gcv", 101, (1, 10))
    with pytest.raises(ValueError):
        amort.plan(1024, 3, "gcv", 100, (1, 10))
    with pytest.raises(ValueError):
        amort.plan(128, 3, "gcv", 100, (1, 10, 100, 1000))
    with pytest.raises(ValueError):
        amort.plan(64, 3, "gcv", 100, (10, 100))


def test_nested_penalty_prefixes_span_the_search_range() -> None:
    import numpy as np

    full = amort.lambda_grid(1000)
    assert np.array_equal(full[:10], amort.lambda_grid(10))
    assert np.array_equal(full[:100], amort.lambda_grid(100))
    assert full[0] == pytest.approx(1.0)
    assert len(set(full.tolist())) == 1000
    assert float(np.min(full[:10])) < 0.1
    assert float(np.max(full[:10])) > 10.0
    assert np.isfinite(full).all()


def test_three_actual_criterion_evaluators_agree_at_one_lambda() -> None:
    # This is deterministic numerical API smoke, NOT an empirical timing result.
    source = ROOT / "paper/benchmarks/experiment006/run.py"
    sys.path.insert(0, str(source.parent))
    engine = load_module(source, "actual_experiment006_criterion_engine")
    y = engine.sample(64, 271828, "high")
    scores = {}
    for method in amort.METHODS:
        evaluator = engine.Evaluator(64, 2, method)
        coords = evaluator.prepare_series(y, 0.0)
        score = evaluator.evaluate(y, 0.0, 0.1, "gcv",
                                   coordinates=coords, reuse_factor=False)
        scores[method] = float(score)
    assert scores["banded_cholesky"] == pytest.approx(
        scores["naive_inverse"], rel=1e-5, abs=1e-6)
    assert scores["spectral_svd"] == pytest.approx(
        scores["naive_inverse"], rel=1e-5, abs=1e-6)


def test_cumulative_timing_and_complete_criterion_parity_with_mock_evaluator() -> None:
    class FakeEvaluator:
        def __init__(self, n, d, method):
            self.method = method

        def prepare_series(self, y, mu):
            return ("cached", tuple(y))

        def evaluate(self, y, mu, lam, criterion, coordinates, reuse_factor=False):
            assert criterion == "gcv" and reuse_factor is False
            return (lam - 1.0) ** 2 + y[0] * 0.0

    class FakeEngine:
        Evaluator = FakeEvaluator

        @staticmethod
        def sample(n, seed, amplitude):
            return [1.0] * n

    config = amort.plan(16, 2, "gcv", 1, (1, 10))
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=amort.FIELDS)
    writer.writeheader()
    rows = amort.run_seed(FakeEngine, config, 0, amort.lambda_grid(10), writer)
    assert len(rows) == 6
    assert all(r["status"] == "ok" for r in rows)
    for method in amort.METHODS:
        first = next(r for r in rows if r["method"] == method and r["checkpoint"] == 1)
        ten = next(r for r in rows if r["method"] == method and r["checkpoint"] == 10)
        assert first["attempted"] == 1 and ten["attempted"] == 10
        assert first["evaluation_s"] <= ten["evaluation_s"]
        assert ten["total_cold_s"] == ten["setup_s"] + ten["evaluation_s"]
    assert amort.numerical_audit(rows)["mismatches"] == []


def test_renderer_never_accepts_incomplete_or_unverified_100_seed_data(tmp_path) -> None:
    inp = tmp_path / "archived_input"
    inp.mkdir()
    rows = []
    for seed in range(100):
        for method in amort.METHODS:
            rows.append({
                "seed_index": seed, "checkpoint": 1, "method": method,
                "status": "ok", "completed": 1,
                "setup_s": 0.3, "evaluation_s": 0.2, "total_cold_s": 0.5,
            })
    with (inp / "timings.csv").open("w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    meta = {
        "experiment": "experiment012",
        "status": "complete_pending_publication_review",
        "seeds": 100, "checkpoints": [1],
        "timings_sha256": hashlib.sha256((inp / "timings.csv").read_bytes()).hexdigest(),
    }
    (inp / "metadata.json").write_text(json.dumps(meta), encoding="utf8")
    (inp / "numerical_audit.json").write_text(json.dumps({"mismatches": []}), encoding="utf8")
    _, loaded = figures.load_complete(inp)
    assert len(loaded) == 300
    assert len(figures.summarize(loaded, [1])) == 3
    (inp / "timings.csv").write_bytes((inp / "timings.csv").read_bytes() + b"corrupted")
    with pytest.raises(ValueError, match="SHA-256"):
        figures.load_complete(inp)
