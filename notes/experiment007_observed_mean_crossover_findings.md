# Experiment007 — Measured mu='data' fit-only switching results

**Measured 2026-11-02 on PCAG103A-08; no package installation.**

Validated confirmation:
https://github.com/heri-espino/trendestimation/actions/runs/41510943429
Raw results, environment, 85-digit subset, and generated analysis:
https://github.com/heri-espino/trendestimation/tree/results/experiment007-selfhosted-41510943429

**Actual run dimensions:**
n={64,128,256}, d={1,2,3,4,5,6},
mu_policy={data,zero}, scale={low,high}, S={.2,.5,.75,.9,.95,.99,1},
12 paired independent seeds and 3 cold-repetition timings per seed,
four fit workloads (M=1/7 and R=1/3), four solver families
(spectral SVD, primal banded Cholesky, sparse SuperLU, FFT PCG).

The fit receives mu="data" for the primary experiment. It is
estimated separately for EACH observed series as mean(D_d y).
The known latent mu_true from the data generator is archived
only as a QA diagnostic, never used for fitting. The mu=0 policy
remains a controlled comparison.

13,824 workload timing records; 72,576 numerical checks;
11,372/13,824 complete workload timing records pass EVERY
relevant fit QA check. Only 3,072 of the individual QA checks
use an independent 85-digit reference (n<=128,d>=5,S>=.9,
first of three series); the rest are SVD-proxy comparisons.
No full MxR workload has all its candidate fits independently
85-digit-certified. Method rankings below remain **descriptive**.

## Results: observed-data mean, full seven-S grid, three series

Each entry is the fastest method after excluding any method with
a missing or numerically invalid candidate fit. Low/high denote
observation magnitude, not mu=0 versus mu=data.

| n | d | Low amplitude | High amplitude |
|--:|--:|---|---|
| 64 | 1 | Cholesky | Cholesky |
| 64 | 2 | Cholesky | Cholesky |
| 64 | 3 | Cholesky | Cholesky |
| 64 | 4 | SVD | SVD |
| 64 | 5 | SVD | SVD |
| 64 | 6 | SVD | SVD |
| 128 | 1 | Cholesky | Cholesky |
| 128 | 2 | Cholesky | Cholesky |
| 128 | 3 | Cholesky | Sparse LU |
| 128 | 4 | Sparse LU | SVD |
| 128 | 5 | SVD | SVD |
| 128 | 6 | SVD | SVD |
| 256 | 1 | Cholesky | Cholesky |
| 256 | 2 | Cholesky | Cholesky |
| 256 | 3 | Sparse LU | Sparse LU |
| 256 | 4 | FFT PCG | FFT PCG |
| 256 | 5 | SVD | SVD |
| 256 | 6 | SVD | SVD |

For this one workload, the provisional timing ratio T_SVD/T_winner
at n=256,d=1 is 7.50 (low scale) or 7.43 (high);
at d=2, 6.35/6.41; at d=3, 4.13/4.06;
at d=4 only 1.052/1.016. The d=4 advantage of PCG
is too small to support an automatic switch from this
one-session study.

## Observed-data-mean numerical consistency

Across BOTH data magnitudes, 12 seeds, three independent series
and seven S levels (504 sampled fit checks per n,d,method):

| n | d | SVD | Banded Cholesky | Sparse LU | FFT PCG |
|--:|--:|--:|--:|--:|--:|
| 64 | 4 | 504/504 | 468/504 | 504/504 | 504/504 |
| 64 | 5 | 504/504 | 334/504 | 464/504 | 504/504 |
| 64 | 6 | 504/504 | 270/504 | 432/504 | 456/504 |
| 128 | 4 | 504/504 | 388/504 | 471/504 | 504/504 |
| 128 | 5 | 504/504 | 287/504 | 432/504 | 503/504 |
| 128 | 6 | 504/504 | 253/504 | 397/504 | 432/504 |
| 256 | 4 | 504/504 | 335/504 | 434/504 | 504/504 |
| 256 | 5 | 504/504 | 256/504 | 428/504 | 432/504 |
| 256 | 6 | 504/504 | 185/504 | 370/504 | 428/504 |

These are per-fit *agreement/rejection* counts, not independent
Bernoulli probabilities: the seven S values share y and d, and
many cases use SVD as the comparator. For n<=128 high d/high S,
the independent Decimal reference offers stronger, but still
restricted, evidence. No numerical-accuracy conclusion for
n=131072 or unsampled S values is warranted.

## Do we choose a new switching threshold?

**No permanent policy yet.** A rule based on d alone is already
contradicted by the workload- and n-dependent timing crossover.
The previously implemented guarded_svd_cholesky fallback should
remain labeled a historical numerical safeguard for a restricted
n,d,S range, NOT a production automatic fastest-method selector.

The measured n=256,d=4 PCG advantage is 1.6-5.2% while competing
direct methods have accuracy failures in some S cells; it
would be unjustified to hard-code that as a universal improvement.
The n=128,d=3 winner changes between low and high magnitude
under mu="data", and it changes again for the mu=0 control.

The next algorithm selection problem is constrained optimization:

  minimize expected end-to-end time
  over numerically COMPLETE, error-bounded, memory-feasible methods,
  conditional on (n,d,S-grid,M,R,mu_policy,signal scale).

For high d at very large n, full dense SVD becomes infeasible,
and the present study does not yet provide a stable universal
structure-exploiting replacement. More data from 512 through 131072
and **full criterion** selection pipelines are essential.

## Important distinct theoretical point

The plugin mean mu_data=mean(D*y) is unbiased for
mu_true=mean(D*tau_true) under zero-mean noise, but is NOT equal
to that unknown mean in a finite sample. For i.i.d. errors,
and n>=2d, its noise variance is

    2*sigma^2*binom(2d-2,d-1)/(n-d)^2.

The multiplier is 2 at d=1 and 504 at d=6, so high d
amplifies endpoint-noise variance. See
notes/experiment007_theory_of_data_mu.md for a full derivation.
A jointly optimized mean mu=mean(D*tau_hat) is a different
penalized problem and has different nullity/smoothness EDF.

**Paper scope:** This is FIT-ONLY timing, NOT the computational
cost of complete CV/GCV/BIC/AICc/MLE selection. Those criteria
require explicitly modeling the data-dependent mean and
its leverage/EDF effects, plus all trace/mapping costs.

Future experiments must store matched raw time and QA records,
seed, numerical oracle type, code revision and reproducible
machine environment. This report cites immutable, actual
measurement files and does not interpolate unrun sizes.
