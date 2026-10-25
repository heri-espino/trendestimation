"""Publishing helper safety tests: allowlist, dry-run, and provenance."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.publish_generated_outputs import (
    discover_publishable,
    import_study,
    is_allowed_file,
    locate_import_sources,
    write_manifest,
)


def _write(path: Path, content: str = "generated") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_publishable_paths_are_strict_allowlist(tmp_path):
    timing = _write(
        tmp_path / "paper/benchmarks/solver_study_runs/pilot-01/raw_measurements.csv",
        "case_id,method\n1,svd\n",
    )
    stats = _write(
        tmp_path / "paper/benchmarks/results/full_fit_timings.csv",
        "n,seconds\n20,0.001\n",
    )
    slide = _write(
        tmp_path / "slides/professor_lecture/figures/trend.svg",
        "<svg></svg>",
    )
    _write(tmp_path / "paper/benchmarks/results/secrets.json", "{}")
    _write(tmp_path / "paper/private-source.pdf", "licensed PDF")
    _write(tmp_path / "docs/_build/index.html", "<html></html>")
    _write(tmp_path / ".env", "password=not-for-github")
    result = discover_publishable(tmp_path)
    assert result == sorted([timing, stats, slide])
    assert is_allowed_file(timing, tmp_path)
    assert not is_allowed_file(tmp_path / ".env", tmp_path)


def test_import_is_lossless_and_avoids_unsafe_files(tmp_path):
    source = tmp_path / "local" / "solver-study"
    raw = _write(source / "raw_measurements.csv", "unit,method\n0,svd\n")
    _write(source / "study_metadata.json", '{"seed": 3}')
    _write(source / "analysis" / "results.md", "Observed numbers only")
    _write(source / "analysis" / "secret.json", '{"public": false}')
    _write(source / "analysis" / ".env", "private")
    _write(source / "timing.tmp", "ignored")

    located = locate_import_sources(tmp_path, [str(source)])
    assert located == [source.resolve()]
    dest = tmp_path / "paper/benchmarks/solver_study_runs/imported-01"
    planned = import_study(source, dest, dry_run=True)
    assert len(planned) == 3
    assert not dest.exists()
    copied = import_study(source, dest, dry_run=False)
    assert len(copied) == 3
    assert (dest / "raw_measurements.csv").read_bytes() == raw.read_bytes()
    assert not (dest / "analysis" / "secret.json").exists()
    assert not (dest / "analysis" / ".env").exists()


def test_publication_manifest_records_sha_and_portable_paths(tmp_path):
    artifact = _write(
        tmp_path / "paper/benchmarks/results/full_fit_timings.csv",
        "n,time\n1,0.1\n",
    )
    manifest = write_manifest(
        [artifact], tmp_path, "deadbeef", "20261025-010001",
    )
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["source_git_revision"] == "deadbeef"
    assert len(data["files"]) == 1
    assert data["files"][0]["path"] == "paper/benchmarks/results/full_fit_timings.csv"
    assert len(data["files"][0]["sha256"]) == 64
    assert data["files"][0]["bytes"] == artifact.stat().st_size
    assert "/Users/" not in manifest.read_text(encoding="utf-8")
