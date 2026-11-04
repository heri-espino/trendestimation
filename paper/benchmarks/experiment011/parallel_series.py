"""Opt-in per-independent-series multiprocessing throughput for Experiment011.

Do not mix its records with the serial complete-criterion latency dataset.
Each worker constructs its *own* mapper/evaluator and works on a single
deterministically generated series. Therefore factor/SVD/grid-mapping
preparation is duplicated across processes, not shared as in the
sequential multi-series evaluator. This is a different throughput
architecture, not a like-for-like R-series cache benchmark.

The controller limits this experiment to small n <= 256, M <= 1000.
Each group contains one method and one repeat, with identical series
seeds across methods, BLAS threads fixed to one, and bounded independent
workers. No subprocess executes a large factorial.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import multiprocessing as mp
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEGACY = ROOT / "paper" / "benchmarks" / "experiment006"
OUTPUTS = HERE / "runs_parallel"
POLICIES = ("direct_s", "mapped_lambda")
WORKLOADS = ("one_s_multiple_series", "grid_multiple_series")
SCALAR_METHODS = ("spectral_svd", "banded_cholesky", "naive_inverse")
ROW_FIELDS = (
    "case_id", "method", "block", "repeat", "series_index", "seed",
    "n", "d", "mu_policy", "amplitude", "criterion",
    "M", "R_total", "coordinate", "workload", "status",
    "selected_s", "selected_score", "method_setup_s", "mapper_setup_s",
    "series_projection_s", "s_to_lambda_s", "criterion_s", "attributed_total_s",
    "evaluations", "comment",
)


def _task(parameters: dict) -> dict:
    """Run one independent series; callable under Windows spawn."""
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS",
                "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    import numpy as np
    from threadpoolctl import threadpool_limits
    sys.path.insert(0, str(LEGACY))
    from run import (
        Evaluator, grid_of_s, sample, memory_budget_status,
    )
    from selected_inverse import BandedTrace
    from trendestimation import TrendSmoother

    case = parameters["case"]
    method = parameters["method"]
    repeat = parameters["repeat"]
    j = parameters["series_index"]
    seed = parameters["seed_base"] + 100000 * repeat + 23*j + 29*case["n"] + 7*case["d"]
    n, d, m = case["n"], case["d"], case["grid_denominator"]
    y = sample(n, seed, case["amplitude"])
    mu = float(np.mean(np.diff(y, n=d))) if case["mu"] == "data" else float(case["mu"])
    results = []
    with threadpool_limits(limits=1):
        start = perf_counter()
        try:
            mapper = TrendSmoother(n, d)
            mapper_setup_s = perf_counter()-start
            start = perf_counter()
            evaluator = Evaluator(n, d, method)
            method_setup_s = perf_counter()-start
            start = perf_counter()
            coordinates = evaluator.prepare_series(y, mu)
            projection_s = perf_counter()-start
            failed = None
        except (ValueError, ArithmeticError, MemoryError,
                ImportError, np.linalg.LinAlgError) as exc:
            failed = f"setup_failed_{type(exc).__name__}: {exc}"[:180]
            mapper_setup_s = max(0., perf_counter()-start)
            method_setup_s = 0.
            projection_s = 0.
            evaluator = mapper = coordinates = None

        for workload in WORKLOADS:
            ss = np.array([.5]) if workload.startswith("one_s") else grid_of_s(m)
            for policy in POLICIES:
                # Per-worker resource gate is a separate, explicitly
                # labeled workload from the serial R-series gate.
                budget = memory_budget_status(
                    n,d,method,m,parameters["max_dense_bytes"],
                    parameters["max_work"],workload,1,1
                )
                row = dict(
                    case_id=case["id"], method=method,
                    block=parameters["block"],repeat=repeat,
                    series_index=j, seed=seed, n=n,d=d,
                    mu_policy=case["mu"],amplitude=case["amplitude"],
                    criterion=case["criterion"],M=len(ss),
                    R_total=parameters["series_count"],
                    coordinate=policy, workload=workload,
                    status="ok",selected_s=math.nan,selected_score=math.nan,
                    method_setup_s=method_setup_s,
                    mapper_setup_s=mapper_setup_s,
                    series_projection_s=projection_s,
                    s_to_lambda_s=0.,criterion_s=0.,
                    attributed_total_s=0.,evaluations=0,comment="",
                )
                if failed is not None or budget!="eligible":
                    row["status"]=failed.split(":")[0] if failed else budget
                    row["comment"]=failed or "explicit resource preflight"
                    results.append(row)
                    continue
                try:
                    start=perf_counter()
                    mapped = (
                        [mapper.lambda_for_smoothness(float(s)) for s in ss]
                        if policy=="mapped_lambda" else None
                    )
                    row["s_to_lambda_s"]=perf_counter()-start if mapped is not None else 0.
                    scores=[]
                    for k,s in enumerate(ss):
                        if mapped is None:
                            start=perf_counter()
                            lam=mapper.lambda_for_smoothness(float(s))
                            row["s_to_lambda_s"]+=perf_counter()-start
                        else:
                            lam=mapped[k]
                        start=perf_counter()
                        value=evaluator.evaluate(
                            y,mu,lam,case["criterion"],
                            coordinates=coordinates,reuse_factor=False
                        )
                        row["criterion_s"]+=perf_counter()-start
                        row["evaluations"]+=1
                        if math.isfinite(float(value)):
                            scores.append((float(value),float(s)))
                    if scores:
                        row["selected_score"],row["selected_s"]=min(
                            scores,key=lambda pair:pair[0]
                        )
                    else:
                        row["status"]="criterion_undefined"
                except (ValueError, ArithmeticError, OverflowError,
                        MemoryError, np.linalg.LinAlgError) as exc:
                    row["status"]="numerical_failed"
                    row["comment"]=f"{type(exc).__name__}: {exc}"[:180]
                row["attributed_total_s"]=(
                    mapper_setup_s+method_setup_s+projection_s+
                    row["s_to_lambda_s"]+row["criterion_s"]
                )
                results.append(row)
    return {"method":method,"repeat":repeat,"series_index":j,"rows":results}


def _ensure_blas_1():
    for key in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS",
                "MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
        os.environ[key]="1"


def _startup(_):
    # Warm up spawned process, so the first method's group wall time
    # is not uniquely charged interpreter startup.
    _ensure_blas_1()
    return os.getpid()


def audit_parallel(rows: list[dict], methods: list[str], R: int, repeats: int) -> dict:
    """Exact row coverage and matched float64 selected-score checks."""
    expected={
        (m,r,j,w,p)
        for m in methods for r in range(repeats) for j in range(R)
        for w in WORKLOADS for p in POLICIES
    }
    actual={}
    counts={}
    for row in rows:
        key=(row["method"],int(row["repeat"]),int(row["series_index"]),
             row["workload"],row["coordinate"])
        if key not in expected or key in actual:
            raise ValueError("Duplicate/unplanned parallel-series row "+str(key))
        actual[key]=row
        counts[row["status"]]=counts.get(row["status"],0)+1
        if row["status"]=="ok":
            if not math.isfinite(float(row["attributed_total_s"])):
                raise ValueError("Successful timing is not finite")
            if not 0 <= float(row["selected_s"]) <= 1:
                raise ValueError("Successful selected S outside [0,1]")
            if int(row["evaluations"])!=int(row["M"]):
                raise ValueError("Partial grid mislabeled successful")
    if set(actual)!=expected:
        raise ValueError("Missing parallel-series work cells")
    issues=[]
    paired=0
    for r in range(repeats):
        for j in range(R):
            for w in WORKLOADS:
                for p in POLICIES:
                    group=[actual[(m,r,j,w,p)] for m in methods
                           if actual[(m,r,j,w,p)]["status"]=="ok"]
                    if len(group)<2:
                        continue
                    baseline=next((v for v in group if
                                   v["method"]=="spectral_svd"),group[0])
                    for candidate in group:
                        if candidate is baseline:
                            continue
                        paired+=1
                        sd=abs(float(candidate["selected_s"])-float(baseline["selected_s"]))
                        # ML log likelihood may differ by a lambda-
                        # independent constant across implementations.
                        criterion=parameters_criterion(candidate)
                        ed=(abs(float(candidate["selected_score"])-
                                float(baseline["selected_score"]))/
                            max(1.,abs(float(baseline["selected_score"])))
                            if criterion!="mle" else 0.)
                        if sd>1e-10 or ed>1e-7:
                            issues.append({
                                "repeat":r,"series_index":j,"workload":w,
                                "coordinate":p,"method":candidate["method"],
                                "selected_s_difference":sd,
                                "relative_score_difference":ed,
                            })
    return {
        "classification":(
            "needs_independent_numerical_review" if issues else
            "partial_success_with_skips_or_failures" if counts.get("ok",0)!=len(rows)
            else "insufficient_paired_methods" if paired==0
            else "float64_parity_only_not_precision_certified"
        ),
        "actual_rows":len(rows),"status_counts":dict(sorted(counts.items())),
        "paired_method_comparisons":paired,"issues":issues,
        "caveat":(
            "One independent series per spawned process; setup, mapper "
            "and factor caches are not shared. Group wall time is throughput "
            "latency and cannot be pooled with serial R-series timings. "
            "Selection-score parity is float64, not a precision certificate."
        ),
    }


def parameters_criterion(row):
    return row["criterion"]


def run_parallel(case: dict, *,run_tag: str,block: int,
                 series_count: int,series_workers: int,
                 max_work: float,max_dense_bytes: int,
                 seed_base: int,source_commit: str,
                 source_hashes: dict,dry_run: bool = False) -> dict:
    if case["n"]>256 or case["grid_denominator"]>1000:
        raise ValueError("Parallel per-series mode is restricted to small n<=256 and M<=1000")
    if any(m not in SCALAR_METHODS for m in case["methods"]):
        raise ValueError("Parallel series uses only validated exact scalar pipelines")
    if not 2<=series_count<=32:
        raise ValueError("series_count must be in 2..32")
    if not 1<=series_workers<=min(series_count,32):
        raise ValueError("series_workers must be in 1..min(R,32)")
    if block not in range(case["planned_blocks"]):
        raise ValueError("Out-of-range block")
    if not run_tag or any(ch not in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-" for ch in run_tag):
        raise ValueError("Unsafe run tag")
    methods=list(case["methods"])
    rotation=block%len(methods)
    methods=methods[rotation:]+methods[:rotation]
    output=OUTPUTS/run_tag/case["id"]/f"block{block:03d}"
    metadata={
        "experiment":"experiment011",
        "mode":"independent_series_parallel_throughput",
        "not_comparable_to_serial_r_cache_latency":True,
        "case":case,"method_order":methods,
        "source_commit":source_commit,
        "source_sha256":source_hashes,
        "run_tag":run_tag,"block":block,
        "series_count":series_count,"series_workers":series_workers,
        "blas_threads_per_worker":1,
        "max_work":max_work,"max_dense_bytes":max_dense_bytes,
        "seed_base":seed_base+10000*block,
        "host":platform.platform(),
        "python":sys.version,
        "note":"R separate processes use private factorization/SVD/mapping. "
               "Per-method wall time includes process scheduler/IPC and "
               "is NOT a replacement for serial R-series cache reuse.",
        "status":"not_measured" if dry_run else "started",
    }
    if dry_run:
        return {"output":str(output),"metadata":metadata}
    if output.exists():
        raise FileExistsError("Refusing to overwrite parallel results: "+str(output))
    output.mkdir(parents=True,exist_ok=False)
    (output/"parallel_manifest.json").write_text(
        json.dumps(metadata,indent=2)+"\n",encoding="utf8"
    )
    _ensure_blas_1()
    all_rows=[]
    groups=[]
    try:
        # Windows-safe, real processes, not Python threads pretending
        # to use all CPU logical processors for numerical Python code.
        with ProcessPoolExecutor(max_workers=series_workers,
                                 mp_context=mp.get_context("spawn")) as pool:
            list(pool.map(_startup,range(series_workers)))
            for method in methods:
                for repeat in range(case["repeats_per_block"]):
                    group_start=perf_counter()
                    tasks=[
                        {"case":case,"method":method,"repeat":repeat,
                         "series_index":j,"series_count":series_count,
                         "block":block,"seed_base":metadata["seed_base"],
                         "max_dense_bytes":max_dense_bytes,
                         "max_work":max_work}
                        for j in range(series_count)
                    ]
                    futures=[pool.submit(_task,task) for task in tasks]
                    group_rows=[]
                    for future in as_completed(futures):
                        result=future.result()
                        # Preserve row-level numerical checkpoints while
                        # other series remain in flight.
                        checkpoint=output/f"worker_{method}_r{repeat}_s{result['series_index']:03d}.json"
                        checkpoint.write_text(
                            json.dumps(result,indent=2,allow_nan=True)+"\n",
                            encoding="utf8"
                        )
                        group_rows.extend(result["rows"])
                    elapsed=perf_counter()-group_start
                    all_rows.extend(group_rows)
                    groups.append({
                        "method":method,"repeat":repeat,
                        "series_count":series_count,
                        "series_workers":series_workers,
                        "group_elapsed_wall_s":elapsed,
                        "series_per_wall_second":series_count/elapsed,
                        "complete_row_count":len(group_rows),
                    })
        with (output/"parallel_raw_times.csv").open(
                "w",encoding="utf8",newline="") as handle:
            writer=csv.DictWriter(handle,fieldnames=ROW_FIELDS)
            writer.writeheader()
            writer.writerows(sorted(all_rows,key=lambda x:
                (methods.index(x["method"]),x["repeat"],x["series_index"],
                 x["workload"],x["coordinate"])))
        with (output/"parallel_method_wall.csv").open(
                "w",encoding="utf8",newline="") as handle:
            writer=csv.DictWriter(handle,fieldnames=list(groups[0]))
            writer.writeheader();writer.writerows(groups)
        qa=audit_parallel(all_rows,methods,series_count,
                          case["repeats_per_block"])
        (output/"parallel_qa.json").write_text(
            json.dumps(qa,indent=2)+"\n",encoding="utf8"
        )
        metadata["status"]="completed_with_recorded_rows"
        metadata["row_count"]=len(all_rows)
        metadata["qa_classification"]=qa["classification"]
        metadata["complete_utc"]=datetime.now(timezone.utc).isoformat()
        metadata["raw_sha256"]=hashlib.sha256(
            (output/"parallel_raw_times.csv").read_bytes()).hexdigest()
        (output/"parallel_manifest.json").write_text(
            json.dumps(metadata,indent=2)+"\n",encoding="utf8"
        )
        print(f"Parallel series: {len(all_rows)} actual rows, "
              f"{len(groups)} method/repeat throughput groups, "
              f"{qa['classification']}")
        return {"output":str(output),"metadata":metadata,"qa":qa}
    except BaseException as exc:
        metadata["status"]="failed_or_interrupted"
        metadata["error"]=f"{type(exc).__name__}: {exc}"[:500]
        (output/"parallel_manifest.json").write_text(
            json.dumps(metadata,indent=2)+"\n",encoding="utf8"
        )
        raise
