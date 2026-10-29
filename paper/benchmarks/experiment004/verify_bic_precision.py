"""Experiment004: BIC small-S audit and independent high-precision PLS QA.

Reuses run_pilot.py's fixed synthetic seed and S-to-lambda mapping.
Outputs raw BIC and fit-validation rows; no full computational factorial.

    python paper/benchmarks/experiment004/verify_bic_precision.py \
        --out paper/benchmarks/experiment004/runs/<unique-validation-id>
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import mpmath as mp
import numpy as np
from scipy.linalg import cholesky_banded, cho_solve_banded
from scipy.optimize import brentq
from scipy.special import expit

import run_pilot as pilot

SMALL_S = (
    1e-12, 1e-10, 1e-8, 1e-6, 1e-4, .001, .005,
    .01, .02, .05, .1, .2, .5, .9,
)
HIGH_S = (.9, .99, .999, .999999, 1 - 1e-8, 1 - 1e-12)


def seeded_observations(n):
    actual = pilot.truth(n, "smooth")
    # Same seed scheme as the completed 20-seed pilot, first iid seed.
    rng = np.random.default_rng(
        np.random.SeedSequence([20261028, n, 0, 0, 0])
    )
    return actual, actual + pilot.noise(n, "iid", rng)


def fixed_mean(model, y, policy):
    if policy == "fixed_zero":
        return 0.0
    if policy == "observed_difference":
        return float(np.mean(model["D"] @ y))
    raise ValueError(policy)


def bic_near_zero(n, d, policy):
    model = pilot.prepare(n, d)
    truth, y = seeded_observations(n)
    mu = fixed_mean(model, y, policy)
    z = model["U"].T @ (y - pilot.reference(n, d, mu))
    log_delta = np.log(model["delta"])
    rows = []
    for s in SMALL_S:
        logit = math.log(s) - math.log1p(-s)
        lo = logit - float(log_delta.max()) - 2.
        hi = logit - float(log_delta.min()) + 2.
        loglam = brentq(
            lambda x: float(np.mean(expit(x + log_delta))) - s,
            lo, hi, xtol=1e-12,
        )
        w = expit(loglam + log_delta)
        rss = float(np.sum((w * z)**2))
        edf = n - float(np.sum(w))
        # Paper Eq. (21): log(RSS) - log(n) + EDF*log(n)/n.
        bic = math.log(rss / n) + edf * math.log(n) / n
        fit = y - model["U"] @ (w * z)
        rows.append(dict(
            n=n, d=d, mu_policy=policy, s=s, lambda_=math.exp(loglam),
            rss=rss, edf=edf, bic=bic,
            true_trend_rmse=float(np.sqrt(np.mean((fit-truth)**2))),
        ))
    return rows


def precise_dual_banded(n, d, y, mu, lam, decimal_digits=85):
    """High-precision, banded *dual* solve using no primal normal matrix.

    (D D.T + lambda^(-1) I) u = D y - mu 1
    tau = y - D.T u

    The Toeplitz D D.T bands are (-1)^k binom(2d,d-k).
    Banded Cholesky has O((n-d)d^2) arithmetic and O((n-d)d)
    storage. The reference uses decimal-converted float64 y, mu
    and lambda, so it tests the same parameter inputs as the pilot.
    """
    with mp.workdps(decimal_digits):
        m = n - d
        coeff = [(-1)**(d-j) * math.comb(d,j) for j in range(d+1)]
        obs = [mp.mpf(float(x)) for x in y]
        mm = mp.mpf(float(mu))
        lp = mp.mpf(float(lam))
        rhs = [
            mp.fsum(coeff[j]*obs[i+j] for j in range(d+1))-mm
            for i in range(m)
        ]
        band = [
            mp.mpf((-1)**k * math.comb(2*d,d-k))
            for k in range(d+1)
        ]
        alpha = 1/lp
        L = [[mp.mpf(0) for _ in range(d+1)] for _ in range(m)]
        for i in range(m):
            L[i][0] = mp.sqrt(
                band[0] + alpha -
                mp.fsum(L[i][i-k]**2 for k in range(max(0,i-d),i))
            )
            for j in range(i+1,min(m,i+d+1)):
                partial = mp.fsum(
                    L[j][j-k]*L[i][i-k]
                    for k in range(max(0,j-d),i)
                    if i-k <= d and j-k <= d
                )
                L[j][j-i] = (band[j-i]-partial)/L[i][0]
        v = []
        for i in range(m):
            v.append((
                rhs[i] -
                mp.fsum(L[i][i-j]*v[j] for j in range(max(0,i-d),i))
            )/L[i][0])
        u = [mp.mpf(0) for _ in range(m)]
        for i in range(m-1,-1,-1):
            u[i] = (
                v[i] -
                mp.fsum(
                    L[j][j-i]*u[j]
                    for j in range(i+1,min(i+d+1,m))
                )
            )/L[i][0]
        fitted = obs.copy()
        for i in range(m):
            for j in range(d+1):
                fitted[i+j] -= coeff[j]*u[i]
        # Independent KKT check in high precision:
        # tau - y + lambda D.T(D tau - mu 1) = 0.
        penalty_residual = [
            mp.fsum(coeff[j]*fitted[i+j] for j in range(d+1))-mm
            for i in range(m)
        ]
        kkt = [fitted[i]-obs[i] for i in range(n)]
        for i in range(m):
            for j in range(d+1):
                kkt[i+j] += lp*coeff[j]*penalty_residual[i]
        return (
            np.asarray([float(x) for x in fitted], dtype=float),
            float(max(abs(x) for x in kkt)),
        )


def primal_bands(model):
    n, d = model["n"], model["d"]
    coeff = [(-1)**(d-j)*math.comb(d,j) for j in range(d+1)]
    bands = np.zeros((d+1,n),dtype=float)
    for i in range(n-d):
        for a in range(d+1):
            for b in range(a,d+1):
                bands[b-a,i+a] += coeff[a]*coeff[b]
    return bands


def high_precision_qa(model, policy, s, decimal_digits):
    n, d = model["n"], model["d"]
    _, y = seeded_observations(n)
    mu = fixed_mean(model, y, policy)
    j = int(np.argmin(np.abs(pilot.S_GRID-s)))
    exact_s = float(pilot.S_GRID[j])
    lam = float(model["lambdas"][j])
    ref, kkt = precise_dual_banded(n,d,y,mu,lam,decimal_digits)
    spectral = y - model["U"] @ (
        model["w"][j] *
        (model["U"].T @ (y-pilot.reference(n,d,mu)))
    )
    scale = max(1.,float(np.linalg.norm(ref)))
    row = dict(
        n=n, d=d, mu_policy=policy, mu=mu, s=exact_s, lambda_=lam,
        ref_norm=float(np.linalg.norm(ref)),
        spectral_relative_error=float(np.linalg.norm(spectral-ref)/scale),
        spectral_max_abs=float(np.max(np.abs(spectral-ref))),
        cholesky_relative_error="",
        cholesky_status="factorization_failed",
        high_precision_kkt_max=kkt, decimal_digits=decimal_digits,
    )
    bands = primal_bands(model)
    ab = lam*bands
    ab[0,:] += 1.
    try:
        ch = cholesky_banded(ab,lower=True,check_finite=False)
        other = pilot.reference(n,d,mu) + cho_solve_banded(
            (ch,True),y-pilot.reference(n,d,mu),check_finite=False
        )
        row["cholesky_status"] = "ok"
        row["cholesky_relative_error"] = float(
            np.linalg.norm(other-ref)/scale
        )
    except (np.linalg.LinAlgError,ValueError,OverflowError) as error:
        row["cholesky_status"] = type(error).__name__
    return row


def save_csv(path,rows):
    with path.open("w",newline="",encoding="utf-8") as handle:
        writer = csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--digits",type=int,default=85)
    args=parser.parse_args()
    if args.out.exists():
        parser.error("Output directory already exists; never overwrite")
    if args.digits < 55:
        parser.error("High-precision reference must use >=55 digits")
    args.out.mkdir(parents=True)
    started=perf_counter()
    bic_rows=[]
    fits=[]
    for n in (64,128):
        for d in (1,2,5,6):
            for policy in ("fixed_zero","observed_difference"):
                bic_rows.extend(bic_near_zero(n,d,policy))
    for n in (64,128):
        for d in (5,6):
            model=pilot.prepare(n,d)
            for policy in ("fixed_zero","observed_difference"):
                for s in HIGH_S:
                    fits.append(high_precision_qa(model,policy,s,args.digits))
    # Verify convergence at multiple precisions on the hardest corner
    # cases. This independently tests the high-precision calculation.
    consistency=[]
    for n,d,s in ((128,6,1-1e-12),(128,5,1-1e-12),(128,6,.99)):
        model=pilot.prepare(n,d)
        _,y=seeded_observations(n)
        mu=fixed_mean(model,y,"observed_difference")
        j=int(np.argmin(np.abs(pilot.S_GRID-s)))
        lam=float(model["lambdas"][j])
        fit55,kkt55=precise_dual_banded(n,d,y,mu,lam,55)
        fit110,kkt110=precise_dual_banded(n,d,y,mu,lam,110)
        agreement=float(np.max(np.abs(fit55-fit110)))
        consistency.append(dict(
            n=n,d=d,s=s,fit_max_abs_55_vs_110=agreement,
            kkt_max_55=kkt55,kkt_max_110=kkt110,
        ))
        if agreement > 1e-9:
            raise ArithmeticError("High-precision convergence failed")
    if len(bic_rows)!=224 or len(fits)!=48:
        raise AssertionError("Incomplete scientific factorial")
    if not all(row["high_precision_kkt_max"]<1e-20 for row in fits):
        raise ArithmeticError("High-precision KKT check failed")
    save_csv(args.out/"bic_small_s.csv",bic_rows)
    save_csv(args.out/"high_precision.csv",fits)
    save_csv(args.out/"precision_convergence.csv",consistency)
    meta=dict(
        experiment="experiment004_bic_and_precision_validation",
        date_utc=datetime.now(timezone.utc).isoformat(),
        python=sys.version,numpy=np.__version__,
        scipy=__import__("scipy").__version__,mpmath=mp.__version__,
        host=platform.platform(),decimal_digits=args.digits,
        elapsed_seconds=perf_counter()-started,
        bic_rows=len(bic_rows),high_precision_rows=len(fits),
        convergence_cases=len(consistency),
        d_values=[1,2,5,6],n_values=[64,128],
        mu_policies=["fixed_zero","observed_difference"],
        fixed_input_note=(
            "Synthetic smooth-trend iid-noise seed=0 from original "
            "Experiment004; lambda and mu are frozen float64 inputs."
        ),
        max_spectral_error=max(
            r["spectral_relative_error"] for r in fits
        ),
        max_finite_banded_error=max(
            r["cholesky_relative_error"] for r in fits
            if r["cholesky_relative_error"]!=""
        ),
        cholesky_failures=sum(
            r["cholesky_status"]!="ok" for r in fits
        ),
        max_reference_kkt=max(
            r["high_precision_kkt_max"] for r in fits
        ),
        note=(
            "BIC follows Cortes-Toto 2017 Eq.21. "
            "The low-S BIC limit diverges to negative infinity when "
            "RSS is nonzero for positive lambda. "
            "These are *fit* comparisons, not selected-parameter "
            "or out-of-sample prediction claims."
        ),
    )
    for name in ("bic_small_s.csv","high_precision.csv",
                 "precision_convergence.csv"):
        meta[name+"_sha256"] = hashlib.sha256(
            (args.out/name).read_bytes()
        ).hexdigest()
    (args.out/"metadata.json").write_text(
        json.dumps(meta,indent=2)+"\n",encoding="utf-8"
    )
    print(json.dumps({
        key:meta[key] for key in (
            "bic_rows","high_precision_rows","max_spectral_error",
            "max_finite_banded_error","cholesky_failures",
            "max_reference_kkt","elapsed_seconds",
        )
    },indent=2))


if __name__=="__main__":
    main()
