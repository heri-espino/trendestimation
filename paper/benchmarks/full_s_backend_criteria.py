"""Full normalized S=[0,1] numerical-backend x criterion factorial.

Actual factorization-based CV/GCV/AICc/BIC and conditional Gaussian MLE
using 7 backend pathways, d=0..5, mu=0/.15, all 17 targets including
the exact 0 and 1 and increasingly dense points near 1.

The exact endpoints are *analytical common-limit evaluations*: no finite
Cholesky, LU or eigenvalue factorization at lambda=infinity. Endpoint
timings are excluded from backend speed rankings. MLE d=0 is unsupported
by the public library and reported as not_applicable, never fabricated.
Ill-conditioned high-S finite solves are reported as unstable/failed,
never silently replaced by a spectral score.

Repro from repo root:
  python paper/benchmarks/full_s_backend_criteria.py --preset quick --repeats 2
  python paper/benchmarks/full_s_backend_criteria.py --preset full --repeats 5

All numerical methods evaluate the same penalties: this tests
linear-algebra backends, NOT different candidate sampling policies.
The separate selection_coordinate_mle.py benchmark tests search-space
grid mapping versus native-S inversion.
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
    cho_factor, cho_solve, cholesky_banded, cho_solve_banded,
    eigh, solve_banded, svd,
)
from scipy.special import binom
from threadpoolctl import threadpool_info, threadpool_limits

from trendestimation import TrendSmoother, score_lambda
from trendestimation.core import difference_matrix
from trendestimation.solvers import _penalty_lower_bands

ROOT = Path(__file__).resolve().parent
BACKENDS = ("dense_fresh", "dense_cached", "general_banded",
            "dense_cholesky", "banded_cholesky", "eigh", "svd")
CRITERIA = ("cv", "gcv", "aicc", "bic", "mle")


def complete_s_grid():
    """Exactly 11 deciles + 6 independent near-1 candidates, 17 total."""
    return np.unique(np.r_[np.linspace(0., 1., 11),
                           .95, .99, .999, .9999, .999999,
                           .999999999999])


def observation(n, seed):
    t = np.linspace(0, 1, n)
    rng = np.random.default_rng(seed)
    return .55*np.sin(3*np.pi*t) + .16*t + rng.normal(0, .22, n)


def _reference(n, d, mu):
    return np.full(n, mu) if d == 0 else mu*binom(np.arange(n), d)


def _banded(Q, d):
    """SciPy solve_banded convention ab[u+i-j,j]=A[i,j]."""
    n = len(Q)
    out = np.zeros((2*d+1, n))
    for j in range(n):
        for i in range(max(0,j-d),min(n,j+d+1)):
            out[d+i-j,j] = Q[i,j]
    return out


class Backend:
    """The backend really computes H and fit; GCV/CV need its diagonal/trace."""

    def __init__(self, n, d, method, criterion="mle"):
        self.n, self.d, self.method = n,d,method
        self.I = np.eye(n)
        self.D = difference_matrix(n,d)
        self.Q = None
        self.B = None
        self.U = None
        self.delta = None
        self.U2 = None
        # The MLE normalizing log pseudo-determinant is shared among
        # backends. This reusable d-specific constant is part of
        # the setup for EVERY direct pathway, not a free spectral score.
        # Construct D D.T (r x r) and its determinant once when d>=1.
        if d>=1 and criterion=="mle" and method not in ("svd","eigh"):
            sign, val = np.linalg.slogdet(self.D @ self.D.T)
            if sign <= 0:
                raise ArithmeticError("D D.T determinant not positive")
            self.logdet_DDT = float(val)
        else:
            self.logdet_DDT = float("nan")

        if method in ("dense_cached", "dense_cholesky"):
            self.Q = self.D.T @ self.D
        elif method == "general_banded":
            self.Q = self.D.T @ self.D
            self.B = _banded(self.Q,d)
        elif method == "banded_cholesky":
            self.B = _penalty_lower_bands(n,d)
        elif method in ("svd","eigh"):
            if method=="svd":
                _, sing, vt=svd(self.D,full_matrices=True,check_finite=False)
                self.U=vt.T
                self.delta=np.r_[sing**2,np.zeros(d)]
            else:
                values,vectors=eigh(self.D.T@self.D,check_finite=False)
                # Set the theoretical d null eigenvalues EXACTLY to zero.
                self.U = vectors[:, ::-1]
                self.delta = np.r_[values[d:][::-1],np.zeros(d)]
                if np.any(self.delta[:n-d]<=0):
                    raise ArithmeticError("Nonpositive penalized eigenvalues")
            self.U2=self.U**2
        elif method!="dense_fresh":
            raise ValueError(method)

    def calculate(self, y, lam, mu, criterion):
        """Return objective and diagnostics at one finite positive lambda.

        MLE is evaluated using the backend's own computed trend/H and its
        method-specific log-determinant (or actual spectral attenuation).
        The common precomputed logdet(D D.T) is included in preparation.
        Direct banded LU uses a dense slogdet of A only for MLE, counted
        in its timing. No backend borrows the SVD's MLE score.
        """
        n,d=self.n,self.d
        ref=_reference(n,d,mu)
        centered=y-ref
        if self.method in ("svd","eigh"):
            a=1/(1+lam*self.delta)
            z=self.U.T@centered
            residual=self.U@((1-a)*z)
            edf=float(a.sum())
            diagH=self.U2@a
            if criterion=="mle":
                zpos=z[:n-d]
                delta=self.delta[:n-d]
                logc=np.logaddexp(0., -np.log(lam)-np.log(delta))
                weighted=float(np.sum(zpos*zpos*np.exp(-logc)))
                score=(n-d)*np.log(weighted/(n-d))+float(logc.sum())
                return float(score),edf,float(np.linalg.norm(residual))
        else:
            Q=self.Q
            if self.method=="dense_fresh":
                Q=self.D.T@self.D
            # MLE needs no leverage/EDF: do not charge it for n
            # unnecessary identity right-hand sides.
            rhs = (centered if criterion=="mle"
                   else np.column_stack((centered,self.I)))
            if self.method in ("dense_fresh","dense_cached"):
                A=self.I+lam*Q
                solved=np.linalg.solve(A,rhs)
                logdetA=None
            elif self.method=="dense_cholesky":
                A=self.I+lam*Q
                f=cho_factor(A,lower=True,check_finite=False)
                solved=cho_solve(f,rhs,check_finite=False)
                logdetA=2*float(np.log(np.diag(f[0])).sum())
            elif self.method=="general_banded":
                ab=lam*self.B.copy()
                ab[d]+=1
                solved=solve_banded((d,d),ab,rhs,check_finite=False)
                logdetA=None
            else:
                ab=lam*self.B.copy()
                ab[0]+=1
                factor=cholesky_banded(ab,lower=True,check_finite=False)
                solved=cho_solve_banded((factor,True),rhs,check_finite=False)
                logdetA=2*float(np.log(factor[0]).sum())
            if criterion=="mle":
                projected=solved
                H=None
                edf=float("nan")
                diagH=None
            else:
                projected,H=solved[:,0],solved[:,1:]
                edf=float(np.trace(H))
                diagH=np.diag(H)
            residual=centered-projected
            if criterion=="mle":
                # This logdet computation is charged to direct routes.
                if logdetA is None:
                    if self.method=="general_banded":
                        # General banded solver API does not expose its
                        # factorization; dense determinant is additional cost.
                        A=self.I+lam*(self.D.T@self.D)
                    sign,logdetA=np.linalg.slogdet(A)
                    if sign<=0:
                        raise ArithmeticError("Nonpositive determinant")
                logc=logdetA-(n-d)*np.log(lam)-self.logdet_DDT
                weighted=float(centered@residual)
                if weighted<=0:
                    raise ArithmeticError("Nonpositive likelihood energy")
                return float((n-d)*np.log(weighted/(n-d))+logc),edf,float(np.linalg.norm(residual))
        rss=float(residual@residual)
        if criterion=="cv":
            denom=1.0-diagH
            if np.any(denom<=0):
                raise ArithmeticError("Nonpositive LOOCV leverage denominator")
            return float(np.mean((residual/denom)**2)),edf,float(np.sqrt(rss))
        if criterion=="gcv":
            den=1-edf/n
            return (float((rss/n)/den**2) if den>1e-10 else float("inf")),edf,float(np.sqrt(rss))
        eps=np.finfo(float).eps*max(1.0,float(centered@centered))
        if rss<=eps:
            return float("inf"),edf,float(np.sqrt(rss))
        common=np.log(rss/n)
        if criterion=="bic":
            return float(common+edf*np.log(n)/n),edf,float(np.sqrt(rss))
        den=n-edf-2
        return (float(common+(2*edf+1)/den) if den>0 else float("inf")),edf,float(np.sqrt(rss))


def run(preset="quick",repeats=2,seed=20261026,threads=1,
        output=ROOT/"results"/"full_s_backend_criteria"):
    if preset not in ("smoke","quick","full"):
        raise ValueError(preset)
    if repeats<1 or threads<1:
        raise ValueError("repeats/threads must be positive")
    ns={"smoke":(16,),"quick":(24,),"full":(24,48)}[preset]
    seeds={"smoke":(seed,),"quick":(seed,),"full":(seed,seed+1)}[preset]
    rows=[]
    grid_rows=[]
    summary=[]
    with threadpool_limits(limits=threads):
        env=dict(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            python=sys.version, platform=platform.platform(),
            processor=platform.processor(), scipy=scipy.__version__,
            numpy=np.__version__, threadpools=threadpool_info(),
            blas_threads=threads, preset=preset, repeats=repeats,
            seeds=list(seeds), n=list(ns), d=list(range(6)),
            mu=[0.,.15], methods=list(BACKENDS), criteria=list(CRITERIA),
            note="Method-specific CV/GCV/AICc/BIC/MLE complete objective "
                 "including leverage/EDF/likelihood. Analytical endpoints "
                 "are shared by all methods, not timed as factorizations. "
                 "MLE d=0 not supported. Near-1 failed/unstable solves "
                 "are tracked, not replaced with spectral results."
        )
        for n in ns:
            for d in range(6):
                sm=TrendSmoother(n,d)
                targets=complete_s_grid()
                t0=perf_counter()
                lambdas=np.array([sm.lambda_for_smoothness(float(s)) for s in targets])
                map_time=perf_counter()-t0
                recovered=np.array([sm.smoothness(float(v)) for v in lambdas])
                if not np.allclose(recovered,targets,atol=2e-10,rtol=0):
                    raise AssertionError(f"S inversion mismatch {n=} {d=}")
                for idx,(s,lam) in enumerate(zip(targets,lambdas)):
                    grid_rows.append(dict(n=n,d=d,index=idx,S=float(s),
                                          lambda_=float(lam),
                                          recovered_S=float(recovered[idx]),
                                          is_endpoint=bool(s==0 or s==1),
                                          map_total_s=float(map_time)))
                for seed_i in seeds:
                    y=observation(n,seed_i+n+17*d)
                    for mu in (0.,.15):
                        for criterion in CRITERIA:
                            if criterion=="mle" and d==0:
                                for method in BACKENDS:
                                    rows.append(dict(
                                        n=n,d=d,seed=seed_i,mu=mu,criterion=criterion,
                                        method=method,index=-1,S=float("nan"),
                                        lambda_=float("nan"),score=float("nan"),
                                        reference=float("nan"),elapsed_s=0.,
                                        setup_s=0.,error=float("nan"),
                                        status="not_applicable_d0_mle",edf=float("nan"),
                                        residual_norm=float("nan")))
                                continue
                            baseline=np.array([
                                score_lambda(sm,y,lambda_=float(lam),
                                             criterion=criterion,mu=mu)
                                for lam in lambdas])
                            for method in BACKENDS:
                                start=perf_counter()
                                try:
                                    backend=Backend(n,d,method,criterion)
                                    setup=perf_counter()-start
                                except Exception as exc:
                                    for idx,(s,lam) in enumerate(zip(targets,lambdas)):
                                        rows.append(dict(
                                            n=n,d=d,seed=seed_i,mu=mu,criterion=criterion,
                                            method=method,index=idx,S=float(s),
                                            lambda_=float(lam),score=float("nan"),
                                            reference=float(baseline[idx]),
                                            elapsed_s=0.,setup_s=float("nan"),
                                            error=float("nan"),
                                            status="setup_failed_"+type(exc).__name__,
                                            edf=float("nan"),residual_norm=float("nan")))
                                    continue
                                for idx,(s,lam) in enumerate(zip(targets,lambdas)):
                                    if idx in (0,len(targets)-1):
                                        # Exact limits are analytically common across
                                        # all methods; benchmark NO fake solve time.
                                        rows.append(dict(
                                            n=n,d=d,seed=seed_i,mu=mu,criterion=criterion,
                                            method=method,index=idx,S=float(s),
                                            lambda_=float(lam),score=float(baseline[idx]),
                                            reference=float(baseline[idx]),elapsed_s=0.,
                                            setup_s=setup,error=0.,status="analytic_limit",
                                            edf=float(n if idx==0 else d),
                                            residual_norm=float("nan")))
                                        continue
                                    try:
                                        # First, validate against the canonical
                                        # spectral criterion *outside timing*.
                                        value,edf,rnorm=backend.calculate(
                                            y,float(lam),mu,criterion)
                                        ref=float(baseline[idx])
                                        err=(abs(value-ref) if np.isfinite(ref)
                                             and np.isfinite(value) else float("inf"))
                                        if not np.isfinite(ref):
                                            # Undefined is a criterion decision,
                                            # not necessarily a failed factorization.
                                            status="criterion_undefined"
                                            err=float("nan")
                                        elif np.isfinite(value) and np.isclose(
                                            value,ref,rtol=1e-5,atol=1e-5
                                        ):
                                            status="ok"
                                        else:
                                            status="unstable_numerics"
                                        duration=[]
                                        for _ in range(repeats):
                                            t0=perf_counter()
                                            backend.calculate(y,float(lam),mu,criterion)
                                            duration.append(perf_counter()-t0)
                                        runtime=float(np.median(duration))
                                    except (np.linalg.LinAlgError, ValueError,
                                            FloatingPointError, ArithmeticError,
                                            OverflowError) as exc:
                                        value=float("nan")
                                        edf=rnorm=runtime=err=float("nan")
                                        status="factorization_failed_"+type(exc).__name__
                                    rows.append(dict(
                                        n=n,d=d,seed=seed_i,mu=mu,criterion=criterion,
                                        method=method,index=idx,S=float(s),
                                        lambda_=float(lam),score=float(value),
                                        reference=float(baseline[idx]),
                                        elapsed_s=runtime,setup_s=setup,error=float(err),
                                        status=status,edf=float(edf),
                                        residual_norm=float(rnorm)))
                print(f"[full S] n={n} d={d}: all criteria, mu, backends, "
                      f"tail and exact endpoints recorded",flush=True)
        # Any competitor whose high-S numerical score disagrees is
        # NOT allowed to win a timing ranking on that grid.
        grouped={}
        for row in rows:
            if row["index"]<0:
                continue
            key=(row["n"],row["d"],row["seed"],row["mu"],
                 row["criterion"],row["method"])
            grouped.setdefault(key,[]).append(row)
        for key,rec in grouped.items():
            finite=[r for r in rec if r["status"]=="ok"]
            issues=[r for r in rec if r["status"] not in ("ok","analytic_limit")]
            summary.append(dict(
                n=key[0],d=key[1],seed=key[2],mu=key[3],
                criterion=key[4],method=key[5],
                valid_points=len(finite),invalid_points=len(issues),
                all_interior_valid=len(finite)==len(complete_s_grid())-2,
                total_finite_eval_s=float(sum(r["elapsed_s"] for r in finite)),
                setup_s=float(rec[0]["setup_s"]),
                selected_S=float(min(
                    (r for r in rec if np.isfinite(r["score"]) and
                     r["status"] in ("ok","analytic_limit")),
                    key=lambda r:r["score"],default={"S":float("nan")})["S"])))
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    def write(name,data):
        with (output/name).open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    write("candidate_scores_and_times.csv",rows)
    write("full_grid_summary.csv",summary)
    write("s_lambda_grid.csv",grid_rows)
    (output/"environment.json").write_text(
        json.dumps(env,indent=2),encoding="utf-8")
    print(f"Recorded {len(rows)} scored/backend candidates, "
          f"{len(summary)} whole-grid summaries in {output}",flush=True)
    return rows,summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preset",choices=("smoke","quick","full"),default="quick")
    p.add_argument("--repeats",type=int,default=2)
    p.add_argument("--seed",type=int,default=20261026)
    p.add_argument("--threads",type=int,default=1)
    p.add_argument("--output",type=Path,
                   default=ROOT/"results"/"full_s_backend_criteria")
    a=p.parse_args()
    run(a.preset,a.repeats,a.seed,a.threads,a.output)


if __name__=="__main__":
    main()
