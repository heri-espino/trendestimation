#!/usr/bin/env python3
r"""Restyle EVERY paper figure from cached research evidence, never rerun benchmarks.

Windows 11 PowerShell, from the repository root:
    python -m pip install -r paper/requirements.txt
    python paper/computational-statistics-submission/render_all_figures.py --scope all

Prerequisites: pinned AwesomeFigures, pdflatex/latexmk and already archived
experiment measurements. Only ONE legacy NOAA plot-data .dat can need
deterministic reconstruction on a fresh checkout. This is a fixed-parameter
fit, NOT a statistical selection run or a timing benchmark.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FIGURES=HERE/"figures"
DATA=HERE/"data"
SOURCE_FILES=(
    DATA/"noaa_mlo_monthly_1990_2026_09.csv",
    DATA/"fred_fedfunds_2010_2026_09.csv",
    DATA/"provenance.json",
    DATA/"co2_full_dashboards.json",
    DATA/"co2_recent_dashboards.json",
    DATA/"fedfunds_full_dashboards.json",
    DATA/"co2_full_results.json",
    DATA/"co2_recent_results.json",
    DATA/"fedfunds_full_results.json",
    HERE/"research/final_vm/inversion/raw_inversions.csv",
    HERE/"research/final_vm/inversion/summary.csv",
    HERE/"research/final_vm/solver/raw_measurements.csv",
    HERE/"research/final_vm/solver/analysis/paired_comparisons.csv",
    ROOT/"paper/benchmarks/results/full_s_search_modes/search_mode_timings.csv",
    ROOT/"paper/benchmarks/full_s_reference/full_grid_summary.csv",
    ROOT/"paper/benchmarks/full_s_search_reference/search_mode_timings.csv",
    ROOT/"paper/benchmarks/selection_coordinate_reference/selector_timings.csv",
)


def digest(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Cannot restyle: cached experiment missing {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def steps(scope: str) -> list[tuple[str,...]]:
    python=sys.executable
    output=[
        (python,str(HERE/"make_current_examples.py"),"--render-only"),
        (python,str(HERE/"make_selection_dashboards.py"),"--render-only"),
    ]
    if scope=="all":
        # These renderers read committed .dat/CSV and invoke publication
        # typography; none run timing benchmarks or select new criteria.
        output.extend([
            (python,"paper/figures/render_awesomefigures.py"),
            (python,"paper/figures/render_full_s_factorial.py"),
            (python,"paper/figures/render_full_s_search_modes.py"),
            (python,"paper/benchmarks/report_windows_full_s.py"),
        ])
    output.append((python,str(HERE/"render_final_computation.py")))
    return output


def run(scope: str="all", *, dry_run: bool=False, build_pdf:bool=True) -> dict:
    if scope not in ("all","submission"):
        raise ValueError("Scope must be all or submission")
    planned=steps(scope)
    missing=[str(path.relative_to(ROOT)) for path in SOURCE_FILES if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "The renderer will NOT replace measurements or re-run experiments. "
            f"Restore committed input files first: {missing}"
        )
    before={str(p.relative_to(ROOT)):digest(p) for p in SOURCE_FILES}
    missing_legacy=not (ROOT/"paper/figures/mauna_loa_1990_2026_09.dat").exists()
    if scope=="all" and missing_legacy:
        # Deterministic interpolation of a fixed published S=0.86
        # is one-time figure-data materialization, NOT a benchmark.
        planned.insert(2,(
            sys.executable,"paper/figures/make_updated_mauna_loa.py",
        ))
    if build_pdf:
        planned.append(("latexmk","-pdf","-interaction=nonstopmode",
                        "-halt-on-error","main.tex"))
    for args in planned:
        print("[render-only]", " ".join(map(str,args)),flush=True)
        if dry_run:
            continue
        # All scripts operate from the repo root. latexmk must use the
        # standalone manuscript directory for figure-relative paths.
        subprocess.run(args,check=True,cwd=HERE if args[0]=="latexmk" else ROOT)
    if dry_run:
        return {"dry_run":True,"source_sha256":before,
                "planned":[list(s) for s in planned]}
    after={str(p.relative_to(ROOT)):digest(p) for p in SOURCE_FILES}
    if before!=after:
        raise RuntimeError(
            "Archival data changed during rendering. Do NOT commit; "
            "find and revert modified numerical source files."
        )
    if build_pdf and not (HERE/"main.pdf").is_file():
        raise FileNotFoundError("The Springer manuscript PDF was not generated")
    generated=sorted(
        str(path.relative_to(ROOT))
        for path in FIGURES.glob("*")
        if path.is_file() and path.suffix in (".pdf",".svg",".png")
    )
    if len(generated)<50:
        raise RuntimeError(
            f"Only {len(generated)} paper figure assets present; "
            "expected at least 50. Check missing sources and outputs."
        )
    report={
        "mode":"render_only_from_archived_results",
        "theme":"AwesomeFigures pinned Okabe-Ito high-contrast palette",
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "scope":scope,"rebuilt_manuscript":build_pdf,
        "experiment_source_sha256":before,
        "sources_unchanged":True,
        "published_assets":generated,
        "commands":[list(s) for s in planned],
        "explanation":(
            "No selection criterion was optimized and no statistical "
            "timing experiment was executed. Archived selected parameters "
            "deterministically reproduce the fitted dashboard curves. "
            "Source checksums were verified before and after rendering."
        ),
    }
    (HERE/"figure_render_manifest.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8",
    )
    print(f"[render-only] {len(generated)} assets; archival inputs unchanged",flush=True)
    return report


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope",choices=("all","submission"),default="all")
    parser.add_argument("--dry-run",action="store_true")
    parser.add_argument("--no-pdf",action="store_true",
                        help="Render figures only, no latexmk compilation")
    args=parser.parse_args()
    run(args.scope,dry_run=args.dry_run,build_pdf=not args.no_pdf)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
