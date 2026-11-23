"""Experiment013: guarded, resumable full factorial of complete PLS criteria.

The full requested lattice is represented as a coverage plan, *including*
computationally excluded cells. Execution measures only a prespecified,
budget-feasible subset; other cells retain explicit nonmeasured statuses.
Each method's first/cumulative costs are recorded at nested candidate prefixes.
Original Experiment011 and Experiment012 outputs are never read or overwritten.

Run from the repository root:
    python paper/benchmarks/experiment013/run.py --phase small
    python paper/benchmarks/experiment013/run.py --phase small --seeds 100 \
        --out paper/benchmarks/experiment013/runs/PC08_small001 --execute
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
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
ENGINE = ROOT / "paper/benchmarks/experiment006/run.py"
GRID_SOURCE = ROOT / "paper/benchmarks/experiment012/run.py"
NS = (32, 64, 128, 256, 512, 1024, 2048)
DS = (1, 2, 3)
CRITERIA = ("cv", "gcv", "mle", "aicc", "bic")
METHODS = ("naive_inverse", "banded_cholesky", "spectral_svd")
COUNTS = (1, 10, 100, 1000, 10000)
PHASES = {"small": (32, 64), "medium": (128, 256, 512),
          "large": (1024, 2048), "all": NS}
FIELDS = (
    "experiment", "run_id", "source_commit", "n", "d", "criterion",
    "mu_policy", "amplitude", "R", "coordinate", "seed_index", "seed",
    "method", "M", "status", "requested", "completed",
    "finite_scores", "undefined_scores", "method_setup_s", "first_evaluation_s", "cumulative_evaluation_s",
    "total_cold_s", "selected_lambda", "selected_score", "error",
)
PLAN_FIELDS = ("n", "d", "criterion", "method", "M", "eligibility", "work_units",
               "memory_bytes")


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout.strip()


def seed_for(index: int, n: int, d: int) -> int:
    """Use Experiment012's independent seed scheme; criteria share the same y."""
    return 1_500_000_000 + index * 100_003 + 29 * n + 7 * d


def candidates(count: int):
    """Same nested penalty sequence as Experiment012, no S-inversion overhead."""
    import numpy as np

    def van_der_corput(k: int) -> float:
        value, power = 0.0, 0.5
        while k:
            value += (k & 1) * power
            k >>= 1
            power *= 0.5
        return value

    positions = np.fromiter((van_der_corput(i) for i in range(1, count + 1)),
                            dtype=float, count=count)
    return np.exp(math.log(1e-3) + positions * math.log(1e6))


def resource_status(n: int, d: int, criterion: str, method: str, m: int,
                    *, max_work: int, dense_limit_n: int,
                    max_dense_bytes: int) -> tuple[str, int, int]:
    """Published operation-count *policy* (not runtime or observed memory).

    Penalize naive O(n^3 M), scalar-band O(n(d+1)^2 M), and
    spectral-CV O(n^2 M); spectral scalar scoring uses O(n M).
    Dense SVD's O(n^3) setup is limited separately by dense_limit_n.
    """
    if n not in NS or d not in DS or criterion not in CRITERIA or method not in METHODS:
        raise ValueError("Unsupported design axis")
    if m not in COUNTS:
        raise ValueError("Unsupported candidate prefix")
    if method == "naive_inverse":
        memory = 7 * 8 * n * n
        units = n**3 * m
    elif method == "spectral_svd":
        memory = 5 * 8 * n * n
        units = n**2 * m if criterion == "cv" else n * m
    else:
        memory = 16 * n * (d + 1)
        units = n * (d + 1) ** 2 * m
    if memory > max_dense_bytes:
        return "skipped_dense_memory", units, memory
    if method == "spectral_svd" and n > dense_limit_n:
        return "skipped_svd_setup_policy", units, memory
    if method == "naive_inverse" and n > 256:
        return "skipped_naive_runtime_policy", units, memory
    if units > max_work:
        return "skipped_work_budget", units, memory
    return "eligible", units, memory


def configuration(args) -> dict:
    if not 1 <= args.seeds <= 100:
        raise ValueError("Specify 1..100 independent seeds")
    if not 1 <= args.max_work <= 1_000_000_000:
        raise ValueError("Maximum work-policy bound exceeded")
    if args.dense_limit_n not in NS:
        raise ValueError("Dense limit must be a declared n")
    ns = PHASES[args.phase] if args.n is None else tuple(
        int(x) for x in args.n.split(","))
    ds = tuple(int(x) for x in args.d.split(","))
    crit = tuple(x.strip().lower() for x in args.criteria.split(","))
    counts = tuple(x for x in COUNTS if x <= args.max_candidates)
    if (not ns or len(set(ns)) != len(ns) or any(n not in NS for n in ns)
        or not ds or len(set(ds)) != len(ds) or any(d not in DS for d in ds)
        or not crit or len(set(crit)) != len(crit)
        or any(c not in CRITERIA for c in crit)
        or args.max_candidates not in COUNTS
        or not counts):
        raise ValueError("Invalid or duplicate factorial axis values")
    if any(d >= n for n in ns for d in ds):
        raise ValueError("Difference order must be smaller than n")
    return {
        "experiment": "experiment013", "design": "100seed_core_direct_lambda",
        "n": list(ns), "d": list(ds), "criteria": list(crit),
        "methods": list(METHODS), "checkpoints": list(counts),
        "seeds": args.seeds, "seed_stream": "Experiment012 seed_for",
        "mu_policy": "fixed_zero", "amplitude": "low",
        "R": 1, "coordinate": "direct_lambda",
        "phase": args.phase, "max_work": args.max_work,
        "dense_limit_n": args.dense_limit_n,
        "max_dense_bytes": args.max_dense_bytes, "blas_threads": 1,
        "primary_question": "complete criterion setup and candidate-count amortization",
        "limitations": [
            "Operations are a prespecified eligibility proxy, not measured seconds",
            "CV spectral candidate work is quadratic; scalar criteria differ",
            "Naive full large-n grids are intentionally resource-ineligible",
            "Only fixed mu=0 and one low-amplitude series in core design",
            "Candidate prefixes are direct lambda, not normalized smoothness S",
        ],
    }


def plan_rows(config: dict) -> list[dict]:
    records = []
    for n, d, criterion, method, m in itertools.product(
        config["n"], config["d"], config["criteria"],
        METHODS, config["checkpoints"],
    ):
        status, work, memory = resource_status(
            n, d, criterion, method, m,
            max_work=config["max_work"],
            dense_limit_n=config["dense_limit_n"],
            max_dense_bytes=config["max_dense_bytes"],
        )
        records.append(dict(n=n, d=d, criterion=criterion, method=method, M=m,
                            eligibility=status, work_units=work,
                            memory_bytes=memory))
    return records


def missing_record(config, n, d, criterion, method, idx, m, status, error=""):
    return {**dict.fromkeys(FIELDS, ""), "experiment": "experiment013",
            "run_id": config["run_id"], "source_commit": config["source_commit"],
            "n": n, "d": d, "criterion": criterion,
            "mu_policy": config["mu_policy"], "amplitude": config["amplitude"],
            "R": 1, "coordinate": config["coordinate"], "seed_index": idx,
            "seed": seed_for(idx, n, d), "method": method, "M": m,
            "status": status, "requested": m, "completed": 0,
            "finite_scores": 0, "undefined_scores": 0, "error": error}


def run_method(engine, config: dict, n: int, d: int, criterion: str,
               idx: int, method: str, grid) -> list[dict]:
    """One setup and prefix timings, with invalid/expensive cells explicit."""
    checkpoints = config["checkpoints"]
    statuses = {
        m: resource_status(
            n, d, criterion, method, m,
            max_work=config["max_work"],
            dense_limit_n=config["dense_limit_n"],
            max_dense_bytes=config["max_dense_bytes"],
        )[0] for m in checkpoints
    }
    permitted = [m for m in checkpoints if statuses[m] == "eligible"]
    result = {}
    if not permitted:
        return [missing_record(config,n,d,criterion,method,idx,m,statuses[m])
                for m in checkpoints]
    seed = seed_for(idx,n,d)
    y = engine.sample(n,seed,config["amplitude"])
    setup_start = perf_counter()
    try:
        evaluator = engine.Evaluator(n,d,method)
        coord = evaluator.prepare_series(y,0.0)
    except Exception as exc:
        return [missing_record(config,n,d,criterion,method,idx,m,
                "setup_failed" if statuses[m]=="eligible" else statuses[m],
                f"{type(exc).__name__}: {str(exc)[:160]}")
                for m in checkpoints]
    setup = perf_counter()-setup_start
    elapsed = 0.
    first = None
    completed = 0
    finite_scores = 0
    undefined_scores = 0
    best = (float("inf"), None)
    failure = ""
    last_permitted = max(permitted)
    for i, lam in enumerate(grid[:last_permitted], start=1):
        if not failure:
            t0 = perf_counter()
            try:
                value = float(evaluator.evaluate(
                    y, 0.0, float(lam), criterion,
                    coordinates=coord, reuse_factor=False))
                # The core scoring API returns +inf for criterion-undefined
                # candidates (notably AICc where n - edf - 2 <= 0).
                # This is a documented rejection of this candidate, NOT
                # a failed factorization. Time the call and keep searching.
                if math.isnan(value) or value == -math.inf:
                    raise ArithmeticError("NaN or -infinity criterion score")
            except Exception as exc:
                elapsed += perf_counter()-t0
                failure=f"{type(exc).__name__}: {str(exc)[:160]}"
            else:
                delta = perf_counter()-t0
                elapsed += delta
                completed += 1
                if first is None:
                    first = delta
                if value == math.inf:
                    undefined_scores += 1
                else:
                    finite_scores += 1
                    if value < best[0]:
                        best=(value,float(lam))
        if i in permitted:
            if failure or completed != i:
                status = "numerical_failed"
            elif finite_scores == 0:
                status = "criterion_undefined"
            else:
                status = "ok"
            row = missing_record(config,n,d,criterion,method,idx,i,status,failure)
            row.update({
                "completed":completed,
                "finite_scores":finite_scores,
                "undefined_scores":undefined_scores,
                "method_setup_s":setup,
                "first_evaluation_s":first if first is not None else "",
                "cumulative_evaluation_s":elapsed,
                "total_cold_s":setup+elapsed,
                "selected_lambda":best[1] if best[1] is not None else "",
                "selected_score":best[0] if best[1] is not None else "",
            })
            result[i]=row
    for m in checkpoints:
        if m not in result:
            result[m]=missing_record(config,n,d,criterion,method,idx,m,statuses[m])
    return [result[m] for m in checkpoints]


def records_done(output: Path, config: dict) -> set[tuple]:
    """Resume exclusively complete method groups; refuse partial/duplicate groups."""
    path=output/"timings.csv"
    if not path.exists():
        return set()
    groups={}
    with path.open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f)
        if tuple(reader.fieldnames or ())!=FIELDS:
            raise ValueError("CSV schema differs; cannot resume")
        for row in reader:
            key=(int(row["n"]),int(row["d"]),row["criterion"],
                 int(row["seed_index"]),row["method"])
            if row["run_id"] != config["run_id"] or row["source_commit"]!=config["source_commit"]:
                raise ValueError("CSV source/run tag differs; cannot resume")
            groups.setdefault(key,[]).append(int(row["M"]))
    for key, ms in groups.items():
        if sorted(ms)!=config["checkpoints"]:
            raise ValueError(f"Partial or duplicate method group: {key}")
    return set(groups)


def write_manifest(path: Path, rows: list[dict]) -> None:
    with path.open("w",newline="",encoding="utf8") as f:
        wr=csv.DictWriter(f,fieldnames=PLAN_FIELDS)
        wr.writeheader()
        wr.writerows(rows)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase",choices=tuple(PHASES),default="small")
    parser.add_argument("--n",help="Optional comma-separated n subset, e.g. 32,64")
    parser.add_argument("--d",default="1,2,3")
    parser.add_argument("--criteria",default="cv,gcv,mle,aicc,bic")
    parser.add_argument("--seeds",type=int,default=100)
    parser.add_argument("--max-candidates",type=int,default=10000)
    parser.add_argument("--max-work",type=int,default=50_000_000)
    parser.add_argument("--dense-limit-n",type=int,default=512)
    parser.add_argument("--max-dense-bytes",type=int,default=2*1024**3)
    parser.add_argument("--out",type=Path)
    parser.add_argument("--execute",action="store_true")
    parser.add_argument("--resume",action="store_true")
    args=parser.parse_args()
    config=configuration(args)
    overview=plan_rows(config)
    statuses={}
    for row in overview:
        statuses[row["eligibility"]]=statuses.get(row["eligibility"],0)+1
    print(json.dumps({"n":config["n"],"d":config["d"],
                      "criteria":config["criteria"],"seeds":config["seeds"],
                      "method_grid_checkpoint_cells":len(overview),
                      "seed_cells":len(overview)*config["seeds"],
                      "planned_eligibility":statuses},indent=2),flush=True)
    if not args.execute:
        print("PLAN ONLY; no numerical measurements executed.")
        return 0
    if args.out is None:
        parser.error("--execute requires an explicit, new --out directory")
    if Path.cwd().resolve()!=ROOT:
        raise RuntimeError("Run from repository root")
    for var in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS",
                "NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
        os.environ[var]="1"
    sys.path.insert(0,str(ENGINE.parent))
    import run as engine
    from threadpoolctl import threadpool_limits, threadpool_info
    import numpy as np
    import scipy
    output=args.out.resolve()
    config.update({
        "run_id":output.name,
        "source_commit":git_sha(),
        "engine_sha256":source_hash(ENGINE),
        "experiment012_grid_sha256":source_hash(GRID_SOURCE),
        "runner_sha256":source_hash(Path(__file__)),
        "numpy":np.__version__, "scipy":scipy.__version__,
        "python":sys.version, "host":platform.node(),
        "platform":platform.platform(), "blas_info":threadpool_info(),
    })
    meta=output/"metadata.json"
    if args.resume:
        if not meta.is_file():
            raise FileNotFoundError("Cannot resume without metadata.json")
        old=json.loads(meta.read_text(encoding="utf8"))
        if old!=config:
            raise ValueError("Resume metadata/source does not match initial run")
    else:
        output.mkdir(parents=True,exist_ok=False)
        meta.write_text(json.dumps(config,indent=2)+"\n",encoding="utf8")
        write_manifest(output/"coverage_plan.csv",overview)
    done=records_done(output,config)
    file=output/"timings.csv"
    with file.open("a",newline="",encoding="utf8") as stream:
        writer=csv.DictWriter(stream,fieldnames=FIELDS)
        if stream.tell()==0:
            writer.writeheader()
        grid=candidates(max(config["checkpoints"]))
        with threadpool_limits(limits=1):
            for n,d,criterion,idx in itertools.product(
                config["n"],config["d"],config["criteria"],range(config["seeds"])
            ):
                order=METHODS[(idx+n+d)%3:]+METHODS[:(idx+n+d)%3]
                for method in order:
                    key=(n,d,criterion,idx,method)
                    if key in done:
                        continue
                    rows=run_method(engine,config,n,d,criterion,idx,method,grid)
                    writer.writerows(rows)
                    stream.flush()
                    done.add(key)
                if idx%10==0:
                    print(f"Recorded n={n}, d={d}, {criterion}, seed={idx+1}/{config['seeds']}",
                          flush=True)
    expected=(len(config["n"])*len(config["d"])*len(config["criteria"])*
              config["seeds"]*len(METHODS))
    if len(done)!=expected:
        raise RuntimeError(f"Incomplete method groups: {len(done)} != {expected}")
    evidence={
        "experiment":"experiment013", "source_commit":config["source_commit"],
        "groups":len(done), "expected_groups":expected,
        "row_count":expected*len(config["checkpoints"]),
        "timings_sha256":source_hash(file),
        "coverage_sha256":source_hash(output/"coverage_plan.csv"),
        "measurement_state":"complete_recorded_statuses_not_publication_certification",
    }
    (output/"completion.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf8")
    print("Completed immutable source-specific measurements:",output,flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
