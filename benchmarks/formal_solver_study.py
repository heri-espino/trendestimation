"""Blocked, reproducible solver timing study with raw per-trial observations.

Usage (from repository root, after pip install -e . threadpoolctl):
  python benchmarks/formal_solver_study.py --preset smoke --seeds 3 --repeats 2 --output-dir build/solver-study
  python benchmarks/formal_solver_study.py --preset quick --seeds 20 --repeats 5 --threads 1 --output-dir build/solver-study

Study design:
- Independent data seeds are the unit for subsequent statistical inference.
- For each seed and repetition, all three methods receive identical data
  and candidate penalties; their evaluation order is freshly randomized.
- Trial measurements record setup, batched reconstructed trends, end-to-end
  setup+batch, and amortized prepared single-fit time, all in nanoseconds.
- Preparation and correctness checks are outside the timed trials.
- Never treat the individual lambda evaluations as independent samples.
- The existing TrendSmoother score-selection backend is NOT benchmarked:
  full trend reconstruction and scalar CV/GCV/EDF are different workloads.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

import numpy as np
import scipy
from threadpoolctl import threadpool_info, threadpool_limits

from trendestimation.solvers import PreparedPLSSolver
from compare_solver_backends import METHODS, cases_for

FIELDS = (
    "case_id", "n", "order", "evaluations", "mu", "seed_index", "data_seed",
    "block", "method", "position", "setup_ns", "batch_ns",
    "end_to_end_ns", "single_amortized_ns", "stored_bytes",
)
CORRECTNESS_FIELDS = (
    "case_id", "n", "order", "evaluations", "mu",
    "seed_index", "method", "max_abs_error_vs_svd", "relative_max_error",
)


def git_revision() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL,
            text=True, timeout=3,
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def data_for(n: int, order: int, case_id: int, data_seed: int) -> np.ndarray:
    """Independent synthetic observation realization at a fixed workload."""
    rng = np.random.default_rng(
        np.random.SeedSequence([data_seed, case_id, n, order])
    )
    t = np.linspace(0.0, 1.0, n)
    return (np.sin(7 * t) + 0.3 * t + rng.normal(0.0, 0.1, n))


def verify_case(
    y: np.ndarray, n: int, d: int, lambdas: np.ndarray,
    mu: float, case_id: int, seed_index: int,
) -> list[dict]:
    """Verify the numerical output before timing any block."""
    baseline = PreparedPLSSolver(n, d, method="svd").fit_many(
        y, lambdas, mu=mu,
    )
    scale = max(1.0, float(np.max(np.abs(baseline))))
    tolerance = 1e-6 + 1e-7 * scale
    results = []
    for method in METHODS:
        actual = PreparedPLSSolver(n, d, method=method).fit_many(
            y, lambdas, mu=mu,
        )
        error = float(np.max(np.abs(actual - baseline)))
        relative = error / scale
        if not np.isfinite(error) or error > tolerance:
            raise AssertionError(
                f"Unacceptable numerical disagreement: case={case_id},"
                f"seed={seed_index}, method={method}, error={error},"
                f"tolerance={tolerance}"
            )
        results.append({
            "case_id": case_id, "n": n, "order": d,
            "evaluations": len(lambdas), "mu": mu,
            "seed_index": seed_index, "method": method,
            "max_abs_error_vs_svd": error, "relative_max_error": relative,
        })
    return results


def measure_block(
    y: np.ndarray, n: int, d: int, lambdas: np.ndarray, mu: float,
    *, seed_index: int, data_seed: int, case_id: int,
    block: int, single_calls: int, random_seed: int,
) -> list[dict]:
    """Randomized-order matched trial with no I/O inside timed regions."""
    rng = np.random.default_rng(
        np.random.SeedSequence([random_seed, case_id, seed_index, block])
    )
    permutation = [str(x) for x in rng.permutation(METHODS)]
    observations = []
    for position, method in enumerate(permutation):
        start = perf_counter_ns()
        fitter = PreparedPLSSolver(n, d, method=method)
        after_setup = perf_counter_ns()
        batch = fitter.fit_many(y, lambdas, mu=mu)
        after_batch = perf_counter_ns()
        # This is a distinct secondary workload, averaged over calls.
        for _ in range(single_calls):
            fitted = fitter.fit(y, lambda_=float(lambdas[0]), mu=mu)
        after_singles = perf_counter_ns()
        # Materialize all returned results (no lazy evaluation).
        if batch.shape != (len(lambdas), n) or fitted.shape != (n,):
            raise AssertionError("Incorrect output shape in timing block")
        setup = after_setup - start
        full_batch = after_batch - after_setup
        observations.append({
            "case_id": case_id, "n": n, "order": d,
            "evaluations": len(lambdas), "mu": mu,
            "seed_index": seed_index, "data_seed": data_seed,
            "block": block, "method": method, "position": position,
            "setup_ns": setup, "batch_ns": full_batch,
            "end_to_end_ns": after_batch - start,
            "single_amortized_ns": (after_singles - after_batch) / single_calls,
            "stored_bytes": fitter.stored_bytes,
        })
    return observations


def save_csv(path: Path, rows: list[dict], fields: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("smoke", "quick", "full"), default="smoke")
    parser.add_argument("--seeds", type=int, default=12,
                        help="Independent synthetic data replicates, not timing rounds.")
    parser.add_argument("--repeats", type=int, default=4,
                        help="Paired randomized timing blocks for each data seed.")
    parser.add_argument("--single-calls", type=int, default=20,
                        help="Repeated prepared single fits per timed method; amortized.")
    parser.add_argument("--master-seed", type=int, default=20261025)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if min(args.seeds, args.repeats, args.single_calls, args.threads) < 1:
        parser.error("seeds, repeats, single-calls and threads must all be positive")
    if args.master_seed < 0:
        parser.error("master-seed must be nonnegative")

    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    workload_cases = cases_for(args.preset)
    raw, accuracy = [], []
    with threadpool_limits(limits=args.threads):
        # Keep numerical kernels warm, outside all measured trials.
        for case_id, (n, d, m, mu) in enumerate(workload_cases):
            lambdas = np.geomspace(1e-4, 1e4, m)
            for seed_index in range(args.seeds):
                data_seed = args.master_seed + seed_index
                y = data_for(n, d, case_id, data_seed)
                accuracy.extend(verify_case(
                    y, n, d, lambdas, mu, case_id, seed_index,
                ))
                for method in METHODS:
                    PreparedPLSSolver(n, d, method=method).fit_many(
                        y, lambdas, mu=mu,
                    )
                for block in range(args.repeats):
                    raw.extend(measure_block(
                        y, n, d, lambdas, mu,
                        case_id=case_id, seed_index=seed_index,
                        data_seed=data_seed, block=block,
                        single_calls=args.single_calls,
                        random_seed=args.master_seed,
                    ))
        blas = threadpool_info()

    save_csv(output / "raw_measurements.csv", raw, FIELDS)
    save_csv(output / "numerical_accuracy.csv", accuracy, CORRECTNESS_FIELDS)
    metadata = {
        "protocol_version": "paired_solver_study_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_revision": git_revision(),
        "preset": args.preset, "master_seed": args.master_seed,
        "independent_seeds": args.seeds, "timing_blocks_per_seed": args.repeats,
        "single_calls_per_timing": args.single_calls,
        "methods": list(METHODS),
        "workload_cases": [
            {"case_id": i, "n": n, "order": d, "evaluations": m, "mu": mu}
            for i, (n, d, m, mu) in enumerate(workload_cases)
        ],
        "timing_unit": "nanoseconds", "primary_metric": "end_to_end_ns",
        "inferential_unit": "independent_data_seed_median_across_timing_blocks",
        "randomized_order": True, "verification_before_timing": True,
        "environment": {
            "python": sys.version.split()[0], "numpy": np.__version__,
            "scipy": scipy.__version__, "platform": platform.platform(),
            "processor": platform.processor(), "logical_cpu_count": os.cpu_count(),
            "blas_threads_requested": args.threads, "threadpools": blas,
        },
        "limitations": (
            "Single host/session: comparisons characterize these workloads and "
            "this machine, not universal performance. Multiple blocks on the "
            "same seed and hardware are repeated technical measurements, not "
            "independent experimental observations. Timing noise can be serially "
            "correlated; reproducibility on additional sessions and machines "
            "is required before publication-level general claims."
        ),
    }
    (output / "study_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8",
    )
    print(f"Saved {len(raw)} per-method timing rows and "
          f"{len(accuracy)} numerical comparisons to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
