"""Experiment005: fit-only structured solver timing with strict validity gating.

Run from repository root:
 python paper/benchmarks/experiment005/run.py --preset smoke
 python paper/benchmarks/experiment005/run.py --preset quick --repeats 5
 python paper/benchmarks/experiment005/run.py --preset large --repeats 7

No results are invented. Every attempted fit records elapsed time,
independent banded-Cholesky parity and normal-equation residual. If an
iterative solver fails, it is marked FAILED, never included in winners.
S mapping and CV/GCV selection are outside this fit-only experiment.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from scipy.sparse import diags
from threadpoolctl import threadpool_info, threadpool_limits

from trendestimation import PreparedPLSSolver

HERE = Path(__file__).resolve().parent
METHODS = (
    ("cholesky", {}),
    ("banded_lu", {}),
    ("sparse_lu", {}),
    ("sparse_lu_cached", {"method": "sparse_lu", "factor_cache": True}),
    ("sparse_cholesky", {"factor_cache": True}),
    ("pcg_fft", {"method": "pcg", "preconditioner": "fft"}),
    ("pcg_dst", {"method": "pcg", "preconditioner": "dst"}),
    ("pcg_jacobi", {"method": "pcg", "preconditioner": "jacobi"}),
)


def cases(preset):
    if preset == "smoke":
        return [(36, 2, 0.0), (36, 3, 0.15)]
    if preset == "quick":
        return [(n, d, mu) for n in (64, 256)
                for d in (1, 2, 3, 6) for mu in (0.0, 0.15, "data")]
    if preset == "large":
        return [(n, d, mu) for n in (2048, 8192)
                for d in (1, 2, 3, 4, 5, 6)
                for mu in (0.0, 0.15, "data")]
    raise ValueError("preset must be smoke, quick, or large")


def generate(n, seed):
    t = np.linspace(-1., 1., n)
    return .7*np.sin(3*np.pi*t) + .08*t + np.random.default_rng(seed).normal(0,.12,n)


def direct_residual(y, tau, lam, d, mu):
    """Compute the original normal-equation relative residual without dense Q."""
    from math import comb
    D = diags([
        np.full(len(y)-d, (-1.)**(d-j)*comb(d,j)) for j in range(d+1)
    ], list(range(d+1)),shape=(len(y)-d,len(y)),format="csc")
    m = float(np.mean(D@y)) if mu == "data" else float(mu)
    rhs = y + lam*m*np.asarray(D.T@np.ones(len(y)-d)).ravel()
    residual = tau + lam*(D.T@(D@tau)) - rhs
    return float(np.linalg.norm(residual)/max(1.,np.linalg.norm(rhs)))


def run(preset="smoke", *, repeats=2, threads=1, seed=20261102, output=None):
    if repeats < 1 or threads < 1:
        raise ValueError("repeats and threads must be positive")
    target = Path(output) if output else HERE/"runs"/("local-"+preset)
    target.mkdir(parents=True,exist_ok=True)
    penalties = (0.01, 1.0) if preset=="smoke" else (0.001, .1, 10., 1000.)
    rows = []
    with threadpool_limits(limits=threads):
        env = {
            "created_utc":datetime.now(timezone.utc).isoformat(),
            "platform":platform.platform(), "processor":platform.processor(),
            "logical_cpus":os.cpu_count(), "python":sys.version,
            "numpy":np.__version__, "scipy":scipy.__version__,
            "blas_threads":threads, "threadpools":threadpool_info(),
            "preset":preset,"repeats":repeats,
            "methods":[p[0] for p in METHODS],
            "lambda_grid":list(penalties),
            "selection_grid":None,
            "scope":"fit-only, not EDF, CV, GCV, BIC or MLE",
        }
        for ci,(n,d,mu) in enumerate(cases(preset)):
            y = generate(n, seed + 7*n + 13*d)
            reference = PreparedPLSSolver(n, d, method="cholesky")
            for name, opts in METHODS:
                method = opts.get("method",name)
                started = perf_counter()
                try:
                    solver = PreparedPLSSolver(
                        n,d,method=method,**{
                            k:v for k,v in opts.items() if k!="method"
                        }, cg_rtol=1e-9, cg_maxiter=min(2000,5*n))
                    prep = perf_counter()-started
                    init_status = "ok"
                except (ImportError,ValueError) as exc:
                    init_status = type(exc).__name__+": "+str(exc)
                    prep = float("nan")
                    solver = None
                for lam in penalties:
                    truth = reference.fit(y,lambda_=lam,mu=mu)
                    for repeat in range(repeats):
                        cache_hit = bool(
                            solver is not None and solver.structured is not None
                            and solver.structured.factor_cache
                            and lam in solver.structured._factors
                        )
                        if solver is None:
                            rows.append({
                                "n":n,"d":d,"mu":str(mu),"lambda":lam,
                                "method":name,"repeat":repeat,
                                "setup_s":prep,"fit_s":float("nan"),
                                "max_abs_error":float("nan"),
                                "relative_residual":float("nan"),
                                "pcg_iterations":None,
                                "stored_bytes":None,
                                "cached_factors":None,
                                "cache_hit":False,"status":init_status,
                            })
                            continue
                        started=perf_counter()
                        try:
                            actual=solver.fit(y,lambda_=lam,mu=mu)
                            elapsed=perf_counter()-started
                            error=float(np.max(abs(actual-truth)))
                            rel=direct_residual(y,actual,lam,d,mu)
                            # These are quality gates; errors are not removed
                            # from the saved raw measurements.
                            status=("ok" if error<=2e-6 and rel<=2e-7
                                    else "invalid_numerics")
                        except (ValueError, ArithmeticError, OverflowError,
                                np.linalg.LinAlgError) as exc:
                            elapsed=perf_counter()-started
                            status=type(exc).__name__+": "+str(exc)
                            error=rel=float("nan")
                        rows.append({
                            "n":n,"d":d,"mu":str(mu),"lambda":lam,
                            "method":name,"repeat":repeat,
                            "setup_s":prep,"fit_s":elapsed,
                            "max_abs_error":error,
                            "relative_residual":rel,
                            "pcg_iterations":solver.cg_iterations,
                            "stored_bytes":solver.stored_bytes,
                            "cached_factors":solver.cached_factor_count,
                            "cache_hit":cache_hit,"status":status,
                        })
            print(f"[{ci+1}/{len(cases(preset))}] n={n}, d={d}, mu={mu}",
                  flush=True)
    csv_path=target/"raw_measurements.csv"
    with csv_path.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    env["source_sha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (target/"environment.json").write_text(json.dumps(env,indent=2)+"\n",encoding="utf8")
    groups={}
    for row in rows:
        key=(row["n"],row["d"],row["mu"],row["lambda"],row["method"])
        groups.setdefault(key,[]).append(row)
    summary=[]
    for (n,d,mu,lam,method),group in groups.items():
        complete = all(r["status"]=="ok" for r in group)
        times=[r["fit_s"] for r in group if r["status"]=="ok"]
        warm = [r["fit_s"] for r in group if
                r["status"] == "ok" and r["cache_hit"]]
        setup = group[0]["setup_s"]
        summary.append(dict(
            n=n,d=d,mu=mu,lambda_=lam,method=method,
            valid=complete,valid_repetitions=len(times),
            median_fit_s=float(np.median(times)) if complete else float("nan"),
            first_cold_fit_s=group[0]["fit_s"] if complete else float("nan"),
            warm_cached_median_s=(
                float(np.median(warm)) if complete and warm else float("nan")),
            full_repeated_fit_s=sum(times) if complete else float("nan"),
            setup_plus_repeated_fit_s=(
                setup+sum(times) if complete else float("nan")),
            initial_setup_s=setup,
            max_error=max((r["max_abs_error"] for r in group if
                           np.isfinite(r["max_abs_error"])),default=float("nan")),
        ))
    with (target/"summary.csv").open("w",newline="",encoding="utf8") as h:
        w=csv.DictWriter(h,fieldnames=list(summary[0]))
        w.writeheader();w.writerows(summary)
    (target/"RESULTS.md").write_text(
        "# Experiment005 local fit-only run\n\n"
        f"- Preset: {preset}; attempted measurements: {len(rows)}\n"
        f"- Numerically valid measurements: {sum(r['status']=='ok' for r in rows)}\n"
        "- All failures remain in raw_measurements.csv.\n"
        "- First fit, subsequent cache hits, and end-to-end repeated costs are separate.\n"
        "- Timing ranks must use only cases with complete valid repetitions.\n"
        "- The original statistical-selection experiment remains separate.\n",
        encoding="utf8",
    )
    return rows,summary


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preset",choices=["smoke","quick","large"],default="smoke")
    p.add_argument("--repeats",type=int,default=2)
    p.add_argument("--threads",type=int,default=1)
    p.add_argument("--seed",type=int,default=20261102)
    p.add_argument("--output",type=Path,default=None)
    a=p.parse_args()
    run(a.preset,repeats=a.repeats,threads=a.threads,seed=a.seed,output=a.output)
