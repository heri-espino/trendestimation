#!/usr/bin/env python3
"""Compile archived manuscript sources on the designated Windows Conda runner.

This is a TeX-only build. It never executes scientific experiments, figure
renderers, dataset downloads or benchmark scripts. For Elsevier manuscripts
it copies the repository's original CAS v2.4 support files into the checkout.

Examples:
    python scripts/build_papers_pc08.py --list
    python scripts/build_papers_pc08.py --paper all --dry-run
    python scripts/build_papers_pc08.py --paper csda-a --output-dir paper/builds/pc08/local001
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
CAS_TEMPLATE = ROOT / "paper" / "els-cas-templates"
CAS_FILES = ("cas-dc.cls", "cas-common.sty", "cas-model2-names.bst")
EXPECTED_RUNNER = "PCAG103A-08"
EXPECTED_ENV = "trendestimation"


@dataclass(frozen=True)
class Paper:
    id: str
    folder: str
    entry: str
    template: str
    title: str


PAPERS = (
    Paper("csda-a", "paper/csda-spectral-smoothness", "main.tex", "cas",
          "CSDA A — spectral smoothness and numerical reliability"),
    Paper("csda-b", "paper/csda-computational-costs", "main.tex", "cas",
          "CSDA B — amortized computational costs"),
    Paper("springer", "paper", "main.tex", "springer",
          "Springer Computational Statistics — implementation"),
    Paper("ngsim", "paper/ngsim-jerk-case-study", "main.tex", "cas",
          "NGSIM real-vehicle jerk case study"),
    Paper("direct-weights", "paper/direct-spectral-weights", "main.tex", "cas",
          "Direct spectral weights — theoretical working draft"),
    Paper("historical-springer", "paper/computational-statistics-submission",
          "main.tex", "springer", "Historical Computational Statistics manuscript"),
    Paper("historical-sncs", "paper/computational-statistics-submission",
          "sncs_main.tex", "springer", "Historical SN Computer Science manuscript"),
)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def input_fingerprints(paper: Paper) -> dict[str, str]:
    folder = ROOT / paper.folder
    # Include source, precomputed LaTeX tables, graphics and input imagery.
    # Figure rendering and scientific experiments are deliberately not run.
    paths = [folder / paper.entry]
    for pattern in (
        "*.tex", "*.bib", "sections/*.tex", "generated/*.tex",
        "figures/*.pdf", "figures/*.png", "figures/*.pgf",
    ):
        paths.extend(folder.glob(pattern))
    if paper.template == "cas":
        paths.extend(CAS_TEMPLATE / name for name in CAS_FILES)
    return {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in sorted(set(paths)) if path.is_file()
    }


def selected_papers(name: str) -> tuple[Paper, ...]:
    return PAPERS if name == "all" else tuple(p for p in PAPERS if p.id == name)


def validate_sources(papers: tuple[Paper, ...]) -> None:
    for paper in papers:
        path = ROOT / paper.folder / paper.entry
        if not path.is_file():
            raise FileNotFoundError(f"Required manuscript entrypoint missing: {path}")
        if paper.template == "cas":
            for filename in CAS_FILES:
                template = CAS_TEMPLATE / filename
                if not template.is_file():
                    raise FileNotFoundError(f"Author-supplied CAS template missing: {template}")


def validate_runner() -> None:
    runner = os.environ.get("RUNNER_NAME", "")
    if runner != EXPECTED_RUNNER:
        raise RuntimeError(
            f"Wrong runner: {runner!r}; expected exactly {EXPECTED_RUNNER!r}."
        )
    if platform.system() != "Windows":
        raise RuntimeError("PC08 manuscript builds must use Windows.")
    # Conda Python resides directly inside .../envs/trendestimation/python.exe.
    if Path(sys.executable).parent.name.casefold() != EXPECTED_ENV:
        raise RuntimeError(
            f"Expected Conda environment {EXPECTED_ENV!r}, "
            f"but Python is {sys.executable!r}."
        )


def ensure_tex_tools() -> dict[str, str]:
    result = {}
    for tool in ("latexmk", "pdflatex", "bibtex"):
        location = shutil.which(tool)
        if location is None:
            raise RuntimeError(
                f"{tool} is unavailable on PATH. The existing PC08 MiKTeX/LaTeX "
                "and Perl setup must be accessible to the GitHub runner account. "
                "No system packages are automatically installed."
            )
        result[tool] = location
    return result


def prepare_springer_inputs(output_root: Path) -> list[dict[str, str]]:
    """Restore two missing, *derived* inputs, never benchmark outputs.

    The author already committed the seed-19 synthetic criteria table as
    criteria_table.example.tex. The September-2026 NOAA figure is
    regenerated only when absent, using the frozen 441-month data and
    the repository's existing figure scripts (not a new experiment).
    """
    table = ROOT / "paper" / "criteria_table.tex"
    example = ROOT / "paper" / "criteria_table.example.tex"
    figure = ROOT / "paper" / "figures" / "mauna_loa_1990_2026_09.pdf"
    data = ROOT / "paper" / "figures" / "mauna_loa_1990_2026_09.dat"
    if not table.is_file():
        if not example.is_file() or not example.read_text(encoding="utf-8").strip():
            raise RuntimeError("Frozen synthetic criteria_table.example.tex is missing")
        shutil.copy2(example, table)
    if not figure.is_file():
        preplog = output_root / "springer-preparation.log"
        commands = (
            [sys.executable, "paper/figures/make_updated_mauna_loa.py"],
            [sys.executable, "paper/figures/render_awesomefigures.py", "--figures-only"],
        )
        with preplog.open("w", encoding="utf-8", errors="replace") as handle:
            for command in commands:
                handle.write("Command: " + " ".join(command) + "\n")
                handle.flush()
                subprocess.run(
                    command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT,
                    check=True, timeout=600,
                )
        if not data.is_file():
            raise RuntimeError("NOAA 441-month trend input was not generated")
    if not figure.is_file() or figure.stat().st_size < 100:
        raise RuntimeError("NOAA figure was not generated")
    if not table.is_file() or table.stat().st_size < 100:
        raise RuntimeError("Frozen synthetic criteria table is empty")
    return [
        {"path": p.relative_to(ROOT).as_posix(), "sha256": sha256(p)}
        for p in (table, figure, data) if p.is_file()
    ]


def compile_one(paper: Paper, output_root: Path) -> dict[str, object]:
    folder = ROOT / paper.folder
    log = output_root / f"{paper.id}.log"
    archive_pdf = output_root / f"{paper.id}.pdf"
    repository_pdf = folder / Path(paper.entry).with_suffix(".pdf")
    started = time.perf_counter()
    record: dict[str, object] = {
        "id": paper.id,
        "title": paper.title,
        "entry": f"{paper.folder}/{paper.entry}",
        "repository_pdf": repository_pdf.relative_to(ROOT).as_posix(),
        "artifact_pdf": archive_pdf.relative_to(ROOT).as_posix()
        if archive_pdf.is_relative_to(ROOT) else str(archive_pdf),
        "log": log.relative_to(ROOT).as_posix()
        if log.is_relative_to(ROOT) else str(log),
        "template": paper.template,
        "status": "failed",
        "source_sha256": input_fingerprints(paper),
    }
    try:
        if paper.id == "springer":
            record["prepared_inputs"] = prepare_springer_inputs(output_root)
            record["source_sha256"] = input_fingerprints(paper)
        if paper.template == "cas":
            for name in CAS_FILES:
                shutil.copy2(CAS_TEMPLATE / name, folder / name)
        # -g forces a new compile even if an older main.pdf is tracked.
        command = [
            "latexmk", "-pdf", "-g",
            "-interaction=nonstopmode", "-file-line-error",
            "-halt-on-error", paper.entry,
        ]
        print(f"[{paper.id}] Compiling {record['entry']}", flush=True)
        with log.open("w", encoding="utf-8", errors="replace") as handle:
            handle.write("Command: " + " ".join(command) + "\n\n")
            handle.flush()
            proc = subprocess.run(
                command, cwd=folder, stdout=handle, stderr=subprocess.STDOUT,
                check=False, timeout=1200,
            )
        record["exit_code"] = proc.returncode
        if proc.returncode != 0:
            raise RuntimeError(f"latexmk returned exit code {proc.returncode}")
        if not repository_pdf.is_file() or repository_pdf.stat().st_size < 100:
            raise RuntimeError(f"Compiled PDF not found or empty: {repository_pdf}")
        shutil.copy2(repository_pdf, archive_pdf)
        record.update({
            "status": "ok",
            "pdf_sha256": sha256(archive_pdf),
            "pdf_bytes": archive_pdf.stat().st_size,
        })
        print(f"[{paper.id}] OK: {record['pdf_bytes']} bytes", flush=True)
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
        with log.open("a", encoding="utf-8") as handle:
            handle.write(f"\nBUILD FAILURE: {record['error']}\n")
        print(f"[{paper.id}] FAILED: {record['error']}", file=sys.stderr, flush=True)
    finally:
        record["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--paper", choices=("all",) + tuple(p.id for p in PAPERS), default="all"
    )
    parser.add_argument("--output-dir", default="paper/builds/pc08/local001")
    parser.add_argument("--require-runner", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    selected = selected_papers(args.paper)
    validate_sources(selected)

    if args.list or args.dry_run:
        for paper in selected:
            print(f"{paper.id:22s} {paper.folder}/{paper.entry} [{paper.template}]")
        if args.list or args.dry_run:
            return 0

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {
        "schema": 1,
        "source_commit": git_head(),
        "started_utc": now_utc(),
        "finished_utc": None,
        "requested": args.paper,
        "runner": os.environ.get("RUNNER_NAME", "local"),
        "platform": platform.platform(),
        "python": sys.executable,
        "conda_environment": EXPECTED_ENV if args.require_runner else os.environ.get("CONDA_DEFAULT_ENV"),
        "tools": {},
        "results": [],
    }
    manifest_file = output_dir / "build_manifest.json"

    def save_manifest() -> None:
        manifest_file.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    save_manifest()
    try:
        if args.require_runner:
            validate_runner()
        manifest["tools"] = ensure_tex_tools()
    except Exception as exc:
        manifest["preflight_error"] = f"{type(exc).__name__}: {exc}"
        manifest["finished_utc"] = now_utc()
        save_manifest()
        (output_dir / "preflight_error.txt").write_text(
            str(manifest["preflight_error"]) + "\n", encoding="utf-8"
        )
        print(manifest["preflight_error"], file=sys.stderr, flush=True)
        return 2

    for paper in selected:
        manifest["results"].append(compile_one(paper, output_dir))
        save_manifest()
    manifest["finished_utc"] = now_utc()
    save_manifest()
    success = sum(p["status"] == "ok" for p in manifest["results"])
    print(f"Compiled {success}/{len(selected)} manuscripts; manifest: {manifest_file}")
    return 0 if success == len(selected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
