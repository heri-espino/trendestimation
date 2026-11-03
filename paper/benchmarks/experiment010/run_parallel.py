"""Parallel, uncapped, source-archived Experiment010 on a Windows VM.

Each independent method/case pair runs in its own child Python process.
Numerical BLAS threads are pinned to 1 by the parent launcher.
The main thread alone checkpoints the manifest/ledger and collects results.
No per-method/whole-run wall-clock timeout or estimated-work exclusion.
Physical dense-memory preflight, solver numerical failures, and errors remain.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import run_batches as B


def run_one(item, output, *, repeats, series_count, max_dense_bytes, seed):
    """Worker owns only its unique method directory and streaming log."""
    identifier, cfg, method = item
    folder = Path("slices") / identifier / method
    dest = output / folder
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(B.EXP006 / "run.py"),
        "--preset", "slice", "--n", str(cfg["n"]),
        "--d", str(cfg["d"]), "--mu", cfg["mu"],
        "--amplitude", cfg["amplitude"],
        "--criterion", cfg["criterion"],
        "--grid-denominator", str(cfg["denominator"]),
        "--methods", method, "--threads", "1",
        "--repeats", str(repeats),
        "--series-count", str(series_count),
        "--max-work", "inf",
        "--max-dense-bytes", str(max_dense_bytes),
        "--seed", str(seed),
        "--conditional-data-mu",
        "--allow-unbounded-runtime",
        "--output", str(dest),
    ]
    started = perf_counter()
    log = dest.parent / (method + ".log")
    try:
        with log.open("w", encoding="utf-8") as stream:
            stream.write("started_utc=" +
                         datetime.now(timezone.utc).isoformat() + "\n")
            stream.write("process_parallel=True; runtime_timeout=None\n")
            stream.flush()
            # Nothing accumulates in the parent process; subprocesses each
            # produce their own independent partial raw_times.csv checkpoint.
            proc = subprocess.run(cmd, stdout=stream,
                                  stderr=subprocess.STDOUT,
                                  check=False, cwd=B.ROOT)
        elapsed = perf_counter() - started
        if proc.returncode:
            status, reason, measured = (
                "execution_failed", "exit_code=" + str(proc.returncode), 0)
        elif not (dest / "raw_times.csv").is_file():
            status, reason, measured = (
                "missing_raw_csv", "Process returned without raw CSV", 0)
        else:
            with (dest / "raw_times.csv").open(
                    newline="", encoding="utf-8") as stream:
                raw = list(csv.DictReader(stream))
            status = "completed_with_csv"
            reason = ""
            measured = sum(r["status"] == "ok" for r in raw)
    except Exception as exc:
        elapsed = perf_counter() - started
        status, reason, measured = (
            "process_error", type(exc).__name__ + ": " + str(exc)[:250], 0)
        with log.open("a", encoding="utf-8") as stream:
            stream.write("process_exception=" + reason + "\n")
    return dict(case_id=identifier, configuration=cfg, method=method,
                status=status, folder=str(folder) if
                status == "completed_with_csv" else "",
                elapsed_s=elapsed, reason=reason,
                measured_rows=measured)


def execute_parallel(output, *, shard_index=0, shard_count=16,
                     start_attempt=0, max_method_attempts=10,
                     workers=8, max_dense_bytes=2 * 1024**3,
                     total_parallel_dense_bytes=16 * 1024**3,
                     repeats=2, series_count=2, seed=20261102):
    if output.exists():
        raise FileExistsError("Refusing to overwrite existing output: " +
                              str(output))
    if not (1 <= workers <= 32):
        raise ValueError("workers must be in [1,32]")
    if not (1 <= max_method_attempts <= 1000):
        raise ValueError("max_method_attempts must be in [1,1000]")
    if repeats < 1 or series_count < 2 or max_dense_bytes < 1:
        raise ValueError("Invalid repeat, series or memory budget")
    if total_parallel_dense_bytes < max_dense_bytes * workers:
        raise ValueError(
            "Parallel dense-memory reservation exceeded: workers*"
            "max_dense_bytes must not exceed total_parallel_dense_bytes.")
    all_work = B.attempts("comprehensive", shard_index, shard_count)
    if not 0 <= start_attempt <= len(all_work):
        raise ValueError("Invalid start_attempt for selected shard")
    work = all_work[start_attempt:
                    start_attempt + max_method_attempts]
    if not work:
        raise ValueError("No method-case attempts remain in this shard")
    started = perf_counter()
    output.mkdir(parents=True)
    sha = B.source_sha()
    meta = dict(
        created_utc=datetime.now(timezone.utc).isoformat(),
        source_sha=sha, host=platform.platform(), python=sys.version,
        runner_name=os.environ.get("RUNNER_NAME"),
        mode="parallel_uncapped", workers=workers, blas_threads_per_worker=1,
        max_seconds=None, per_method_seconds=None,
        max_work="unbounded", max_dense_bytes=max_dense_bytes,
        total_parallel_dense_bytes=total_parallel_dense_bytes,
        repeats=repeats, series_count=series_count, seed=seed,
        shard_index=shard_index, shard_count=shard_count,
        start_attempt=start_attempt,
        max_method_attempts=max_method_attempts,
        planned_attempts_in_shard=len(all_work),
        numerical_accuracy_note="Selected-score parity is not independent "
                                "high-precision forward-error certification.",
        timing_note="Parallel-process throughput timings run under CPU "
                    "contention and must not be pooled as standalone serial "
                    "benchmark latencies.",
    )
    (output / "run_metadata.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    masks = B.manifest(
        output / "full_factorial_plan.csv.gz",
        max_work=math.inf, repeats=repeats, series_count=series_count,
        max_dense_bytes=max_dense_bytes,
        shard_index=shard_index, shard_count=shard_count,
        preset="comprehensive", scope="shard",
        allow_unbounded_runtime=True)
    results = {}
    futures = {}
    for offset, item in enumerate(work):
        identifier, cfg, method = item
        reasons = [
            B.memory_budget_status(
                cfg["n"], cfg["d"], method, cfg["denominator"],
                max_dense_bytes, math.inf, scenario,
                1 if "one_series" in scenario else series_count,
                repeats, allow_unbounded_runtime=True)
            for scenario in B.SCENARIOS
        ]
        if "eligible" not in reasons:
            results[offset] = dict(
                case_id=identifier, configuration=cfg, method=method,
                status="resource_ineligible_all_workloads",
                folder="", elapsed_s=0.0,
                reason=";".join(sorted(set(reasons))),
                measured_rows=0)
    # Initial checkpoint includes pending and excluded attempts. If the
    # controller is interrupted, successful worker CSVs survive on disk.
    ledger_location = None
    def write_ledger():
        nonlocal ledger_location
        records = []
        for position, (identifier, cfg, method) in enumerate(work):
            result = results.get(position)
            records.append(dict(
                case_id=identifier, **cfg, method=method,
                status=(result["status"] if result is not None
                        else "pending_or_running"),
                reason=(result["reason"] if result is not None else ""),
                elapsed_s=(result["elapsed_s"] if result is not None else ""),
                measured_rows=(result["measured_rows"] if result is not None
                               else ""),
                run_id=os.environ.get("GITHUB_RUN_ID", ""),
                source_sha=sha))
        ledger_location = B.archive_ledger(
            output / "method_attempts.csv", records)
        return records
    write_ledger()
    runnable = [(position, item) for position, item in enumerate(work)
                if position not in results]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for pos, item in runnable:
            future = executor.submit(
                run_one, item, output, repeats=repeats,
                series_count=series_count,
                max_dense_bytes=max_dense_bytes, seed=seed)
            futures[future] = pos
        print("Parallel tasks:", len(runnable),
              "workers:", workers, flush=True)
        for future in as_completed(futures):
            pos = futures[future]
            result = future.result()
            results[pos] = result
            write_ledger()
            print("[{}/{}] {}: {} ({:.2f}s)".format(
                len(results), len(work), result["method"],
                result["status"], result["elapsed_s"]), flush=True)
    ledger = write_ledger()
    outcomes = [results[pos] for pos in range(len(work))]
    (output / "outcomes.json").write_text(
        json.dumps(outcomes, indent=2) + "\n", encoding="utf-8")
    parity = B.aggregate(output, outcomes)
    statuses = Counter(o["status"] for o in outcomes)
    summary = dict(
        attempt_counts=dict(statuses),
        planned_attempts_in_shard=len(all_work),
        start_attempt=start_attempt,
        next_attempt_offset=start_attempt + len(work),
        actual_attempted=len(work),
        completed_method_slices=statuses["completed_with_csv"],
        successful_raw_timing_rows=sum(o["measured_rows"] for o in outcomes),
        planned_manifest_statuses=masks,
        elapsed_s=perf_counter() - started,
        parallel_workers=workers,
        ledger_checkpoint_file=(str(ledger_location.relative_to(output))
                                if ledger_location is not None else None),
        note=("No solver wall-clock timeouts, full per-worker logs, "
              "durable row-level numerical checkpoint; parallel contention "
              "changes timing interpretation; parity is not proof."),
        **parity)
    (output / "batch_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--shard-index", type=int, default=0)
    p.add_argument("--shard-count", type=int, default=16)
    p.add_argument("--start-attempt", type=int, default=0)
    p.add_argument("--max-method-attempts", type=int, default=10)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--max-dense-bytes", type=int, default=2 * 1024**3)
    p.add_argument("--total-parallel-dense-bytes", type=int,
                   default=16 * 1024**3)
    p.add_argument("--repeats", type=int, default=2)
    p.add_argument("--series-count", type=int, default=2)
    p.add_argument("--seed", type=int, default=20261102)
    a = p.parse_args()
    summary = execute_parallel(
        a.output, shard_index=a.shard_index,
        shard_count=a.shard_count,
        start_attempt=a.start_attempt,
        max_method_attempts=a.max_method_attempts,
        workers=a.workers,
        max_dense_bytes=a.max_dense_bytes,
        total_parallel_dense_bytes=a.total_parallel_dense_bytes,
        repeats=a.repeats, series_count=a.series_count, seed=a.seed)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
