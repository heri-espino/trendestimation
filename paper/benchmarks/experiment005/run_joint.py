"""Experiment005: paired numerical accuracy and wall time on the SAME PLS runs.

Run from repository root; no publication run should silently use these pilots.
The 85-digit independent dual reference and criterion scoring are outside
timed blocks. Each double-precision solve is timed and its returned values
are subsequently validated. No invalid/partial grid is allowed to win.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

import numpy as np
import scipy
from threadpoolctl import threadpool_limits, threadpool_info

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
EX004 = BENCH / "experiment004"
for folder in (str(BENCH), str(EX004)):
    if folder not in sys.path:
        sys.path.insert(0, folder)

import run_pilot as pilot  # noqa: E402
from verify_stable_solvers import observations, mean_value  # noqa: E402
from verify_bic_precision import precise_dual_banded  # noqa: E402
from full_s_backend_criteria import Backend, complete_s_grid  # noqa: E402
from trendestimation import TrendSmoother, score_lambda  # noqa: E402
from trendestimation.solvers import PreparedPLSSolver  # noqa: E402

METHODS = ("svd", "eigh", "banded_cholesky")
FIT_METHOD = {"svd":"svd", "eigh":"eigh", "banded_cholesky":"cholesky"}
CRITERIA = ("cv", "gcv", "aicc", "bic", "mle")
MU_POLICIES = ("fixed_zero", "observed_difference")
TOL = 1e-5


def design(preset):
    if preset == "smoke":
        return ((24,), (3,), ("smooth",), ("iid",), (0,))
    if preset == "pilot":
        return ((32,64), (2,3,5,6), ("smooth","kink"),
                ("iid","ar1"), (0,))
    if preset == "full":
        return ((64,128), (1,2,3,4,5,6), ("smooth","kink"),
                ("iid","ar1"), (0,1,2))
    raise ValueError(preset)


def save_csv(path, rows):
    if not rows:
        raise ValueError("Cannot archive empty evidence")
    with path.open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def median_measure(action, repeats):
    times=[]
    first=None
    for _ in range(repeats):
        started=perf_counter_ns()
        value=action()
        duration=(perf_counter_ns()-started)/1e6
        times.append(duration)
        if first is None:
            first=value
    return first,statistics.median(times),times


def reference_limit(n,d,y,mu, s):
    if s == 0:
        return y.copy()
    # The polynomial nullspace is of degree d-1 after subtracting
    # the fixed-mean reference polynomial p_mu.
    x=np.linspace(-1,1,n)
    basis=np.polynomial.legendre.legvander(x,d-1)
    centered=y-pilot.reference(n,d,mu)
    return pilot.reference(n,d,mu)+basis@np.linalg.lstsq(
        basis,centered,rcond=None
    )[0]


def benchmark(args):
    ns,ds,shapes,noises,seeds=design(args.preset)
    grid=complete_s_grid()
    assert len(grid)==17 and grid[0]==0 and grid[-1]==1
    fit_rows=[]
    select_rows=[]
    preparation=[]
    reference_rows=[]
    start_all=perf_counter_ns()

    with threadpool_limits(limits=args.threads):
        for n in ns:
            for d in ds:
                smoother,svd_setup,svd_times=median_measure(
                    lambda:TrendSmoother(n,order=d),args.repeats
                )
                lambdas,map_ms,map_times=median_measure(
                    lambda:np.array([
                        smoother.lambda_for_smoothness(float(s))
                        for s in grid
                    ]),args.repeats
                )
                recovered=np.array([
                    smoother.smoothness(float(lam)) for lam in lambdas
                ])
                if not np.allclose(recovered,grid,rtol=0,atol=5e-10):
                    raise ArithmeticError("S-to-lambda inversion mismatch")
                # Prepare both distinct operations and record separate,
                # independently timed, cold allocations.
                prepared={}
                for method in METHODS:
                    try:
                        (fit_solver,fit_setup,_)=median_measure(
                            lambda:PreparedPLSSolver(
                                n,order=d,method=FIT_METHOD[method]),
                            args.repeats
                        )
                        prepared[method]=(fit_solver,fit_setup,"ok")
                    except Exception as exc:
                        prepared[method]=(None,float("nan"),
                                          type(exc).__name__)
                    preparation.append(dict(
                        n=n,d=d,method=method,
                        spectral_setup_ms=svd_setup,
                        s_grid_mapping_ms=map_ms,
                        fit_backend_setup_ms=prepared[method][1],
                        setup_status=prepared[method][2],
                        candidate_count=len(grid),
                        iterations_repeats=args.repeats
                    ))
                for shape in shapes:
                    for noise in noises:
                        for seed in seeds:
                            truth,y=observations(n,shape,noise,seed)
                            for mu_policy in MU_POLICIES:
                                mu=mean_value({"D":pilot.difference_matrix(n,d)},y,mu_policy)
                                key=dict(n=n,d=d,shape=shape,noise=noise,seed=seed,
                                         mu_policy=mu_policy,mu=mu)
                                references=[]
                                for j,(s,lam) in enumerate(zip(grid,lambdas)):
                                    if s==0 or s==1:
                                        truth_ref=reference_limit(n,d,y,mu,s)
                                        kkt=float("nan")
                                        kind="analytic_endpoint_not_independent_85digit"
                                    else:
                                        truth_ref,kkt=precise_dual_banded(
                                            n,d,y,mu,float(lam),
                                            decimal_digits=args.digits)
                                        kind="85_digit_dual_cholesky"
                                        if not math.isfinite(kkt) or kkt>1e-18:
                                            raise ArithmeticError(
                                                f"Reference KKT failure {n=} {d=} {s=} {kkt=}")
                                    references.append(truth_ref)
                                    reference_rows.append({
                                        **key,"j":j,"s":float(s),"lambda_":float(lam),
                                        "reference_kind":kind,"reference_kkt":kkt,
                                        "reference_norm":float(np.linalg.norm(truth_ref)),
                                    })
                                fits_by_method={}
                                for method in METHODS:
                                    solver,setup_ms,setup_status=prepared[method]
                                    for j,(s,lam) in enumerate(zip(grid,lambdas)):
                                        row={**key,"method":method,"j":j,
                                             "s":float(s),"lambda_":float(lam),
                                             "method_setup_ms":setup_ms,
                                             "fit_ms":float("nan"),"status":"failure",
                                             "failure_detail":"",
                                             "reference_rel_l2":float("nan"),
                                             "reference_max_abs":float("nan"),
                                             "latent_trend_rmse":float("nan"),
                                             "reference_kind":reference_rows[-len(grid)+j]["reference_kind"]}
                                        try:
                                            if solver is None:
                                                raise ArithmeticError(setup_status)
                                            fit,fit_ms,_=median_measure(
                                                lambda:solver.fit(
                                                    y,lambda_=float(lam),mu=mu),
                                                args.repeats
                                            )
                                            if not np.all(np.isfinite(fit)):
                                                raise ArithmeticError("nonfinite fit")
                                            scale=max(1.,float(np.linalg.norm(references[j])))
                                            rel=float(np.linalg.norm(fit-references[j])/scale)
                                            row.update(
                                                fit_ms=fit_ms,
                                                status="valid" if rel<=args.tolerance else "inaccurate",
                                                reference_rel_l2=rel,
                                                reference_max_abs=float(np.max(
                                                    np.abs(fit-references[j]))),
                                                latent_trend_rmse=float(np.sqrt(
                                                    np.mean((fit-truth)**2))),
                                            )
                                            fits_by_method[(method,j)]=(fit,fit_ms,rel)
                                        except Exception as exc:
                                            row["failure_detail"]=type(exc).__name__+":"+str(exc)[:100]
                                        fit_rows.append(row)

                                for criterion in CRITERIA:
                                    # Independent criterion truth is assessed outside
                                    # all measured solve/selection operations.
                                    baseline=np.asarray([
                                        score_lambda(smoother,y,
                                            lambda_=float(lam),
                                            criterion=criterion,mu=mu)
                                        for lam in lambdas
                                    ],dtype=float)
                                    eligible=(grid>=.10 if criterion=="bic"
                                              else np.ones(len(grid),dtype=bool))
                                    baseline_valid=eligible&np.isfinite(baseline)
                                    oracle_rmse=float(np.min([
                                        np.sqrt(np.mean((fit-truth)**2))
                                        for fit in references
                                    ]))
                                    for method in METHODS:
                                        row={**key,"criterion":criterion,
                                             "method":method,
                                             "candidate_count":len(grid),
                                             "eligible_count":int(eligible.sum()),
                                             "reference_finite_scores":int(baseline_valid.sum()),
                                             "status":"failed",
                                             "selected_s":float("nan"),
                                             "selected_lambda":float("nan"),
                                             "selected_index":-1,
                                             "selected_score":float("nan"),
                                             "selection_score_rel_error_max":float("nan"),
                                             "selected_fit_reference_error":float("nan"),
                                             "selected_true_rmse":float("nan"),
                                             "oracle_true_rmse":oracle_rmse,
                                             "score_only_ms":float("nan"),
                                             "fit_ms":float("nan"),
                                             "score_backend_setup_ms":float("nan"),
                                             "fit_backend_setup_ms":prepared[method][1],
                                             "mapping_ms":map_ms,
                                             "assembled_cold_ms":float("nan"),
                                             "warm_selection_ms":float("nan"),
                                             "failure_detail":""}
                                        try:
                                            backend,setup_ms,_=median_measure(
                                                lambda:Backend(n,d,method,criterion),
                                                args.repeats)
                                            row["score_backend_setup_ms"]=setup_ms
                                            def score_grid():
                                                scores=np.empty(len(grid))
                                                for j,(s,lam) in enumerate(zip(grid,lambdas)):
                                                    if s==0 or s==1:
                                                        # Common analytic limit; never
                                                        # benchmark fake infinite-lambda solve.
                                                        scores[j]=baseline[j]
                                                    else:
                                                        scores[j]=backend.calculate(
                                                            y,float(lam),mu,criterion)[0]
                                                return scores
                                            measured,score_ms,_=median_measure(
                                                score_grid,args.repeats)
                                            row["score_only_ms"]=score_ms
                                            status_ok=True
                                            errors=[]
                                            for j in np.flatnonzero(eligible):
                                                ref,got=baseline[j],measured[j]
                                                if np.isfinite(ref):
                                                    if not np.isfinite(got):
                                                        status_ok=False
                                                    else:
                                                        re=abs(got-ref)/max(1.,abs(ref))
                                                        errors.append(re)
                                                        if re>args.tolerance:
                                                            status_ok=False
                                                elif np.isfinite(got):
                                                    status_ok=False
                                            row["selection_score_rel_error_max"]=(
                                                max(errors) if errors else float("nan"))
                                            if not status_ok or not baseline_valid.any():
                                                row["status"]="invalid_complete_grid"
                                            else:
                                                masked=np.where(baseline_valid,measured,np.inf)
                                                idx=int(np.argmin(masked))
                                                row.update(selected_index=idx,
                                                           selected_s=float(grid[idx]),
                                                           selected_lambda=float(lambdas[idx]),
                                                           selected_score=float(measured[idx]))
                                                record=fits_by_method.get((method,idx))
                                                if record is None:
                                                    row["status"]="selected_fit_failure"
                                                else:
                                                    fit,fit_ms,rel=record
                                                    row["fit_ms"]=fit_ms
                                                    row["selected_fit_reference_error"]=rel
                                                    row["selected_true_rmse"]=float(np.sqrt(
                                                        np.mean((fit-truth)**2)))
                                                    if rel>args.tolerance:
                                                        row["status"]="selected_fit_inaccurate"
                                                    else:
                                                        row["status"]="valid"
                                                        # Stage-sum, not a separately
                                                        # measured cold application wall time.
                                                        row["warm_selection_ms"]=score_ms+fit_ms
                                                        row["assembled_cold_ms"]=(
                                                            map_ms+setup_ms+
                                                            prepared[method][1]+score_ms+fit_ms)
                                        except Exception as exc:
                                            row["failure_detail"]=type(exc).__name__+":"+str(exc)[:130]
                                        select_rows.append(row)
    return grid,fit_rows,select_rows,preparation,reference_rows,(perf_counter_ns()-start_all)/1e9


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--preset",choices=("smoke","pilot","full"),
                        default="smoke")
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--digits",type=int,default=85)
    parser.add_argument("--repeats",type=int,default=3)
    parser.add_argument("--threads",type=int,default=1)
    parser.add_argument("--tolerance",type=float,default=TOL)
    args=parser.parse_args()
    if args.out.exists():
        parser.error("Never overwrite an existing experiment005 run directory")
    if args.digits<55 or args.repeats<2 or args.threads<1 or args.tolerance<=0:
        parser.error("Require digits>=55, repeats>=2, threads>=1, tolerance>0")
    args.out.mkdir(parents=True)
    try:
        grid,fits,selections,setup,references,elapsed=benchmark(args)
        paths={
            "fit_accuracy_runtime.csv":fits,
            "selection_accuracy_runtime.csv":selections,
            "setup_and_mapping.csv":setup,
            "reference_checks.csv":references,
        }
        for filename,rows in paths.items():
            save_csv(args.out/filename,rows)
        status={kind:sum(r["status"]==kind for r in selections)
                for kind in sorted({r["status"] for r in selections})}
        summary={
            "experiment":"experiment005_joint_accuracy_runtime",
            "preset":args.preset,
            "purpose":"same-data same-penalty paired accuracy and elapsed time",
            "created_utc":datetime.now(timezone.utc).isoformat(),
            "platform":platform.platform(),"python":sys.version,
            "numpy":np.__version__,"scipy":scipy.__version__,
            "blas_threads":args.threads,"threadpools":threadpool_info(),
            "repeats":args.repeats,"digits":args.digits,
            "reference_tolerance":args.tolerance,
            "n":list(design(args.preset)[0]),
            "d":list(design(args.preset)[1]),
            "S":list(map(float,grid)),
            "mu_policies":list(MU_POLICIES),"methods":list(METHODS),
            "criteria":list(CRITERIA),
            "fit_rows":len(fits),
            "selection_rows":len(selections),
            "reference_rows":len(references),
            "selection_status_counts":status,
            "elapsed_seconds":elapsed,
            "scope":[
                "Trend recovery RMSE, not forecast RMSE.",
                "BIC restricts S>=0.10; sensitivity to 0.05 deferred.",
                "Observed-difference mu is a conditional plug-in.",
                "85-digit checks freeze float64 lambda, mu, y and exclude timing.",
                "Endpoint validation is analytical, not independent multiprecision.",
                "Score-only and fit-only timing stages are measured separately.",
                "Assembled cold totals are sums of measured stages, not a new wall-clock sample.",
                "Invalid complete grids and selected-fit discrepancies cannot win time ranking.",
                "Do not compare differently spaced lambda candidate sets.",
                "Baseline spectral score audit is outside timed blocks."
            ],
        }
        for name in paths:
            summary[name+"_sha256"]=hashlib.sha256(
                (args.out/name).read_bytes()).hexdigest()
        (args.out/"summary.json").write_text(
            json.dumps(summary,indent=2,allow_nan=False)+"\n",
            encoding="utf8")
        print(json.dumps({k:summary[k] for k in (
            "fit_rows","selection_rows","reference_rows",
            "selection_status_counts","elapsed_seconds")},indent=2))
    except Exception:
        # Preserve partial output rather than pretending it is complete.
        (args.out/"INCOMPLETE.txt").write_text(
            "Experiment005 failed before successful summary; never publish as completed.\n")
        raise


if __name__=="__main__":
    main()
