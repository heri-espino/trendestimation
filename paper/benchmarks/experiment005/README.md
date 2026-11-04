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

## High-order reference validity

The original banded-Cholesky reference uses a degree-d polynomial shift,
which can lose precision for high orders and large n. Experiment005 now
computes the reference normal-equation residual before comparing any new
method. If that residual exceeds the declared threshold, all corresponding
comparisons are flagged `reference_unreliable` and excluded from
performance rankings. CHOLMOD's independent small-n verification uses a
separate dense solve and a backward-residual check, not the banded result
alone. A sufficiently accurate high-order reference is still required
before making claims about the large-n solver frontier.

Each subsequent CI smoke uses a unique GitHub Actions run-id directory;
original smoke, v2 and v3 archives remain intact.

## Separate historical joint accuracy/runtime study

# Experiment005 — Joint numerical accuracy and measured computational cost

## Objective

Combine the *two already completed CSDA companions* in **one matched run**.
Numerical error, historical latent-trend recovery RMSE, selected normalized
smoothness and measured elapsed time are collected on **the same inputs,
penalty grid, algorithm, mean policy, and machine**. Do not paste together
errors from Experiment004 and timings from the earlier Windows factorial.

**This is a new experiment, not a rerun of either manuscript.** The
numerical-validity pilot is a prerequisite to a much larger timing factorial.

## Mathematical model and interpretation

For each n and d>=1, the estimator solves
\`min_tau ||y-tau||^2+lambda||D_d tau-mu*1||^2\`.
The trace-defined normalized coordinate
\`S=(n-tr((I+lambda*D.T@D)^-1))/(n-d)\` is in [0,1].
All compared methods receive **the same 17 S targets and exactly the same
mapped lambda values**; lambda is merely an internal solver parameter.

Main backends: full SVD with shift-free fitting, symmetric Gram
eigendecomposition, and banded Cholesky. The end-to-end criterion scorer
uses the backend's own score computation, not a silent substitution
from the SVD selector. Criteria: conditional CV, GCV, AICc, profiled
Gaussian variance-component marginal ML, and residual BIC *restricted
to S>=0.10*, explicitly as a sensitivity analysis. BIC restriction
is not claimed to repair the interpolation-boundary pathology.

Mean policies: fixed 0 and \`mean(D_d@y)\`. The latter is an empirical
**conditional plug-in**, not the same model as fixed nonzero mu,
not adaptively recomputed LOOCV and not jointly estimated MLE.

Known latent trends and iid/AR1 noise use the exact seed convention from
Experiment004. Here RMSE is recovery of the latent *historical trend*, not
future-forecast error.

## Reference and timing methodology

- **Independent reference**: the 85-digit dual banded solve from
  Experiment004 with float64 y, lambda and mu frozen. Assert KKT residual
  <=1e-18. The S=0 and S=1 endpoints use exact analytical limit fits,
  marked separately; they are **not 85-digit interior reference cases**.
- **Fit timing**: each public PreparedPLSSolver.fit call is repeated and
  its median elapsed time recorded, then compare its *returned fit*
  against the independent reference and the known latent truth.
- **Selection timing**: each individual backend actually evaluates the
  eligible candidates of the same S grid. Endpoint criterion scores
  are provided analytically, not timed as fake infinite-lambda solves.
  Score correctness is checked **outside** timed sections against the
  current public spectral API. Only a complete valid grid and a
  reference-accurate selected fit may count toward timing winners.
- **Setup**: distinct recorded measurements for creating TrendSmoother,
  converting the complete grid, preparing the fit backend, and
  preparing a criterion backend. Full cold costs are *assembled sums of
  these measured stages*, not a separate stopwatch reading. Warm
  selection excludes shared setup. Never treat the 85-digit reference
  or post-hoc validity work as part of the library's runtime.
- All timings are machine-specific wall times, with controlled BLAS
  threads and per-case repeated blocks. Seeds, **not individual timing
  repeats**, are the independent Monte Carlo sampling units.

## Presets

| preset | n | d | truth / noise | seeds |
|---|---|---|---|---|
| smoke | 24 | 3 | smooth / iid | 0 |
| pilot | 32,64 | 2,3,5,6 | smooth,kink / iid,AR1 | 0 |
| full (manual only) | 64,128 | 1,2,3,4,5,6 | smooth,kink / iid,AR1 | 0,1,2 |

Each preset includes both mean policies, all five criteria, all three
backends and the 17-point S grid. In pilot the multiple data-generating
conditions are **not** multiple independent seeds; full is necessary
for meaningful seed-level sampling uncertainty.

Run from root after source installation:

\`\`\`powershell
conda activate trendestimation
python -m pip install -e . mpmath threadpoolctl
python paper/benchmarks/experiment005/run_joint.py --preset smoke --repeats 3 --out paper/benchmarks/experiment005/runs/smoke-local001
python paper/benchmarks/experiment005/run_joint.py --preset pilot --repeats 5 --out paper/benchmarks/experiment005/runs/pilot-local001
\`\`\`

The dedicated GitHub-hosted workflow executes **smoke then pilot only**;
it deliberately does not use the user's PCAG103A-08 runner. Do not run
the full preset without review of the pilot's failures and budget.
Every run directory is immutable (refuses overwrites), and results are
committed to this experiment branch with environment metadata and SHA256.
Do not merge the experiment with the manuscript before reviewing its
validation report.

## Outputs

- \`fit_accuracy_runtime.csv\`: one row per matched fitting call;
  elapsed fit milliseconds, 85-digit relative error, max absolute error,
  trend RMSE, status and failure reason.
- \`selection_accuracy_runtime.csv\`: each actual full-grid criterion
  search, exact selected S and lambda, criterion score accuracy,
  selected-fit error, latent-trend RMSE, and timed stages; invalid
  partial grids have an explicit status and cannot be winning methods.
- \`reference_checks.csv\`: precision and KKT audit for the same
  candidate and data realization.
- \`setup_and_mapping.csv\`: spectral setup, smoothness-grid mapping,
  backend preparation times and statuses.
- \`summary.json\`: environment, counts, design, hash provenance,
  caveats and run completion record.

## Scientific decision gates for the final CSDA manuscript

1. Confirm all source hashes and the finite S mapping against the
   package; verify reference KKT and multiprecision convergence for
   difficult d=5,6 high-S cases.
2. Present validity/inaccuracy/failed counts across **every matched
   candidate**, not just survivors.
3. Distinguish criterion-selection errors and fitted-trend error;
   never report fit-only timing as full CV/ML selection time.
4. Estimate time--RMSE Pareto fronts only on **complete, paired,
   numerically admissible** sets, with seed-block uncertainty once
   a sufficiently large independent-seed run is collected.
5. Preserve specialized structured CV/GCV prior-art competitors as a
   fairness requirement before making universal speed claims.
6. Only then integrate numerical and computing results into the
   final combined Elsevier CSDA manuscript.

No historical Experiment004 or Windows measurement files are modified.

## Separate historical paired precision/runtime study

# Experiment005 — Paired numerical accuracy and computational cost

## Objective

This is the missing paired study linking the two separate CSDA drafts:
numerical fidelity versus the same-parameter multiprecision trend and
statistical recovery RMSE, together with setup, selection and fitting
times on the SAME observations and machine.

**A — Frozen-S fit comparison.** The nine methods from Experiment004
are independently timed (setup and per-fit median/MAD) for the SAME
finite positive lambda corresponding to a common target S. The
85-decimal-digit *independent banded-dual* reference is solved
OUTSIDE the timing window, using the frozen float64 observation,
lambda and mu. Measure numerical relative L2, max absolute error,
and true in-sample latent-trend RMSE. Invalid methods cannot win.

**B — End-to-end full S-grid selection.** CV, GCV, AICc, restricted
residual BIC and profiled Gaussian marginal ML are timed with three
criterion backends: full SVD, eigendecomposition and banded Cholesky.
For each series, the two search policies evaluate the EXACT SAME
complete normalized S grid with analytical endpoints:
(i) repeatedly invert S during scoring, or (ii) invert once and
reuse mapped penalties. Selected fitted trends are evaluated against
known simulation truth and a frozen-parameter high-precision reference.
All candidate criterion values are verified against the SVD-library
double-precision score outside timing.

There is NO independently sampled log-lambda grid in this experiment:
lambda is a numerical implementation detail, not the user-facing axis.

### Important interpretation

- Numerical error: relative L2 to a SAME-lambda independent MP trend.
- Statistical error: RMSE to true simulated latent trend, not a forecast.
- Criterion validity: every candidate matches the SVD double-precision
  library to relative tolerance 1e-5; this is not a high-precision proof
  of the criterion itself.
- Exact endpoints are independently certified: S=0 has reference
  tau=y, and S=1 uses multiprecision constrained polynomial QR
  with both moment optimality and D_d tau=mu constraints checked.
  These exact endpoint references are computed OUTSIDE timing.
- BIC uses S>=0.10 as a sensitivity restriction, not a repaired model.
- Observed-difference mean = mean(D_d y) is a conditional empirical
  plug-in, not joint Gaussian MLE of mu.
- Direct methods that fail at near-one smoothness are reported as invalid,
  not silently replaced by a spectral fit.
- Reference solves are NEVER charged to any implementation's runtime.
- Phase-summed cold total is labeled as accounting, NOT an independently
  timed continuous span. Setup structures for the score and fitted curve
  can be separate and both are charged.

### Presets and scale

| Preset | n | d | shapes/noise | Independent seeds | Full S grid |
| --- | --- | --- | --- | --- | --- |
| smoke | 24 | 3,6 | smooth, iid | 1 | 17 nodes |
| quick | 32,64 | 1,3,5,6 | smooth/kink, iid/AR1 | 2 | 110 nodes |
| full | 48,96,128 | 1,2,3,4,5,6 | smooth/kink, iid/AR1 | 10 | 110 nodes |

Both fixed mu=0 and observed-difference plug-in are included throughout.
The nine fit methods are the original Experiment004 METHODS and are
independently timed, not timed as a group. Selection has three distinct
methods and two equivalent coordinate policies. The full preset may be
expensive; validate smoke and quick before running full.

### Windows PowerShell from repository root

~~~powershell
conda activate trendestimation
python -m pip install -e ".[dev,plot]"
python -m pip install mpmath threadpoolctl
python -m pytest -q tests/test_experiment005_paired.py

python paper\benchmarks\experiment005\paired_run.py --preset smoke --repeats 3 --digits 85 --out paper\benchmarks\experiment005\runs\pilot-windows-01
python paper\benchmarks\experiment005\paired_run.py --preset quick --repeats 7 --digits 85 --out paper\benchmarks\experiment005\runs\quick-windows-01

git add -f paper/benchmarks/experiment005/runs/pilot-windows-01/
git add -f paper/benchmarks/experiment005/runs/quick-windows-01/
git commit -m "experiment005: archive paired numerical accuracy and runtime"
git push
~~~

Output directories MUST be unique; the runner refuses to overwrite.
Large results, configs, raw CSVs, hashes, and machine metadata belong
in the repository (or documented LFS/external storage if too large).
Results from Linux CI and Windows cannot be pooled as host-independent times.

### Outputs

- fit_accuracy_timing.csv: paired nine-method numerical and statistical
  fit errors, per-method setup, fit median/MAD, failure status.
- selection_accuracy_timing.csv: complete-S-grid criterion scores,
  per-backend numerical failures, selected S, score discrepancy, selection
  and fitted-trend runtime, RMSE/oracle gap, MP verification.
- grid_mapping_times.csv: one-time SVD and inverse-grid preparation.
- summary.json: preset, software/host/BLAS, numerical status counts,
  reproducibility parameters and SHA256 of source CSVs.

### Next scientific gate

After smoke/quick, compute **eligible-only** accuracy–runtime Pareto
frontiers and paired bootstrap confidence intervals across independent
replicates, separately by workload, n, d, noise and mu policy. Do not
interpret 110 grid nodes as 109 independent replicates. Report numerical
failure frequency as a third axis. Only after these results are audited
should the two CSDA manuscripts be combined.

### First paired evidence

See RESULTS_PILOT.md and the archived quick-hosted-40967124055 run.
The script analyze.py writes eligible-only Pareto summaries and
AwesomeFigures vector PDF/SVG plots from the saved CSVs. Its plots
compare only identical n,d,trend shape,noise and mu conditions.
