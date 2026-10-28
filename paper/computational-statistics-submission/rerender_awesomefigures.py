#!/usr/bin/env python3
"""Rebuild paper figures with AwesomeFigures, never re-run experiments.

PowerShell (repository root):
    python -m pip install -e ".[dev,plot]"
    python -m pip install -r paper/requirements.txt
    python paper/computational-statistics-submission/rerender_awesomefigures.py

Both scopes REQUIRE pdflatex/MiKTeX for the actual Springer document
font and physical sizes. The default --scope journal covers every SNCS
figure and archived 4x6 supplementary dashboard. --scope all also
renders legacy paper/figures/ at its own publication dimensions.
Then compile sncs_main.tex with build_sncs.ps1, or use the GitHub CI workflow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from contrast_theme import provenance, require_awesomefigures
from render_all_figures import SOURCE_FILES
from sncs_expand_results import SOURCE_PATHS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLOT_ROOT = HERE / "figures"
SOURCE_ARCHIVE = tuple(sorted(set(SOURCE_FILES) | set(SOURCE_PATHS)))


def sha256(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(
            f"Archived experiment is missing; will not rerun it: {path}"
        )
    return hashlib.sha256(path.read_bytes()).hexdigest()


def commands(scope: str = "journal") -> list[tuple[str, ...]]:
    if scope not in {"journal", "all"}:
        raise ValueError("scope must be journal or all")
    cli = sys.executable
    steps = [
        (
            cli, str(HERE / "render_all_figures.py"),
            "--scope", "all" if scope == "all" else "submission", "--no-pdf",
        ),
        (cli, "paper/benchmarks/report_windows_full_s.py"),
        (cli, str(HERE / "sncs_expand_results.py")),
    ]
    for mode in ("zero", "data"):
        for series in ("co2_full", "co2_recent", "fedfunds_full"):
            steps.append((
                cli, str(HERE / "sncs_dashboard.py"),
                "--mu", mode, "--dataset", series,
            ))
    if scope == "all":
        # Other publication figures use af.latex_style, so genuine TeX is
        # necessary for their physical typography and publication font.
        steps.append((cli, "paper/figures/render_mle_benchmarks.py"))
    return steps


def mentioned_figures() -> set[str]:
    files = (
        "sncs_main.tex",
        "sncs_expanded_theory.tex",
        "sncs_expanded_experiments.tex",
        "sncs_expanded_applications.tex",
        "sncs_expanded_software.tex",
    )
    mentioned: set[str] = set()
    for file in files:
        value = (HERE / file).read_text(encoding="utf-8")
        mentioned.update(re.findall(r"\{figures/([a-zA-Z0-9_-]+\.pdf)\}", value))
    return mentioned


def run(*, scope: str = "journal", dry_run: bool = False) -> dict:
    require_awesomefigures()
    if not dry_run and shutil.which("pdflatex") is None:
        raise RuntimeError(
            "Exact SN Computer Science fonts and sizes require pdflatex on PATH "
            "even with --scope journal. Install MiKTeX or TeX Live; there is "
            "no silent DejaVu fallback for publication PDFs."
        )
    before = {str(path.relative_to(ROOT)): sha256(path) for path in SOURCE_ARCHIVE}
    planned = commands(scope)
    if dry_run:
        return {
            "scope": scope,
            "source_sha256": before,
            "commands": [list(command) for command in planned],
            "awesomefigures": provenance(strict=True),
            "dry_run": True,
        }
    for command in planned:
        print("[AwesomeFigures archived-only]", " ".join(command), flush=True)
        env = os.environ.copy()
        env["TRENDESTIMATION_TEX_FIGURES"] = "1"
        subprocess.run(command, cwd=ROOT, check=True, env=env)
    after = {str(path.relative_to(ROOT)): sha256(path) for path in SOURCE_ARCHIVE}
    if before != after:
        raise RuntimeError(
            "A protected archived numerical source changed while drawing. "
            "Do not commit outputs until the numeric archive is restored."
        )
    referenced = mentioned_figures()
    missing = sorted(name for name in referenced if not (PLOT_ROOT / name).is_file())
    if missing:
        raise FileNotFoundError(
            f"SNCS manuscript figure dependencies not available: {missing}"
        )
    from contrast_theme import latex_layout
    measured = latex_layout()
    audit_files = sorted(PLOT_ROOT.glob("*.typography.json"))
    covered = {p.name.removesuffix(".typography.json") + ".pdf" for p in audit_files}
    unverified = sorted(set(referenced) - covered)
    if unverified:
        raise RuntimeError(
            "The manuscript cites PDFs not exported with measured TeX fonts: "
            + repr(unverified)
        )
    files = sorted(
        str(p.relative_to(ROOT))
        for p in PLOT_ROOT.iterdir()
        if p.is_file() and p.suffix in {".pdf", ".svg", ".png"}
    )
    if len(files) < 100:
        raise RuntimeError(f"Only {len(files)} journal figure assets present.")
    if scope == "all":
        files += sorted(
            str(p.relative_to(ROOT))
            for p in (ROOT / "paper" / "figures").iterdir()
            if p.is_file() and p.suffix in {".pdf", ".svg"}
        )
    result = {
        "mode": "publication_figures_from_frozen_results",
        "scope": scope,
        "awesomefigures": provenance(),
        "sources_unchanged": True,
        "source_sha256": before,
        "no_benchmarks_or_selectors_rerun": True,
        "compiled_pdf": False,
        "publication_typography": {
            "manuscript": str(HERE.relative_to(ROOT) / "sncs_main.tex"),
            "textwidth_pt": measured.textwidth_pt,
            "columnwidth_pt": measured.columnwidth_pt,
            "body_font_pt": measured.fontsize_pt,
            "font_family": measured.font_family,
            "font_name": measured.font_name,
            "exact_tex_pdf": True,
            "audited_pdf_files": len(audit_files),
            "manuscript_pdf_audit_covered": len(covered & referenced),
        },
        "figure_files": files,
        "manuscript_referenced_figures": sorted(referenced),
        "commands": [list(command) for command in planned],
    }
    destination = HERE / "awesomefigures_render_manifest.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        f"Verified {len(files)} figure assets and {len(before)} immutable "
        "archived inputs; numeric results unchanged.", flush=True,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("journal", "all"), default="journal")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(scope=args.scope, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
