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


## Experiment006: complete-criterion computational factorial — current research PR #95

The next sequential experiment lives under paper/benchmarks/experiment006/.
Draft branch: research/experiment006-full-computational-factorial; do not
merge while it is under numerical review. Existing Experiments001–005,
manuscripts, notebooks and results remain unchanged.

Core new mathematical algorithm: selected_inverse.py implements exact
banded-Cholesky Takahashi-style selected inversion O(n d^2), giving trace,
conditional EDF, exact fixed-mu LOOCV leverage and S(lambda) inversion
without dense eigendecomposition for d=1,...,6. Independent parity tests
validate across dense inverse and the public spectral scores.

run.py is the first integrated **three-method** full-criterion benchmark:
actual naive dense inverse, full SVD, and banded Cholesky plus selected
inverse. It times one/grid S x one/multiple independent series, and
direct-S versus S-to-lambda pretranslation. Seven n values up to 131072,
fixed mu=0/0.15, two observation amplitude scales and five criteria
are represented. The full n*d*mu*scale*grid*method*criterion tensor is
a *planned* factorial; only small test observations have been performed
by CI, not publication-scale Windows runs. plan.py records explicit
skips and missing complete-criterion implementations for the other
Experiment005 sparse/PCG fit-only methods.

The experiment must NEVER report that PCG fitting time is equivalent
to complete GCV/CV/MLE time. S=1 is lambda infinity (analytical
constrained limit); mu=data is conditional MLE only; RSS-BIC is
degenerate at S->0. Large nonzero-mu high-d polynomials need much
stronger numerical validation. Naive dense inverse is infeasible
for n=131072 (one 128-GiB float64 matrix).

Refer to paper/benchmarks/experiment006/README.md for PowerShell
worktree, factor levels, CLI and source retention. The user prefers
their workstation for heavy experiments and will commit/push raw
measurements on a separate branch. Do not automatically schedule
the full factorial on GitHub runners.

The next tasks are complete sparse/PCG statistical-criterion pathways,
a compiled selected-inverse kernel and adaptive high-precision S-grid
mapping, statistically fair paired CPU timings and analysis of
measured scaling versus theory. This is a draft research PR, not a
claim of final computational superiority.
