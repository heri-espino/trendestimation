"""Experiment011: safe staged campaign for complete-criterion PLS runtimes.

This code deliberately reuses the EXISTING and tested Experiment006
complete-criterion runner; it does not copy its numerical implementations
or import unmerged Experiment010 PR APIs. There is no default timing run.

Examples from the repository root (PowerShell):
    python paper/benchmarks/experiment011/campaign.py list
    python paper/benchmarks/experiment011/campaign.py plan
    python paper/benchmarks/experiment011/campaign.py run --case smoke_gcv_n64_d1_m100 --run-tag local001 --block 0
    python paper/benchmarks/experiment011/campaign.py run --case pilot_cv_n128_d3_m100 --run-tag vm001 --block 0
    python paper/benchmarks/experiment011/campaign.py run --case confirm_cv_n256_d3_m1000 --run-tag vm001 --block 0 --allow-confirm

The method order rotates with --block. For a publication candidate use
blocks 0,1,2 with two distinct seeded repeats per block. Raw measurement
CSV and failures always remain on disk and must be committed and pushed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "paper" / "benchmarks" / "experiment006" / "run.py"
CASE_FILE = HERE / "cases.json"
RUNS = HERE / "runs"
VALID_STAGES = ("smoke", "pilot", "confirm")
VALID_CRITERIA = ("cv", "gcv", "aicc", "bic", "mle")
METHODS = (
    "spectral_svd", "banded_cholesky", "naive_inverse",
    "sparse_cholesky_banded_trace",
)
VALID_IDS = re.compile(r"^[a-z0-9][a-z0-9_]{2,90}$")
VALID_TAGS = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,48}$")


@contextmanager
def approved_experiment011_size(engine, n: int):
    """Admit 2048/4096 only for this one Experiment011 run.

    Experiment006 and Experiment008 keep their original declared
    factor levels and published full-factorial plan. This changes
    only run_slice's admission check, not a numerical algorithm.
    """
    old_levels = engine.N_LEVELS
    if n not in old_levels and n not in (2048, 4096):
        raise ValueError("Unsupported Experiment011 size")
    try:
        if n not in old_levels:
            engine.N_LEVELS = (*old_levels, n)
        yield
    finally:
        engine.N_LEVELS = old_levels


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT,
            check=True, capture_output=True, text=True, timeout=8
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def load_design() -> dict:
    design = json.loads(CASE_FILE.read_text(encoding="utf-8"))
    if design["experiment"] != "experiment011" or design["schema_version"] != 1:
        raise ValueError("Experiment011 design schema changed unexpectedly")
    if design["parent_runner"] != "paper/benchmarks/experiment006/run.py":
        raise ValueError("Benchmark engine must be the reviewed full-criterion source")
    if design["blas_threads"] != 1:
        raise ValueError("Isolated latency campaign must use exactly one BLAS thread")
    if design["max_work"] <= 0 or design["max_dense_bytes"] <= 0:
        raise ValueError("Positive numerical and memory budgets are required")
    seen = set()
    for case in design["cases"]:
        case_id = case["id"]
        if not VALID_IDS.fullmatch(case_id) or case_id in seen:
            raise ValueError("Bad or duplicate case id: " + str(case_id))
        seen.add(case_id)
        if case["stage"] not in VALID_STAGES:
            raise ValueError("Unrecognized stage")
        if "max_work" in case:
            if case["stage"]!="confirm" or case["n"]!=1024 or case["d"]!=4:
                raise ValueError("Per-case work increase is only allowed for n1024 d4 confirm")
            if not design["max_work"] < case["max_work"] <= 750_000_000:
                raise ValueError("Case work budget exceeds predeclared cap")
        if case["criterion"] not in VALID_CRITERIA:
            raise ValueError("Unrecognized criterion")
        if case["n"] not in (64, 128, 256, 512, 1024, 2048, 4096):
            raise ValueError("Case exceeds declared finite-size pilot design")
        if case["d"] not in (1, 2, 3, 4, 5, 6) or case["d"] >= case["n"]:
            raise ValueError("Invalid finite-difference order")
        if case["grid_denominator"] not in (100, 1000, 10000, 100000):
            raise ValueError("Invalid normalized-S grid")
        if case["mu"] not in ("0", "0.15", "data"):
            raise ValueError("Unexpected mean/reference policy")
        if case["conditional_data_mu"] != (case["mu"] == "data"):
            raise ValueError("Data-derived mu requires explicit conditional flag")
        if case["amplitude"] not in ("low", "high"):
            raise ValueError("Invalid scale")
        if not case["methods"] or len(set(case["methods"])) != len(case["methods"]):
            raise ValueError("Bad method list")
        if set(case["methods"]) - set(METHODS):
            raise ValueError("Not an implemented complete-criterion method")
        if case["series_count"] < 2 or case["repeats_per_block"] < 1:
            raise ValueError("Invalid paired design")
        if case["planned_blocks"] != (1 if case["stage"] == "smoke" else 3):
            raise ValueError("Blocks must be predeclared")
    return design


def select_case(design: dict, name: str) -> dict:
    candidates = [x for x in design["cases"] if x["id"] == name]
    if len(candidates) != 1:
        raise ValueError(f"Unknown case {name!r}; run 'list' first")
    return candidates[0]


def preflights(case: dict, design: dict) -> list[dict]:
    # Numerical resource gates are imported from the actual benchmark source.
    sys.path.insert(0, str(SOURCE.parent))
    from run import SCENARIOS, memory_budget_status
    result = []
    for method in case["methods"]:
        for scenario in SCENARIOS:
            r = 1 if "one_series" in scenario else case["series_count"]
            state = memory_budget_status(
                case["n"], case["d"], method, case["grid_denominator"],
                design["max_dense_bytes"],
                case.get("max_work",design["max_work"]),
                scenario, r, case["repeats_per_block"]
            )
            result.append({
                "case": case["id"], "method": method,
                "scenario": scenario, "R": r,
                "M": 1 if scenario.startswith("one_s") else case["grid_denominator"],
                "preflight": state,
            })
    return result


def plan(args: argparse.Namespace) -> None:
    design = load_design()
    records = []
    for case in design["cases"]:
        cases = preflights(case, design)
        records.append({
            "case": case["id"], "stage": case["stage"],
            "n": case["n"], "d": case["d"],
            "criterion": case["criterion"],
            "candidate_count": case["grid_denominator"],
            "methods": case["methods"],
            "planned_blocks": case["planned_blocks"],
            "repeats_per_block": case["repeats_per_block"],
            "preflights": cases,
            "max_work_for_this_case":case.get("max_work",design["max_work"]),
            "status": "planned_not_measured",
        })
    summary = Counter(v["preflight"] for row in records for v in row["preflights"])
    payload = {
        "experiment": "experiment011",
        "schema": 1,
        "data_type": "planned_eligibility_not_observed_timing",
        "design_sha256": sha256_file(CASE_FILE),
        "runner_sha256": sha256_file(SOURCE),
        "cases": records,
        "preflight_counts": dict(sorted(summary.items())),
        "note": "Budget and memory feasibility are only preflight predictions. "
                "No actual numerical run is implied.",
    }
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    # Keep the original 21-case plan immutable; the eight additional
    # d=4/large-n cases require their own versioned plan.
    path = args.output or HERE / "plans" / "experiment011_plan_expanded.json"
    if path.is_file() and path.read_text(encoding="utf-8") != content:
        raise FileExistsError(
            f"Existing plan differs: {path}; review the proposed change first"
        )
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"PLAN ONLY: {len(records)} cases, {sum(summary.values())} method/scenario preflights")
    print("Preflight states:", dict(sorted(summary.items())))
    print("Saved:", path)


def run_one(args: argparse.Namespace) -> None:
    design = load_design()
    if not args.case:
        raise ValueError("--case is required; no implicit batch or factorial runs")
    if not args.run_tag or not VALID_TAGS.fullmatch(args.run_tag):
        raise ValueError("--run-tag must be a safe machine/run ID, e.g. PCAG103A08_001")
    case = select_case(design, args.case)
    if case["stage"] == "confirm" and not args.allow_confirm:
        raise PermissionError("Confirm-sized cases require --allow-confirm")
    if args.block < 0 or args.block >= case["planned_blocks"]:
        raise ValueError("Block is outside the predeclared independent blocks")
    if Path.cwd().resolve() != ROOT.resolve():
        raise RuntimeError("Run from the repository root to preserve Git/environment provenance")
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    # Rotating the order across blocks reduces (but does not eliminate)
    # the fixed-order/thermal drift of the inherited sequential engine.
    methods = list(case["methods"])
    shift = args.block % len(methods)
    methods = methods[shift:] + methods[:shift]
    block_name = f"block{args.block:03d}"
    path = RUNS / args.run_tag / case["id"] / block_name
    config = {
        "experiment": "experiment011", "case": case,
        "block": args.block, "method_order": methods,
        "threads": 1, "python_executable": sys.executable,
        "seed": design["seed_base"] + 10000 * args.block,
        "source_commit": git_sha(),
        "source_file_sha256": sha256_file(SOURCE),
        "case_design_sha256": sha256_file(CASE_FILE),
        "inherited_runner": design["parent_runner"],
        "preflights": preflights(case, design),
        "max_work_for_this_case":case.get("max_work",design["max_work"]),
        "n_level_extension": (
            "Experiment011-only admission of 2048/4096, no change to the"
            " Experiment006 or Experiment008 factorial"
            if case["n"] in (2048, 4096) else "unchanged"
        ),
        "status": "not_measured" if args.dry_run else "started",
        "caveats": [
            "One worker per invocation; exactly one BLAS thread",
            "total_cold_s uses inherited setup attribution; not fresh-process cold start",
            "conditional mu=data CV is not refitted leave-one-out CV",
            "Gaussian MLE score levels may have constant-offset differences",
            "fit-only times must not be compared with complete criterion runs",
        ],
    }
    if args.dry_run:
        print(json.dumps({"path": str(path), "config": config}, indent=2))
        return
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite a run or checkpoint: {path}")
    path.mkdir(parents=True, exist_ok=False)
    manifest = path / "experiment011_case.json"
    manifest.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    # Actual analysis and timestamps stay in the run folder; no fake rows.
    sys.path.insert(0, str(SOURCE.parent))
    import run as inherited_runner
    try:
        mu = "data" if case["mu"] == "data" else float(case["mu"])
        # Experiment006 deliberately froze its older factorial n levels.
        # Its run_slice rejects additional n before any numerical work.
        # Extend ONLY that input-admission tuple during this one call;
        # no solver, criterion, work guard, old manifest or other
        # experiment is modified. Restore it on success or failure.
        with approved_experiment011_size(inherited_runner, case["n"]):
            rows, _ = inherited_runner.run_slice(
                n=case["n"], d=case["d"], mu=mu,
                amplitude=case["amplitude"], criterion=case["criterion"],
                denominator=case["grid_denominator"], methods=tuple(methods),
                repeats=case["repeats_per_block"], R=case["series_count"],
                max_work=case.get("max_work",design["max_work"]),
                max_dense_bytes=design["max_dense_bytes"],
                output=path / "measurements", threads=1,
                seed=config["seed"],
                conditional_data_mu=case["conditional_data_mu"],
            )
        # Independent post-run QA is always persisted, even when some
        # rows have numerical_failed or budget_exceeded status.
        from verify import audit_run
        audit = audit_run(path)
        config["status"] = "measured_pending_review"
        config["completed_utc"] = datetime.now(timezone.utc).isoformat()
        config["actual_rows"] = len(rows)
        config["qa_status"] = audit["classification"]
        config["raw_sha256"] = sha256_file(path / "measurements" / "raw_times.csv")
        manifest.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        print("ARCHIVE THIS FOLDER (including failures):", path)
        print("QA:", audit["classification"], audit["status_counts"])
        print("Do not claim a speed winner before independent numerical audit.")
    except BaseException as exc:
        config["status"] = "failed_or_interrupted"
        config["error_type"] = type(exc).__name__
        config["error"] = str(exc)
        config["traceback"] = traceback.format_exc()[-4000:]
        manifest.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List predeclared cases; does not execute")
    p = sub.add_parser("plan", help="Store full planned eligibility manifest; no timing")
    p.add_argument("--output", type=Path, default=None)
    r = sub.add_parser("run", help="Run exactly one case and one independent block")
    r.add_argument("--case", required=True)
    r.add_argument("--run-tag", required=True)
    r.add_argument("--block", type=int, default=0)
    r.add_argument("--allow-confirm", action="store_true")
    r.add_argument("--dry-run", action="store_true")
    ps = sub.add_parser(
        "parallel-series",
        help="OPT-IN separate throughput experiment for independent small series"
    )
    ps.add_argument("--case", required=True)
    ps.add_argument("--run-tag", required=True)
    ps.add_argument("--block", type=int, default=0)
    ps.add_argument("--series-count", type=int, default=None,
                    help="Independent series, default case R; may increase to 32")
    ps.add_argument("--series-workers", type=int, default=None,
                    help="Separate processes; default min(8,R), maximum 32")
    ps.add_argument("--allow-confirm", action="store_true")
    ps.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.command == "list":
        for c in load_design()["cases"]:
            print(c["stage"], c["id"], "n",c["n"],"d",c["d"],
                  "M",c["grid_denominator"],"criterion",c["criterion"])
    elif args.command == "plan":
        plan(args)
    elif args.command == "parallel-series":
        if not VALID_TAGS.fullmatch(args.run_tag):
            raise ValueError("Invalid --run-tag")
        design=load_design()
        case=select_case(design,args.case)
        if case["stage"]=="confirm" and not args.allow_confirm:
            raise PermissionError("Confirm cases require --allow-confirm")
        if Path.cwd().resolve()!=ROOT.resolve():
            raise RuntimeError("Run from repository root for provenance")
        from parallel_series import run_parallel
        count=case["series_count"] if args.series_count is None else args.series_count
        workers=min(8,count) if args.series_workers is None else args.series_workers
        result=run_parallel(
            case,run_tag=args.run_tag,block=args.block,
            series_count=count,series_workers=workers,
            max_work=design["max_work"],
            max_dense_bytes=design["max_dense_bytes"],
            seed_base=design["seed_base"],source_commit=git_sha(),
            source_hashes={
                "experiment006":sha256_file(SOURCE),
                "experiment011_cases":sha256_file(CASE_FILE),
                "experiment011_parallel_series":sha256_file(
                    HERE/"parallel_series.py"
                ),
            },
            dry_run=args.dry_run
        )
        if args.dry_run:
            print(json.dumps(result,indent=2))
        else:
            print("Separate throughput archive:",result["output"])
            print("NOT interchangeable with serial shared-cache timing results.")
    else:
        run_one(args)


if __name__ == "__main__":
    main()
