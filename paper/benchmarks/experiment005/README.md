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
| quick | 32,64 | 1,3,5,6 | smooth/kink, iid/AR1 | 2 | 109 nodes |
| full | 48,96,128 | 1,2,3,4,5,6 | smooth/kink, iid/AR1 | 10 | 109 nodes |

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

python paper\benchmarks\experiment005\run.py --preset smoke --repeats 3 --digits 85 --out paper\benchmarks\experiment005\runs\pilot-windows-01
python paper\benchmarks\experiment005\run.py --preset quick --repeats 7 --digits 85 --out paper\benchmarks\experiment005\runs\quick-windows-01

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
interpret 109 grid nodes as 109 independent replicates. Report numerical
failure frequency as a third axis. Only after these results are audited
should the two CSDA manuscripts be combined.
