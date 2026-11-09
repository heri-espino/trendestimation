# Experiment006 — verified joint unknown-mean REML results ledger

**Completed on PCAG103A-08, November 9, 2026.** [Successful Windows workflow #42639588117](https://github.com/heri-espino/trendestimation/actions/runs/42639588117). This is the completed scientific comparison on immutable Experiment005 and Experiment004 sources, with the **corrected exact 15-S grid** and all diagnostic outputs. Executed research commit: 1eecebd302ba08c661d4dfa88a9eb297d76538d1. Subsequent changes correct test import resolution only; scientific formulas and outcomes are unchanged.

## Exact saved data and directory paths

**Full persistent VM run:**

    C:\Users\175199\Documents\TrendEstimation-PaperC\experiment006\run-42639588117-a1

**Git results-only archive:** [results/paper-c-exp006-pc08-42639588117-a1](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp006-pc08-42639588117-a1/paper/ngsim-jerk-case-study/experiments/experiment006/runs/pc08-42639588117-a1).

Inside Git, all files are below:

    paper/ngsim-jerk-case-study/experiments/experiment006/runs/pc08-42639588117-a1/

The recursive [file_inventory.json](https://github.com/heri-espino/trendestimation/blob/results/paper-c-exp006-pc08-42639588117-a1/paper/ngsim-jerk-case-study/experiments/experiment006/runs/pc08-42639588117-a1/metadata/file_inventory.json) records **47 generated files, 18,531,914 bytes excluding itself**, in directories pilot, confirm, real, logs and metadata. It includes every relative path, size and SHA-256.

Each stage directory preserves complete files named selections_rows.csv, forecasts_rows.csv, jerk_rows.csv, cv_rows.csv, summary.csv, paired_comparisons.csv, selection_diagnostics.csv, shrinkage_diagnostics.csv, regime_forecast_summary.csv, run_manifest.json, RESULTS.md, DIAGNOSTICS.md, plus known_jerk_summary.csv for synthetic stages. The metadata directory contains executed source commit, exact source paths, dependency freeze and file checksums; logs contains all three execution transcripts and preflight tests.

The previously generated clean/noisy synthetic trajectories and raw FHWA data were referenced and SHA-256 verified, **not regenerated**. Source SHA-256: simulation pilot 8669b5690730955535195e9fe7a5b4bd75c2861851f291b62a7634bbd797af5f; simulation confirm 02bf89afe84c39c653a557abcb479c7746ed282b5ce81c493abbca74b991690d; NGSIM selected positions e6b594edd0cde7165302c4c7b65720645ec940122af23152db24f7eb1230598e. The original complete synthetic source remains in the Experiment005 results branch; FHWA source CSV pages remain in the university VM Experiment004 source directory.

## Actual completion counts

| Stage | Source trials / episodes | New forecasts | Likelihood selections | Training-only alpha-CV choices | Historical jerk records |
| --- | ---: | ---: | ---: | ---: | ---: |
| Synthetic pilot | 96 | 3,456 | 480 | 576 | 1,056 |
| Synthetic confirmation | **1,296** | **46,656** | **6,480** | **7,776** | **14,256** |
| Real NGSIM | **200** | **7,200** | **1,000** | **1,200** | 2,200 without true jerk |

Every original trial was evaluated. Earlier Experiment005/004 forecast rows were included in the matched summaries with archived-source labeling. Original source files, prior results and papers were not overwritten.

## Methods actually compared

(1) Joint GLS-mean-adjusted Gaussian REML with a continuous scalar lambda search and exact zero/infinite limits; (2) the same corrected REML restricted to **exactly** 15 predeclared normalized smoothness candidates; (3) fixed-mu=0 Gaussian profiled likelihood with continuous lambda search; (4) raw sample third-difference mean plug-in and continuous fixed-mu Gaussian likelihood; (5) training global cubic OLS mean plug-in and continuous fixed-mu Gaussian likelihood; (6) training-only rolling-origin validation of alpha in {0,0.5,1} multiplying the full-history joint-REML reference mean, with lambda fixed by joint REML. Every method uses the same d=3 PLS smoother and both three-point and local-25 forecast rules, evaluated at 0.5, 1 and 2 seconds.

**Audit correction:** Windows workflow #42638094948 initially included an undeclared zero boundary in the nominal grid comparator. Its historical branch and logs are preserved, but not used for this ledger. Corrected run #42639588117 restricts the grid to exactly the declared S values. The continuous optimizer still evaluates both endpoint limits. The mesh/refinement search is **not certified global**.

## Known discrete jerk recovery — simulation confirmation

The exact target is D3(clean historical position) divided by 0.1 cubed, in m/s³. Pooled RMSE across 1,296 frozen confirmation trials:

| Policy | Jerk RMSE (m/s³) |
| --- | ---: |
| **Fixed-mu Gaussian profile ML, global cubic OLS reference** | **2.441257** |
| Fixed-mu Gaussian profile ML, zero reference | 2.587379 |
| Joint unknown-mu REML, continuous | 3.294994 |
| Joint REML, exact 15-S grid | 4.101415 |
| Fixed-mu Gaussian profile ML, raw third-difference mean | 7.707732 |

Nested alpha shrinkage has historical finite-difference jerk RMSE about 3.29 m/s³, depending on the forecast rule/horizon. Mean-adjusted REML is statistically coherent but **did not minimize true historical jerk error** in the tested DGP mixture.

## Future clean position — simulation confirmation (local25 extrapolation)

| Policy | 0.5 s | 1 s | 2 s |
| --- | ---: | ---: | ---: |
| **Fixed zero mu, continuous profile ML** | **0.269675** | **0.405257** | **0.849158** |
| Archived fixed zero mu, 15-S profile ML | 0.275599 | 0.413242 | 0.860666 |
| Fixed global cubic OLS mu, continuous profile ML | 0.272800 | 0.435296 | 1.010690 |
| Joint REML, continuous | 0.306591 | 0.497717 | 1.171512 |
| Joint REML, corrected 15-S grid | 0.304842 | 0.496636 | 1.176034 |
| Joint REML with training-only alpha shrinkage | 0.310350 | 0.462241 | 1.026520 |
| Archived GCV cubic smoothing spline | 0.567347 | 0.971005 | 2.170480 |

Joint REML is **not** a universally optimal forecast choice. Shrinkage improves the continuous joint REML one-second forecast from 0.498 to 0.462 m, but does not beat fixed-zero continuous profile ML.

## Future recorded position — real NGSIM

| Policy / continuation | 0.5 s | 1 s | 2 s |
| --- | ---: | ---: | ---: |
| **Archived GCV cubic spline, quadratic Taylor** | **0.135427** | **0.348043** | **0.878735** |
| Joint REML continuous, three-point recurrence | 0.145722 | 0.533078 | 2.027175 |
| Joint REML continuous, local25 | 0.316758 | 0.577506 | 1.359621 |
| Fixed zero profile ML continuous, local25 | 0.340637 | 0.618420 | 1.344673 |
| Joint REML with training-only alpha shrinkage, local25 | 0.329448 | 0.591118 | 1.348648 |

All real NGSIM validation is against **recorded future position**, not independently observed physical jerk. The GCV spline still has the best pooled RMSE at all three horizons. The five coarse recording-time session proxies do not support reliable population-level confidence intervals. The paired session-block bootstrap is explicitly exploratory.

## Critical smoothing-boundary finding

Among 1,296 synthetic confirmation trials, continuous joint REML selected median normalized S=0.9552 and the infinite-penalty limit **304 times**; corrected grid REML selected median S=0.95 and infinity **307 times**. The raw sample-reference plug-in estimator selected less smooth fits and much larger reference jerk, especially under endpoint contamination.

Among **200 real NGSIM episodes**, continuous joint REML selected the **lambda→0 boundary in 161 cases (80.5%)**; median S=0. The continuous fixed-zero Gaussian profile likelihood also selected lambda→0 in 161 cases. The corrected 15-point grid **never** evaluates zero and has median selected S=0.05, the smallest allowed value. A zero-penalty fit is an interpolating unsmoothed historical trend, so it must be reported as model-selection boundary behavior, not a claim that smoothing is unnecessary.

The mean absolute reference jerk in synthetic confirmation was approximately 0.20 m/s³ for joint REML, 0.17 for global cubic OLS, and **5.63** for the unstable raw sample mean, consistent with telescoping and endpoint noise amplification.

## Statistical and publication boundaries

These are paired measurements of the *same archived simulation seeds* or *same archived real episodes* and do not constitute new independent samples. Known truth exists only for the synthetic model. The Gaussian REML estimate jointly optimizes the likelihood, but this does not imply minimum jerk or forecast MSE. Optimizing alpha on earlier training windows prevents outer-future leakage but does not confer universal extrapolation optimality. The confidence intervals in paired_comparisons.csv are conditional simulation estimates or five-block descriptive sensitivity intervals; there are multiple methods and horizons with no familywise correction.

**Next research task:** Investigate why independent-error Gaussian likelihood selects zero smoothing on so many NGSIM episodes, compare measurement-noise models and regime dependence in a new sequential experiment, and incorporate both favorable and unfavorable simulation/real findings into Paper C. Do not silently alter boundary policies or tune parameters on the final future observations. This study changes no prior archived runs or unrelated Springer/CSDA work.
