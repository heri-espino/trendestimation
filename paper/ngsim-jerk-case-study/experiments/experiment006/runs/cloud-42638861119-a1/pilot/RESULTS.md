# Experiment006 synthetic pilot: unknown-mu REML and forecast shrinkage

**Completed samples:** 96; full source SHA-256: 7c513e3ff546929f26f463688a7c0282700562d5f01bf526a250658ff041d84a.
All selections and inner rolling-origin validation use historical data only.
Joint REML eliminates one unknown mean coefficient; the fixed-mu selectors
profile the nuisance variance but condition on a prechosen mean.

## One-second future-position RMSE (lower is better)

| Method | Matched windows | RMSE (m) |
| --- | ---: | ---: |
| archived:pls_mle_oracle_local25 | 96 | 0.364954 |
| archived:pls_mle_oracle_guerrero_last3 | 96 | 0.389975 |
| archived:pls_mle_ols_global_local25 | 96 | 0.430831 |
| fixed_zero_continuous_local25 | 96 | 0.431050 |
| archived:pls_mle_zero_local25 | 96 | 0.436593 |
| archived:pls_mle_ols_global_guerrero_last3 | 96 | 0.439595 |
| plugin_global_ols_continuous_local25 | 96 | 0.443597 |
| plugin_global_ols_continuous_guerrero_last3 | 96 | 0.452185 |
| archived:pls_gcv_oracle_local25 | 96 | 0.470966 |
| joint_reml_continuous_local25 | 96 | 0.492164 |
| archived:pls_gcv_zero_local25 | 96 | 0.492281 |
| shrink_tscv_local25 | 96 | 0.494773 |
| fixed_zero_continuous_guerrero_last3 | 96 | 0.498115 |
| joint_reml_grid_local25 | 96 | 0.501179 |
| archived:pls_gcv_ols_global_local25 | 96 | 0.503514 |
| archived:pls_mle_zero_guerrero_last3 | 96 | 0.525700 |
| shrink_tscv_guerrero_last3 | 96 | 0.533521 |
| archived:raw_local_quad25 | 96 | 0.537248 |
| joint_reml_continuous_guerrero_last3 | 96 | 0.539898 |
| joint_reml_grid_guerrero_last3 | 96 | 0.565837 |
| archived:spline_gcv_taylor2 | 96 | 1.112332 |
| archived:pls_mle_ols_tail25_local25 | 96 | 1.581659 |
| archived:pls_gcv_ols_tail25_local25 | 96 | 1.614953 |
| archived:pls_mle_ols_tail25_guerrero_last3 | 96 | 1.863846 |
| archived:savgol21_taylor2 | 96 | 2.021937 |
| archived:pls_gcv_ols_global_guerrero_last3 | 96 | 2.708131 |
| plugin_sample_continuous_guerrero_last3 | 96 | 4.943490 |
| archived:pls_mle_sample_guerrero_last3 | 96 | 5.213634 |
| archived:pls_gcv_oracle_guerrero_last3 | 96 | 5.663248 |
| archived:pls_gcv_zero_guerrero_last3 | 96 | 5.667233 |
| archived:pls_gcv_ols_tail25_guerrero_last3 | 96 | 5.933999 |
| archived:pls_gcv_sample_guerrero_last3 | 96 | 7.563597 |
| archived:pls_mle_sample_local25 | 96 | 9.435141 |
| plugin_sample_continuous_local25 | 96 | 9.435831 |
| archived:pls_gcv_sample_local25 | 96 | 9.472163 |

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
