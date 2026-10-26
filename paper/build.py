#!/usr/bin/env python3
"""Build Computational Statistics article with Springer Nature's official format.

Examples (from any working directory):

    python paper/build.py
    python paper/build.py --figures
    python paper/build.py --render-figures --pdf
    python paper/build.py --pdf --package
    python paper/build.py --benchmarks --benchmark-preset quick --repeats 5
    python paper/build.py --tables
    python paper/build.py --pdf
    python paper/build.py --all --benchmark-preset full --repeats 7
    python paper/build.py --dry-run --all
    python paper/build.py --clean

Default: regenerate numerical data, export AwesomeFigures vector PDFs,
and compile the Springer Nature paper. Heavy timing benchmarks remain opt-in.

All outputs remain in paper/. No library source file is modified.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

PAPER = Path(__file__).resolve().parent
REPOSITORY = PAPER.parent
BENCHMARK_RESULTS = PAPER / "benchmarks" / "results"

FIGURE_GENERATORS = (
    "paper/figures/make_figures.py",
    "paper/figures/make_extended_figures.py",
    "paper/figures/make_updated_mauna_loa.py",
    "paper/figures/benchmark_orders.py",
)
FIGURE_RENDERER = "paper/figures/render_awesomefigures.py"
REQUIRED_PDF_INPUTS = (
    PAPER / "figures" / "cortes_toto_synthetic.pdf",
    PAPER / "criteria_table.tex",
    PAPER / "figures" / "mauna_loa_1990_1999.pdf",
    PAPER / "figures" / "mauna_loa_1990_2026_09.pdf",
    PAPER / "figures" / "high_order_numerics.pdf",
)
BENCHMARK_CSVS = (
    BENCHMARK_RESULTS / "full_fit_timings.csv",
    BENCHMARK_RESULTS / "trace_timings.csv",
    BENCHMARK_RESULTS / "environment.json",
)
BENCHMARK_TABLES = (
    BENCHMARK_RESULTS / "full_fit_table.tex",
    BENCHMARK_RESULTS / "trace_table.tex",
    BENCHMARK_RESULTS / "benchmark_environment.tex",
)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    actions = parser.add_argument_group("steps")
    actions.add_argument(
        "--figures", action="store_true",
        help="Run numerical figure generators, render AwesomeFigures vector PDFs, and create the criteria table.",
    )
    actions.add_argument(
        "--render-figures", action="store_true",
        help="Redraw existing .dat/benchmark results using matched SMCCA LaTeX fonts.",
    )
    actions.add_argument(
        "--benchmarks", action="store_true",
        help="Measure full-fit and EDF/trace timing; automatically generate result tables.",
    )
    actions.add_argument(
        "--tables", action="store_true",
        help="Regenerate benchmark LaTeX tables from EXISTING measured CSVs.",
    )
    actions.add_argument(
        "--pdf", action="store_true",
        help="Compile main.tex using latexmk; existing figures are required.",
    )
    actions.add_argument(
        "--all", action="store_true",
        help="Generate figures, run opt-in benchmarks, build tables, and compile PDF.",
    )
    actions.add_argument(
        "--package", action="store_true",
        help="Package the current PDF and flatten all LaTeX sources into a journal-ready ZIP.",
    )
    actions.add_argument(
        "--clean", action="store_true",
        help="Clean ONLY LaTeX auxiliary files and main.pdf; preserve figures and raw data.",
    )
    options = parser.add_argument_group("options")
    options.add_argument(
        "--benchmark-preset", choices=("smoke", "quick", "full"), default="quick",
        help="Benchmark workload; only used with --benchmarks or --all (default: quick).",
    )
    options.add_argument(
        "--repeats", type=int, default=5,
        help="Independent benchmark repetitions (default: 5).",
    )
    options.add_argument(
        "--blas-threads", type=int, default=1,
        help="BLAS threads in benchmark subprocesses (default: 1).",
    )
    options.add_argument(
        "--latex-engine", choices=("pdflatex", "xelatex", "lualatex"),
        default="pdflatex",
        help="LaTeX engine selected through latexmk (default: pdflatex).",
    )
    options.add_argument(
        "--dry-run", action="store_true",
        help="Print each command and intended inputs without executing or writing files.",
    )
    return parser


def _command(cmd: list[str], *, cwd: Path, dry_run: bool) -> None:
    print(f"[paper] {cwd}: {shlex.join(cmd)}", flush=True)
    if dry_run:
        return
    subprocess.run(cmd, cwd=cwd, check=True)


def _git_sha() -> str | None:
    try:
        process = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPOSITORY,
            check=True, capture_output=True, text=True,
        )
        return process.stdout.strip() or None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _verify_required(paths: tuple[Path, ...], reason: str) -> None:
    missing = [str(path.relative_to(REPOSITORY)) for path in paths if not path.is_file()]
    if missing:
        raise ValueError(
            reason + " Missing file(s): " + ", ".join(missing)
        )


def check_bibliography(path: Path) -> int:
    """Catch duplicate BibTeX citation keys before costly paper experiments.

    Keys are checked case-insensitively and by their source line.
    BibTeX syntax errors beyond duplicated keys remain the job of BibTeX.
    """
    if not path.is_file():
        raise ValueError(f"Missing bibliography file: {path}")
    entries = re.compile(
        r"^[ \t]*@[A-Za-z]+[ \t]*\{[ \t]*([^,\s]+)[ \t]*,",
        re.MULTILINE,
    )
    seen: dict[str, int] = {}
    duplicates: list[str] = []
    text = path.read_text(encoding="utf-8")
    for match in entries.finditer(text):
        key = match.group(1)
        line_number = text.count("\n", 0, match.start()) + 1
        normal_key = key.casefold()
        if normal_key in seen:
            duplicates.append(
                f"{key!r} (lines {seen[normal_key]} and {line_number})"
            )
        else:
            seen[normal_key] = line_number
    if duplicates:
        raise ValueError(
            "Duplicate BibTeX citation keys in "
            f"{path}: {', '.join(duplicates)}. "
            "Remove or rename duplicates before building the manuscript."
        )
    if not seen:
        raise ValueError(f"No BibTeX references found in {path}")
    return len(seen)


def _latex_source_identity(source: str) -> dict[str, str]:
    """Identify the LaTeX class and citation format without compiling it."""
    match = re.search(
        r"\\documentclass\s*(?:\[([^\]]*)\])?\s*\{([^{}]+)\}", source
    )
    if match is None:
        raise ValueError("paper/main.tex has no valid \\documentclass declaration")
    options = match.group(1) or ""
    document_class = match.group(2).strip()
    # sn-jnl itself loads natbib and sets the .bst from its class option.
    springer_styles = (
        "sn-mathphys-ay", "sn-mathphys-num", "sn-basic",
        "sn-apa", "sn-chicago", "sn-vancouver-ay", "sn-vancouver-num",
        "sn-aps", "sn-nature",
    )
    styles = [style for style in springer_styles if style in options.split(",")]
    if document_class == "sn-jnl" and styles:
        bib_style = styles[0]
    else:
        style = re.search(r"\\bibliographystyle\s*\{([^{}]+)\}", source)
        bib_style = style.group(1) if style else ""
    return {"document_class": document_class, "bib_style": bib_style}


def _prepare_latex_transition(paper: Path) -> list[str]:
    """Discard obsolete LaTeX auxiliaries when journal or .bst changes.

    The legacy SMCCA .aux contains \\NAT@force@numbers and abbrv citations.
    Springer sn-mathphys-ay reads .aux *before* BibTeX can rebuild it, so
    the class switch otherwise errors out immediately. Never delete figures,
    benchmark CSVs, source files, or manuscript data.
    """
    main = paper / "main.tex"
    if not main.is_file():
        raise ValueError(f"Missing manuscript source {main}")
    identity = _latex_source_identity(main.read_text(encoding="utf-8-sig"))
    if identity["document_class"] != "sn-jnl":
        raise ValueError(
            "The manuscript is still using the previous journal class "
            f"({identity['document_class']!r}). Pull the latest main branch "
            "and confirm paper/main.tex starts with "
            "\\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}."
        )
    if identity["bib_style"] != "sn-mathphys-ay":
        raise ValueError(
            f"Expected sn-mathphys-ay author-year bibliography; "
            f"found {identity['bib_style']!r}."
        )
    state_path = paper / ".latex_build_identity.json"
    prior = None
    if state_path.is_file():
        try:
            prior = json.loads(state_path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            prior = None

    aux = paper / "main.aux"
    aux_text = aux.read_text(encoding="utf-8", errors="replace") if aux.is_file() else ""
    bib_from_aux = re.search(r"\\bibstyle\s*\{([^{}]+)\}", aux_text)
    forced_numeric = r"\NAT@force@numbers" in aux_text
    stale_bib = (
        bib_from_aux is not None
        and bib_from_aux.group(1) != identity["bib_style"]
    )
    stale_identity = prior is not None and prior != identity
    needs_reset = stale_bib or forced_numeric or stale_identity
    removed: list[str] = []
    if needs_reset:
        # Target *only* files produced by TeX/BibTeX/latexmk, never inputs
        # or expensive computed experimental artifacts.
        extensions = (
            ".aux", ".bbl", ".blg", ".fdb_latexmk", ".fls", ".log",
            ".out", ".toc", ".lof", ".lot", ".synctex.gz",
            ".bcf", ".run.xml",
        )
        for extension in extensions:
            path = paper / ("main" + extension)
            if path.is_file():
                path.unlink()
                removed.append(path.name)
        # latexmk will overwrite the draft PDF. Keep any previous PDF until
        # successful compilation rather than destroying a user's last copy.
        print(
            "[paper] Changed LaTeX class/bibliography detected: "
            "removed obsolete auxiliary files "
            + (", ".join(removed) if removed else "(none)"),
            flush=True,
        )
    return removed


def _save_latex_identity(paper: Path) -> None:
    identity = _latex_source_identity((paper / "main.tex").read_text(encoding="utf-8-sig"))
    (paper / ".latex_build_identity.json").write_text(
        json.dumps(identity, indent=2) + "\n", encoding="utf-8"
    )


def _latexmk_command(engine: str, clean: bool = False) -> list[str]:
    if clean:
        return ["latexmk", "-C", "main.tex"]
    flag = {
        "pdflatex": "-pdf",
        "xelatex": "-xelatex",
        "lualatex": "-lualatex",
    }[engine]
    return [
        "latexmk", flag, "-interaction=nonstopmode",
        "-halt-on-error", "-file-line-error", "main.tex",
    ]


def run(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)

    if args.repeats < 1 or args.blas_threads < 1:
        parser.error("--repeats and --blas-threads must be positive integers")
    if args.clean and any((
        args.figures, args.render_figures, args.benchmarks,
        args.tables, args.pdf, args.package, args.all
    )):
        parser.error("--clean cannot be combined with generation or --all")
    if args.benchmark_preset != "quick" and not (
        args.benchmarks or args.all or args.clean
    ):
        parser.error("--benchmark-preset requires --benchmarks or --all")

    if args.clean:
        if not args.dry_run and shutil.which("latexmk") is None:
            parser.error("latexmk is not on PATH; install a TeX distribution")
        _command(_latexmk_command(args.latex_engine, clean=True),
                 cwd=PAPER, dry_run=args.dry_run)
        return 0

    # The default build is deterministic figures + PDF, NOT a long benchmark.
    explicit_steps = any((
        args.figures, args.render_figures, args.benchmarks,
        args.tables, args.pdf, args.package, args.all,
    ))
    figures = args.figures or args.all or not explicit_steps
    redraw = args.render_figures
    benchmarks = args.benchmarks or args.all
    tables = args.tables or benchmarks
    pdf = args.pdf or args.all or not explicit_steps
    if not benchmarks and args.benchmark_preset != "quick":
        parser.error("--benchmark-preset requires --benchmarks or --all")

    if not args.dry_run:
        if pdf and shutil.which("latexmk") is None:
            parser.error(
                "latexmk is not on PATH. Install a TeX distribution, or "
                "run --figures/--benchmarks/--tables without --pdf."
            )
        try:
            if tables and not benchmarks:
                _verify_required(
                    BENCHMARK_CSVS,
                    "--tables needs measured benchmark CSV files. "
                    "Run with --benchmarks to obtain them first.",
                )
            if pdf and not (figures or redraw):
                _verify_required(
                    REQUIRED_PDF_INPUTS,
                    "--pdf needs prior generated figures and criteria_table.tex. "
                    "Run --figures --pdf (or omit flags for a default build)." ,
                )
        except ValueError as exc:
            parser.error(str(exc))
        if pdf and not benchmarks and any(path.is_file() for path in BENCHMARK_TABLES):
            print(
                "[paper] NOTE: Existing benchmark tables will be reused. "
                "Check their host/revision metadata, or rerun --benchmarks.",
                flush=True,
            )

    # Validate inexpensive bibliographic invariants BEFORE running costly
    # figure generators and benchmark sweeps, even when using --all.
    if not args.dry_run and pdf:
        try:
            count = check_bibliography(PAPER / "bibliografia.bib")
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        print(f"[paper] Bibliography preflight: {count} unique citation keys", flush=True)
        try:
            _prepare_latex_transition(PAPER)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))

    start = perf_counter()
    steps: list[dict] = []

    def step(name: str, command: list[str], working_dir: Path) -> None:
        t0 = perf_counter()
        _command(command, cwd=working_dir, dry_run=args.dry_run)
        steps.append({
            "name": name,
            "command": command,
            "working_directory": str(working_dir),
            "elapsed_seconds": round(perf_counter() - t0, 6),
        })

    try:
        if figures:
            for script in FIGURE_GENERATORS:
                step("generate:" + Path(script).name,
                     [sys.executable, script], REPOSITORY)
            step("render:awesomefigures",
                 [sys.executable, FIGURE_RENDERER],
                 REPOSITORY)
        elif redraw:
            step("render:awesomefigures-from-existing-data",
                 [sys.executable, FIGURE_RENDERER],
                 REPOSITORY)
        if benchmarks:
            step(
                "benchmark:fits-and-traces",
                [
                    sys.executable, "paper/benchmarks/run_all.py",
                    "--preset", args.benchmark_preset,
                    "--repeats", str(args.repeats),
                    "--blas-threads", str(args.blas_threads),
                ],
                REPOSITORY,
            )
            step("render:benchmark-figures",
                 [sys.executable, FIGURE_RENDERER, "--benchmarks-only"],
                 REPOSITORY)
        elif tables:
            step(
                "tables:existing-benchmark-CSV",
                [sys.executable, "paper/benchmarks/write_paper_results.py"],
                REPOSITORY,
            )
            step("render:benchmark-figures",
                 [sys.executable, FIGURE_RENDERER, "--benchmarks-only"],
                 REPOSITORY)
        if pdf:
            if not args.dry_run:
                _verify_required(
                    REQUIRED_PDF_INPUTS,
                    "Cannot compile PDF because required inputs were not generated.",
                )
                if tables:
                    _verify_required(
                        BENCHMARK_TABLES,
                        "Benchmark LaTeX tables were not generated successfully.",
                    )
            step("compile:PDF", _latexmk_command(args.latex_engine), PAPER)
            if not args.dry_run:
                _save_latex_identity(PAPER)
        if args.package or args.all:
            step(
                "package:Computational-Statistics",
                [sys.executable, "paper/package_submission.py"],
                REPOSITORY,
            )
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"[paper] Build failed: {exc}", file=sys.stderr, flush=True)
        return 1

    if not args.dry_run:
        record = {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "git_revision": _git_sha(),
            "platform": platform.platform(),
            "python": sys.version,
            "flags": vars(args),
            "steps": steps,
            "total_elapsed_seconds": round(perf_counter() - start, 6),
            "pdf": str(PAPER / "main.pdf") if pdf else None,
            "benchmark_results": (
                str(BENCHMARK_RESULTS) if benchmarks or tables else
                "reused when present"
            ),
        }
        (PAPER / "build_manifest.json").write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )
        print("[paper] Build manifest: paper/build_manifest.json")
    if pdf:
        print("[paper] " + (
            "Planned PDF: paper/main.pdf" if args.dry_run
            else "PDF: paper/main.pdf"
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
