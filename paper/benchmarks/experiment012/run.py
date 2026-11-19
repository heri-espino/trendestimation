"""Experiment012: genuine incremental complete-criterion timings for three backends.

Each seed defines one independent observation series. For each backend, prepare
the full solver once and evaluate the SAME strictly positive penalty grid.
Measure total initialization and cumulative criterion work at 1/10/100/1000
candidates, without treating setup-excluded accounting as a separate warm run.

Plan only by default; --execute on the PC08 Windows runner to measure.
Completed Experiment011 records are never rewritten or rerun.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ENGINE_PATH = ROOT / "paper" / "benchmarks" / "experiment006" / "run.py"
METHODS = ("naive_inverse", "banded_cholesky", "spectral_svd")
CHECKPOINTS = (1, 10, 100, 1000)
FIELDS = (
    "seed_index", "seed", "n", "d", "criterion", "method",
    "checkpoint", "attempted", "completed", "status",
    "setup_s", "evaluation_s", "total_cold_s", "first_evaluation_s",
    "selected_lambda", "selected_score", "last_score", "error",
)
BASE_SEED = 1_500_000_000


def seed_for(index: int, n: int, d: int) -> int:
    """Distinct, predeclared seeds (not the legacy 97-seed streams)."""
    return BASE_SEED + index * 100_003 + 29 * n + 7 * d


def lambda_grid(count: int):
    """Nested log-uniform low-discrepancy penalties, shared by all methods.

    The first candidate is lambda=1. Subsequent prefixes spread over the
    entire range, unlike sorted geomspace whose first 100 of 1000 values
    occupy only its extreme lower tail. Every prefix is identical across
    runs having different final checkpoint counts.
    """
    import numpy as np
    if count < 1:
        raise ValueError("Candidate count must be positive")

    def radical_inverse(k: int) -> float:
        value, factor = 0.0, 0.5
        while k:
            value += factor * (k & 1)
            k >>= 1
            factor *= 0.5
        return value

    positions = np.array([radical_inverse(i) for i in range(1, count + 1)])
    return np.exp(np.log(1e-3) + positions * np.log(1e6))


def plan(n: int, d: int, criterion: str, seeds: int, checkpoints) -> dict:
    if not 16 <= n <= 256 or d not in (1, 2, 3, 4) or d >= n:
        raise ValueError("This bounded study supports 16<=n<=256, 1<=d<=4")
    if criterion not in ("cv", "gcv"):
        raise ValueError("Only full CV/GCV criteria are predeclared")
    if not 1 <= seeds <= 100:
        raise ValueError("Seed count must be between 1 and 100")
    values = tuple(sorted(set(int(x) for x in checkpoints)))
    if not values or values[0] != 1 or values[-1] > 1000 or any(x < 1 for x in values):
        raise ValueError("Checkpoints must begin at one and not exceed 1000")
    # Conservative work guard: explicit inversions scale cubically per lambda.
    # 100 seeds x 1000 dense inversions at n>=128 are not an acceptable default.
    if n > 128 and values[-1] > 10:
        raise ValueError("For n>128 limit to 1,10; use a separate reviewed budget")
    if n > 64 and values[-1] > 100:
        raise ValueError("For n>64 limit to 1,10,100; use a separate reviewed budget")
    return {
        "experiment": "experiment012",
        "kind": "controlled_incremental_complete_criterion_timing",
        "n": n, "d": d, "criterion": criterion,
        "seeds": seeds, "checkpoints": list(values),
        "methods": list(METHODS),
        "mu": 0.0, "amplitude": "low",
        "coordinate": "direct_lambda",
        "penalty_min": 1e-3, "penalty_max": 1e3,
        "blas_threads": 1,
        "series_per_seed": 1,
        "note": "Different lambda candidates, not repeated inverse of an unchanged matrix. "
                "No penalty-coordinate inversion and no shared cross-method setup.",
    }


def run_seed(engine, config: dict, index: int, lambdas, writer) -> list[dict]:
    """Run one seed without duplicating its draws; all methods see identical y."""
    seed = seed_for(index, config["n"], config["d"])
    y = engine.sample(config["n"], seed, config["amplitude"])
    rows = []
    methods = METHODS[index % len(METHODS):] + METHODS[:index % len(METHODS)]
    for method in methods:
        start = perf_counter()
        try:
            evaluator = engine.Evaluator(config["n"], config["d"], method)
            coord = evaluator.prepare_series(y, 0.0)
        except Exception as exc:
            setup_s = perf_counter() - start
            for checkpoint in config["checkpoints"]:
                row = {
                    "seed_index": index, "seed": seed,
                    "n": config["n"], "d": config["d"],
                    "criterion": config["criterion"], "method": method,
                    "checkpoint": checkpoint, "attempted": 0, "completed": 0,
                    "status": "setup_failed", "setup_s": setup_s,
                    "evaluation_s": 0.0, "total_cold_s": setup_s,
                    "first_evaluation_s": "", "selected_lambda": "",
                    "selected_score": "", "last_score": "",
                    "error": f"{type(exc).__name__}: {str(exc)[:160]}",
                }
                writer.writerow(row)
                rows.append(row)
            continue
        setup_s = perf_counter() - start
        elapsed, first, attempted, completed = 0.0, None, 0, 0
        best = (math.inf, None)
        last_score = None
        failure = ""
        for k, lam in enumerate(lambdas, start=1):
            if not failure:
                attempted += 1
                start = perf_counter()
                try:
                    score = float(evaluator.evaluate(
                        y, 0.0, float(lam), config["criterion"],
                        coordinates=coord, reuse_factor=False,
                    ))
                    if not math.isfinite(score):
                        raise ArithmeticError("Non-finite criterion score")
                except Exception as exc:
                    elapsed += perf_counter() - start
                    failure = f"{type(exc).__name__}: {str(exc)[:160]}"
                else:
                    this = perf_counter() - start
                    elapsed += this
                    if first is None:
                        first = this
                    completed += 1
                    last_score = score
                    if score < best[0]:
                        best = (score, float(lam))
            if k not in config["checkpoints"]:
                continue
            status = "ok" if not failure and completed == k else "incomplete"
            row = {
                "seed_index": index, "seed": seed,
                "n": config["n"], "d": config["d"],
                "criterion": config["criterion"], "method": method,
                "checkpoint": k, "attempted": attempted, "completed": completed,
                "status": status, "setup_s": setup_s,
                "evaluation_s": elapsed, "total_cold_s": setup_s + elapsed,
                "first_evaluation_s": first if first is not None else "",
                "selected_lambda": best[1] if best[1] is not None else "",
                "selected_score": best[0] if best[1] is not None else "",
                "last_score": last_score if last_score is not None else "",
                "error": failure,
            }
            writer.writerow(row)
            rows.append(row)
        # No loop repeats a completed candidate simply to collect a checkpoint.
    return rows


def numerical_audit(rows: list[dict]) -> dict:
    """Compare the selected criterion among all three valid complete searches."""
    by = {}
    for row in rows:
        by.setdefault((int(row["seed_index"]), int(row["checkpoint"])), {})[row["method"]] = row
    compared, mismatches, incomplete = 0, [], 0
    for (seed, checkpoint), observed in sorted(by.items()):
        if set(observed) != set(METHODS) or any(
            item["status"] != "ok" for item in observed.values()
        ):
            incomplete += 1
            continue
        ref = observed["naive_inverse"]
        for method in ("banded_cholesky", "spectral_svd"):
            selected = observed[method]
            score_a = float(ref["selected_score"])
            score_b = float(selected["selected_score"])
            lam_a = float(ref["selected_lambda"])
            lam_b = float(selected["selected_lambda"])
            compared += 1
            if not (
                abs(score_a - score_b) <= 1e-6 * max(1.0, abs(score_a))
                and abs(lam_a - lam_b) <= 1e-10 * max(1.0, abs(lam_a))
            ):
                mismatches.append({
                    "seed": seed, "checkpoint": checkpoint, "method": method,
                    "naive_score": score_a, "method_score": score_b,
                    "naive_lambda": lam_a, "method_lambda": lam_b,
                })
    return {
        "comparisons": compared,
        "incomplete_seed_checkpoint_groups": incomplete,
        "mismatches": mismatches,
        "valid_pair_count": compared - len(mismatches),
        "qualification": "Selected-score float64 parity, not full-grid high-precision certification",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=64)
    parser.add_argument("--d", type=int, default=3)
    parser.add_argument("--criterion", default="gcv", choices=("cv", "gcv"))
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--checkpoints", default="1,10,100,1000")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--execute", action="store_true",
                        help="Explicit benchmark opt-in; default only validates and prints plan")
    args = parser.parse_args()
    config = plan(args.n, args.d, args.criterion, args.seeds,
                  args.checkpoints.split(","))
    print(json.dumps(config, indent=2))
    if not args.execute:
        print("PLAN ONLY; no timings measured.")
        return 0
    if args.out is None:
        parser.error("--execute requires an explicit new --out directory")
    if args.out.exists():
        raise FileExistsError("Refuse to overwrite an archived run directory")
    if Path.cwd().resolve() != ROOT:
        raise RuntimeError("Execute from repository root")
    for var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS"):
        os.environ[var] = "1"

    # Import the existing numerical implementation; do not duplicate criteria.
    sys.path.insert(0, str(ENGINE_PATH.parent))
    import run as engine
    import numpy as np
    import scipy
    from threadpoolctl import threadpool_limits

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    config.update({
        "python": sys.version, "numpy": np.__version__,
        "scipy": scipy.__version__, "platform": platform.platform(),
        "machine": platform.node(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "engine_sha256": hashlib.sha256(ENGINE_PATH.read_bytes()).hexdigest(),
        "git_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
            text=True, check=True,
        ).stdout.strip(),
        "status": "in_progress",
    })
    (out / "metadata.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf8")
    lams = lambda_grid(max(config["checkpoints"]))
    all_rows = []
    with (out / "timings.csv").open("w", newline="", encoding="utf8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        with threadpool_limits(limits=1):
            for index in range(config["seeds"]):
                rows = run_seed(engine, config, index, lams, writer)
                all_rows.extend(rows)
                stream.flush()
                print(f"Seed {index + 1}/{config['seeds']}: "
                      f"{sum(r['status']=='ok' for r in rows)} complete cells",
                      flush=True)
    audit = numerical_audit(all_rows)
    (out / "numerical_audit.json").write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8")
    config["status"] = "complete_pending_publication_review"
    config["complete_rows"] = sum(r["status"] == "ok" for r in all_rows)
    config["total_rows"] = len(all_rows)
    config["timings_sha256"] = hashlib.sha256((out / "timings.csv").read_bytes()).hexdigest()
    (out / "metadata.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf8")
    print(f"Saved {len(all_rows)} measurements and {len(audit['mismatches'])} parity alerts")
    # Incomplete/failed numerical comparisons remain explicit and do not
    # enter the valid paired timing analysis.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
