# Experiment004 — expanded REAL NGSIM GCV/ML + spline forecasts

**Status:** completed_real_ngsim_expanded

No simulated positions or jerk were created. All outcomes compare forecasts with recorded future NGSIM positions.

Downloaded eligible trajectory episodes: **200**.
These are episode units, **not verified unique physical vehicles**.
One predeclared origin per episode; each sample is an overlapping horizon of the same episode.

## RMSE of future observed position (meters), all sites

| Method | 0.5 s | 1 s | 2 s |
| --- | ---: | ---: | ---: |
| pls_gcv_zero_last3 | 0.145254 | 0.516648 | 1.880504 |
| pls_gcv_zero_local25 | 0.340639 | 0.618422 | 1.344673 |
| pls_gcv_sample_last3 | 0.147630 | 0.535176 | 2.025396 |
| pls_gcv_sample_local25 | 0.316623 | 0.576409 | 1.353547 |
| pls_mle_zero_last3 | 0.143349 | 0.512384 | 1.868646 |
| pls_mle_zero_local25 | 0.340638 | 0.618422 | 1.344671 |
| pls_mle_sample_last3 | 0.145743 | 0.531006 | 2.014156 |
| pls_mle_sample_local25 | 0.316623 | 0.576410 | 1.353546 |
| spline_gcv_taylor2 | 0.135427 | 0.348043 | 0.878735 |
| savgol_21_taylor2 | 0.354719 | 0.850622 | 2.410597 |
| raw_local_quad25 | 0.340630 | 0.618412 | 1.344662 |

## Paired exploratory inference (method minus GCV spline)

Negative ΔMSE favors the named method. Stratified bootstrap resamples
**trajectory episodes**, not individual forecast steps. Dependence
within recording sessions remains, so these intervals are **exploratory**.
No multiple-testing correction or claim of population significance.

| Method | Horizon | n paired | ΔMSE (m²) | 95% bootstrap interval (m²) |
| --- | ---: | ---: | ---: | --- |
| pls_gcv_zero_last3 | 5 | 200 | 0.00276 | [-0.00660, 0.01181] |
| pls_gcv_zero_local25 | 5 | 200 | 0.09769 | [0.06850, 0.13134] |
| pls_gcv_sample_last3 | 5 | 200 | 0.00345 | [-0.00582, 0.01272] |
| pls_gcv_sample_local25 | 5 | 200 | 0.08191 | [0.05647, 0.11225] |
| pls_mle_zero_last3 | 5 | 200 | 0.00221 | [-0.00694, 0.01101] |
| pls_mle_zero_local25 | 5 | 200 | 0.09769 | [0.06898, 0.13184] |
| pls_mle_sample_last3 | 5 | 200 | 0.00290 | [-0.00666, 0.01152] |
| pls_mle_sample_local25 | 5 | 200 | 0.08191 | [0.05639, 0.11079] |
| savgol_21_taylor2 | 5 | 200 | 0.10749 | [0.07614, 0.14479] |
| raw_local_quad25 | 5 | 200 | 0.09769 | [0.06968, 0.13008] |
| pls_gcv_zero_last3 | 10 | 200 | 0.14579 | [0.05017, 0.25926] |
| pls_gcv_zero_local25 | 10 | 200 | 0.26131 | [0.17891, 0.36204] |
| pls_gcv_sample_last3 | 10 | 200 | 0.16528 | [0.06334, 0.29176] |
| pls_gcv_sample_local25 | 10 | 200 | 0.21111 | [0.14027, 0.30020] |
| pls_mle_zero_last3 | 10 | 200 | 0.14140 | [0.04375, 0.25759] |
| pls_mle_zero_local25 | 10 | 200 | 0.26131 | [0.17864, 0.36843] |
| pls_mle_sample_last3 | 10 | 200 | 0.16083 | [0.06123, 0.29001] |
| pls_mle_sample_local25 | 10 | 200 | 0.21111 | [0.13903, 0.29772] |
| savgol_21_taylor2 | 10 | 200 | 0.60242 | [0.43188, 0.79214] |
| raw_local_quad25 | 10 | 200 | 0.26130 | [0.17380, 0.36589] |
| pls_gcv_zero_last3 | 20 | 200 | 2.76412 | [1.59249, 4.14616] |
| pls_gcv_zero_local25 | 20 | 200 | 1.03597 | [0.65210, 1.48634] |
| pls_gcv_sample_last3 | 20 | 200 | 3.33005 | [1.96564, 4.98011] |
| pls_gcv_sample_local25 | 20 | 200 | 1.05991 | [0.66341, 1.47889] |
| pls_mle_zero_last3 | 20 | 200 | 2.71966 | [1.58004, 4.16671] |
| pls_mle_zero_local25 | 20 | 200 | 1.03597 | [0.65911, 1.47983] |
| pls_mle_sample_last3 | 20 | 200 | 3.28465 | [1.93967, 4.82495] |
| pls_mle_sample_local25 | 20 | 200 | 1.05991 | [0.67529, 1.46961] |
| savgol_21_taylor2 | 20 | 200 | 5.03880 | [3.73102, 6.53789] |
| raw_local_quad25 | 20 | 200 | 1.03594 | [0.66211, 1.50437] |

## Method interpretation and unavoidable limitations

- PLS MLE means **profiled Gaussian marginal-likelihood selection**
  in this repository, a REML-style criterion, NOT an assertion of
  exact joint Guerrero likelihood MLE for (lambda, mu, sigma²).
- Training-derived mu is conditional; its estimation is not refit
  for every held-out leave-one-out sample.
- NGSIM Vehicle_ID can repeat. Recorded episodes are defined by
  location, ID, start time and frame/time continuity; repeated
  drivers across episodes or shared scenes can induce dependence.
- Ground-truth physical jerk is NOT observed; this experiment
  supports only statistical analysis of recorded-position forecasts.
- If the data-selection screen favors typical motions or the first
  IDs, sampling need not represent the full traffic population.
- Complete raw source pages, selected trajectories, all model rows,
  environment and file inventory are retained in the persistent VM
  directory listed in the run manifest. Their exact hashes are
  recorded so another agent can audit them.
