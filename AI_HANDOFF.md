# AI_HANDOFF — latest

## Experiment005: sparse/iterative PLS, current branch

Branch: feature/experiment005-structured-solvers; PR #94.

Existing SVD/eigh/banded-Cholesky preserved; added banded_lu, sparse_lu
(SuperLU), optional sparse_cholesky (real CHOLMOD), and matrix-free PCG
with fft/dst/jacobi/none preconditioners. The new methods are fit-only.
Matrix A and RHS are built without a high-degree polynomial subtraction.

Review src/trendestimation/_structured_solvers.py, the integration in
src/trendestimation/solvers.py, tests/test_experiment005_structured_solvers.py
and paper/benchmarks/experiment005/run.py. Numerical correctness/parity,
normal-equation residuals, finite lambda, zero & infinity limits,
fixed/plug-in mu, convergence failures and factor-cache reuse are tested.

Do NOT claim fastest sparse Cholesky without separately installing and
timing optional SuiteSparse CHOLMOD. FFT/DST are approximate surrogate
preconditioners; convergence depends on conditioning and boundaries.

The next research step is to run the larger experiment005 preset on the
author's Windows workstation and publish the evidence to the repository,
then compare fit-only performance and full criterion selection separately.

Previous experimental timing data and the two CSDA manuscripts remain
unchanged. Maintain their provenance and do not alter recorded values.
