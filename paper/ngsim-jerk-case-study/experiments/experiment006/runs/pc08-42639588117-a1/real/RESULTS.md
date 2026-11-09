# Experiment006 real real: unknown-mu REML and forecast shrinkage

**Completed samples:** 200; full source SHA-256: e6b594edd0cde7165302c4c7b65720645ec940122af23152db24f7eb1230598e.
All selections and inner rolling-origin validation use historical data only.
Joint REML eliminates one unknown mean coefficient; the fixed-mu selectors
profile the nuisance variance but condition on a prechosen mean.

## One-second future-position RMSE (lower is better)

| Method | Matched windows | RMSE (m) |
| --- | ---: | ---: |
| archived:spline_gcv_taylor2 | 200 | 0.348043 |
| archived:pls_mle_zero_last3 | 200 | 0.512384 |
| plugin_global_ols_continuous_guerrero_last3 | 200 | 0.514386 |
| fixed_zero_continuous_guerrero_last3 | 200 | 0.514491 |
| shrink_tscv_guerrero_last3 | 200 | 0.515982 |
| archived:pls_gcv_zero_last3 | 200 | 0.516648 |
| archived:pls_mle_sample_last3 | 200 | 0.531006 |
| joint_reml_grid_guerrero_last3 | 200 | 0.531134 |
| joint_reml_continuous_guerrero_last3 | 200 | 0.533078 |
| plugin_sample_continuous_guerrero_last3 | 200 | 0.533374 |
| archived:pls_gcv_sample_last3 | 200 | 0.535176 |
| plugin_sample_continuous_local25 | 200 | 0.576406 |
| archived:pls_gcv_sample_local25 | 200 | 0.576409 |
| archived:pls_mle_sample_local25 | 200 | 0.576410 |
| joint_reml_continuous_local25 | 200 | 0.577506 |
| joint_reml_grid_local25 | 200 | 0.578081 |
| shrink_tscv_local25 | 200 | 0.591118 |
| archived:raw_local_quad25 | 200 | 0.618412 |
| fixed_zero_continuous_local25 | 200 | 0.618420 |
| archived:pls_mle_zero_local25 | 200 | 0.618422 |
| archived:pls_gcv_zero_local25 | 200 | 0.618422 |
| plugin_global_ols_continuous_local25 | 200 | 0.653222 |
| archived:savgol_21_taylor2 | 200 | 0.850622 |

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
