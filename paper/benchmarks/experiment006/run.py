"""Experiment006: timed full-criterion selection on a single reproducible slice.

The entire 7*n, 6*d, 3*mu, 2*scale, 4*grid, 5*criterion
experiment is sliced by CLI arguments to avoid an impossible single job.
Four workloads: (R=1,M=1), (R=1,M>1), (R>1,M=1), (R>1,M>1).
Same candidate set for direct-S (inversion per candidate) and mapped-lambda
(one translation shared per search). Timings include *all* work.

Run from repo root (the recommended entrypoint is PowerShell):
 python paper/benchmarks/experiment006/run.py --preset smoke
 python paper/benchmarks/experiment006/run.py --n 256 --d 3 \
   --mu 0.15 --amplitude high --criterion gcv --grid-denominator 1000 \
   --methods banded_cholesky,spectral_svd,naive_inverse --repeats 5 \
   --output paper/benchmarks/experiment006/runs/my-host/exp006-a

CAVEAT: Only spectral SVD, banded+selected-inverse and actual dense
inverse currently implement complete criteria. Other Experiment005
backends are fit-only and are intentionally not disguised as selectors.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import tracemalloc
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from scipy.special import binom
from threadpoolctl import threadpool_info, threadpool_limits

from trendestimation import TrendSmoother, PreparedPLSSolver
from trendestimation.core import difference_matrix
from trendestimation.criteria import _score_from_coordinates
from selected_inverse import BandedTrace, selected_inverse, difference_gram_logdet

HYBRID_METHODS=(
    "banded_lu_banded_trace","sparse_lu_banded_trace",
    "sparse_cholesky_banded_trace","pcg_fft_banded_trace",
    "pcg_dst_banded_trace","pcg_jacobi_banded_trace")
METHODS=("naive_inverse","spectral_svd","banded_cholesky",
         "guarded_svd_cholesky")+HYBRID_METHODS
CRITERIA=("cv","gcv","bic","aicc","mle")
POLICIES=("direct_s","mapped_lambda")
SCENARIOS=("one_s_one_series","grid_one_series",
           "one_s_multiple_series","grid_multiple_series")
N_LEVELS=(64,128,256,512,1024,16384,131072)
D_LEVELS=(1,2,3,4,5,6)
GRID_DENOMINATORS=(100,1000,10000,100000)


def grid_of_s(denominator:int):
    """Exactly {1/M,2/M,...,(M-1)/M,1}; natively includes exact S=1."""
    if denominator not in GRID_DENOMINATORS:
        raise ValueError(f"grid denominator not in {GRID_DENOMINATORS}")
    g=np.arange(1,denominator+1,dtype=float)/denominator
    g[-1]=1.
    return g


def sample(n:int,seed:int,amplitude:str):
    if amplitude not in ("low","high"):
        raise ValueError("Amplitude must be low or high")
    t=np.linspace(0,1,n)
    rng=np.random.default_rng(seed)
    base=.5*np.sin(2*np.pi*t)+.2*t+rng.normal(0,.1,n)
    return (1e-3 if amplitude=="low" else 1e6)*base


def git_sha():
    try:
        return subprocess.run(
            ["git","rev-parse","HEAD"],text=True,check=True,
            capture_output=True,timeout=5).stdout.strip()
    except (OSError,subprocess.SubprocessError):
        return "unknown"


def naive_score(n,d,y,lam,mu,criterion,Q=None,H=None):
    """Actual dense inverse baseline, not a hidden solve."""
    if not np.isfinite(lam):
        return BandedTrace(n,d).fit_stats(y,lam,mu,criterion)["score"]
    if Q is None:
        D=difference_matrix(n,d)
        Q=D.T@D
    else:
        D=None
    A=np.eye(n)+lam*Q
    # Deliberately naive dense inversion per lambda if inverse isn't cached.
    H=np.linalg.inv(A) if H is None else H
    edf=float(np.trace(H))
    ref=mu*binom(np.arange(n,dtype=float),d)
    centered=y-ref
    residual=centered-H@centered
    rss=float(residual@residual)
    if criterion=="cv":
        denom=1-np.diag(H)
        if np.any(denom<=0): return float("inf")
        return float(np.mean((residual/denom)**2))
    if criterion=="gcv":
        den=1-edf/n
        return float((rss/n)/den**2) if den>1e-10 else float("inf")
    if criterion=="mle":
        if lam<=0: return float("inf")
        m=n-d
        weighted=float(centered@residual)
        if weighted<=0: return float("inf")
        sign,logdet=np.linalg.slogdet(A)
        if sign<=0: raise ArithmeticError("Dense A determinant invalid")
        return float(m*np.log(weighted/m)+logdet-m*np.log(lam)-difference_gram_logdet(n,d))
    eps=np.finfo(float).eps*max(1.,float(centered@centered))
    if rss<=eps: return float("inf")
    base=float(np.log(rss/n))
    if criterion=="bic": return base+edf*np.log(n)/n
    den=n-edf-2
    return (base+(2*edf+1)/den if den>0 else float("inf"))


def memory_budget_status(n,d,method,denom,max_dense_bytes,max_work,scenario,R,repeats,*,
                         allow_unbounded_runtime=False):
    """A skip is an explicit reproducible result, never an unnoticed omission."""
    M=1 if scenario.startswith("one_s") else denom
    if method=="naive_inverse":
        if n*n*8*7>max_dense_bytes:
            return "infeasible_dense_memory"
        if n>512 and not allow_unbounded_runtime:
            return "infeasible_naive_runtime"
    if method in ("spectral_svd","guarded_svd_cholesky") and (
            method=="spectral_svd" or d>=5):
        if n*n*8*5>max_dense_bytes:
            return "infeasible_dense_memory"
        if n>2048 and not allow_unbounded_runtime:
            return "infeasible_svd_runtime"
    # Conservative accounting in Python loop units; override explicitly
    # on a machine capable of completing this particular slice.
    work=float(n)*max(1,d*d)*M*R*repeats
    if method=="naive_inverse":
        work=float(n**3)*M*R*repeats
    if method=="spectral_svd" or (
            method=="guarded_svd_cholesky" and d>=5):
        work=float(n*n)*M*R*repeats
    if work>max_work: return "budget_exceeded"
    return "eligible"


class Evaluator:
    def __init__(self,n,d,method):
        self.n,self.d,self.method=n,d,method
        # Conservative, explicit policy: use independently accuracy-verified
        # shift-free spectral formulation for d>=5. For d<=4 use banded.
        # Dense memory/runtime gates prevent claiming large-n applicability.
        self.actual_backend=(
            ("spectral_svd" if d>=5 else "banded_cholesky")
            if method=="guarded_svd_cholesky" else method)
        self.spectral=(TrendSmoother(n,d)
                       if self.actual_backend=="spectral_svd" else None)
        self.banded=(BandedTrace(n,d) if (
            self.actual_backend=="banded_cholesky" or
            method in HYBRID_METHODS
        ) else None)
        self.hybrid=None
        if method in HYBRID_METHODS:
            if method.startswith("pcg_"):
                pc=method.split("_")[1]
                self.hybrid=PreparedPLSSolver(
                    n,d,method="pcg",preconditioner=pc,
                    cg_rtol=1e-9,cg_maxiter=min(5000,10*n))
            else:
                self.hybrid=PreparedPLSSolver(
                    n,d,method=method.removesuffix("_banded_trace"),
                    factor_cache=False)
        self.Q=None
        if method=="naive_inverse":
            D=difference_matrix(n,d)
            self.Q=D.T@D
        self._cache={}
        self._cached_diagnostics={}

    def prepare_series(self,y,mu):
        """Spectral projection cached per independent series, not per lambda."""
        if self.spectral is None:return None
        _,_,_,coord=self.spectral._prepare(y,mu)
        return coord

    def evaluate(self,y,mu,lam,criterion,coordinates=None,
                 reuse_factor=False):
        if self.spectral is not None:
            return _score_from_coordinates(
                self.spectral,coordinates,lambda_=lam,name=criterion)
        if self.banded is not None:
            L=z=None
            if np.isfinite(lam) and reuse_factor:
                if lam not in self._cache:
                    factor=self.banded.factor(lam)
                    chosen=selected_inverse(factor)
                    self._cache[lam]=factor
                    self._cached_diagnostics[lam]=chosen
                L=self._cache[lam]
                z=self._cached_diagnostics[lam]
            if self.hybrid is not None:
                if np.isposinf(lam):
                    return self.banded.fit_stats(
                        y,lam,mu,criterion)["score"]
                if self.hybrid.structured is not None:
                    self.hybrid.structured.factor_cache=reuse_factor
                tau=self.hybrid.fit(y,lambda_=lam,mu=mu)
                return self.banded.score_external(
                    y,tau,lam,mu,criterion,factor=L,selected=z)
            return self.banded.fit_stats(
                y,lam,mu,criterion,factor=L,selected=z)["score"]
        H=None
        if np.isfinite(lam) and reuse_factor:
            if lam not in self._cache:
                self._cache[lam]=np.linalg.inv(np.eye(self.n)+lam*self.Q)
            H=self._cache[lam]
        return naive_score(
            self.n,self.d,y,lam,mu,criterion,Q=self.Q,H=H
        )


def _row(n,d,mu,amplitude,criterion,denom,method,policy,scenario,
         repeat,R,M,setup_s,map_s,eval_s,score,s_selected,status,
         candidates,comment=""):
    return dict(
        n=n,d=d,mu=str(mu),amplitude=amplitude,criterion=criterion,
        grid_denominator=denom,method=method,coordinate=policy,
        workload=scenario,repeat=repeat,R=R,M=M,
        selected_s=s_selected,selected_score=score,
        method_setup_s=setup_s,s_to_lambda_s=map_s,
        candidate_evaluation_s=eval_s,
        total_cold_s=setup_s+map_s+eval_s,
        total_warm_s=map_s+eval_s,
        evaluations=candidates,status=status,comment=comment,
    )


def run_slice(n=64,d=2,mu=0.,amplitude="low",criterion="gcv",
              denominator=100,methods=METHODS,repeats=3,R=8,
              max_work=5e7,max_dense_bytes=2*1024**3,
              output=None,threads=1,seed=20261102,
              conditional_data_mu=False,allow_unbounded_runtime=False):
    if n not in N_LEVELS or d not in D_LEVELS or d>=n:
        raise ValueError("n and d must be requested factorial levels")
    if criterion not in CRITERIA:raise ValueError("Unknown criterion")
    if isinstance(mu,str) and mu!="data":
        raise ValueError("mu must be numeric or 'data'")
    if mu=="data" and criterion!="mle" and not conditional_data_mu:
        raise ValueError("mu='data' with fixed-mean criteria requires conditional_data_mu=True; scores are CONDITIONAL plug-in, not refitted CV")
    if denominator not in GRID_DENOMINATORS:
        raise ValueError("Invalid grid")
    if repeats<1 or R<2 or threads<1:raise ValueError("Bad repeat/R/threads")
    if any(x not in METHODS for x in methods):
        raise ValueError("Only complete-criterion backends may be timed")
    output=Path(output or ("paper/benchmarks/experiment006/runs/local-slice"))
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to overwrite archived run: {output}")
    targets=grid_of_s(denominator)
    rows=[]
    # Save each completed row before starting the next long calculation.
    # An interrupted process leaves an explicit, incomplete CSV on disk.
    output.mkdir(parents=True, exist_ok=True)
    def emit_row(row):
        rows.append(row)
        checkpoint=output/"raw_times.csv"
        temporary=output/"raw_times.tmp"
        with temporary.open("w",newline="",encoding="utf-8") as handle:
            writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(checkpoint)

    with threadpool_limits(limits=threads):
        # The coordinate mapper belongs to the same (n,d) problem and
        # may be reused across ALL mu, series, criterion and methods.
        t0=perf_counter()
        if n<=512:
            mapper=TrendSmoother(n,d)
            mapping_backend="full_svd"
        else:
            mapper=BandedTrace(n,d)
            mapping_backend="exact_banded_selected_inverse"
        mapper_setup_s=perf_counter()-t0
        def invert(s):
            return mapper.lambda_for_smoothness(float(s)) if n<=512 else mapper.lambda_for_s(float(s))
        for method in methods:
            t0=perf_counter()
            evaluator=None
            # Never allocate a dense n-by-n array before resource gating.
            preflight=memory_budget_status(
                n,d,method,denominator,max_dense_bytes,float("inf"),
                "one_s_one_series",1,1,
                allow_unbounded_runtime=allow_unbounded_runtime)
            if preflight!="eligible":
                setup_s=mapper_setup_s
                failure=preflight
            else:
                try:
                    evaluator=Evaluator(n,d,method)
                    setup_s=perf_counter()-t0+mapper_setup_s
                except (ValueError,ArithmeticError,np.linalg.LinAlgError,
                        MemoryError,ImportError) as exc:
                    setup_s=perf_counter()-t0+mapper_setup_s
                    failure="setup_failed_"+type(exc).__name__
                else:
                    failure=None
            for scenario in SCENARIOS:
                nr = (1 if "one_series" in scenario else R)
                ss=np.array([.5]) if scenario.startswith("one_s") else targets
                M=len(ss)
                for policy in POLICIES:
                    budget=memory_budget_status(
                        n,d,method,denominator,max_dense_bytes,max_work,
                        scenario,nr,repeats,
                        allow_unbounded_runtime=allow_unbounded_runtime)
                    if failure or budget!="eligible":
                        emit_row(_row(
                            n,d,mu,amplitude,criterion,denominator,method,
                            policy,scenario,-1,nr,M,setup_s,0.,0.,
                            float("nan"),float("nan"),
                            failure or budget,0,
                            "Not run: explicit resource or setup gate"))
                        continue
                    for repeat in range(repeats):
                        series=[sample(n,seed+100000*repeat+23*k+
                                       29*n+7*d,amplitude)
                                for k in range(nr)]
                        # Pre-project *once* for every y, not per candidate:
                        tpre=perf_counter()
                        coords=[evaluator.prepare_series(y,mu if mu!="data"
                                   else float(np.mean(np.diff(y,n=d))))
                                for y in series]
                        series_setup_s=perf_counter()-tpre
                        tmap=perf_counter()
                        mapped=None
                        if policy=="mapped_lambda":
                            try:
                                mapped=[invert(s) for s in ss]
                            except (ValueError, ArithmeticError,
                                    OverflowError,np.linalg.LinAlgError) as exc:
                                emit_row(_row(
                                    n,d,mu,amplitude,criterion,denominator,
                                    method,policy,scenario,repeat,nr,M,
                                    setup_s+series_setup_s,
                                    perf_counter()-tmap,0.,
                                    float("nan"),float("nan"),
                                    "mapping_failed_"+type(exc).__name__,0,
                                    str(exc)[:180]))
                                continue
                        map_s=perf_counter()-tmap if mapped is not None else 0.
                        evaluator._cache.clear()
                        evaluator._cached_diagnostics.clear()
                        if evaluator.hybrid is not None:
                            if evaluator.hybrid.structured is not None:
                                evaluator.hybrid.structured._factors.clear()
                            evaluator.hybrid._band_factors.clear()
                        reuse=nr>1 and evaluator.spectral is None
                        # Cache only if a full collection of retained factors
                        # fits in the explicitly reported memory budget.
                        if reuse and method=="naive_inverse":
                            reuse=M*n*n*8<max_dense_bytes//2
                        if reuse and (evaluator.banded is not None):
                            # A conservative 4x multiplier includes
                            # selected inverse plus opaque LU/CHOLMOD factors.
                            reuse=M*n*(d+1)*8*4<max_dense_bytes//2
                        scores=[]
                        tscore=0.
                        calls=0
                        failed=None
                        for j,y in enumerate(series):
                            mean=(float(np.mean(np.diff(y,n=d)))
                                  if mu=="data" else float(mu))
                            coord=coords[j]
                            for k,s in enumerate(ss):
                                try:
                                    if mapped is None:
                                        st=perf_counter()
                                        lam=invert(s)
                                        map_s+=perf_counter()-st
                                    else:lam=mapped[k]
                                    st=perf_counter()
                                    value=evaluator.evaluate(
                                        y,mean,lam,criterion,
                                        coordinates=coord,reuse_factor=reuse)
                                    tscore+=perf_counter()-st
                                    calls+=1
                                    scores.append((float(value),float(s)))
                                except (ValueError,ArithmeticError,OverflowError,
                                        np.linalg.LinAlgError,MemoryError) as exc:
                                    failed=type(exc).__name__+": "+str(exc)[:170]
                                    break
                            if failed:break
                        finite=[x for x in scores if np.isfinite(x[0])]
                        if failed:
                            state="numerical_failed"
                        elif not finite:
                            state="criterion_undefined"
                        else:
                            state="ok"
                        best=min(finite,key=lambda x:x[0]) if finite else (
                            float("nan"),float("nan"))
                        emit_row(_row(
                            n,d,mu,amplitude,criterion,denominator,method,
                            policy,scenario,repeat,nr,M,
                            setup_s+series_setup_s,map_s,tscore,
                            best[0],best[1],state,calls,failed or ""))
                    print(f"{method}: {scenario} {policy} complete",flush=True)
    output.mkdir(parents=True,exist_ok=True)
    path=output/"raw_times.csv"
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    summary={}
    for row in rows:
        key=(row["method"],row["coordinate"],row["workload"])
        summary.setdefault(key,[]).append(row)
    derived=[]
    for key,values in summary.items():
        eligible=[x for x in values if x["status"]=="ok"]
        state="ok" if len(eligible)==len(values) else "invalid_or_skipped"
        times=np.array([x["total_cold_s"] for x in eligible],dtype=float)
        rng=np.random.default_rng(7006)
        bootstrap=(
            np.mean(times[rng.integers(0,len(times),(2000,len(times)))],axis=1)
            if len(times)>=2 and state=="ok" else None)
        derived.append(dict(
            method=key[0],coordinate=key[1],workload=key[2],
            valid_all=state=="ok",valid_repeats=len(eligible),
            expected_repeats=repeats,
            mean_total_s=(
                float(np.mean(times)) if state=="ok" else float("nan")),
            sd_total_s=(
                float(np.std(times,ddof=1))
                if state=="ok" and len(times)>=2 else float("nan")),
            mean_bootstrap_ci95_low_s=(
                float(np.quantile(bootstrap,.025))
                if bootstrap is not None else float("nan")),
            mean_bootstrap_ci95_high_s=(
                float(np.quantile(bootstrap,.975))
                if bootstrap is not None else float("nan")),
            median_total_cold_s=(
                float(np.median(times)) if state=="ok" else float("nan")),
            median_total_warm_s=(
                float(np.median([x["total_warm_s"] for x in eligible]))
                if state=="ok" else float("nan")),
        ))
    with (output/"summary.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(derived[0]))
        w.writeheader();w.writerows(derived)
    # Paired relative costs against the explicit naive inverse baseline:
    # same n,d,mu,amplitude,criterion,scenario,coordinate,seed block.
    baseline={
        (r["workload"],r["coordinate"],r["repeat"]):r
        for r in rows if r["method"]=="naive_inverse" and r["status"]=="ok"
    }
    comparisons=[]
    for r in rows:
        key=(r["workload"],r["coordinate"],r["repeat"])
        b=baseline.get(key)
        if r["status"]!="ok" or b is None:
            continue
        if r["total_cold_s"]<=0:
            continue
        comparisons.append(dict(
            n=n,d=d,criterion=criterion,mu=str(mu),amplitude=amplitude,
            method=r["method"],coordinate=r["coordinate"],
            workload=r["workload"],repeat=r["repeat"],
            naive_time_s=b["total_cold_s"],
            candidate_time_s=r["total_cold_s"],
            paired_speedup=b["total_cold_s"]/r["total_cold_s"],
        ))
    with (output/"paired_speedups.csv").open("w",newline="",encoding="utf-8") as f:
        if comparisons:
            w=csv.DictWriter(f,fieldnames=list(comparisons[0]))
            w.writeheader();w.writerows(comparisons)
        else:
            f.write("n,d,criterion,mu,amplitude,method,coordinate,workload,repeat,naive_time_s,candidate_time_s,paired_speedup\n")
    meta=dict(
        n=n,d=d,mu=mu,amplitude=amplitude,criterion=criterion,
        mean_policy_note=(
            "conditional_plugin_not_refitted" if mu=="data" and criterion!="mle"
            else "conditional_plugin_mle" if mu=="data"
            else "fixed_numeric_reference_mean"
        ),
        denominator=denominator,methods=list(methods),R=R,
        repeats=repeats,policies=list(POLICIES),scenarios=list(SCENARIOS),
        exact_S_one=True,grid_starts_at_positive_s=True,
        mapping_backend=mapping_backend,
        mapper_setup_s=mapper_setup_s,
        max_work=("unbounded" if math.isinf(max_work) else max_work),
        max_dense_bytes=max_dense_bytes,
        allow_unbounded_runtime=allow_unbounded_runtime,
        seed=seed,host=platform.platform(),python=sys.version,
        numpy=np.__version__,scipy=scipy.__version__,
        threadpools=threadpool_info(),blas_threads=threads,
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        git_sha=git_sha(),note=(
            "Selection is minimum of actually evaluated candidate scores. "
            "BIC mathematical divergence at S->0+ is not repaired. "
            "Scores across criteria are not directly comparable. "
            "All incomplete/invalid records excluded from winner rankings. "
            "n<=512 mapping uses a shared SVD; larger n uses selected inversion."),
    )
    (output/"environment.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
    return rows,derived


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preset",choices=["smoke","slice"],default="smoke")
    p.add_argument("--n",type=int,default=64)
    p.add_argument("--d",type=int,default=2)
    p.add_argument("--mu",default="0.15")
    p.add_argument("--amplitude",choices=("low","high"),default="low")
    p.add_argument("--criterion",choices=CRITERIA,default="gcv")
    p.add_argument("--grid-denominator",type=int,default=100)
    p.add_argument("--methods",default="banded_cholesky,spectral_svd,naive_inverse")
    p.add_argument("--repeats",type=int,default=2)
    p.add_argument("--series-count",type=int,default=3)
    p.add_argument("--threads",type=int,default=1)
    p.add_argument("--seed",type=int,default=20261102)
    p.add_argument("--max-work",type=float,default=5e7)
    p.add_argument("--allow-unbounded-runtime",action="store_true")
    p.add_argument("--max-dense-bytes",type=int,default=2*1024**3)
    p.add_argument("--output",type=Path,default=None)
    p.add_argument("--conditional-data-mu",action="store_true",help="Opt into conditional plug-in mu=data scores; NOT fully refitted LOOCV")
    a=p.parse_args()
    mu=a.mu if a.mu=="data" else float(a.mu)
    opts=dict(n=a.n,d=a.d,mu=mu,amplitude=a.amplitude,
              criterion=a.criterion,denominator=a.grid_denominator,
              methods=tuple(x.strip() for x in a.methods.split(",")),
              repeats=a.repeats,R=a.series_count,threads=a.threads,
              max_work=a.max_work,max_dense_bytes=a.max_dense_bytes,
              output=a.output,seed=a.seed,conditional_data_mu=a.conditional_data_mu,
              allow_unbounded_runtime=a.allow_unbounded_runtime)
    if a.preset=="smoke":
        opts.update(n=64,d=2,mu=.15,amplitude="low",criterion="gcv",
                    denominator=100,methods=("banded_cholesky","spectral_svd"),
                    repeats=1,R=2)
    out=run_slice(**opts)
    print("Recorded",len(out[0]),"raw rows and",len(out[1]),"summary rows")


if __name__=="__main__":
    main()
