# Experiment009 — Theoretical crossover surface for SVD and banded Cholesky

## Objective and notation

Study numerical timing, NOT statistical RMSE, using series length n,
difference order d=1,...,6, M smoothing candidates, R independent series,
and criterion C. Compare dense SVD of D_d and banded Cholesky of
A_lambda=I+lambda D_d.T D_d. The S coordinate is invariant to the observed
data and the chosen fixed or plug-in mean; the right-hand side is not.

## Theory for complete selection criteria

After separating any common S-to-lambda translation cost, a model is

    T_SVD = a*n^3 + b*R*n^2 + c_C*M*R*n^(q_C),

where q_C=1 for global scalar spectral criteria (under sufficient cached
projections), and q_C=2 for ordinary CV leverage computations.
For banded Cholesky with shared factors/selected inverse across series:

    T_Chol = u*M*n*d^2 + v*M*R*n*d + O(n*d).

Define Delta=T_SVD-T_Chol. If

    L = u*n*d^2 + v*R*n*d - c_C*R*n^(q_C) > 0,

the theoretical crossover in number of candidate values is

    M_star = (a*n^3+b*R*n^2)/L.

SVD wins the simplified time comparison for M>M_star, and banded
Cholesky wins for M<M_star. If L<=0, SVD cannot amortize the
preparation cost by increasing M in this model.

For fixed M,R,d and growing n, banded asymptotically beats dense
SVD. Ignoring secondary terms gives n_star proportional to
d*sqrt(M*u/a). But Big-O alone CANNOT determine u/a, so a
numerical switching surface requires implementation/hardware
calibration. The pure theoretical family is indexed by M,R,C.

All recommendations must pass independent numerical-error
and memory-feasibility checks. The implementation dense-SVD
budget is approximately 40*n^2 bytes plus O(n^3) work.

## Separate model for full fitted trends

Experiment007 reconstructs the entire fitted series for each
penalty. Dense SVD then costs O(n^2) PER fit, not O(n) as for
a scalar GCV score:

    T_SVD_fit = a_f*n^3 + b_f*R*n^2 + c_f*M*R*n^2.

The historical Experiment007 banded fitting did not cache
factors across different independent series:

    T_Chol_fit = O(M*R*n*d^2) + O(M*R*n*d).

Thus it is invalid to calibrate the complete-criterion shared-factor
model on Experiment007 fit-only observations.

## Mapping, exact S=1 and actual benchmark caveat

Cached S-to-lambda mapping may be shared by both methods.
If mapping differs, its actual costs must be added to each solver.
Experiment008 at n<=512 uses a common SVD mapper; its cost is
included in BOTH reported cold solver times. This is a pipeline
comparison, not a pure factorization comparison. The AICc
calibration therefore includes an n^3 feature in the Cholesky
cost to account for shared spectral preparation.

At S=1, lambda=+infinity is treated analytically as a constrained
limit, not as one more finite-penalty Cholesky factorization.

## Observational inputs, reproducibility and holdout protocol

The code in crossover.py fits NONNEGATIVE coefficients of
the theoretically derived computational terms using SciPy NNLS.

FIT-only input: Experiment007 12-seed Windows timing summaries,
n=64/128/256, d=1..6, M=1/7, R=1/3, mu=data/zero,
two amplitudes. Train on n=64,128 and hold out n=256.
Numerical fit parity is not an independent high-precision proof.

Complete-criterion AICc input: Experiment008 Windows mapped-lambda
results, n=64/128/256/512, d=1..6, M=1/100, R=1/2,
conditional mu=data, high amplitude. Train on n<=256 and
hold out n=512. Only a fully valid SVD/Cholesky pair can
contribute to empirical switching agreement.

Primary original data branches:
- results/experiment007-selfhosted-41510943429
- results/experiment008-41529113497-broad

Every paired source observation is frozen with a source GitHub
path under data/. The fit-only and full-AICc results are NOT pooled.
The constants for CV, GCV, BIC and MLE are NOT inferred from AICc
without criterion-specific calibration.

Execute from repo root:

    python paper/benchmarks/experiment009/crossover.py --output paper/benchmarks/experiment009/runs/unique-id

The hosted workflow produces calibration.json, source-linked
paired measurement comparisons, the M,R,n,d indexed theoretical
surfaces and PDF/SVG/PNG heatmaps. Generated results are committed
to a separate immutable run-ID branch.

## Candidate policy, not yet a production default

For a given (n,d,M,R,C,mu,S-grid), first reject unavailable memory,
unvalidated numerics and convergence failures. Among verified
candidates, prefer SVD if its calibrated expected time is
below 0.8 times Cholesky's; prefer Cholesky for the reverse.
Otherwise regard the region as ambiguous and collect more
paired timings. A 20% margin is a practical proposed threshold,
NOT a derived confidence bound.

No policy at n=16384/131072 can be certified by extrapolation from
training data at n<=256/512. A large-n high-order structured
method with certified forward accuracy remains an open problem.

A fitted empirical exponent is not a proof of algorithmic Big-O.
Retain raw timings, rejected cells, 85-digit-reference caveats,
source code, figures and handoff for independent researchers.
