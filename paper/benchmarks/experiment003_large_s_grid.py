#!/usr/bin/env python3
"""Experiment003 — long-series preparation, S->lambda mapping, and cache reuse.

Independent, new benchmark; do not overwrite experiments 001 or 002.
A matched finite S grid is inverted using both (1) banded eigenvalues only,
and (2) the existing full-SVD TrendSmoother. Every solver receives the
SAME precomputed lambda candidates. An explicitly known-lambda banded
baseline does NOT pay for finding the inverse mapping.

Phases are timed separately:
  (A) banded penalty assembly / eigenvalues-only setup / full-SVD setup
  (B) one entire S->lambda map with either cached spectrum
  (C) banded factor-grid creation
  (D) one/remaining series: uncached or cached banded full trends,
      full spectral trends, native-S GCV or mapped-grid GCV
  (E) derived total workflow costs (sums of measured components)

Use --preset smoke to verify on a cheap machine. Publication-quality runs
on the author's own workstation use --preset full or --preset large.
No previous benchmark results are read or rewritten.

PowerShell:
 python paper/benchmarks/experiment003_large_s_grid.py --preset smoke --no-publish
 python paper/benchmarks/experiment003_large_s_grid.py --preset quick --publish
 python paper/benchmarks/experiment003_large_s_grid.py --preset full --publish
 python paper/benchmarks/experiment003_large_s_grid.py --preset large --publish

Run only ONE publication preset at a time. Raw rows, source snapshot, QA
and analysis are saved in a unique GitHub-tracked run folder.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from scipy.linalg import cholesky_banded, cho_solve_banded, eig_banded
from scipy.optimize import brentq
from scipy.special import binom, expit
from threadpoolctl import threadpool_info, threadpool_limits

from trendestimation import TrendSmoother
from trendestimation.solvers import _penalty_lower_bands

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "paper" / "benchmarks" / "experiment003_large_s_grid"
PHASES = (
    "bands_setup", "band_eigenvalues_setup", "svd_setup",
    "s_grid_map_banded", "s_grid_map_svd", "chol_factor_grid",
    "chol_uncached_first", "chol_uncached_remaining",
    "chol_cached_first", "chol_cached_remaining",
    "spectral_trends_first", "spectral_trends_remaining",
    "gcv_native_first", "gcv_native_remaining",
    "gcv_mapped_first", "gcv_mapped_remaining",
)
PRESETS = {
    "smoke": ([(48, 2, 5, 2)], [0.0], 1, 1),
    "quick": ([(128, 2, 11, 4), (256, 2, 11, 4),
               (256, 2, 1, 4), (256, 2, 21, 4)], [0.0, 0.15], 2, 3),
    "full": ([(256, 2, 21, 4), (512, 2, 21, 4),
              (1024, 2, 21, 4), (512, 2, 1, 4),
              (512, 2, 81, 4), (512, 1, 21, 4),
              (512, 3, 21, 4), (512, 2, 21, 1),
              (512, 2, 21, 12)], [0.0, 0.15], 3, 4),
    # Larger n clearly separates asymptotic trends but SVD is expensive.
    "large": ([(1024, 2, 21, 4), (1536, 2, 21, 4),
               (2048, 2, 21, 4), (1024, 2, 81, 4)],
              [0.0, 0.15], 2, 3),
}


def timed(callback):
    start = perf_counter()
    result = callback()
    elapsed = perf_counter() - start
    if not (math.isfinite(elapsed) and elapsed >= 0):
        raise ArithmeticError("Invalid elapsed time")
    return result, elapsed


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def git_revision():
    try:
        return _git("rev-parse", "HEAD")
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def data_vectors(n, d, R, seed):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, n)
    trend = 0.65 * np.sin(t * 8) + 0.18 * np.cos(t * 17) + 0.4 * t
    return rng.normal(loc=trend, scale=0.22, size=(R, n))


def positive_banded_eigenvalues(bands, n, d):
    """Obtain only the eigenvalues, never the dense n-by-n eigenvectors."""
    values = eig_banded(bands, lower=True, eigvals_only=True, check_finite=False)
    values = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(values)) or values.shape != (n,):
        raise ArithmeticError("Banded eigenvalue solver returned invalid spectrum")
    # The smallest d modes are theoretically zero; compare to a zero tolerance.
    if values[d] <= 0:
        raise ArithmeticError(
            f"Positive penalty eigenvalues not resolved (n={n}, d={d}); "
            "record this limitation; do not silently change the solver."
        )
    return values[d:]


def map_s_grid(svals, eigenvalues):
    """Invert using a stable log-penalty coordinate and spectrum only."""
    positive = np.asarray(eigenvalues, dtype=float)
    if np.any(~np.isfinite(positive)) or np.any(positive <= 0):
        raise ValueError("Must provide only positive penalty eigenvalues")
    logdelta = np.log(positive)
    low = -float(np.max(logdelta)) - 42.
    high = -float(np.min(logdelta)) + 42.

    def s_at(loglam):
        return float(np.mean(expit(loglam + logdelta)))

    lambdas = []
    for s in svals:
        target = float(s)
        if not 0 < target < 1:
            raise ValueError("Timing grid must use interior S targets")
        root = brentq(lambda z: s_at(z)-target, low, high,
                      xtol=1e-12, rtol=9e-15, maxiter=180)
        lam = float(np.exp(root))
        if not np.isfinite(lam):
            raise ArithmeticError("S inverse not finite")
        lambdas.append(lam)
    result = np.asarray(lambdas)
    if not np.all(np.diff(result) > 0):
        raise ArithmeticError("Mapped penalties must be strictly increasing")
    attained = np.array([s_at(math.log(v)) for v in result])
    if not np.allclose(attained, svals, rtol=0, atol=5e-10):
        raise ArithmeticError("S-to-lambda mapped candidates miss target")
    return result


def _chol_factors(bands, lambdas):
    return [
        cholesky_banded(
            make_matrix(bands, float(lam)), lower=True, check_finite=False
        ) for lam in lambdas
    ]


def make_matrix(bands, lam):
    factor = np.asarray(bands, dtype=float).copy()
    factor *= lam
    factor[0] += 1.
    return factor


def _reference(n, d, mu):
    return float(mu)*binom(np.arange(n,dtype=float),d)


def chol_curves(y, reference, bands, lambdas, factors=None):
    rhs=np.asarray(y)-reference
    last=None
    for j,lam in enumerate(lambdas):
        factor = (factors[j] if factors is not None
                  else cholesky_banded(
                      make_matrix(bands,float(lam)),lower=True,
                      check_finite=False))
        last=reference+cho_solve_banded(
            (factor,True),rhs,check_finite=False
        )
        if not np.all(np.isfinite(last)):
            raise ArithmeticError("Nonfinite banded curve")
    return last


def spectral_curves(model, y, mu, lambdas):
    # Real spectral computation, project each series once for all M curves.
    _, _, reference, coordinates = model._prepare(y, mu)
    last=None
    for lam in lambdas:
        alpha=model._attenuation(float(lam))
        last=reference + model.eigenvectors @ (alpha*coordinates)
    return last


def gcv_scores(model, y, mu, lambdas):
    """Classical fixed-mu spectral GCV: RSS, EDF, identical penalties."""
    _, _, _, coordinates=model._prepare(y,mu)
    squared=coordinates*coordinates
    n=model.n
    scores=[]
    for lam in lambdas:
        a=model._attenuation(float(lam))
        edf=float(a.sum())
        denom=n-edf
        if not np.isfinite(denom) or denom<=1e-10:
            raise ArithmeticError("Undefined GCV denominator")
        rss=float(np.dot((1.-a)**2,squared))
        scores.append(float(n*rss/(denom*denom)))
    return np.asarray(scores)


def single_measure(n, d, M, R, mu, seed, repetition):
    sgrid=np.linspace(.15,.8,M)
    rng_seed=int(seed+1009*n+37*d+19*M)
    ys=data_vectors(n,d,R,rng_seed)
    reference=_reference(n,d,mu)
    bands,t_bands=timed(lambda:_penalty_lower_bands(n,d))
    band_eigs,t_band_eigs=timed(lambda:positive_banded_eigenvalues(bands,n,d))
    model,t_svd=timed(lambda:TrendSmoother(n,order=d))
    lb,t_map_banded=timed(lambda:map_s_grid(sgrid,band_eigs))
    ls,t_map_svd=timed(lambda:map_s_grid(sgrid,model.eigenvalues[:n-d]))
    # Both candidate maps must match. This is *not* a separate log-lambda grid.
    map_error=float(np.max(np.abs(lb-ls)/np.maximum(1.,ls)))
    if map_error>2e-5:
        raise ArithmeticError(f"Banded and SVD S inverses disagree: {map_error}")
    lambdas=ls
    factors,t_factors=timed(lambda:_chol_factors(bands,lambdas))

    # Independent QA outside timing: compare full trends and objective scores.
    sample=[0,M//2,M-1]
    max_abs=0.
    for j in sample:
        lam=float(lambdas[j])
        candidate=chol_curves(ys[0],reference,bands,[lam])
        target=spectral_curves(model,ys[0],mu,[lam])
        max_abs=max(max_abs,float(np.max(abs(candidate-target))))
    if max_abs>1e-5:
        raise ArithmeticError(f"Banded vs SVD trend disagreement: {max_abs}")
    z=gcv_scores(model,ys[0],mu,lambdas)
    if not np.all(np.isfinite(z)):
        raise ArithmeticError("Nonfinite mapped GCV scores")
    values=[]
    def record(phase,seconds):
        values.append({"phase":phase,"seconds":float(seconds)})

    for phase,value in [
        ("bands_setup",t_bands), ("band_eigenvalues_setup",t_band_eigs),
        ("svd_setup",t_svd),("s_grid_map_banded",t_map_banded),
        ("s_grid_map_svd",t_map_svd),("chol_factor_grid",t_factors)
    ]:
        record(phase,value)

    functions={
        "chol_uncached":lambda y:chol_curves(y,reference,bands,lambdas),
        "chol_cached":lambda y:chol_curves(y,reference,bands,lambdas,factors),
        "spectral_trends":lambda y:spectral_curves(model,y,mu,lambdas),
        "gcv_native":lambda y:gcv_scores(
            model,y,mu,map_s_grid(sgrid,model.eigenvalues[:n-d])),
        "gcv_mapped":lambda y:gcv_scores(model,y,mu,lambdas),
    }
    # Randomize method ordering in each block to limit systematic drift.
    names=list(functions)
    random.Random(seed*1111+repetition).shuffle(names)
    summaries={}
    for method in names:
        f=functions[method]
        _,first=timed(lambda:f(ys[0]))
        _,remaining=timed(lambda:[f(y) for y in ys[1:]])
        record(method+"_first",first)
        record(method+"_remaining",remaining)
        summaries[method]=(first,remaining)
    # Derived arithmetic explicitly separates common setup and measured use.
    endtotals={
        "chol_lambda_cold":t_bands+sum(summaries["chol_uncached"]),
        "chol_lambda_cached":t_bands+t_factors+sum(summaries["chol_cached"]),
        "chol_S_band_eigs_cached":t_bands+t_band_eigs+t_map_banded
                                  +t_factors+sum(summaries["chol_cached"]),
        "spectral_lambda_trends":t_svd+sum(summaries["spectral_trends"]),
        "spectral_S_trends":t_svd+t_map_svd+sum(summaries["spectral_trends"]),
        "spectral_lambda_GCV":t_svd+sum(summaries["gcv_mapped"]),
        "spectral_S_GCV_native":t_svd+sum(summaries["gcv_native"]),
        "spectral_S_GCV_cached":t_svd+t_map_svd+sum(summaries["gcv_mapped"]),
    }
    return values, endtotals, {
        "max_abs_trend_error":max_abs,
        "max_relative_lambda_map_error":map_error,
        "selected_gcv_s":float(sgrid[int(np.argmin(z))]),
        "min_gcv":float(np.min(z)),
        "spectral_basis_bytes":int(model.eigenvectors.nbytes+model.eigenvalues.nbytes),
        "banded_factor_grid_bytes":int(sum(f.nbytes for f in factors)),
        "banded_eigen_spectrum_bytes":int(band_eigs.nbytes),
    }


def csv_write(path,rows):
    if not rows:
        raise ValueError("Cannot write empty experiment")
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def aggregate(raw,key,value):
    groups=defaultdict(list)
    for row in raw:
        tag=tuple(row[k] for k in key)
        groups[tag].append(float(row[value]))
    out=[]
    for k,values in sorted(groups.items()):
        a=np.asarray(values)
        out.append(dict(zip(key,k),n_samples=len(a),
                        median_seconds=float(np.median(a)),
                        mad_seconds=float(np.median(abs(a-np.median(a)))),
                        min_seconds=float(a.min()),max_seconds=float(a.max())))
    return out


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def publish(run_dir):
    rel=run_dir.resolve().relative_to(ROOT.resolve())
    current=_git("branch","--show-current")
    if not current or current in ("main","master"):
        raise RuntimeError("Use a distinct experiment branch before --publish")
    # Commit only this run, not other dirty or unrelated repository changes.
    subprocess.run(["git","add","-f","--",str(rel)],cwd=ROOT,check=True)
    staged=_git("diff","--cached","--name-only")
    if not staged:
        return
    other=[line for line in staged.splitlines() if not line.startswith(rel.as_posix()+"/")]
    if other:
        raise RuntimeError(f"Unrelated changes already staged: {other}. "
                           "Do not mix them into a research experiment commit.")
    _git("commit","-m",f"experiment003: archive {run_dir.name} large-S-grid timings")
    subprocess.run(["git","push","origin",current],cwd=ROOT,check=True)
    print(f"[experiment003] GitHub artifacts pushed to branch {current}",flush=True)


def run(preset="smoke",seed=20261028,blas_threads=1,
        run_dir=None,publish_results=False):
    if preset not in PRESETS:
        raise ValueError("Unknown preset")
    if blas_threads<1:
        raise ValueError("blas_threads must be >=1")
    cases,mus,seeds,repeats=PRESETS[preset]
    if run_dir is None:
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir=BASE/"runs"/f"exp003_{stamp}_{preset}_seed{seed}"
    run_dir=Path(run_dir).resolve()
    if run_dir.exists():
        raise FileExistsError(f"Never overwrite an experiment run: {run_dir}")
    run_dir.mkdir(parents=True)
    metadata={
        "experiment":"experiment003","preset":preset,
        "utc_start":datetime.now(timezone.utc).isoformat(),
        "git_revision":git_revision(),"platform":platform.platform(),
        "python":sys.version,"numpy":np.__version__,"scipy":scipy.__version__,
        "processor":platform.processor(),"logical_cpus":os.cpu_count(),
        "blas_threads":blas_threads,"threads":None,
        "seed_root":seed,"independent_seed_count":seeds,
        "technical_repetitions":repeats,"cases":cases,"mus":mus,
        "s_range":[.15,.8],"note":(
            "Independent synthetic series; exact matched S->lambda grid. "
            "Banded-eigenvalues-only and SVD mapping separately timed. "
            "Cholesky known-lambda baseline excludes mapping by design. "
            "Full curve timing and GCV scoring are separate workloads. "
            "Aggregated end-to-end costs sum independently measured phases. "
            "Do not use technical repetitions as independent data seeds."
        )
    }
    raw,full,quality=[],[],[]
    try:
        (run_dir/"environment.json").write_text(
            json.dumps(metadata,indent=2)+"\n",encoding="utf-8"
        )
        with threadpool_limits(limits=blas_threads):
            metadata["threads"]=threadpool_info()
            total=len(cases)*len(mus)*seeds*repeats
            counter=0
            for n,d,M,R in cases:
                for mu in mus:
                    for i in range(seeds):
                        real_seed=seed+100003*i
                        for repeat in range(repeats):
                            counter+=1
                            print(f"[{counter}/{total}] n={n},d={d},M={M},"
                                  f"R={R},mu={mu},seed={real_seed},"
                                  f"repeat={repeat}",flush=True)
                            phases,endtoend,qa=single_measure(
                                n,d,M,R,mu,real_seed,repeat
                            )
                            common=dict(n=n,d=d,M=M,R=R,mu=mu,
                                        seed=real_seed,repeat=repeat)
                            raw.extend({**common,**p} for p in phases)
                            full.extend({**common,"workflow":name,
                                         "seconds":float(value)}
                                        for name,value in endtoend.items())
                            quality.append({**common,**qa})
        metadata["utc_end"]=datetime.now(timezone.utc).isoformat()
        csv_write(run_dir/"raw_phases.csv",raw)
        csv_write(run_dir/"raw_workflows.csv",full)
        csv_write(run_dir/"numerical_validation.csv",quality)
        key=["n","d","M","R","mu"]
        csv_write(run_dir/"phase_summary.csv",
                  aggregate(raw,key+["phase"],"seconds"))
        csv_write(run_dir/"workflow_summary.csv",
                  aggregate(full,key+["workflow"],"seconds"))
        # Median technical timing within each independent data seed;
        # this is the valid unit for any subsequent cross-seed inference.
        csv_write(run_dir/"seed_level_workflows.csv",
                  aggregate(full,key+["seed","workflow"],"seconds"))
        csv_write(run_dir/"seed_level_phases.csv",
                  aggregate(raw,key+["seed","phase"],"seconds"))
        metadata["raw_phase_rows"]=len(raw)
        metadata["workflow_rows"]=len(full)
        metadata["max_abs_trend_error"]=max(x["max_abs_trend_error"]
                                          for x in quality)
        (run_dir/"environment.json").write_text(
            json.dumps(metadata,indent=2)+"\n",encoding="utf-8"
        )
        manifest={"experiment":"experiment003","complete":True,
                  "git_revision":metadata["git_revision"],
                  "files":{p.name:sha256(p) for p in sorted(run_dir.iterdir())
                           if p.is_file() and p.name!="manifest.json"}}
        (run_dir/"manifest.json").write_text(
            json.dumps(manifest,indent=2)+"\n",encoding="utf-8"
        )
        print(f"[experiment003] COMPLETE — {len(raw)} raw phase rows; "
              f"{len(full)} derived workflow rows; folder: {run_dir}",flush=True)
        if publish_results:
            publish(run_dir)
        return run_dir
    except BaseException as error:
        # Preserve informative crash and partial progress before VM closes.
        (run_dir/"FAILURE.txt").write_text(
            f"{type(error).__name__}: {error}\n"
            f"Collected {len(raw)} phase records, {len(full)} workflows.\n",
            encoding="utf-8",
        )
        if raw: csv_write(run_dir/"partial_phases.csv",raw)
        if full: csv_write(run_dir/"partial_workflows.csv",full)
        if quality: csv_write(run_dir/"partial_validation.csv",quality)
        if publish_results:
            try: publish(run_dir)
            except Exception as e:
                print(f"Could not push partial results: {e}",file=sys.stderr)
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset",choices=tuple(PRESETS),default="smoke")
    parser.add_argument("--seed",type=int,default=20261028)
    parser.add_argument("--blas-threads",type=int,default=1)
    parser.add_argument("--run-dir",type=Path,default=None)
    parser.add_argument("--publish",dest="publish",action="store_true",
                        help="Commit and push generated artifacts on current feature branch")
    parser.add_argument("--no-publish",dest="publish",action="store_false")
    parser.set_defaults(publish=False)
    opts=parser.parse_args()
    run(preset=opts.preset,seed=opts.seed,blas_threads=opts.blas_threads,
        run_dir=opts.run_dir,publish_results=opts.publish)


if __name__=="__main__":
    main()
