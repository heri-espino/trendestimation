# Experiment007 — VERIFIED smoothness versus known noise and jerk variability

**Completed: November 9, 2026.** The full paired factorial calibration study ran successfully on [Windows PCAG103A-08 #42660204414](https://github.com/heri-espino/trendestimation/actions/runs/42660204414) and independently on [GitHub-hosted Linux #42660028292](https://github.com/heri-espino/trendestimation/actions/runs/42660028292). Both used identical frozen scientific code, configuration, and seed streams. Do not mistake two computations with identical seeds for independent data replications.

- Windows executed SHA: 4a94a9e6f2a76b835f9655b755fa0712825f35c4.
- Linux executed SHA: 43392d7a904a94fd86fe5bbfe74091ad8dd933c7. Difference is Windows workflow addition, not scientific model changes.
- Windows persistent VM directory: C:\Users\175199\Documents\TrendEstimation-PaperC\experiment007\run-42660204414-a1
- [All Windows results, first-party generated data, figures and SHA inventory](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp007-pc08-42660204414-a1/paper/ngsim-jerk-case-study/experiments/experiment007/runs/pc08-42660204414-a1).
- [Independent Linux computations and complete data archive](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp007-cloud-42660028292-a1/paper/ngsim-jerk-case-study/experiments/experiment007/runs/cloud-42660028292-a1).
- [Exact Windows file-by-file SHA-256 inventory](https://github.com/heri-espino/trendestimation/blob/results/paper-c-exp007-pc08-42660204414-a1/paper/ngsim-jerk-case-study/experiments/experiment007/runs/pc08-42660204414-a1/metadata/file_inventory.json): **39 generated files, 8,114,088 bytes excluding the inventory**, under pilot, pilot/figures, confirm, confirm/figures, logs, metadata.
- Linux inventory: **37 generated files, 8,193,523 bytes**. Platform-specific logs and serialization differ slightly; numerical scientific conclusions agree.

## Full generated file layout

    <run-root>/
      pilot/
        config.json
        trials.jsonl.gz
        theory_cells.csv
        selections.csv
        per_cell.csv
        interventions.csv
        effects_summary.csv
        calibration_summary.csv
        summary.json
        RESULTS.md
        run_manifest.json
        figures/
          S_vs_observation_noise_known_mu_reml.png
          S_vs_observation_noise_joint_reml.png
          S_vs_observation_noise_global_ols_plugin_mle.png
          S_vs_observation_noise_gcv_zero_mu.png
          S_calibration_iid.png
      confirm/  (same complete set with separate seed namespace)
      metadata/
        source_commit.txt
        runner_name.txt                (Windows)
        requirements-resolved.txt
        data_provenance.txt
        file_inventory.json
      logs/
        preflight.log                  (Windows)
        pilot.log
        confirm.log

The recursive JSON inventory is the authoritative directory and file manifest. Each stored file is identified by exact relative path, byte length, SHA-256 and run identity. The archive includes the actual clean/noisy positions, true finite-difference jerks, measurement errors, standardized random innovation draws, random seeds, all selection decisions, all pairwise comparisons and figures. No prior Experiment004–006 artifacts or unrelated Springer/CSDA studies were overwritten or rerun.

## Experimental design and counts

n=80 historical positions, interval 0.1s, difference order d=3. Independent factorial factors: position noise SD 0.01/0.05/0.20 m; jerk innovation SD 0.5/2/8 m/s³; jerk processes iid, AR(1) rho .7, sign reversal; measurement noise iid, AR(1) rho .65, randomly signed ±4-SD endpoint outlier. Baseline mean jerk 0.25 m/s³.

- Pilot: 162 cases, 648/648 valid PLS selections, 6 independent parent draws.
- Confirmation: **1,944 cases, 7,776/7,776 valid PLS selections, 72 independent parent draws**, zero invalid selections.
- Each parent shares exactly the same standardized jerk innovation and measurement noise across 27 factorial conditions. The 1,944 outcomes are not independent sample units.
- Four selection policies per case: known generating reference mean + fixed Gaussian likelihood (**oracle control**), unknown-mean joint REML, noisy training global cubic OLS reference + fixed Gaussian profile likelihood, and GCV with mu=0 on the historical exact 15-value S grid.
- Full analyses: **324 method/condition cells, 6,048 paired intervention rows, 108 parent-cluster bootstrap effect summaries, 36 calibration summaries**, and five figures per stage.

## Mathematical truth and what it means

Under independent Gaussian observation errors and Gaussian innovations in D3 of true positions, the variance ratio is lambda_true = sigma_epsilon²/(dt^6 sigma_jerk²). The normalized PLS smoothness evaluated at lambda_true is

    S_true = mean_j [lambda_true delta_j / (1 + lambda_true delta_j)].

It is the average *spectral fraction of the D3-observation covariance attributable to measurement noise*. For correlated errors/jerks or randomized endpoint outliers, the exact full-covariance fraction is

    S_cov = trace( solve(C_jerk + C_noise, C_noise) ) / (n-3).

This is not generally the same as scalar-penalty S when the covariance model is wrong. The sign-reversal regime additionally violates the constant-mean jerk assumption. True physical observation precision is inverse observation-error variance; S is a relative fraction and cannot independently identify absolute precision.

## Primary result — correct iid Gaussian model

Each estimator was evaluated on **216 paired conditions**, but only 24 independent parent draws, with three observation SD × three jerk SD combinations per parent.

| Selection policy | Spearman correlation: selected S versus exact theoretical fraction | MAE(S) | Bias(S) |
| --- | ---: | ---: | ---: |
| Known-mu Gaussian REML (**oracle only**) | 0.9668 | 0.01072 | +0.00067 |
| **Joint unknown-mu REML** | **0.9654** | **0.01148** | +0.00209 |
| Training global cubic OLS reference + Gaussian profile ML | 0.9662 | 0.01430 | +0.00688 |
| GCV, fixed mu=0, 15-S grid | 0.9007 | 0.02486 | −0.01555 |

The Spearman coefficient is descriptive across dependent factorial cells, NOT a 216-independent-observation significance test. In this correctly specified covariance model joint REML has better S calibration than the practical global OLS plug-in, despite Experiment006 showing a different ranking for **known physical jerk recovery**. Smoothness calibration and physical jerk loss are different optimization targets.

## Primary result — paired intervention tests, joint REML

| Paired manipulation | Exact theoretical mean delta S | Estimated mean delta S | 95% cluster-bootstrap interval (24 independent parents) |
| --- | ---: | ---: | --- |
| Increase observation SD 0.01 → 0.20 m at fixed jerk variability | +0.14511 | **+0.14980** | [+0.14539,+0.15436] |
| Increase jerk innovation SD 0.5 → 8 m/s³ at fixed observation noise | −0.13374 | **−0.13872** | [−0.14284,−0.13448] |
| Simultaneously scale observation and jerk SD: (0.05,2) → (0.20,8) | 0 | approximately 0 (−9.1e−11) | [−9.1e−10,+7.3e−10] |

The third contrast is *mathematical scale invariance*: observation variance changes by a factor of **16**, hence absolute observation precision changes by the inverse factor, while theoretical and fitted S remain constant. It **disproves** the interpretation that the smoothing index measures absolute sensor accuracy/precision.

## Important model-misspecification results — joint REML

| True jerk process | Observation errors | Spearman selected S versus exact covariance fraction | MAE(S) | Bias(S) |
| --- | --- | ---: | ---: | ---: |
| iid | iid (**correct model**) | **0.965** | **0.0115** | +0.0021 |
| iid | **AR(1)** correlated observations | 0.834 | **0.0712** | −0.0708 |
| AR(1) jerk innovations | iid | 0.964 | 0.0308 | −0.0256 |
| AR(1) jerk innovations | AR(1) observations | 0.884 | **0.1111** | −0.1111 |
| iid | randomized last-point ±4-SD outlier | 0.957 | 0.0135 | −0.0012 |
| abrupt jerk sign reversal | iid | 0.937 | 0.0214 | −0.0106 |
| abrupt jerk sign reversal | AR(1) observations | 0.821 | 0.0806 | −0.0802 |

The estimates often preserve **directional tracking** despite substantial **quantitative miscalibration**, especially under serially correlated observation noise. Hence a broad claim that selected S always measures "how clean" sensor data are is not supported.

## Cross-platform reproducibility

Identical correct-model Spearman results were obtained on Windows and Linux. The joint-REML calibration MAE was 0.0114782422672 (Windows) and 0.0114782420359 (Linux), a difference ~2.3e−10. The paired intervention directions and conclusions also matched to displayed precision. Both independent computations used the same random seed parent draws, not additional independent subjects.

## Manuscript conclusion and limits

**Defensible:** Under the specified iid Gaussian third-order PLS model, normalized S equals average spectral noise attribution at the true variance ratio. Selected S can closely approximate this known relative fraction in controlled DGPs. This interpretation has an established precursor in Guerrero's variance-ratio/relative precision framework; the experiment's distinctive contribution is a transparent third-order physical jerk calibration and stress-test.

**Not defensible:** S measures absolute precision, universally indicates NGSIM sensor quality, proves a certain share of positions are wrong, or ensures superior forecasting. Neither known true jerk nor known sensor error exists for real FHWA NGSIM observations. Do not claim historical priority for PLS forecasting or normalized index mathematics.

**Next research question, not authorized as part of this experiment:** whether modeling correlated observation errors can correct the largest observed calibration failure, and whether independent sensor repeats can identify absolute observation variance. These would require a separately preregistered Experiment008, not retroactive alteration of this verified result.
