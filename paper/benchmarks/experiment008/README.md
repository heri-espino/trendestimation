# Experiment008 — Complete-criterion computational timing tensor

**Goal:** Measure computing time only, not RMSE. Each actual measured timing includes its status, solver, n, d, mean policy, magnitude, criterion, S-grid size, coordinate strategy, workload and repetition.

## Full factorial

Experiment008 enumerates all n={64,128,256,512,1024,16384,131072}; d=1,...,6; mean policies mu=0, mu=data, and fixed mu=0.15 control; observation magnitude low/high; CV/GCV/BIC/AICc/MLE; four smoothness grids with M=100,1000,10000,100000, all including S=1; four workloads {one S / one series, grid S / one series, one S / multiple series, grid S / multiple series}; direct S versus pretranslated lambda; and 10 complete-criterion solver/hybrid backends. The one-S workload is not redundantly counted for four grid sizes.

`run_batches.py` saves the *full plan* in `full_factorial_plan.csv.gz`, marking resource-ineligible cells. A planned cell is NOT a measured timing result. Real times appear only in `slices/*/raw_times.csv` rows with `status=ok`. Incomplete, undefined, infeasible and numerically failed records remain explicit.

## Run and repository preservation

GitHub Actions `.github/workflows/experiment008-full-factorial.yml` launches separate bounded pilot and broad batches on self-hosted Windows runner PCAG103A-08, using the EXISTING non-admin Conda environment named `trendestimation`. It neither installs Python nor modifies system packages. Each run saves its outputs under an immutable run-ID results branch, as well as a GitHub Actions artifact.

From the repository root, an equivalent command is:

```powershell
conda run --no-capture-output -n trendestimation python paper\benchmarks\experiment008\run_batches.py --preset pilot --max-seconds 600 --max-slices 24 --repeats 2 --series-count 2 --max-work 30000000 --output paper\benchmarks\experiment008\runs\my-unique-run
```

## Scientific safeguards

- The naive baseline calls actual dense `np.linalg.inv`; a dense 131072-by-131072 float64 array alone uses 128 GiB. The full naive factorial at n=131072 is computationally infeasible and must be marked so.
- The SVD solver is dense O(n^3) setup, O(n^2) storage. Banded Cholesky plus selected inverse is O(n d^2) arithmetic per penalty for fixed d, but can be numerically inaccurate near high smoothness; sparse/PCG hybrids additionally pay exact criterion diagnostic costs.
- The target grid includes S=1 as an analytic lambda=infinity endpoint, not a gigantic finite lambda.
- `mu=data` uses each series' observed difference mean. CV, GCV, BIC and AICc are explicitly CONDITIONAL plug-in scores in this benchmark; they are NOT the same as fully refitting the estimated mu for every held-out sample. MLE is conditional plug-in.
- `direct_s` maps S to lambda at score-evaluation time; `mapped_lambda` pretranslates the identical candidate grid. Timing comparisons must not confound different candidate sets.
- The RSS-based BIC has an interpolation boundary degeneracy as S tends to zero. The finite S grid is a constraint, not a theoretical remedy.
- A 100000-point mapping at n=131072 may require too many operations; do not interpret an omitted or budget-limited cell as a zero-time benchmark.

## Deliverables and next steps

Each batch saves a compressed full manifest, batch configuration, per-slice timing CSV, mean/median summaries, paired naive speedups, numerical statuses and machine/BLAS details. Analyze only complete valid repetitions, estimate log-log scaling on matched factor cells, preserve all artifacts in Git, and extend to further bounded batches without overwriting historical results.
