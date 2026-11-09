# Experiment006 synthetic confirm: unknown-mu REML and forecast shrinkage

**Completed samples:** 1296; full source SHA-256: 02bf89afe84c39c653a557abcb479c7746ed282b5ce81c493abbca74b991690d.
All selections and inner rolling-origin validation use historical data only.
Joint REML eliminates one unknown mean coefficient; the fixed-mu selectors
profile the nuisance variance but condition on a prechosen mean.

## One-second future-position RMSE (lower is better)

| Method | Matched windows | RMSE (m) |
| --- | ---: | ---: |
| archived:pls_mle_oracle_local25 | 1296 | 0.384884 |
| fixed_zero_continuous_local25 | 1296 | 0.405257 |
| archived:pls_mle_zero_local25 | 1296 | 0.413242 |
| plugin_global_ols_continuous_local25 | 1296 | 0.435296 |
| archived:pls_mle_ols_global_local25 | 1296 | 0.438164 |
| archived:pls_gcv_oracle_local25 | 1296 | 0.447321 |
| archived:pls_gcv_zero_local25 | 1296 | 0.449313 |
| shrink_tscv_local25 | 1296 | 0.462241 |
| archived:pls_gcv_ols_global_local25 | 1296 | 0.478124 |
| archived:raw_local_quad25 | 1296 | 0.482739 |
| joint_reml_grid_local25 | 1296 | 0.496636 |
| joint_reml_continuous_local25 | 1296 | 0.497717 |
| archived:pls_mle_oracle_guerrero_last3 | 1296 | 0.587487 |
| plugin_global_ols_continuous_guerrero_last3 | 1296 | 0.604215 |
| archived:pls_mle_ols_global_guerrero_last3 | 1296 | 0.616060 |
| fixed_zero_continuous_guerrero_last3 | 1296 | 0.634017 |
| archived:pls_mle_zero_guerrero_last3 | 1296 | 0.659201 |
| shrink_tscv_guerrero_last3 | 1296 | 0.738328 |
| joint_reml_continuous_guerrero_last3 | 1296 | 0.760378 |
| joint_reml_grid_guerrero_last3 | 1296 | 0.779695 |
| archived:spline_gcv_taylor2 | 1296 | 0.971005 |
| archived:pls_mle_ols_tail25_local25 | 1296 | 1.204729 |
| archived:pls_gcv_ols_tail25_local25 | 1296 | 1.230195 |
| archived:pls_mle_ols_tail25_guerrero_last3 | 1296 | 1.422168 |
| archived:savgol21_taylor2 | 1296 | 1.481177 |
| archived:pls_gcv_ols_global_guerrero_last3 | 1296 | 3.138274 |
| archived:pls_gcv_oracle_guerrero_last3 | 1296 | 3.237442 |
| archived:pls_gcv_zero_guerrero_last3 | 1296 | 3.271087 |
| archived:pls_gcv_ols_tail25_guerrero_last3 | 1296 | 3.404273 |
| plugin_sample_continuous_guerrero_last3 | 1296 | 3.654714 |
| archived:pls_mle_sample_guerrero_last3 | 1296 | 3.900587 |
| archived:pls_gcv_sample_guerrero_last3 | 1296 | 5.007758 |
| archived:pls_mle_sample_local25 | 1296 | 7.625005 |
| plugin_sample_continuous_local25 | 1296 | 7.625311 |
| archived:pls_gcv_sample_local25 | 1296 | 7.654658 |

## Scientific limits
- Real data target is future recorded camera position; true jerk is unavailable.
- Synthetic target is future clean analytic position and exact D3 jerk.
- Older PLS/spline baselines are read-only, from the archived original runs.
- Continuous optimization checks a 61-point logarithmic lattice and its
  observed minima and boundaries; it is not a certified globally optimal solver.
- Shrinkage alpha uses nested historical rolling-origin folds and
  a full-window REML penalty; it is forecast-targeted, not pure REML.
- Real bootstrap samples only five coarse capture blocks; no population
  significance claim. Simulation intervals condition on the chosen DGP.
- No future truth enters reference or smoothing-parameter selection.
