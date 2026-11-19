"""Cheap Paper C maintenance regression checks; no experiments or Windows runner."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "ngsim-jerk-case-study"
WORKFLOWS = ROOT / ".github" / "workflows"


def test_final_publication_hashes_and_canonical_source_inventory() -> None:
    inventory = PAPER / "publication_sha256.txt"
    entries = {}
    for line in inventory.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", maxsplit=1)
        assert len(digest) == 64
        entries[relative] = digest
        file_path = PAPER / relative
        assert file_path.is_file(), relative
        assert hashlib.sha256(file_path.read_bytes()).hexdigest() == digest, relative

    assert len(entries) == 16
    assert {"main.pdf", "atlas_supplement.pdf", "main.tex", "atlas_supplement.tex"} <= set(entries)
    assert {"generated/awesomefigures_atlas_manifest.json",
            "generated/visual_suite_manifest.json",
            "generated/exp008_methods_figure_manifest.json"} <= set(entries)
    assert (PAPER / "publication_sha256_legacy_pre_atlas.txt").is_file()

    checker = PAPER / "check_publication_hashes.py"
    result = subprocess.run(
        [sys.executable, str(checker), "--check"],
        check=False, capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_paper_c_windows_workflows_require_manual_scoped_dispatch() -> None:
    atlas = (WORKFLOWS / "paper-c-awesomefigures-atlas-pc08.yml").read_text(encoding="utf-8")
    manuscript = (WORKFLOWS / "paper-c-manuscript-pc08.yml").read_text(encoding="utf-8")
    for workflow in (atlas, manuscript):
        # No implicit expensive Windows run when source files change.
        assert "  workflow_dispatch:" in workflow
        assert "\n  push:" not in workflow
        assert "workflow_dispatch' -or $env:GITHUB_REF_TYPE" in workflow
        assert "^(feature|fix|paper)/paper-c-" in workflow
        assert "$paperCBranch -ne 'main'" in workflow
        assert "Source commit mismatch" in workflow

    # Source-backed artifacts may be published on a scoped branch, never on main.
    assert "if: success() && github.ref_name != 'main'" in atlas
    assert "Disallowed publication branch (main is archive-only)" in atlas
    assert "Branch advanced; do not push a PDF compiled from stale source" in atlas
    assert "results/paper-c-awesomefigures-pc08-$env:GITHUB_RUN_ID-a$env:GITHUB_RUN_ATTEMPT" in atlas
