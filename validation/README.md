# Independent numerical verification

This is **in-sample** finite-difference penalized least squares, not forecast-optimal smoothing.

For D = D_d, the order-d forward-difference operator, 0 <= d < n, and fixed mu,
the minimizer solves (I + lambda D.T D) tau = y + lambda mu D.T 1.
At lambda = 0, tau = y. At exact lambda = infinity, tau is the nearest
point to y on the affine constraint D tau = mu 1.

An independent endpoint oracle constructs a particular solution p of
D p = mu 1 and an orthonormal basis N for ker(D). It then computes
p + N N.T (y-p), distinct from the package's spectral smoothing routine.
The rank of D is n-d, so the nullity and limiting conditional EDF equal d.

## Numerical oracles

* Difference stencils: repeated differences of the identity matrix.
* Finite lambda: directly accumulate combinatorial D.T D entries into
  general-band storage; solve the banded normal equations with SciPy.
* Infinite lambda: constrained Euclidean projection via least-squares
  particular solution and orthonormal null-space basis.
* EDF: independent trace of dense linear solves for small examples.
* CV: explicit leave-one-out refits, with one fidelity weight removed.
  The original difference penalty remains on the full grid. This is
  ordinary in-sample CV with fixed numeric mu, not rolling or future CV.

## Invariants and limitations

Test analytic order-zero shrinkage, polynomial nullspace preservation,
KKT residuals, endpoint constraints and limits, monotone nonincreasing
penalty residuals and nondecreasing data residuals with lambda,
EDF bounds and monotonicity, varying n/d/mu, and finite numerical
agreement across two independent solver families.

Tolerances are problem-dependent (roughly 1e-12 to 1e-6), not claims of
uniform accuracy for arbitrarily large n, d, or lambda. High-order
difference operators can become very ill-conditioned. Numerical
disagreements should be interpreted with conditioning and backward
error, not automatically as errors in one implementation.

## Test locally

    python -m pip install -e '.[dev]'
    python -m pytest -q tests/test_numerical_validation.py

## Manual benchmark

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python benchmarks/profile_solver_costs.py --n 32 64 128 --order 2 --evaluations 20 --repetitions 3 --output results/numerical-costs.json

No automatic benchmark or result-writing workflow is installed.
Without --output only stdout JSON is produced.

Benchmark fields distinguish one-time SVD setup, one-time banded
assembly, equivalent full-trend fit sweeps, spectral EDF trace
evaluation, and GCV grid selection with projection reuse. EDF/GCV
times are **not** equivalent workloads to full reconstructed trends.
Explicit array-storage byte counts are **not** peak process RSS nor
temporary LAPACK/BLAS memory. Timings are machine-specific and
do not establish unconditional solver superiority.

Related methods: Guerrero (2007); Cortés-Toto, Guerrero & Reyes (2017);
Weinert (2007), Efficient computation for Whittaker-Henderson smoothing.
No third-party journal PDFs are committed.
