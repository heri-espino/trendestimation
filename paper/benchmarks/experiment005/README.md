# Experiment005 — Structured and iterative PLS solvers

## Research question

Can sparse direct factorizations, general banded LU, and preconditioned
conjugate gradient outperform existing banded Cholesky when fitting one or
many smoothness-indexed PLS trends? Under which n, difference order d,
reference mean mu, penalty lambda, and reuse count?

This experiment complements the 80,640-row archived selection benchmark.
It does **not** imply that faster fits automatically yield faster CV/GCV/AICc/
BIC/MLE selection. Those criteria require additional EDF and, for exact CV,
leverage computations. The S-to-lambda conversion is unchanged and remains
spectral. Tests use the already-established mathematically equivalent
linear system; the full SVD fit-only default is preserved.

## Methods

- cholesky: existing symmetric banded Cholesky, SciPy LAPACK.
- banded_lu: new general banded LU using solve_banded.
- sparse_lu: new SciPy SuperLU via splu, with optional factor caching.
- sparse_lu_cached: sparse LU with saved factor for repeat identical lambdas.
- sparse_cholesky: genuine CHOLMOD via optional scikit-sparse; no silent LU.
- pcg_fft: matrix-free CG with circulant Fourier spectral preconditioner.
- pcg_dst: matrix-free CG with a Dirichlet sine spectral preconditioner.
- pcg_jacobi: matrix-free CG with diagonal preconditioner.

The finite-difference operator D is sparse. The exact normal equation is
(I + lambda D.T D) tau = y + lambda mu D.T 1.
This is different from removing a high-order polynomial reference from y,
which may introduce catastrophic cancellation.

For fixed d, banded Cholesky is O(nd^2) to factorize and O(nd) per solve.
General sparse LU is not always O(n), because its fill and ordering depend
on geometry. PCG costs O(k nd) for k iterations and matrix-vector products,
plus O(n log n) for each FFT preconditioner application, or O(n log n)
for each DST. FFT/DST circulant/Dirichlet symbols are not exact natural
boundary eigenvectors and need not converge in a small constant k.

## Run and preserve actual results

From the repository root:

    conda activate trendestimation
    python -m pip install -e ".[dev]"
    python -m pytest -q tests/test_experiment005_structured_solvers.py
    python paper/benchmarks/experiment005/run.py --preset smoke
    python paper/benchmarks/experiment005/run.py --preset quick --repeats 5
    python paper/benchmarks/experiment005/run.py --preset large --repeats 7

For real sparse Cholesky, install SuiteSparse and scikit-sparse separately.
On machines without it, the CHOLMOD rows record ImportError, never a fake
result from sparse LU. Banded/PCG/other methods still run.

Result files (under runs/local-<preset>/):
- raw_measurements.csv: every attempt, including every failed convergence.
- summary.csv: per-workload medians only if every repetition passes.
- environment.json: OS, Python, NumPy, SciPy, BLAS threadpool and script hash.
- RESULTS.md: what ran, what passed and what remains.

Commit and push genuine results to the same experiment branch, or to a
separate results-only branch if multiple agents are working concurrently.
Do not overwrite runs created on another PC. Specify --output for unique
run directories. Do not commit proprietary input datasets or secrets.

The project has not recorded timing results for these new implementations
until this experiment actually runs on the designated host. CI tests parity
and small-scale operations, not large benchmark speed.

## Initial hosted smoke accounting correction

The first automatically archived `runs/hosted-smoke/` used a median of
three repeated solves, mixing the initial sparse factorization with
subsequent cache hits. Its raw data and original summary remain preserved
for audit but its one-number cached-sparse median is **not** a fair
cold-start comparison. The corrected `runs/hosted-smoke-v2/` separates
first-cold-fit time, warm-cache-hit median, total repeated solves and
setup-plus-total time. Only the second format should support any
cold-versus-warm statement. These are tiny n=36 hosted smoke timings,
not a benchmark of the author's Windows machine or of d=6.
