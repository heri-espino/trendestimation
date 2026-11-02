"""Experiment008: archive full planned factorial and execute honest timing slices.

Every call to Experiment006 run_slice times all four workloads, direct-S
and translated-lambda policies, and every requested method. The full
Cartesian grid is *planned*, not claimed measured when infeasible.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

HERE=Path(__file__).resolve().parents[1]/"experiment006"
sys.path.insert(0,str(HERE))
from run import (D_LEVELS,GRID_DENOMINATORS,METHODS,N_LEVELS,
                 SCENARIOS,POLICIES,CRITERIA,memory_budget_status)


def configurations(preset):
    # Deterministically cover each d, criterion, amplitude, mean policy,
    # multiple n and all grid densities in a bounded first batch.
    # The COMPLETE Cartesian product is in the accompanying manifest.
    ordered=[]
    for n in (64,128,256,512,1024):
        for d in D_LEVELS:
            for criterion_index,criterion in enumerate(CRITERIA):
                for mean in ("0","data"):
                    for scale in ("low","high"):
                        for denominator in GRID_DENOMINATORS:
                            ordered.append(dict(n=n,d=d,criterion=criterion,mu=mean,
                                                amplitude=scale,denominator=denominator))
    # High-n sizes cannot be evaluated by dense SVD/inversion and are
    # prioritized only for guarded, small-workload structured slices.
    for n in (16384,131072):
        for d in D_LEVELS:
            ordered.append(dict(n=n,d=d,criterion="gcv",mu="data",
                                amplitude="low",denominator=100))
            ordered.append(dict(n=n,d=d,criterion="cv",mu="0",
                                amplitude="high",denominator=100))
    if preset=="smoke":
        return [
            dict(n=64,d=1,criterion="gcv",mu="0",
                 amplitude="low",denominator=100),
            dict(n=64,d=6,criterion="mle",mu="data",
                 amplitude="high",denominator=100),
        ]
    if preset=="pilot":
        selected=[]
        for i,(n,d) in enumerate(
            [(64,1),(64,2),(64,3),(64,4),(64,5),(64,6),
             (128,1),(128,2),(128,3),(128,4),(128,5),(128,6),
             (256,1),(256,2),(256,3),(256,4),(256,5),(256,6),
             (512,1),(512,3),(512,6),(1024,1),(1024,4),(1024,6)]
        ):
            selected.append(dict(
                n=n,d=d,criterion=CRITERIA[i%5],
                mu="data" if i%2 else "0",
                amplitude="high" if (i//2)%2 else "low",
                denominator=(100,1000,10000,100000)[(i//2)%4]
            ))
        return selected
    if preset=="broad":
        # Round-robin matched (n,d) blocks, so a bounded batch samples
        # every feasible size and all six orders BEFORE another grid
        # density/criterion; do not spend the full budget on n=64 only.
        keys=[(n,d) for n in (64,128,256,512,1024)
              for d in D_LEVELS]
        buckets={}
        for key in keys:
            subset=[x for x in ordered if
                    x["n"]==key[0] and x["d"]==key[1]]
            buckets[key]=sorted(subset,key=lambda x:(
                x["denominator"],x["criterion"],x["amplitude"],x["mu"]))
        result=[]
        for i in range(max(len(bucket) for bucket in buckets.values())):
            result.extend(buckets[k][i] for k in keys if i<len(buckets[k]))
        return result+[x for x in ordered if x["n"]>=16384]
    raise ValueError("Unknown preset")


def planned_cells(path,*,repeats=2,R=2,max_work=4e6,
                  max_dense_bytes=2*1024**3):
    # Every requested axis, including both mean policies and optional
    # fixed nonzero reference, and all four workloads. This outputs
    # PLAN statuses, never synthetic measured times.
    if path.exists(): raise FileExistsError(path)
    counts=Counter()
    k=0
    path.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(path,"wt",encoding="utf-8",newline="") as stream:
        columns=("n","d","mu","amplitude","criterion","method",
                 "grid_denominator","workload","coordinate","R","M",
                 "planned_fits","score_semantics","plan_status")
        writer=csv.DictWriter(stream,fieldnames=columns)
        writer.writeheader()
        for n in N_LEVELS:
            for d in D_LEVELS:
                for mu in ("0","data","0.15"):
                    for amplitude in ("low","high"):
                        for criterion in CRITERIA:
                            for method in METHODS:
                                for workload in SCENARIOS:
                                    denoms=((0,) if workload.startswith("one_s")
                                            else GRID_DENOMINATORS)
                                    for denominator in denoms:
                                        for coordinate in POLICIES:
                                            M=1 if denominator==0 else denominator
                                            nr=1 if "one_series" in workload else R
                                            # Use 100 only to communicate the
                                            # single-S workload to resource guard.
                                            status=memory_budget_status(
                                                n,d,method,max(100,denominator),
                                                max_dense_bytes,max_work,
                                                workload,nr,repeats)
                                            semantics=("conditional_plugin_not_refitted"
                                                if mu=="data" and criterion!="mle"
                                                else "conditional_plugin_mle"
                                                if mu=="data" else "fixed_mu")
                                            writer.writerow(dict(
                                                n=n,d=d,mu=mu,amplitude=amplitude,
                                                criterion=criterion,method=method,
                                                grid_denominator=denominator,
                                                workload=workload,coordinate=coordinate,
                                                R=nr,M=M,planned_fits=M*nr*repeats,
                                                score_semantics=semantics,
                                                plan_status=status))
                                            k+=1
                                            counts[status]+=1
    return k,counts


def methods_for(n):
    if n<=128:
        return ("naive_inverse","spectral_svd","banded_cholesky",
                "sparse_lu_banded_trace","pcg_fft_banded_trace")
    if n<=1024:
        return ("naive_inverse","spectral_svd","banded_cholesky",
                "sparse_lu_banded_trace")
    return ("naive_inverse","spectral_svd","banded_cholesky",
            "sparse_lu_banded_trace")


def execute(output,preset="pilot",*,max_seconds=900,
            max_slices=25,repeats=2,R=2,max_work=4e6,
            per_slice_seconds=55,
            max_dense_bytes=2*1024**3):
    if output.exists():raise FileExistsError(f"Refusing to overwrite {output}")
    output.mkdir(parents=True)
    started=perf_counter()
    configurations_all=configurations(preset)
    candidates=[]
    for i,cfg in enumerate(configurations_all):
        task={**cfg,"index":i,"methods":methods_for(cfg["n"])}
        # Not all slices can be measured. Keep every requested choice
        # and its actual selection status in the batch manifest.
        candidates.append(task)
    with (output/"batch_manifest.json").open("w",encoding="utf-8") as stream:
        json.dump(dict(preset=preset,created_utc=datetime.now(timezone.utc).isoformat(),
                       run_id=os.environ.get("GITHUB_RUN_ID"),
                       runner=os.environ.get("RUNNER_NAME"),
                       python=sys.version,host=platform.platform(),
                       max_seconds=max_seconds,max_slices=max_slices,
                       per_slice_seconds=per_slice_seconds,
                       repeats=repeats,R=R,max_work=max_work,
                       score_semantics="mu=data is conditional plug-in",
                       all_tasks=len(candidates),tasks=candidates),
                  stream,indent=2)
    total,counts=planned_cells(output/"full_factorial_plan.csv.gz",
                               repeats=repeats,R=R,max_work=max_work,
                               max_dense_bytes=max_dense_bytes)
    all_status=[]
    n_completed=0
    for cfg in candidates:
        elapsed=perf_counter()-started
        if elapsed>=max_seconds or n_completed>=max_slices:
            all_status.append({**cfg,"status":"not_executed_batch_limit",
                               "elapsed_s":elapsed,
                               "reason":"Bounded runner budget; not a timing measurement"})
            continue
        folder=(output/"slices"/(
            f"{cfg['index']:05d}_n{cfg['n']}_d{cfg['d']}_"
            f"{cfg['mu'].replace('.','p')}_{cfg['amplitude']}_"
            f"{cfg['criterion']}_M{cfg['denominator']}"))
        t0=perf_counter()
        try:
            # Bound EACH slice independently: one high-d numerical S-grid
            # inversion must not monopolize the whole university runner.
            cmd=[
                sys.executable,str(HERE/"run.py"),
                "--preset","slice","--n",str(cfg["n"]),
                "--d",str(cfg["d"]),"--mu",cfg["mu"],
                "--amplitude",cfg["amplitude"],
                "--criterion",cfg["criterion"],
                "--grid-denominator",str(cfg["denominator"]),
                "--methods",",".join(cfg["methods"]),
                "--repeats",str(repeats),"--series-count",str(R),
                "--max-work",str(max_work),
                "--max-dense-bytes",str(max_dense_bytes),
                "--threads","1","--conditional-data-mu",
                "--output",str(folder),
            ]
            subprocess.run(cmd,check=True,timeout=per_slice_seconds)
            with (folder/"raw_times.csv").open(
                    "r",newline="",encoding="utf-8") as stream:
                rows=list(csv.DictReader(stream))
            outcome=Counter(row["status"] for row in rows)
            all_status.append({**cfg,"status":"completed_with_recorded_cells",
                               "elapsed_s":perf_counter()-t0,
                               "result_folder":str(folder.relative_to(output)),
                               "row_status_counts":dict(outcome),
                               "measured_rows":sum(row["status"]=="ok" for row in rows)})
            n_completed+=1
        except subprocess.TimeoutExpired:
            all_status.append({**cfg,"status":"slice_timeout_no_credible_time",
                               "elapsed_s":perf_counter()-t0,
                               "reason":f"Per-slice {per_slice_seconds}s execution ceiling"})
            n_completed+=1
        except Exception as exc:
            all_status.append({**cfg,"status":"slice_execution_error",
                               "elapsed_s":perf_counter()-t0,
                               "reason":f"{type(exc).__name__}: {exc}"[:300]})
            n_completed+=1
        # Write a durable ledger after EACH completed slice, so partial
        # results remain interpretable even if the process is interrupted.
        (output/"slice_status.json").write_text(
            json.dumps(all_status,indent=2)+"\n",encoding="utf-8")
        print(f"[{n_completed}/{max_slices}] {cfg['n']=} {cfg['d']=} "
              f"{cfg['criterion']=} {cfg['mu']=} {cfg['denominator']=} "
              f"-> {all_status[-1]['status']}; {perf_counter()-started:.1f}s",
              flush=True)
    (output/"slice_status.json").write_text(
        json.dumps(all_status,indent=2)+"\n",encoding="utf-8")
    sums=Counter(x["status"] for x in all_status)
    metadata=dict(actual_completed_slices=n_completed,
                  observed_slices_with_raw_csv=sum(x["status"]=="completed_with_recorded_cells"
                                                    for x in all_status),
                  total_candidate_slices=len(candidates),
                  planned_factorial_rows=total,
                  planned_resource_status_counts=dict(counts),
                  slice_status_counts=dict(sums),
                  seconds=perf_counter()-started,
                  note=("Every plan row is a requested combination, "
                        "NOT an observed computing time. Actual timings are "
                        "ONLY in slice raw_times.csv with status=ok. "
                        "The n=131072 naive inverse is infeasible. "
                        "All 4 workloads, both coordinate policies, all "
                        "five criteria, mean policies and exact S=1 "
                        "are represented without fabricated measurements."))
    (output/"batch_summary.json").write_text(
        json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    return metadata


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--preset",choices=("smoke","pilot","broad"),default="pilot")
    p.add_argument("--max-seconds",type=float,default=900.)
    p.add_argument("--max-slices",type=int,default=25)
    p.add_argument("--per-slice-seconds",type=int,default=55)
    p.add_argument("--repeats",type=int,default=2)
    p.add_argument("--series-count",type=int,default=2)
    p.add_argument("--max-work",type=float,default=4e6)
    args=p.parse_args()
    print(json.dumps(execute(args.output,args.preset,max_seconds=args.max_seconds,
                 max_slices=args.max_slices,repeats=args.repeats,
                 R=args.series_count,max_work=args.max_work,
                 per_slice_seconds=args.per_slice_seconds),indent=2))
