"""Append three new independent seeds; never relabel or rerun the 97 frozen seeds.

The historical, validated campaign contains seed indices 3..99 (97 distinct
realizations per case). This extension adds indices 100..102 using the same
seed-generating sequence, yielding 100 *scheduled* realizations per case
only after all 87 new case-seed jobs are actually recorded and audited.

Dry-run by default. Run on the original Windows host with the exact
reviewed environment, then independently inspect and archive both raw records
and status rows. Mixed worker phases must be reported, not pooled as
contention-free timings.

python paper/benchmarks/experiment011/complete_100_seeds.py --run-tag x100a
python paper/benchmarks/experiment011/complete_100_seeds.py --run-tag x100a --execute --large-svd
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import sys

import additional_seeds
import campaign


def extension_jobs(design: dict) -> list[tuple]:
    """Return precisely the three missing indices after the 97 archived seeds."""
    return [
        (i, 1_000_000_000 + 1_000_000 * i, case,
         i % case["planned_blocks"])
        for i in range(97, 100)
        for case in design["cases"]
    ]


def validate_jobs(design: dict, jobs: list[tuple]) -> None:
    expected = {(i + 3, case["id"]) for i in range(97, 100)
                for case in design["cases"]}
    observed = {(i + 3, case["id"]) for i, _seed, case, _block in jobs}
    if len(jobs) != 3 * len(design["cases"]) or observed != expected:
        raise AssertionError("100-seed extension must contain exactly 3 new jobs per case")
    if observed & {(i, case["id"]) for i in range(3, 100)
                   for case in design["cases"]}:
        raise AssertionError("Historical seed indices cannot be repeated")


def inventory_files(root: Path) -> list[dict]:
    """Hash files present in this new archive; never traverse previous runs."""
    results = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in ("report.json", "report.tmp", "file_inventory.json"):
            results.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-tag", required=True)
    parser.add_argument("--execute", action="store_true",
                        help="Explicit opt-in; the default only prints the plan")
    parser.add_argument("--large-svd", action="store_true",
                        help="Retain historical large-n spectral comparison")
    parser.add_argument("--workers", type=int, default=1,
                        help="Maximum concurrent jobs for n<1024 (1..24)")
    args = parser.parse_args()
    if not campaign.VALID_TAGS.fullmatch(args.run_tag):
        parser.error("Run tag does not match the existing Experiment011 naming policy")
    if not 1 <= args.workers <= 24:
        parser.error("--workers must be between 1 and 24")
    design = campaign.load_design()
    work = extension_jobs(design)
    validate_jobs(design, work)
    print(f"New jobs: {len(work)} = 29 cases x 3 seeds (s100, s101, s102)")
    print(f"Total after verified integration: {len(design['cases'])} x 100 = 2900 jobs")
    print("Historical indices s003..s099 are never submitted again.")
    if not args.execute:
        print("PLAN ONLY; no measurements have been performed.")
        return 0
    if Path.cwd().resolve() != campaign.ROOT.resolve():
        raise RuntimeError("Execute from the repository root")
    archive = campaign.HERE / "campaigns" / args.run_tag
    archive.mkdir(parents=True, exist_ok=False)
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[key] = "1"
    report = {
        "experiment": "experiment011",
        "kind": "non_overwriting_three_seed_extension",
        "historical_indices": [3, 99],
        "new_indices": [100, 102],
        "historical_scheduled_jobs": 2813,
        "new_scheduled_jobs": len(work),
        "proposed_total_jobs": 2813 + len(work),
        "source_commit": campaign.git_sha(),
        "design_sha256": campaign.sha256_file(campaign.CASE_FILE),
        "parent_runner_sha256": campaign.sha256_file(campaign.SOURCE),
        "large_svd": args.large_svd,
        "blas_threads": 1,
        "results": [],
        "status": "in_progress",
    }

    def save() -> None:
        tmp = archive / "report.tmp"
        tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf8")
        tmp.replace(archive / "report.json")

    save()
    # Limit dense SVD and large-n jobs to one concurrent worker.
    phases = ([(args.workers, [j for j in work if j[2]["n"] < 1024]),
               (1, [j for j in work if j[2]["n"] >= 1024])]
              if args.large_svd else [(args.workers, work)])
    for workers, phase in phases:
        report.setdefault("phases", []).append({
            "max_concurrent_jobs": workers, "jobs": len(phase)
        })
        save()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(additional_seeds.execute, job, args.run_tag,
                                   archive, args.large_svd) for job in phase]
            for future in as_completed(futures):
                row = future.result()
                row["phase_workers"] = workers
                report["results"].append(row)
                save()
                print(f"Recorded s{row['seed_index']:03d}, {row['case']}, "
                      f"exit={row['returncode']}", flush=True)
    report["status"] = "complete_pending_independent_audit"
    report["counts"] = dict(Counter(row["returncode"] for row in report["results"]))
    save()
    (archive / "file_inventory.json").write_text(
        json.dumps(inventory_files(archive), indent=2) + "\n",
        encoding="utf8"
    )
    print("A new raw-results archive is required before claiming 100 observed seeds.")
    return int(any(row["returncode"] != 0 for row in report["results"]))


if __name__ == "__main__":
    sys.exit(main())
