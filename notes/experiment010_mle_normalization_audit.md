# Experiment010 — MLE score-normalization audit (2026-11-03)

## Why the first pilot cannot be used to rank all MLE solvers

The original Windows run #41586066141 produced 720 timing rows in its
bounded pilot. Among 900 score-parity audit rows, 616 passed the
selected-score comparison (not high-precision validation), 180 were
failed/partial, and **104 disagreed with the spectral criterion**.

Breakdown of the 104 disagreements from the archived pilot:
- 100 involve n=64,d=5, mu="data", amplitude high, MLE.
- 4 involve n=64,d=6, mu=0.15, amplitude high, CV (naive inverse).
Thus 100 of 104 are associated with an identifiable MLE criterion
normalization inconsistency, though residual numerical differences
may remain after fixing the normalization. The d=6 CV cases require
independent numerical inspection, not a speed ranking.

Archived raw records:
https://github.com/heri-espino/trendestimation/tree/results/experiment010-41586066141-a1-pilot/paper/benchmarks/experiment010/runs/windows-41586066141-a1-pilot

## Exact analytical discrepancy: an omitted constant

Let r=n-d and D=D_d, with positive eigenvalues delta_j of D.T D.
For a fixed numeric mu (or the conditional plug-in mu="data"), write
z_j for positive-penalty coordinates of the centered series. The
spectral profile MLE criterion is

    L_spectral(lambda) =
        r log[ (1/r) sum_j z_j^2 * lambda*delta_j/(1+lambda*delta_j) ]
        + sum_j log[ 1 + 1/(lambda*delta_j) ].

The banded implementation uses a dual quadratic form
W=e.T [D D.T+I/lambda]^{-1} e, e=D y-mu 1, which equals the spectral
weighted quadratic in exact arithmetic. It also calculates

    L_banded_old(lambda) =
        r log(W/r) + logdet(I+lambda D.T D) - r log(lambda).

But

    logdet(I+lambda D.T D)-r log(lambda)
      = sum_j log(1+1/(lambda*delta_j))
        + logdet(D D.T).

Consequently

    L_banded_old(lambda)-L_spectral(lambda)
       = logdet(D D.T)

for each FINITE positive lambda, assuming identical results apart from
floating-point error. The naive dense-inverse MLE benchmark likewise
omitted that constant. High-order n=64,d=5 has

    logdet(D_5 D_5.T) ~= 66.32448169.

The observed paired pilot MLE difference was approximately 66.3 at
the selected finite S, consistent with this derivation; further
residual disagreement may reflect high-order conditioning.

**Why the constant must be restored:** The benchmark includes S=1
with EXACT lambda=+infinity. Its limit was evaluated using the correct
spectral/profile normalization. Omitting a constant only for FINITE
lambda while keeping the endpoint on a different scale can change the
selected S and invalidate empirical solver-selection comparisons.
This is more serious than a harmless overall additive log-likelihood
constant. All candidate scores must use a common normalization.

## Stable difference-Gram log determinant without dense matrices

For forward differences of order d over n consecutive equally spaced
observations, we use the exact determinant product identity

    det(D_d D_d.T) =
       product_{j=0}^{d-1}
       [binom(n+j,2*j+1)/binom(2*j,j)].

Its stable log form uses scipy.special.gammaln and only O(d)
arithmetic/storage:

    sum_{j=0}^{d-1} [
        gammaln(n+j+1)-gammaln(n-j)
        -gammaln(2*j+2)-gammaln(2*j+1)
        +2*gammaln(j+1)].

No dense eigendecomposition or near-singular banded Cholesky of
D D.T is needed at n=131072. This identity must be independently
verified against dense slogdet for small n,d, and reported as an
analytical normalization rather than an empirical fit parameter.
The new regression tests compare all mean policies and finite
versus exact-infinite S.

## Corrections and next verification

On PR #100, ONLY the experimental MLE benchmark implementations
were changed: banded fit_stats, hybrid score_external, and naive
dense-inverse MLE. The production spectral likelihood in
src/trendestimation/likelihood.py is not changed.

The original Windows results remain immutable, flagged
"pre-normalization: do not use for cross-backend MLE selection".
A NEW source SHA/re-run must generate corrected, separately archived
timings and parity audits. Even after the normalization correction,
high d, extreme S and amplitude effects require independent
high-precision trend-forward validation before declaring an
algorithm numerically eligible. Confirm the exact S=1 boundary,
and evaluate the small remaining CV disagreements separately.


## Empirical post-correction verification

Post-fix commit 532f0aab8abe3af8a4b47acce9a72e08c7895ea7 passed
GitHub-hosted Python 3.10 and 3.12 tests, documentation, validation,
and both Windows 11 experiment jobs
https://github.com/heri-espino/trendestimation/actions/runs/41587467639.
The corrected pilot again saved 720 actual status=ok timing rows.
Score disagreements fell from 104 to **16** under the SAME
seed/workload design. All 16 remaining disagreements are from
naive inversion (12 d5 MLE; 4 d6 CV), not banded/hybrid MLE.
The corrected numerical parity result supports the analytical
normalization diagnosis but does not certify forward accuracy
of every high-order fitted trend. Do not interpret the original
d5 MLE discrepancies as evidence that the banded methods
were numerically incorrect: the old scores used distinct
criterion additive constants. Preserve both source versions.
