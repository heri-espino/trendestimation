"""Experiment010: bounded, fully archived all-method PLS criterion timings.

Run from the repository root (with PYTHONPATH=src):
    python paper/benchmarks/experiment010/run_batches.py --preset smoke \
      --output paper/benchmarks/experiment010/runs/local-unique

No timings are inferred for skipped/failed jobs. The complete experiment
manifest covers all specified methods, mean policies and candidate densities.
Experiment006 is the single source of truth for scores and timing columns.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[3]
EXP006 = ROOT / "paper" / "benchmarks" / "experiment006"
sys.path.insert(0, str(EXP006))
from run import (CRITERIA, D_LEVELS, GRID_DENOMINATORS, METHODS,
                 N_LEVELS, POLICIES, SCENARIOS, memory_budget_status)  # noqa: E402

MEANS = ("0", "data", "0.15")
AMPLITUDES = ("low", "high")
METHODS_ALL = tuple(METHODS)
COLUMNS = ("case_id", "n", "d", "mu", "amplitude",
           "criterion", "denominator", "method", "status",
           "reason", "elapsed_s", "measured_rows", "run_id", "source_sha")
PAIRED_COLUMNS = ("case_id", "method", "criterion", "mu", "workload",
                  "coordinate", "repeat", "status", "reference_method",
                  "candidate_score", "reference_score", "relative_score_error",
                  "total_cold_s", "total_warm_s", "evaluations", "expected_evaluations")


def case(n, d, mu, amplitude, criterion, denominator):
    return dict(n=int(n), d=int(d), mu=str(mu),
                amplitude=str(amplitude), criterion=str(criterion),
                denominator=int(denominator))


def configurations(preset):
    """Deterministic case set; each case tries EVERY method in METHODS_ALL."""
    if preset == "smoke":
        return [case(64, 1, mu, "high", "gcv", 100) for mu in MEANS]
    if preset == "pilot":
        # Front-load coverage across every d, all 3 means and all 5
        # criteria; the complete pilot still crosses every n,d,C,mu.
        priority = [
            case(n, d, MEANS[i % 3], "high",
                 CRITERIA[(i + (n == 128)) % len(CRITERIA)], 100)
            for n in (64, 128)
            for i, d in enumerate(D_LEVELS)
        ]
        full = [case(n, d, mu, "high", criterion, 100)
                for n, d, criterion in product(
                    (64, 128), D_LEVELS, CRITERIA)
                for mu in MEANS]
        seen = {json.dumps(c, sort_keys=True) for c in priority}
        return priority + [
            c for c in full if json.dumps(c, sort_keys=True) not in seen]
    if preset == "frontier":
        # First class-balanced n>128 challenge: compare ALL three mu
        # policies within each n,d,criterion workload. Each of four
        # blocks has exactly ten methods times three mean policies.
        # Exact same S grid across the 10 complete pipelines.
        blocks = (
            (256, 1, "gcv"),
            (256, 5, "mle"),
            (512, 2, "aicc"),
            (512, 6, "cv"),
        )
        return [
            case(n, d, mu, "high", criterion, 100)
            for n, d, criterion in blocks for mu in MEANS
        ]
    if preset == "comprehensive":
        return [case(*p) for p in product(
            N_LEVELS, D_LEVELS, MEANS, AMPLITUDES,
            CRITERIA, GRID_DENOMINATORS)]
    raise ValueError(f"Unknown preset: {preset}")


def case_id(c):
    raw = json.dumps(c, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"n{c['n']}_d{c['d']}_{c['criterion']}_{digest}"


def attempts(preset, shard_index=0, shard_count=1):
    if shard_count < 1 or not (0 <= shard_index < shard_count):
        raise ValueError("Invalid shard configuration")
    return [(case_id(c), c, method)
            for c in configurations(preset)
            if int(hashlib.sha256(case_id(c).encode()).hexdigest()[:8], 16)
               % shard_count == shard_index
            for method in METHODS_ALL]


def manifest(path, *, max_work, repeats, series_count,
             max_dense_bytes, shard_index, shard_count, preset,
             scope="full", allow_unbounded_runtime=False):
    """Record EVERY planned method-case pair and its conservative mask."""
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    with gzip.open(path, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=(
            *COLUMNS, "workload", "coordinate", "M", "R",
            "score_semantics", "plan_status"))
        writer.writeheader()
        # One complete design-only archive has the full manifest. Distributed
        # execution archives keep the exact selected shard, without repeating
        # hundreds of thousands of unrelated rows per execution batch.
        for c in configurations("comprehensive"):
            identifier = case_id(c)
            in_shard = (int(hashlib.sha256(identifier.encode()).hexdigest()[:8], 16)
                        % shard_count == shard_index)
            if scope == "shard" and not in_shard:
                continue
            for method in METHODS_ALL:
                for workload in SCENARIOS:
                    M = 1 if workload.startswith("one_s") else c["denominator"]
                    R = 1 if "one_series" in workload else series_count
                    status = memory_budget_status(
                        c["n"], c["d"], method, c["denominator"],
                        max_dense_bytes, max_work, workload, R, repeats,
                        allow_unbounded_runtime=allow_unbounded_runtime)
                    counts[status] += 2
                    for coordinate in POLICIES:
                        writer.writerow(dict(
                            case_id=identifier, **c, method=method,
                            status="planned", reason="", elapsed_s="",
                            measured_rows="", run_id="", source_sha="",
                            workload=workload, coordinate=coordinate,
                            M=M, R=R,
                            score_semantics=("conditional_plugin"
                                             if c["mu"] == "data"
                                             else "fixed_reference_mean"),
                            plan_status=status if in_shard else "outside_shard"))
    return dict(counts)


def source_sha():
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True,
            capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def archive_ledger(path, records):
    """Atomically checkpoint the ledger, tolerating transient WinError 5.

    Windows antivirus/indexing or an external reader may temporarily hold the
    destination open. Never delete the existing ledger to force replacement.
    If retries fail, retain a versioned, complete CSV and report its path.
    """
    import time

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(
        f".{path.stem}.{os.getpid()}.{time.time_ns()}.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)
        out.flush()
        os.fsync(out.fileno())

    last_error = None
    for i in range(8):
        try:
            tmp.replace(path)
            return path
        except PermissionError as exc:
            last_error = exc
            time.sleep(min(0.1 * 2 ** i, 1.0))
        except OSError as exc:
            if getattr(exc, "winerror", None) not in (5, 32):
                raise
            last_error = exc
            time.sleep(min(0.1 * 2 ** i, 1.0))

    # A concurrently open ledger must not discard a completed numerical job.
    # The complete record remains in this independent versioned CSV.
    recovery = path.with_name(
        f"{path.stem}.recovery-{len(records)}-{time.time_ns()}.csv")
    try:
        tmp.rename(recovery)
    except OSError:
        recovery = tmp  # Still a complete, closed, durable file.
    print("WARNING: Windows locked the ledger destination; "
          f"checkpoint preserved at {recovery}. "
          f"Original error: {last_error}", flush=True)
    return recovery


def aggregate(output, outcomes):
    """Check selected criterion scores, but do NOT call this precision proof.

    The independent high-precision trend-forward audits of Experiment006
    remain a separate necessary numerical reliability gate.
    """
    by_case = defaultdict(list)
    for item in outcomes:
        if item["status"] != "completed_with_csv":
            continue
        raw = output / item["folder"] / "raw_times.csv"
        if not raw.is_file():
            continue
        with raw.open(newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                by_case[item["case_id"]].append(row)
    parity = []
    reference_count = 0
    failures = Counter()
    for identifier, rows in by_case.items():
        ref = {(r["workload"], r["coordinate"], r["repeat"]): r
               for r in rows if r["method"] == "spectral_svd"
               and r["status"] == "ok" and math.isfinite(
                   float(r["selected_score"]))}
        for r in rows:
            key = (r["workload"], r["coordinate"], r["repeat"])
            baseline = ref.get(key)
            expected = int(r["M"]) * int(r["R"])
            count = int(r["evaluations"])
            reported_ok = (r["status"] == "ok"
                           and count == expected
                           and math.isfinite(float(r["selected_score"])))
            score = float(r["selected_score"])
            ref_score = float(baseline["selected_score"]) if baseline else math.nan
            rel = (abs(score - ref_score) / max(1., abs(ref_score))
                   if reported_ok and baseline is not None else math.nan)
            if not reported_ok:
                status = "failed_or_partial"
            elif baseline is None:
                status = "unverified_no_spectral_reference"
            elif math.isclose(score, ref_score, rel_tol=1e-6, abs_tol=1e-8):
                status = "score_parity_only_not_precision_certified"
                reference_count += 1
            else:
                status = "score_disagreement"
            failures[status] += 1
            parity.append({
                "case_id": identifier, "method": r["method"],
                "criterion": r["criterion"], "mu": r["mu"],
                "workload": r["workload"],
                "coordinate": r["coordinate"], "repeat": r["repeat"],
                "status": status, "reference_method": ("spectral_svd"
                                                        if baseline else ""),
                "candidate_score": score, "reference_score": ref_score,
                "relative_score_error": rel,
                "total_cold_s": r["total_cold_s"],
                "total_warm_s": r["total_warm_s"],
                "evaluations": count, "expected_evaluations": expected,
            })
    with (output / "score_parity_not_certification.csv").open(
            "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=PAIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(parity)
    return {"parity_row_status_counts": dict(failures),
            "parity_agreements_not_precision_proofs": reference_count,
            "parity_rows": len(parity)}


def execute(output, *, preset="smoke", shard_index=0, shard_count=1,
            max_seconds=900, per_method_seconds=50,
            max_method_attempts=40, repeats=1, series_count=2,
            max_work=3e7, max_dense_bytes=2*1024**3,
            seed=20261102, start_attempt=0,
            plan_only=False, manifest_scope="full",
            no_time_limit=False):
    if manifest_scope not in ("full", "shard"):
        raise ValueError("manifest_scope must be full or shard")
    if plan_only and (preset != "comprehensive" or manifest_scope != "full"):
        raise ValueError("Plan-only mode requires the complete comprehensive manifest")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite results: {output}")
    if repeats < 1 or series_count < 2:
        raise ValueError("Invalid repetition/series")
    if not no_time_limit and per_method_seconds < 1:
        raise ValueError("Invalid per-method timeout")
    if not no_time_limit and max_seconds < 1:
        raise ValueError("Invalid whole-run timeout")
    if max_method_attempts < 1:
        raise ValueError("Invalid execution budget")
    if no_time_limit:
        max_work = math.inf  # No estimated-work threshold, not a RAM bypass.
    output.mkdir(parents=True)
    started = perf_counter()
    sha = source_sha()
    all_work = attempts(preset, shard_index, shard_count)
    if not (0 <= start_attempt <= len(all_work)):
        raise ValueError('start_attempt outside selected shard')
    work = all_work[start_attempt:]
    metadata = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "preset": preset, "source_sha": sha,
        "plan_only": plan_only, "manifest_scope": manifest_scope,
        "no_time_limit": no_time_limit,
        "subprocess_timeout_seconds": (None if no_time_limit else per_method_seconds),
        "max_work": ("unbounded" if no_time_limit else max_work),
        "host": platform.platform(), "python": sys.version,
        "runner_name": os.environ.get("RUNNER_NAME"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "shard_index": shard_index, "shard_count": shard_count,
        "methods": METHODS_ALL, "mean_policies": MEANS,
        "criteria": CRITERIA, "coordinates": POLICIES,
        "workloads": SCENARIOS,
        "max_seconds": (None if no_time_limit else max_seconds),
        "per_method_seconds": (None if no_time_limit else per_method_seconds),
        "max_method_attempts": max_method_attempts,
        "repeats": repeats, "series_count": series_count,
        "max_dense_bytes": max_dense_bytes,
        "seed": seed, "planned_attempts_in_shard": len(all_work),
        "start_attempt": start_attempt,
        "attempts_in_this_window": len(work),
        "warning": ("A recorded status=ok is not independent numerical "
                    "certification; high-precision audit required. "
                    "No synthetic timing of skipped methods.")
    }
    (output / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    counts = manifest(output / "full_factorial_plan.csv.gz",
                      max_work=max_work, repeats=repeats,
                      series_count=series_count,
                      max_dense_bytes=max_dense_bytes,
                      shard_index=shard_index, shard_count=shard_count,
                      preset=preset, scope=manifest_scope,
                      allow_unbounded_runtime=no_time_limit)
    if plan_only:
        summary = dict(status="design_only_no_benchmarks",
                       planned_cases=len(configurations("comprehensive")),
                       planned_method_cases=len(all_work),
                       planned_manifest_statuses=counts,
                       successful_raw_timing_rows=0,
                       actual_attempted=0, elapsed_s=perf_counter()-started)
        (output / "batch_summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        return summary
    ledger = []
    outcomes = []
    for i, (identifier, c, method) in enumerate(work):
        elapsed = perf_counter() - started
        remaining = (math.inf if no_time_limit else max_seconds - elapsed)
        if (i >= max_method_attempts or (not no_time_limit and remaining <= 1)):
            status = "not_executed_budget"
            reason = "Whole-run time or attempt budget exhausted"
            elapsed_method = 0.0
            measured = 0
        else:
            # A fully preflight-ineligible method-case must not start an
            # expensive subprocess or invent a measured runtime.
            masks = [
                memory_budget_status(
                    c["n"], c["d"], method, c["denominator"],
                    max_dense_bytes, max_work, scenario,
                    1 if "one_series" in scenario else series_count,
                    repeats, allow_unbounded_runtime=no_time_limit)
                for scenario in SCENARIOS
            ]
            if preset == "comprehensive" and "eligible" not in masks:
                status = "resource_ineligible_all_workloads"
                reason = ";".join(sorted(set(masks)))
                elapsed_method = 0.0
                measured = 0
                print(f"[{start_attempt+i+1}/{len(all_work)}] "
                      f"{identifier} {method}: {status} ({reason})",
                      flush=True)
            else:
                folder = Path("slices") / identifier / method
                dest = output / folder
                dest.parent.mkdir(parents=True, exist_ok=True)
                cmd = [
                    sys.executable, str(EXP006 / "run.py"),
                    "--preset", "slice", "--n", str(c["n"]),
                    "--d", str(c["d"]), "--mu", c["mu"],
                    "--amplitude", c["amplitude"],
                    "--criterion", c["criterion"],
                    "--grid-denominator", str(c["denominator"]),
                    "--methods", method, "--threads", "1",
                    "--repeats", str(repeats),
                    "--series-count", str(series_count),
                    "--max-work", str(max_work),
                    "--max-dense-bytes", str(max_dense_bytes),
                    "--seed", str(seed), "--conditional-data-mu",
                    *(["--allow-unbounded-runtime"] if no_time_limit else []),
                    "--output", str(dest),
                ]
                t0 = perf_counter()
                try:
                    # Stream subprocess output immediately to disk. Uncapped
                    # procedures could run for hours: capture_output=True
                    # would accumulate unbounded logs in host RAM.
                    log_path = dest.parent / f"{method}.log"
                    with log_path.open("w", encoding="utf-8") as log:
                        log.write(f"started_utc={datetime.now(timezone.utc).isoformat()}\n")
                        log.write(f"no_time_limit={no_time_limit}\n")
                        log.flush()
                        proc = subprocess.run(
                            cmd, text=True, stdout=log, stderr=subprocess.STDOUT,
                            timeout=(None if no_time_limit else
                                     min(float(per_method_seconds), max(1., remaining))),
                            check=False, cwd=ROOT)
                    elapsed_method = perf_counter() - t0
                    if proc.returncode:
                        status, reason, measured = (
                            "execution_failed", f"exit_code={proc.returncode}", 0)
                    elif not (dest / "raw_times.csv").is_file():
                        status, reason, measured = (
                            "missing_raw_csv", "Process returned without CSV", 0)
                    else:
                        with (dest / "raw_times.csv").open(
                                newline="", encoding="utf-8") as stream:
                            records = list(csv.DictReader(stream))
                        status, reason, measured = (
                            "completed_with_csv", "", sum(
                                r["status"] == "ok" for r in records))
                except subprocess.TimeoutExpired as exc:
                    elapsed_method = perf_counter() - t0
                    status, reason, measured = (
                        "method_timeout_no_credible_time",
                        f"timeout_seconds={exc.timeout}", 0)
                except (OSError, ValueError) as exc:
                    elapsed_method = perf_counter() - t0
                    status, reason, measured = (
                        "process_error",
                        f"{type(exc).__name__}: {str(exc)[:200]}", 0)
            outcomes.append({
                "case_id": identifier, "configuration": c,
                "method": method, "status": status,
                "folder": str(folder) if status == "completed_with_csv" else "",
                "elapsed_s": elapsed_method, "reason": reason})
            (output / "outcomes.json").write_text(
                json.dumps(outcomes, indent=2) + "\n", encoding="utf-8")
            print(f"[{i+1}/{len(work)}] {identifier} {method}: {status} "
                  f"({elapsed_method:.2f}s)", flush=True)
        ledger.append({
            "case_id": identifier, **c, "method": method,
            "status": status, "reason": reason, "elapsed_s": elapsed_method,
            "measured_rows": measured,
            "run_id": os.environ.get("GITHUB_RUN_ID", ""),
            "source_sha": sha,
        })
        archive_ledger(output / "method_attempts.csv", ledger)
    statuses = Counter(r["status"] for r in ledger)
    parity = aggregate(output, outcomes)
    summary = {
        "attempt_counts": dict(statuses),
        "planned_attempts_in_shard": len(all_work),
        "start_attempt": start_attempt,
        "next_attempt_offset": start_attempt + sum(
            r["status"] != "not_executed_budget" for r in ledger),
        "actual_attempted": sum(
            r["status"] != "not_executed_budget" for r in ledger),
        "completed_method_slices": statuses["completed_with_csv"],
        "successful_raw_timing_rows": sum(
            r["measured_rows"] for r in ledger),
        "planned_manifest_statuses": counts,
        "elapsed_s": perf_counter() - started,
        "note": ("Every timing is in slices/*/*/raw_times.csv with status=ok; "
                 "method_attempts.csv elapsed_s is subprocess wall-clock, "
                 "not a complete criterion observation; method timeouts have "
                 "no valid benchmark time; parity comparison is not a "
                 "high-precision accuracy certification."),
        **parity}
    (output / "batch_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preset",
                        choices=("smoke", "pilot", "frontier", "comprehensive"),
                        default="smoke")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--max-seconds", type=float, default=900.)
    parser.add_argument("--per-method-seconds", type=float, default=50.)
    parser.add_argument("--max-method-attempts", type=int, default=40)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--series-count", type=int, default=2)
    parser.add_argument("--max-work", type=float, default=3e7)
    parser.add_argument("--max-dense-bytes", type=int,
                        default=2 * 1024**3)
    parser.add_argument("--seed", type=int, default=20261102)
    parser.add_argument("--start-attempt", type=int, default=0)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--no-time-limit", action="store_true",
                        help="Disable method and batch runtime cutoffs, including estimated runtime gates; preserve memory guard")
    parser.add_argument("--manifest-scope", choices=("full", "shard"),
                        default="full")
    a = parser.parse_args()
    result = execute(a.output, preset=a.preset,
                     shard_index=a.shard_index,
                     shard_count=a.shard_count,
                     max_seconds=a.max_seconds,
                     per_method_seconds=a.per_method_seconds,
                     max_method_attempts=a.max_method_attempts,
                     repeats=a.repeats, series_count=a.series_count,
                     max_work=a.max_work,
                     max_dense_bytes=a.max_dense_bytes, seed=a.seed,
                     start_attempt=a.start_attempt,
                     plan_only=a.plan_only,
                     manifest_scope=a.manifest_scope,
                     no_time_limit=a.no_time_limit)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
