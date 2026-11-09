# Experiment005 — verified known-jerk simulations and reproducibility ledger

**Completed 2026-11-08 (Mexico City local time)** on the GitHub-hosted runner. [Successful workflow #42547883064](https://github.com/heri-espino/trendestimation/actions/runs/42547883064). The separate [PCAG103A-08 Windows workflow #42547250403](https://github.com/heri-espino/trendestimation/actions/runs/42547250403) remained **queued at last verification**. No independent Windows execution or VM storage has been confirmed; do not conflate cloud results with a VM run.

## Permanent research record

- **Executed source commit:** da7d7a02f0a10ddacea29e4d494bcb2a101e2748.
- **All first-party simulation results, including generated clean and noisy trajectories:** [immutable GitHub archive branch](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp005-cloud-42547883064-a1/paper/ngsim-jerk-case-study/experiments/experiment005/runs/cloud-42547883064-a1).
- **Archive subdirectory:** paper/ngsim-jerk-case-study/experiments/experiment005/runs/cloud-42547883064-a1/
- **Complete file inventory:** metadata/file_inventory.json, documenting **33 generated files, 44,771,054 bytes excluding inventory itself**. Subdirectories: pilot, pilot/figures, confirm, confirm/figures, logs, metadata.
- **Configuration:** pilot/config.json and confirm/config.json match the predeclared [config.json](config.json), with disjoint, deterministic trial seeds.
- **Complete analytic true and noisy x,v,a,j per trial:** pilot/trajectories.jsonl.gz and confirm/trajectories.jsonl.gz.
- **Full raw result files:** forecast_rows.csv, jerk_rows.csv, selection_rows.csv, ablation_rows.csv within both stage folders.
- **All derived analyses:** scenario_forecast_summary.json, scenario_jerk_summary.json, pooled_forecast_summary.json, pooled_jerk_summary.json, paired_bootstrap.json, RESULTS.md, run_manifest.json within both stage folders.
- **Generated figure:** figures/forecast_rmse.png within each stage.
- **Runtime and software provenance:** logs/pilot.log, logs/confirm.log, metadata/source_commit.txt, metadata/requirements-resolved.txt, metadata/file_inventory.json.

These first-party synthetic datasets are committed on the results-only branch; unlike Experiment004, they do not depend on proprietary or external original measurements.

## Verified trial counts

| Stage | Independent seeded trials | GCV/ML selections | Known-jerk fit records | Forecast-error records | Fixed-S 2x2 ablation records | Invalid cases |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pilot | 96 | 960 | 1,152 | 6,624 | 4,608 | 0 |
| Confirmation | **1,296** | **12,960** | **15,552** | **89,424** | **62,208** | **0** |

The 1,296 confirmations (separate from the pilot) comprise 6 analytic regimes × 3 noise levels × 3 noise structures × 24 seeds. The actual confirmation numerical evaluation required approximately **49.25 seconds**, excluding setup/archive. Sampling is 10 Hz with 80 historical training observations and 20 future observations. The GCV and profile-ML selectors use the same finite smoothness grid. The synthetic-only oracle mu uses *known historical truth*, never future data.

## Main result: historical known-discrete-jerk RMSE (m/s³)

The truth is exact D3 of the clean analytic position divided by the sampling interval cubed. This correctly accounts for the finite-difference convention near changes in instantaneous jerk.

| Method | RMSE |
| --- | ---: |
| **PLS, profile ML, global cubic OLS mean** | **2.9177** |
| PLS, profile ML, oracle mean | 2.9182 |
| PLS, profile ML, zero mean | 3.0207 |
| PLS, profile ML, raw sample-difference mean | 9.4957 |
| Savitzky–Golay | 36.8291 |
| GCV cubic smoothing spline | 60.9131 |
| PLS, GCV, zero mean | 68.2422 |

The synthetic simulation substantially favors **profiled Gaussian marginal ML** over GCV for recovering the true finite-difference jerk under this noise model. The same effect was not visible at comparable magnitude in Experiment004 recorded-position forecasting. It must be investigated, not generalized.

The raw sample mean of D3 observed positions is endpoint-sensitive: telescoping collapses it to the difference of historical boundary second differences divided by n-3. It performs poorly in this designed endpoint-contamination scenario.

## Main result: known-clean future-position RMSE (m)

| Method | 0.5 s | 1 s | 2 s |
| --- | ---: | ---: | ---: |
| **PLS profile ML, zero mean, local-25** | 0.2756 | 0.4132 | 0.8607 |
| PLS profile ML, global cubic OLS mean, local-25 | 0.2746 | 0.4382 | 1.0164 |
| PLS profile ML, **synthetic-only oracle** mean, local-25 | **0.2488** | **0.3849** | 0.8592 |
| PLS profile ML, zero mean, three-point recurrence | 0.3655 | 0.6592 | 1.6392 |
| GCV cubic spline, quadratic Taylor | 0.5673 | 0.9710 | 2.1705 |
| Savitzky–Golay, quadratic Taylor | 0.7695 | 1.4812 | 3.7125 |

The GCV PLS, zero mean, last-three-point continuation has much larger error (1.2857/3.2711/10.1890 m at those horizons). The GCV PLS, sample-derived mean, local-25 forecasts are even more unstable (3.5877/7.6547/22.7517 m). A separate forecast continuation and tuning rule materially affect performance.

## Regime-specific conclusion at the 1-second horizon

Root-mean-square aggregation of the equal-replication scenarios within each motion regime:

| True jerk regime | ML PLS zero mean, local25 | ML PLS global OLS mean, local25 | GCV spline |
| --- | ---: | ---: | ---: |
| Constant zero | **0.260** | 0.290 | 0.753 |
| Constant positive | 0.440 | **0.298** | 1.243 |
| Constant negative | 0.456 | **0.291** | 1.121 |
| Sinusoidal | **0.434** | 0.437 | 0.759 |
| Sign reversal | **0.494** | 0.748 | 1.029 |
| Braking pulse | **0.351** | 0.381 | 0.809 |

**Interpretation:** a training-only nonzero global cubic mean is useful for sustained nonzero jerk, but can be worse at sudden changes. Neither a nonzero reference mean nor a forecasting rule is universally superior.

## Contrast with the 200-episode real NGSIM experiment

Experiment004 favored the GCV spline over PLS for future **camera-recorded position RMSE** at all three horizons. Experiment005 instead favors **profile-ML-selected PLS** under analytically known, noisily observed trajectories and a clean future-position target.

This is an important domain/model discrepancy. Hypotheses include real camera systematic error, trajectory complexity, outliers, recording dependence, prior/boundary assumptions, and the different recorded-versus-clean evaluation target. Do not hide the contradiction or present synthetic accuracy as proof of NGSIM physical jerk accuracy.

**Inferential scope:** All Monte Carlo confidence intervals describe the chosen simulation generating processes and artificial scenario mixture. They do not represent the traffic population. The oracle mean is not available on actual camera trajectories. Existing library MLE is *profiled Gaussian marginal likelihood conditional on the reference mean*, not joint estimation of (mean, lambda, noise variance).

## VM preservation status and reproducibility

The Windows workflow is configured to write complete independently executed output to:

    %USERPROFILE%\Documents\TrendEstimation-PaperC\experiment005\run-42547250403-a1\

This directory is **not yet confirmed created**. The separate immutable Git cloud archive above **already stores all 33 generated files**, including both full synthetic datasets. [The import script](sync_cloud_results_to_vm.ps1) can copy and checksum those exact cloud-generated files on PCAG103A-08 without claiming independent Windows computation.

From an existing environment and new unique destination:

    python -m pytest -q tests/test_paper_c_experiment005.py
    python paper/ngsim-jerk-case-study/experiments/experiment005/run.py --stage pilot --output-dir "C:\some-new-run\pilot"
    python paper/ngsim-jerk-case-study/experiments/experiment005/run.py --stage confirm --output-dir "C:\some-new-run\confirm"

No original NGSIM data, Paper C experiment001–004 results, manuscript PDFs or other agents' PRs were altered during this experiment.
