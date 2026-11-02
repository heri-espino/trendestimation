# Experiment009 — Empirical comparison of the theoretical n-by-d crossover surfaces

## Sources and exact outputs

Frozen data and reproducible code are in
paper/benchmarks/experiment009/. The first validated generated result
is in the immutable results branch
results/experiment009-crossover-41537222327 (Actions #41537222327).
A follow-up run adds explicit M_star roots and a class-imbalance warning.

Fit-only Windows source: results/experiment007-selfhosted-41510943429,
12 seed blocks, n=64/128/256, d1..6, mu=data/zero, both scale regimes,
one/grid S (M1/7), one/three series (R1/3).

Complete AICc Windows source: results/experiment008-41529113497-broad,
n=64/128/256/512, d1..6, conditional plug-in mu=data, high scale,
mapped-lambda, M1/100 and R1/2. This study includes spectral S-to-lambda
mapper preparation in BOTH solver reported cold times; it is not a
pure numerical factorization comparison.

## Two distinct theoretical cost models

Complete selection (e.g. global spectral AICc):

    T_svd=a*n^3+b*R*n^2+c_C*M*R*n
    T_chol=u*M*n*d^2+v*M*R*n*d

under reusable banded factors. The mapping overhead must be added or
explicitly treated as shared. Conditional global-score spectral
work has q_C=1; ordinary CV can require q_C=2.

Full fitted trends instead require

    T_svd_fit=a_f*n^3+b_f*R*n^2+c_f*M*R*n^2,
    T_chol_fit=O(M*R*n*d^2)+O(M*R*n*d)

for the Experiment007 Cholesky backend with no factor reuse.

The numerical crossover M_star exists if the per-candidate
Cholesky slope exceeds the SVD slope:

    M_star = (a*n^3+b*R*n^2) /
       (u*n*d^2+v*R*n*d-c_C*R*n^q_C).

The NNLS-fitted terms are machine-specific positive or zero
coefficients, NOT known universal constants. A coefficient fitted
as zero means that component was not identifiable in these observed
workloads; it does NOT imply its theoretical operation count vanishes.

## Actual observed winners: full TREND FITS, M=7, R=3, mu=data, high magnitude

| n | d=1 | d=2 | d=3 | d=4 | d=5 | d=6 |
|---:|---|---|---|---|---|---|
| 64 | Cholesky | Cholesky | Cholesky, near tie | Cholesky invalid | Cholesky invalid | Cholesky invalid |
| 128 | Cholesky | Cholesky | Cholesky invalid | Cholesky invalid | Cholesky invalid | Cholesky invalid |
| 256 | Cholesky | Cholesky | Cholesky invalid | Cholesky invalid | Cholesky invalid | Cholesky invalid |

At n=256,d1/d2, validated complete M=7,R=3 fit-only
Cholesky was 7.43x / 6.41x faster than SVD, respectively, for high
magnitude mu=data. At n=64,d=3, the difference was only about 2.5%.
Cholesky's high-order invalid status is an accuracy/validity
constraint, **not proof SVD is computationally faster**.

## Actual observed winners: complete AICc, M=100, R=2, mu=data, high magnitude

| n | d=1 | d=2 | d=3 | d=4 | d=5 | d=6 |
|---:|---|---|---|---|---|---|
| 64 | SVD | SVD | SVD | SVD | SVD | SVD |
| 128 | SVD | SVD | SVD | SVD | SVD | Cholesky invalid |
| 256 | SVD | SVD | SVD | SVD | Cholesky invalid | Cholesky invalid |
| 512 | SVD grid ineligible | SVD grid ineligible | SVD grid ineligible | Both ineligible | Both ineligible | Both ineligible |

The measured full-criterion AICc pipeline favors SVD over Cholesky
for complete 100-point selection grids at n<=256 wherever both
are eligible. In contrast, the full-trend-fit workload often
favors Cholesky. This is precisely why a universal d-only
solver-selection rule is inappropriate.

## Calibration and held-out n validation

Theory-constrained nonnegative cost coefficients were estimated
from n=64/128 (fit-only) and n=64/128/256 (AICc), leaving n=256
and n=512 respectively completely out of fitting.

First run's validation labels:
- Fit-only holdout n=256: 61/61 classifications correct, BUT every
  one of the 61 comparable cases was a Cholesky win.
- Full-AICc holdout n=512: 8/8 classifications correct, BUT every
  comparable case was also a Cholesky win, and ALL M=100 grid
  SVD rows at n=512 were resource-ineligible.

Thus the nominal 100% holdout accuracy is **not evidence** that the
model predicts a real crossover: the holdout sets contain only
one winning class. Training calibration is also imperfect:
fit-only 137/142 comparable training classifications correct;
AICc 46/60 training classifications correct. This paper must
report class balance alongside predictive accuracy.

The fitted cost coefficients are dependent on the concrete
Python/BLAS implementation, one physical Windows machine,
M grids limited to {1,7} and {1,100} respectively, and a narrow
range of n. The M=100/1000/10000/100000 fit-only surface is
a theory-based extrapolation, NOT observed performance.
The full-AICc surface is NOT a fitted model for CV/GCV/BIC/MLE.

## Proposed conservative dispatch (research hypothesis)

For a requested (n,d,M,R,C,S-grid,mean,scale):
1. Use the distinct criterion-specific cost formula and
   machine-calibrated coefficients, not one universal d cutoff.
2. Reject any method violating RAM/time feasibility. A dense
   n=131072 SVD is not a realistic fallback.
3. Reject any method lacking independent numerical validation
   for the relevant d,S,mu,scale and tolerance; a SVD-proxy fit
   agreement is provisional only.
4. If both are validated, use a 20% hysteresis band around the
   predicted equal-time frontier; otherwise abstain from choosing.
5. Validate actual run-to-run paired timings at the boundary,
   and prefer an explicit user-selected backend where certification
   is missing. Do NOT modify the library default based on this
   sparse experiment.

## Further tests

Measure and certify both methods at n=512 and 1024, d1..6,
M1/7/100/1000 with R1/3, multiple independent seeds, and
all five complete-criterion pipelines. Explicitly time shared
S-grid mapping and factor reuse so n^3 mapping preparation can
be excluded/reincluded without double counting.

Preserve all raw time rows, nonconvergence and numerical failures,
source SHA, plots, NNLS fit coefficients and empirical classification
masks. Never turn unavailable values into extrapolated measurements.
