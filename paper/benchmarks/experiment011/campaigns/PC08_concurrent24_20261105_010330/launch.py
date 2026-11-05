import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

tag = sys.argv[1]
root = Path.cwd()
base = root / "paper/benchmarks/experiment011"
archive = base / "campaigns" / tag
design_path = base / "cases.json"
design = json.loads(design_path.read_text(encoding="utf-8"))
jobs = [
    (case["id"], block)
    for case in design["cases"]
    for block in range(case["planned_blocks"])
]

env = os.environ.copy()
for key in (
    "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "OMP_NUM_THREADS", "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    env[key] = "1"

metadata = {
    "run_tag": tag,
    "mode": "concurrent_case_blocks",
    "max_workers": 24,
    "blas_threads_per_job": 1,
    "case_count": len(design["cases"]),
    "planned_job_count": len(jobs),
    "source_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip(),
    "cases_sha256": hashlib.sha256(
        design_path.read_bytes()
    ).hexdigest(),
    "python": sys.executable,
    "warning": (
        "Contended timings: up to 24 case-block processes share the host. "
        "Do not pool with isolated-latency measurements."
    ),
    "jobs": [],
}
manifest = archive / "campaign.json"

def save():
    temporary = archive / "campaign.tmp"
    temporary.write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    temporary.replace(manifest)

def execute(job):
    case, block = job
    command = [
        sys.executable, str(base / "campaign.py"), "run",
        "--case", case,
        "--run-tag", tag,
        "--block", str(block),
        "--allow-confirm",
    ]
    log = archive / f"{case}_block{block:03d}.log"
    started = time.perf_counter()
    try:
        with log.open("w", encoding="utf-8") as handle:
            result = subprocess.run(
                command, cwd=root, env=env,
                stdout=handle, stderr=subprocess.STDOUT,
                check=False,
            )
        return {
            "case": case, "block": block,
            "returncode": result.returncode,
            "wall_s": time.perf_counter() - started,
            "log": log.name,
        }
    except Exception as error:
        return {
            "case": case, "block": block,
            "returncode": -1, "error": repr(error),
            "log": log.name,
        }

save()
print(
    f"Starting {len(jobs)} jobs from {len(design['cases'])} cases; "
    "maximum 24 concurrent processes.",
    flush=True,
)

with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
    futures = [pool.submit(execute, job) for job in jobs]
    for number, future in enumerate(
        concurrent.futures.as_completed(futures), 1
    ):
        result = future.result()
        metadata["jobs"].append(result)
        save()
        print(
            f"[{number}/{len(jobs)}] {result['case']} "
            f"block={result['block']} exit={result['returncode']}",
            flush=True,
        )

failed = sum(item["returncode"] != 0 for item in metadata["jobs"])
metadata["failed_jobs"] = failed
metadata["status"] = (
    "completed_pending_numerical_review"
    if failed == 0 else "completed_with_failed_jobs"
)
save()
print(f"Finished. Failed jobs: {failed}. Review all per-case QA files.")
sys.exit(1 if failed else 0)
