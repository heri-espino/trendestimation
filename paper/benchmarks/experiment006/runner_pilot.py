"""Bounded, reproducible Experiment006 pilot on a designated Windows runner.

This intentionally does NOT launch the entire factorial. It records every
scenario, coordinate, criterion attempt, numerical status and environment
for small n, including d=6 and nonzero mu. Every run uses a unique
GitHub Actions run-ID folder and has an immutable archive branch.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from run import run_slice


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_root
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"Refusing to overwrite results: {root}")
    root.mkdir(parents=True, exist_ok=True)
    tasks = (
        (
            "pilot001_n64_d2_mu0_gcv",
            dict(
                n=64, d=2, mu=0.0, amplitude="low", criterion="gcv",
                denominator=100,
                methods=(
                    "naive_inverse", "spectral_svd", "banded_cholesky",
                    "guarded_svd_cholesky", "sparse_lu_banded_trace",
                ),
                repeats=2, R=2, threads=1, seed=20261102,
                max_work=3e8,
            ),
        ),
        (
            "pilot002_n128_d6_mu015_cv",
            dict(
                n=128, d=6, mu=0.15, amplitude="high", criterion="cv",
                denominator=100,
                methods=(
                    "spectral_svd", "banded_cholesky",
                    "guarded_svd_cholesky", "sparse_lu_banded_trace",
                    "pcg_fft_banded_trace",
                ),
                repeats=2, R=2, threads=1, seed=20261103,
                max_work=3e8,
            ),
        ),
    )
    manifest = {
        "status": "bounded_pilot_only",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_sha": os.environ.get("GITHUB_SHA"),
        "github_ref": os.environ.get("GITHUB_REF"),
        "runner_name": os.environ.get("RUNNER_NAME"),
        "runner_os": os.environ.get("RUNNER_OS"),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "tasks": [{"name": name, **config} for name, config in tasks],
        "notes": [
            "Not the full 7 n x 6 d x 5 criteria factorial",
            "Includes all four workloads and both S/lambda coordinate policies",
            "All numerical failures and resource skips are preserved",
            "No statistical RMSE or global winner is asserted",
            "Timing comparison is restricted to this particular Windows runner",
        ],
    }
    (root / "pilot_manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8"
    )
    report = [
        "# Experiment006 self-hosted Windows paired pilot",
        "",
        f"- Runner: {manifest['runner_name']}",
        f"- Run ID: {manifest['github_run_id']}",
        f"- Source SHA: {manifest['github_sha']}",
        "- Scope: bounded pilot, **not** the complete factorial",
        "",
        "| Slice | Attempt rows | Valid | Other statuses |",
        "| --- | ---: | ---: | --- |",
    ]
    combined = []
    try:
        for name, config in tasks:
            print(f"START {name} on {manifest['runner_name']}", flush=True)
            rows, _summary = run_slice(
                **config, output=root / name,
            )
            counts = Counter(row["status"] for row in rows)
            combined.extend({"slice": name, **row} for row in rows)
            bad = "; ".join(
                f"{k}: {v}" for k, v in sorted(counts.items()) if k != "ok"
            ) or "none"
            report.append(
                f"| {name} | {len(rows)} | {counts['ok']} | {bad} |"
            )
            print(f"COMPLETE {name}: {dict(counts)}", flush=True)
    except BaseException as exc:
        # Preserve a visible error file; GitHub Actions uploads even on failure.
        (root / "fatal_error.txt").write_text(
            f"{type(exc).__name__}: {exc}\n", encoding="utf-8"
        )
        report.append(f"\nFatal error: {type(exc).__name__}: {exc}\n")
        (root / "RESULTS.md").write_text(
            "\n".join(report) + "\n", encoding="utf-8"
        )
        raise

    with (root / "combined_raw_times.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        if combined:
            writer = csv.DictWriter(stream, fieldnames=list(combined[0]))
            writer.writeheader()
            writer.writerows(combined)
    report.extend([
        "",
        "All values above are **measured attempts**, not inferred speedups.",
        "Incomplete or numerically failed rows are not valid timing winners.",
        "For publication, repeat independent blocks with counterbalanced",
        "method order and much broader n,d,mu,criterion coverage.",
        "",
    ])
    (root / "RESULTS.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print("Pilot result root:", root, flush=True)


if __name__ == "__main__":
    main()
