"""Paired 17-point full-S study: one score, full grid, repeated grids, optimization.

Extends Experiment002, rather than comparing different experiments' timings.
All seven backends, CV/GCV/AICc/BIC/conditional MLE, d=0..5, mu=0/.15.
Compare three finite-grid policies:
  native_s: invert s->lambda within EVERY scored search (mapping charged).
  mapped_s_lambda: map one shared S grid ONCE, then evaluate in lambda.
  native_log_lambda: independently sample a log-lambda grid with identical
     finite endpoint penalties and cardinality (different interior nodes).
And two bounded continuous scalar searches:
  continuous_s: minimize criterion(S^-1(s)); invert at each function call.
  continuous_log_lambda: minimize criterion(exp(x)) in log-lambda.
All policies score the exact lambda=0 and lambda=infinity limits, without
attempting Cholesky factorization there. Bounded continuous optimization
is NOT guaranteed global; its candidates DIFFER from the grid methods.

Measure three workload classes: single middle-point evaluation (S=.5),
one full-grid search on one series, and the same grid reused across
multiple independent series (R=3 in quick, R=8 in full).

Backend setup, candidate mapping and scoring times are reported separately.
For one self-contained search, total_with_mapping counts S->lambda once
for mapped_s_lambda. For multiple methods/criteria, mapping can be shared,
so blindly summing total_with_mapping is NOT the joint workflow time.
Numerically invalid finite tail candidate scores must never win a ranking.
No comparison of raw scores BETWEEN statistical criteria is meaningful.

Run on Windows from repo root:
  python paper/benchmarks/full_s_search_modes.py --preset quick --repeats 3
  python paper/benchmarks/full_s_search_modes.py --preset full --repeats 7
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from scipy.optimize import minimize_scalar
from threadpoolctl import threadpool_info, threadpool_limits

from full_s_backend_criteria import (
    BACKENDS, CRITERIA, Backend, complete_s_grid, observation,
)
from trendestimation import TrendSmoother, score_lambda

HERE = Path(__file__).resolve().parent
SINGLE_POLICIES = ("single_native_s", "single_lambda", "single_mapped_s_lambda")
GRID_POLICIES = ("native_s", "mapped_s_lambda", "native_log_lambda")
CONTINUOUS_POLICIES = ("continuous_s", "continuous_log_lambda")
TARGET_S = 0.5


def design(smoother):
    targets = complete_s_grid()
    t0 = perf_counter()
    mapped = np.asarray([smoother.lambda_for_smoothness(float(s))
                         for s in targets], dtype=float)
    mapping_s = perf_counter() - t0
    np.testing.assert_allclose(
        [smoother.smoothness(float(lam)) for lam in mapped],
        targets, rtol=0, atol=3e-10,
    )
    lo, hi = float(mapped[1]), float(mapped[-2])
    direct = np.r_[0., np.geomspace(lo, hi, len(targets)-2), np.inf]
    assert len(direct) == len(mapped) == 17
    return targets, mapped, direct, mapping_s


def _finite_accuracy(value, reference):
    """Undefined-by-criterion is not a numerical solver failure."""
    if np.isposinf(reference) and np.isposinf(value):
        return "criterion_undefined", 0.0
    if not np.isfinite(reference):
        return "reference_undefined", float("nan")
    if not np.isfinite(value):
        return "numerical_failure", float("nan")
    error = abs(float(value)-float(reference))
    return ("ok" if np.isclose(value, reference, rtol=1e-5, atol=1e-5)
            else "numerical_disagreement"), error


def _score(backend, smoother, y, mu, criterion, lam):
    """Exact S=0/1 score common to methods; never factorize infinity."""
    if lam == 0 or np.isposinf(lam):
        return float(score_lambda(smoother, y, lambda_=float(lam),
                                  mu=mu, criterion=criterion))
    value, _, _ = backend.calculate(y, float(lam), mu, criterion)
    return float(value)


def _get_lambda(policy, v, smoother):
    if policy in ("native_s", "continuous_s"):
        return smoother.lambda_for_smoothness(float(v))
    if policy == "continuous_log_lambda":
        return float(np.exp(v))
    return float(v)


def evaluate_grid(backend, smoother, y, mu, criterion, policy,
                  values, *, check=True):
    """Score ALL candidates, return exact min and per-candidate validity."""
    score_list, reference_list, errors, states = [], [], [], []
    t0 = perf_counter()
    for v in values:
        lam = _get_lambda(policy, v, smoother)
        try:
            score = _score(backend, smoother, y, mu, criterion, lam)
        except (ValueError, ArithmeticError, OverflowError,
                FloatingPointError, np.linalg.LinAlgError):
            score = float("nan")
        score_list.append(score)
        if check:
            reference = float(score_lambda(
                smoother, y, lambda_=lam, mu=mu, criterion=criterion))
            status, error = _finite_accuracy(score, reference)
            reference_list.append(reference)
            states.append(status)
            errors.append(error)
    duration = perf_counter()-t0
    if check:
        # A valid grid can contain criteria-defined infinite losses.
        # It cannot contain a numeric method error or failed factorization.
        valid = all(v in ("ok", "criterion_undefined") for v in states)
        good = [i for i,v in enumerate(score_list) if np.isfinite(v)
                and states[i] == "ok"]
    else:
        valid = False
        good = [i for i,v in enumerate(score_list) if np.isfinite(v)]
    if good:
        best = min(good,key=lambda i: score_list[i])
        winner_lam = _get_lambda(policy,values[best],smoother)
        s_chosen = float(smoother.smoothness(winner_lam))
        score_chosen = float(score_list[best])
    else:
        s_chosen,score_chosen = float("nan"),float("nan")
    return dict(duration=duration, scores=score_list,
                reference=reference_list, errors=errors, states=states,
                valid=valid, s=s_chosen, score=score_chosen)


def continuous_search(backend, smoother, y, mu, criterion, policy,
                      finite_penalties, *, check=True):
    """Bounded local scalar minimization plus analytical endpoint checks.

    NOT a certified global minimization. Grid-search results must remain
    independently reported as the only exhaustively evaluated candidates.
    """
    low, high = float(finite_penalties[1]), float(finite_penalties[-2])
    bounds = ((float(smoother.smoothness(low)),
               float(smoother.smoothness(high)))
              if policy == "continuous_s" else (math.log(low),math.log(high)))
    evaluations = []
    states = []
    def fn(x):
        lam = _get_lambda(policy,x,smoother)
        try:
            score = _score(backend,smoother,y,mu,criterion,lam)
        except (ValueError,ArithmeticError,OverflowError,
                FloatingPointError,np.linalg.LinAlgError):
            score = float("nan")
        evaluations.append((lam,score))
        return score if np.isfinite(score) else 1e100

    start=perf_counter()
    result=minimize_scalar(fn,bounds=bounds,method="bounded",
                           options={"xatol":1e-8,"maxiter":50})
    # The extreme endpoints (including infinity) have to be evaluated,
    # but not attributed to finite factorization. One interior local
    # optimum is NOT a globally certified solution.
    end_candidates=[(0.,_score(backend,smoother,y,mu,criterion,0.)),
                    (float("inf"),_score(backend,smoother,y,mu,criterion,
                                          float("inf")))]
    duration=perf_counter()-start
    candidates=[(lam,v) for lam,v in evaluations+end_candidates
                if np.isfinite(v)]
    if not candidates:
        return dict(duration=duration,valid=False,s=float("nan"),
                    score=float("nan"),calls=len(evaluations),
                    local_success=bool(result.success),
                    n_errors=len(evaluations),benchmark_scope="local")
    best_lam,best_score=min(candidates,key=lambda x:x[1])
    if check:
        for lam,val in evaluations:
            if np.isfinite(val):
                expected=score_lambda(smoother,y,lambda_=lam,
                                      criterion=criterion,mu=mu)
                state,_=_finite_accuracy(val,expected)
                states.append(state)
            else:
                states.append("numerical_failure")
    valid=bool(result.success) and (
        not check or all(v in ("ok","criterion_undefined") for v in states))
    return dict(duration=duration,valid=valid,
                s=float(smoother.smoothness(best_lam)),
                score=float(best_score),calls=len(evaluations),
                local_success=bool(result.success),
                n_errors=sum(v not in ("ok","criterion_undefined")
                             for v in states),
                benchmark_scope="bounded_local_not_global")


def measure_one(n,d,mu,criterion,method,workload,policy,seed,repeats,
                smoother,targets,mapped,direct,grid_map_s,reuse_mode):
    R = workload
    if reuse_mode not in ("shared","cold"):
        raise ValueError(reuse_mode)
    ys=[observation(n, seed+101*i+n+17*d) for i in range(R)]
    if criterion=="mle" and d==0:
        return dict(
            n=n,d=d,mu=mu,criterion=criterion,method=method,R=R,
            workload="single" if policy in SINGLE_POLICIES else
                     ("continuous" if policy in CONTINUOUS_POLICIES else "grid"),
            policy=policy,reuse_mode=reuse_mode,
            status="not_applicable_d0_mle",
            success=False,setup_s=0.,evaluate_s=0.,mapping_once_s=0.,
            total_standalone_s=0.,total_backend_only_s=0.,
            selected_s=float("nan"),mean_score=float("nan"),
            candidate_evaluations=0,valid_series=0,invalid_series=R,
            max_error=float("nan"),repeats=repeats,
            shared_grid_size=17,
        )
    if policy in SINGLE_POLICIES:
        if policy=="single_native_s":
            values=np.array([TARGET_S])
            mode="native_s"
            common_mapping=0.0
        else:
            # Both lambda policies score the SAME S=.5 candidate.
            # The "known lambda" route receives it directly; the
            # mapped route is charged the one-time inverse cost.
            st_map=perf_counter()
            single_lam=smoother.lambda_for_smoothness(TARGET_S)
            single_map_s=perf_counter()-st_map
            values=np.array([single_lam])
            mode="mapped_s_lambda"
            common_mapping=(single_map_s
                            if policy=="single_mapped_s_lambda" else 0.0)
    elif policy=="native_s":
        values=targets
        mode=policy
        common_mapping=0.0
    elif policy=="mapped_s_lambda":
        values=mapped
        mode=policy
        common_mapping=grid_map_s
    elif policy=="native_log_lambda":
        values=direct
        mode=policy
        common_mapping=0.0
    else:
        values=None
        mode=policy
        common_mapping=0.0
    # Validate once, OUTSIDE timed blocks. Scoring reference spectra
    # within the timer would falsely advantage slow/fast backends alike.
    verify_backend=Backend(n,d,method,criterion)
    checks=[]
    for y in ys:
        if policy in CONTINUOUS_POLICIES:
            checks.append(continuous_search(
                verify_backend,smoother,y,mu,criterion,mode,mapped,
                check=True))
        else:
            checks.append(evaluate_grid(
                verify_backend,smoother,y,mu,criterion,mode,values,
                check=True))
    records=[]
    max_error=0.
    for _ in range(repeats):
        setup=0.0
        elapsed=0.0
        shared=None
        if reuse_mode=="shared":
            t0=perf_counter()
            shared=Backend(n,d,method,criterion)
            setup=perf_counter()-t0
        evaluated=[]
        for y in ys:
            backend=shared
            if backend is None:
                t0=perf_counter()
                backend=Backend(n,d,method,criterion)
                setup+=perf_counter()-t0
            t0=perf_counter()
            if policy in CONTINUOUS_POLICIES:
                evaluated.append(continuous_search(
                    backend,smoother,y,mu,criterion,mode,mapped,check=False))
            else:
                evaluated.append(evaluate_grid(
                    backend,smoother,y,mu,criterion,mode,values,check=False))
            elapsed+=perf_counter()-t0
        records.append((setup,elapsed,evaluated))
    setups=np.array([r[0] for r in records])
    evaluations=np.array([r[1] for r in records])
    totals=setups+evaluations
    setup=float(np.median(setups))
    runtime=float(np.median(evaluations))
    total=float(np.median(totals))
    representative=checks
    valid_count=sum(bool(r["valid"]) for r in representative)
    for e in representative:
        if "errors" in e:
            valid_err=[v for v in e["errors"] if np.isfinite(v)]
            max_error=max(max_error,max(valid_err,default=0.))
    selected=[float(e["s"]) for e in representative if np.isfinite(e["s"])]
    scores=[float(e["score"]) for e in representative
            if np.isfinite(e["score"])]
    calls=(sum(e["calls"] for e in representative)
           if policy in CONTINUOUS_POLICIES else R*len(values))
    # Policy-level timing: common S grid was inverted once OUTSIDE
    # method timer; this is charged once for a standalone selection.
    # Across 5 criteria x 7 methods x R series, reuse it ONCE, not 35R.
    return dict(
        n=n,d=d,mu=mu,criterion=criterion,method=method,R=R,
        workload=("single" if policy in SINGLE_POLICIES else
                  ("continuous" if policy in CONTINUOUS_POLICIES else "grid")),
        policy=policy,reuse_mode=reuse_mode,
        status=("ok" if valid_count==R else "numerical_or_criterion_failure"),
        success=valid_count==R,
        setup_s=setup,evaluate_s=runtime,mapping_once_s=common_mapping,
        total_standalone_s=total+common_mapping,total_backend_only_s=total,
        selected_s=float(np.mean(selected)) if selected else float("nan"),
        mean_score=float(np.mean(scores)) if scores else float("nan"),
        candidate_evaluations=calls,valid_series=valid_count,
        invalid_series=R-valid_count,max_error=max_error,
        repeats=repeats,shared_grid_size=17,
    )


def workloads(preset):
    if preset=="smoke":
        return (16,), (1,2), (20261026,), (0,2,5), (
            "cv","gcv","mle"), ("svd","eigh","banded_cholesky"), 1
    if preset=="quick":
        return (24,), (1,3), (20261026,), tuple(range(6)), (
            *CRITERIA,), (*BACKENDS,), 2
    if preset=="full":
        return (24,48), (1,3,8), (20261026,20261027), tuple(range(6)), (
            *CRITERIA,), (*BACKENDS,), 5
    raise ValueError(preset)


def run(preset="quick",repeats=None,seed=20261026,threads=1,
        output=HERE/"results"/"full_s_search_modes"):
    (n_values,R_values,seeds,orders,criteria,backends,
     default_repeats)=workloads(preset)
    repeats=default_repeats if repeats is None else int(repeats)
    if repeats<1 or threads<1:
        raise ValueError("repeats and threads must be positive")
    rows,design_rows=[],[]
    with threadpool_limits(limits=threads):
        meta=dict(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            python=sys.version,platform=platform.platform(),
            scipy=scipy.__version__,numpy=np.__version__,
            blas_threads=threads,threadpools=threadpool_info(),
            preset=preset,repeats=repeats,seeds=list(seeds),
            n=list(n_values),d=list(orders),
            reference_means=[0.,.15],criteria=list(criteria),
            backends=list(backends),R=list(R_values),
            policies=list(SINGLE_POLICIES)+list(GRID_POLICIES)+list(CONTINUOUS_POLICIES),
            reuse_modes=["shared","cold"],
            difference_between_policies=(
                "native_s and mapped_s_lambda use identical 17 candidates; "
                "native_log_lambda uses 17 different interior penalties "
                "with equal finite endpoints; continuous_s/loglambda "
                "perform bounded local minimization and check exact endpoints "
                "but are NOT global optimization. Single is one S=.5 score. "
                "Timed backend setup and evaluation exclude shared grid "
                "construction; standalone mapped runtime counts it once."
            ),
        )
        total=len(n_values)*len(orders)*len(seeds)*2*len(criteria)*len(backends)*len(R_values)*8*2
        count=0
        for n in n_values:
            for d in orders:
                sm=TrendSmoother(n,d)
                targets,mapped,direct,elapsed=design(sm)
                design_rows.append(dict(n=n,d=d,candidate_count=len(targets),
                                        map_once_s=elapsed,
                                        S_min=targets[0],S_max=targets[-1],
                                        finite_lambda_min=mapped[1],
                                        finite_lambda_max=mapped[-2]))
                for seed_i in seeds:
                    for mu in (0.,.15):
                        for criterion in criteria:
                            for method in backends:
                                for R in R_values:
                                    for reuse_mode in ("shared","cold"):
                                        for policy in SINGLE_POLICIES+GRID_POLICIES+CONTINUOUS_POLICIES:
                                            rows.append(measure_one(
                                                n,d,mu,criterion,method,R,policy,
                                                seed_i,repeats,sm,targets,mapped,
                                                direct,elapsed,reuse_mode))
                                            count+=1
                                    if count % 252 == 0:
                                        print(f"[search] {count}/{total} "
                                              f"n={n}, d={d}, R={R}, mu={mu}, "
                                              f"criterion={criterion}",flush=True)
        print(f"Recorded {len(rows)} method/criterion/workload/search cells")
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    def write(name,data):
        with (output/name).open("w",newline="",encoding="utf-8") as stream:
            writer=csv.DictWriter(stream,fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    write("search_mode_timings.csv",rows)
    write("search_grid_preparation.csv",design_rows)
    (output/"environment.json").write_text(
        json.dumps(meta,indent=2),encoding="utf-8")
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preset",choices=("smoke","quick","full"),
                   default="quick")
    p.add_argument("--repeats",type=int,default=None)
    p.add_argument("--seed",type=int,default=20261026)
    p.add_argument("--threads",type=int,default=1)
    p.add_argument("--output",type=Path,
                   default=HERE/"results"/"full_s_search_modes")
    a=p.parse_args()
    run(a.preset,a.repeats,a.seed,a.threads,a.output)


if __name__=="__main__":
    main()
