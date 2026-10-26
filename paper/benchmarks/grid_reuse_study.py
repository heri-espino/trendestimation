"""Six-backend GCV grid-search versus repeated-series factor-reuse benchmark.

Experiments vary difference order d, shared candidate budget M, independent
series count R, fixed numeric mu and two grids with MATCHED penalty endpoints:
log-lambda vs uniform normalized S mapped once to lambda.

Cold: prepare and search independently for each series, repeating setup.
Warm: prepare once for the full (n,d,lambda-grid), reuse fixed penalties'
Cholesky factors (and EDF), spectral decomposition or cached Q across R
independently sampled y. Every selected minimum is an actual GCV optimum
on the finite grid. Timings include factorization AND native EDF computation.
Grid construction is independent/common to backends and reported separately.

Crucially, GCV uses trace(H); for nonspectral methods this explicitly solves
n right-hand sides. Thus this is not the previous full-fit-only benchmark.
CV uses leverage diagonals and is NOT assessed by this GCV experiment.

Windows PowerShell:
 python paper/benchmarks/grid_reuse_study.py --preset quick --repeats 3
 python paper/benchmarks/grid_reuse_study.py --preset full --repeats 7
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from scipy.linalg import (
    cho_factor, cho_solve, cholesky_banded, cho_solve_banded, solve_banded,
)
from scipy.special import binom
from threadpoolctl import threadpool_info, threadpool_limits

from cholesky_comparison import METHODS, _mu_shift
from run_benchmarks import forward_differences, directly_banded_penalty
from trendestimation import TrendSmoother
from trendestimation.solvers import _penalty_lower_bands

HERE = Path(__file__).resolve().parent
NAMES = ("dense_fresh", "dense_cached", "spectral", "banded",
         "dense_cholesky", "banded_cholesky")
assert NAMES == METHODS


def grids(n: int, d: int, M: int):
    """Both policies share identical safe finite lambda endpoints.

    Restrict spectral condition number to approximately 1e8 to keep
    dense positive-definite factorizations meaningful at high d.
    """
    spectral = TrendSmoother(n, order=d)
    positive = spectral.eigenvalues[:n-d]
    low = 1e-3 / float(np.median(positive))
    high = min(1e3 / float(np.median(positive)),
               1e8 / float(np.max(positive)))
    if high <= low:
        raise ValueError("No safe positive penalty interval")
    lam = np.geomspace(low, high, M)
    bounds = [spectral.smoothness(float(v)) for v in (low, high)]
    s = np.linspace(bounds[0], bounds[1], M)
    start = perf_counter()
    mapped = np.asarray([
        spectral.lambda_for_smoothness(float(v)) for v in s
    ])
    mapping_s = perf_counter() - start
    # Enforce mathematical equivalence at the same endpoints.
    mapped[0], mapped[-1] = low, high
    recovered = np.array([spectral.smoothness(float(v)) for v in mapped])
    if not np.allclose(recovered, s, atol=5e-10, rtol=0):
        raise AssertionError("Failed to invert normalized S grid")
    return {"log_lambda":lam, "uniform_s":mapped}, bounds, mapping_s


class CandidateSearch:
    """Native six-solver GCV evaluation with optional cross-series caching."""

    def __init__(self, n: int, d: int, mu: float, method: str,
                 penalties, *, reuse: bool):
        if method not in METHODS:
            raise ValueError(method)
        self.n, self.d, self.mu, self.method = n, d, mu, method
        self.lambdas = np.asarray(penalties, dtype=float)
        self.reuse = reuse
        self.identity = np.eye(n)
        self.saved = {}
        self.shift = None
        self.reference = None
        if method == "spectral":
            self.model = TrendSmoother(n, order=d)
            self.basis = self.model.eigenvectors
            self.deltas = self.model.eigenvalues
            self.reference = float(mu)*binom(np.arange(n,dtype=float),d)
        elif method == "dense_fresh":
            pass  # actual D and Q are rebuilt at each penalty
        elif method in ("dense_cached", "dense_cholesky"):
            self.D = forward_differences(n,d)
            self.Q = self.D.T @ self.D
            self.shift = float(mu) * (self.D.T @ np.ones(n-d))
        else:
            self.shift = _mu_shift(n,d,mu)
            if method == "banded":
                self.bands = directly_banded_penalty(n,d)
            else:
                self.bands = _penalty_lower_bands(n,d)

        if reuse:
            # Full cache initialization is within setup timing. For Cholesky,
            # factor each candidate once and store its exact EDF.
            for j, lam in enumerate(self.lambdas):
                if method == "spectral":
                    alpha = 1/(1+lam*self.deltas)
                    self.saved[j] = (alpha, float(alpha.sum()))
                elif method == "dense_cholesky":
                    factor = cho_factor(self.identity+lam*self.Q,
                                        lower=True,check_finite=False)
                    edf = np.trace(cho_solve(factor,self.identity,
                                             check_finite=False))
                    self.saved[j] = (factor,float(edf))
                elif method == "banded_cholesky":
                    ab = lam*self.bands.copy()
                    ab[0] += 1.0
                    factor = cholesky_banded(ab,lower=True,check_finite=False)
                    edf = np.trace(cho_solve_banded(
                        (factor,True),self.identity,check_finite=False))
                    self.saved[j] = (factor,float(edf))

    def scores(self, y):
        y = np.asarray(y,dtype=float)
        if y.shape != (self.n,):
            raise ValueError("Expected one fixed-size data vector")
        scores = np.empty(len(self.lambdas))
        if self.method == "spectral":
            coords = self.basis.T @ (y-self.reference)
        for j,lam in enumerate(self.lambdas):
            if self.method == "spectral":
                if j in self.saved:
                    alpha, edf = self.saved[j]
                else:
                    alpha = 1/(1+lam*self.deltas)
                    edf = float(alpha.sum())
                trend = self.reference + self.basis @ (alpha*coords)
            elif self.method == "dense_fresh":
                D = forward_differences(self.n,self.d)
                Q = D.T @ D
                shift = float(self.mu)*(D.T@np.ones(self.n-self.d))
                A = self.identity+lam*Q
                trend = np.linalg.solve(A,y+lam*shift)
                edf = float(np.trace(np.linalg.solve(A,self.identity)))
            elif self.method == "dense_cached":
                A = self.identity+lam*self.Q
                trend = np.linalg.solve(A,y+lam*self.shift)
                edf = float(np.trace(np.linalg.solve(A,self.identity)))
            elif self.method == "banded":
                ab = lam*self.bands.copy()
                ab[self.d] += 1
                trend = solve_banded((self.d,self.d),ab,
                                     y+lam*self.shift,check_finite=False)
                edf = float(np.trace(solve_banded(
                    (self.d,self.d),ab,self.identity,check_finite=False)))
            elif self.method == "dense_cholesky":
                if j in self.saved:
                    factor,edf = self.saved[j]
                else:
                    factor=cho_factor(self.identity+lam*self.Q,
                                      lower=True,check_finite=False)
                    edf=float(np.trace(cho_solve(
                        factor,self.identity,check_finite=False)))
                trend=cho_solve(factor,y+lam*self.shift,check_finite=False)
            else:
                if j in self.saved:
                    factor,edf=self.saved[j]
                else:
                    ab=lam*self.bands.copy()
                    ab[0]+=1
                    factor=cholesky_banded(ab,lower=True,check_finite=False)
                    edf=float(np.trace(cho_solve_banded(
                        (factor,True),self.identity,check_finite=False)))
                trend=cho_solve_banded(
                    (factor,True),y+lam*self.shift,check_finite=False)
            # Same classical GCV objective for all six solver paths.
            # n*RSS/(n-EDF)^2, with invalid degenerate denominator rejected.
            scores[j] = self.n * np.sum((y-trend)**2)/(self.n-edf)**2
        if not np.all(np.isfinite(scores)):
            raise ArithmeticError("Nonfinite GCV candidate score")
        return scores


def data_vectors(n,d,seed,R):
    """Same independently seeded observations for both mu values."""
    rng=np.random.default_rng(np.random.SeedSequence([seed,n,d,R]))
    t=np.linspace(0,1,n)
    trend=.6*np.sin(7*t)+.3*np.cos(17*t)+.25*t
    return np.asarray([trend+rng.normal(0,.22,n) for _ in range(R)])


def measure_cell(n,d,M,R,mu,seed,grid_policy,penalties,repeats):
    observations=data_vectors(n,d,seed,R)
    # Untimed exact score comparison on all full candidate sets, all y.
    reference=CandidateSearch(n,d,mu,"spectral",penalties,reuse=True)
    truth=[reference.scores(y) for y in observations]
    results=[]
    for method in METHODS:
        # Prepare/cross-check warm and cold implementations outside timing.
        for cache in ("cold","warm"):
            if cache=="warm":
                prepared=CandidateSearch(n,d,mu,method,penalties,reuse=True)
                found=[prepared.scores(y) for y in observations]
            else:
                found=[CandidateSearch(n,d,mu,method,penalties,
                                       reuse=False).scores(y)
                       for y in observations]
            error = max(float(np.max(np.abs(a-b))) for a,b in zip(found,truth))
            scale = max(1.0,max(float(np.max(abs(v))) for v in truth))
            if error > 2e-5*scale:
                raise AssertionError(
                    f"score mismatch: {method=} {cache=} {n=} {d=} {M=} "
                    f"{R=} {mu=} {error=:.4g} {scale=:.4g}")
            # Check winner equivalence with a suitable numerical tolerance.
            for a,b in zip(found,truth):
                if not np.isclose(float(a.min()),float(b.min()),
                                  rtol=2e-5,atol=2e-7):
                    raise AssertionError("Optimum score mismatch")
            trials=[]
            for _ in range(repeats):
                begin=perf_counter()
                if cache=="warm":
                    model=CandidateSearch(n,d,mu,method,penalties,reuse=True)
                    setup=perf_counter()-begin
                    tick=perf_counter()
                    selected=[model.scores(y) for y in observations]
                    score_duration=perf_counter()-tick
                else:
                    setup=0.0
                    score_duration=0.0
                    for y in observations:
                        tick=perf_counter()
                        model=CandidateSearch(n,d,mu,method,penalties,
                                               reuse=False)
                        setup+=perf_counter()-tick
                        tick=perf_counter()
                        model.scores(y)
                        score_duration+=perf_counter()-tick
                trials.append((setup,score_duration))
            arr=np.asarray(trials)
            total=arr.sum(axis=1)
            results.append({
                "n":n,"d":d,"M":M,"R":R,"mu":mu,"seed":seed,
                "grid_policy":grid_policy,"reuse":cache,"method":method,
                "repeats":repeats,
                "setup_median_s":float(np.median(arr[:,0])),
                "search_median_s":float(np.median(arr[:,1])),
                "total_median_s":float(np.median(total)),
                "total_MAD_s":float(np.median(abs(total-np.median(total)))),
                "max_score_difference":error,
                "selected_score_mean":float(np.mean([v.min() for v in found])),
                "mean_optimum_s":float(np.mean([np.argmin(v) for v in found])),
            })
    return results


def workload(preset):
    if preset=="smoke":
        return ((24,), (1,2), (5,), (1,2))
    if preset=="quick":
        return ((48,), (1,2,3,4), (5,11), (1,4))
    if preset=="full":
        return ((48,80), (1,2,3,4,5), (5,11,21), (1,4,10))
    raise ValueError(preset)


def run(preset="quick",repeats=3,blas_threads=1,seed=20261026,
        output_dir=HERE/"results"/"grid_reuse"):
    if repeats<1 or blas_threads<1:
        raise ValueError("repeats and BLAS threads must be >=1")
    output_dir=Path(output_dir)
    n_values, orders, M_values, R_values=workload(preset)
    outcomes=[]
    grids_used=[]
    with threadpool_limits(limits=blas_threads):
        env={
            "timestamp_utc":datetime.now(timezone.utc).isoformat(),
            "platform":platform.platform(), "cpu":platform.processor(),
            "python":sys.version,"numpy":np.__version__,
            "scipy":scipy.__version__, "logical_cpus":os.cpu_count(),
            "threadpools":threadpool_info(),"blas_threads":blas_threads,
            "preset":preset,"repeats":repeats,"seed":seed,
            "methods":list(METHODS),"orders":list(orders),
            "grid_policies":["log_lambda","uniform_s"],
            "mu_values":[0.0,0.15],
            "git_revision":os.environ.get("GITHUB_SHA","local-unrecorded"),
            "note":"Genuine host-specific GCV grid search, not fit-only timing; "
                   "all lambda candidates shared across backends. "
                   "S grid inversion is separately timed and excluded from "
                   "per-backend solver totals. No CV leverage evaluation.",
        }
        total_cells=len(n_values)*len(orders)*len(M_values)*len(R_values)*2*2
        cell=0
        for n in n_values:
            for d in orders:
                for M in M_values:
                    candidate_grids,s_bounds,map_s=grids(n,d,M)
                    for policy,penalties in candidate_grids.items():
                        grids_used.append(dict(
                            n=n,d=d,M=M,grid_policy=policy,
                            lambda_min=float(penalties[0]),
                            lambda_max=float(penalties[-1]),
                            S_min=float(s_bounds[0]),S_max=float(s_bounds[1]),
                            mapping_s=float(map_s if policy=="uniform_s" else 0)))
                        for R in R_values:
                            for mu in (0.0,0.15):
                                cell+=1
                                current=measure_cell(
                                    n,d,M,R,mu,seed,policy,
                                    penalties,repeats)
                                outcomes.extend(current)
                                fastest=min((r for r in current if r["reuse"]=="warm"),
                                            key=lambda v:v["total_median_s"])
                                print(f"[{cell}/{total_cells}] n={n} d={d} M={M} "
                                      f"R={R} mu={mu:g} {policy}: "
                                      f"warm winner={fastest['method']}, "
                                      f"ms={1e3*fastest['total_median_s']:.3f}",
                                      flush=True)
    output_dir.mkdir(parents=True,exist_ok=True)
    for name,rows in (("gcv_grid_timings.csv",outcomes),
                      ("grid_metadata.csv",grids_used)):
        with (output_dir/name).open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    (output_dir/"environment.json").write_text(
        json.dumps(env,indent=2),encoding="utf-8")
    print("All GCV parity checks passed; measurements:",output_dir)
    return outcomes


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset",choices=("smoke","quick","full"),default="quick")
    parser.add_argument("--repeats",type=int,default=3)
    parser.add_argument("--blas-threads",type=int,default=1)
    parser.add_argument("--seed",type=int,default=20261026)
    parser.add_argument("--output-dir",type=Path,
                        default=HERE/"results"/"grid_reuse")
    args=parser.parse_args()
    run(args.preset,args.repeats,args.blas_threads,args.seed,args.output_dir)

if __name__=="__main__":
    main()
