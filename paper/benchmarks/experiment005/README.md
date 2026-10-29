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
