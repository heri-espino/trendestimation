# Experiment005 confirm — known jerk, controlled position observations

**Trials:** 1296 independent seeded synthetic series.
**Duration:** 32.7 seconds on PCAG103A-08.
**Reference truth:** exact analytic trajectories and discrete third differences;
future forecasts evaluated against clean **known** positions.

## Pooled future clean-position RMSE (meters)

| Horizon | Method | RMSE (m) |
| --- | --- | ---: |
| 5 frames | pls_mle_oracle_local25 | 0.248820 |
| 5 frames | pls_mle_ols_global_local25 | 0.274572 |
| 5 frames | pls_mle_zero_local25 | 0.275599 |
| 5 frames | pls_gcv_oracle_local25 | 0.291711 |
| 5 frames | pls_gcv_zero_local25 | 0.298554 |
| 5 frames | pls_gcv_ols_global_local25 | 0.303750 |
| 5 frames | pls_mle_oracle_guerrero_last3 | 0.317859 |
| 5 frames | raw_local_quad25 | 0.320794 |
| 5 frames | pls_mle_ols_global_guerrero_last3 | 0.334939 |
| 5 frames | pls_mle_zero_guerrero_last3 | 0.365512 |
| 5 frames | spline_gcv_taylor2 | 0.567347 |
| 5 frames | pls_mle_ols_tail25_local25 | 0.635549 |
| 5 frames | pls_gcv_ols_tail25_local25 | 0.654075 |
| 5 frames | pls_mle_ols_tail25_guerrero_last3 | 0.716319 |
| 5 frames | savgol21_taylor2 | 0.769481 |
| 5 frames | pls_gcv_ols_global_guerrero_last3 | 1.225947 |
| 5 frames | pls_gcv_oracle_guerrero_last3 | 1.267859 |
| 5 frames | pls_gcv_zero_guerrero_last3 | 1.285671 |
| 5 frames | pls_gcv_ols_tail25_guerrero_last3 | 1.356059 |
| 5 frames | pls_mle_sample_guerrero_last3 | 1.529762 |
| 5 frames | pls_gcv_sample_guerrero_last3 | 1.902162 |
| 5 frames | pls_mle_sample_local25 | 3.568783 |
| 5 frames | pls_gcv_sample_local25 | 3.587721 |
| 10 frames | pls_mle_oracle_local25 | 0.384884 |
| 10 frames | pls_mle_zero_local25 | 0.413242 |
| 10 frames | pls_mle_ols_global_local25 | 0.438164 |
| 10 frames | pls_gcv_oracle_local25 | 0.447321 |
| 10 frames | pls_gcv_zero_local25 | 0.449313 |
| 10 frames | pls_gcv_ols_global_local25 | 0.478124 |
| 10 frames | raw_local_quad25 | 0.482739 |
| 10 frames | pls_mle_oracle_guerrero_last3 | 0.587487 |
| 10 frames | pls_mle_ols_global_guerrero_last3 | 0.616060 |
| 10 frames | pls_mle_zero_guerrero_last3 | 0.659201 |
| 10 frames | spline_gcv_taylor2 | 0.971005 |
| 10 frames | pls_mle_ols_tail25_local25 | 1.204729 |
| 10 frames | pls_gcv_ols_tail25_local25 | 1.230195 |
| 10 frames | pls_mle_ols_tail25_guerrero_last3 | 1.422168 |
| 10 frames | savgol21_taylor2 | 1.481177 |
| 10 frames | pls_gcv_ols_global_guerrero_last3 | 3.138274 |
| 10 frames | pls_gcv_oracle_guerrero_last3 | 3.237442 |
| 10 frames | pls_gcv_zero_guerrero_last3 | 3.271087 |
| 10 frames | pls_gcv_ols_tail25_guerrero_last3 | 3.404273 |
| 10 frames | pls_mle_sample_guerrero_last3 | 3.900587 |
| 10 frames | pls_gcv_sample_guerrero_last3 | 5.007758 |
| 10 frames | pls_mle_sample_local25 | 7.625005 |
| 10 frames | pls_gcv_sample_local25 | 7.654658 |
| 20 frames | pls_mle_oracle_local25 | 0.859211 |
| 20 frames | pls_mle_zero_local25 | 0.860666 |
| 20 frames | pls_gcv_zero_local25 | 0.926348 |
| 20 frames | pls_gcv_oracle_local25 | 0.960777 |
| 20 frames | raw_local_quad25 | 0.983741 |
| 20 frames | pls_mle_ols_global_local25 | 1.016356 |
| 20 frames | pls_gcv_ols_global_local25 | 1.072020 |
| 20 frames | pls_mle_oracle_guerrero_last3 | 1.511995 |
| 20 frames | pls_mle_ols_global_guerrero_last3 | 1.586163 |
| 20 frames | pls_mle_zero_guerrero_last3 | 1.639231 |
| 20 frames | spline_gcv_taylor2 | 2.170480 |
| 20 frames | pls_mle_ols_tail25_local25 | 3.265454 |
| 20 frames | pls_gcv_ols_tail25_local25 | 3.307205 |
| 20 frames | savgol21_taylor2 | 3.712452 |
| 20 frames | pls_mle_ols_tail25_guerrero_last3 | 3.905138 |
| 20 frames | pls_gcv_ols_global_guerrero_last3 | 9.820897 |
| 20 frames | pls_gcv_oracle_guerrero_last3 | 10.105294 |
| 20 frames | pls_gcv_zero_guerrero_last3 | 10.189020 |
| 20 frames | pls_gcv_ols_tail25_guerrero_last3 | 10.606123 |
| 20 frames | pls_mle_sample_guerrero_last3 | 14.027073 |
| 20 frames | pls_gcv_sample_guerrero_last3 | 17.551143 |
| 20 frames | pls_mle_sample_local25 | 22.692982 |
| 20 frames | pls_gcv_sample_local25 | 22.751666 |

## Historical known-discrete-jerk RMSE (m/s³)

| Method | RMSE |
| --- | ---: |
| pls_mle_ols_global | 2.917679 |
| pls_mle_oracle | 2.918186 |
| pls_mle_zero | 3.020695 |
| pls_mle_ols_tail25 | 4.083832 |
| pls_mle_sample | 9.495749 |
| savgol21_taylor2 | 36.829147 |
| spline_gcv_taylor2 | 60.913063 |
| pls_gcv_ols_global | 68.082994 |
| pls_gcv_oracle | 68.169064 |
| pls_gcv_zero | 68.242209 |
| pls_gcv_ols_tail25 | 68.270842 |
| pls_gcv_sample | 68.487794 |

## Interpretation and limitations

- Scenarios, noise and policy families were frozen in config.json.
- Future-position target is **clean simulated position**, not a recorded video position.
- Primary jerk target is exactly D3(true position)/dt³, aligned to the PLS finite-difference operator.
- The oracle mu is available ONLY in synthetic trials and may not be used on real NGSIM.
- The pooled mixture weights are constructed by design; results are not traffic-population inference.
- Paired bootstrap intervals condition on this artificial generating process; competing methods/horizons were not multiplicity-adjusted.
- Changing the mu fit generally changes the selected lambda; fixed-S crossings in ablation_rows.csv isolate the fit and continuation effects.
- Retain all failure rows, full known/noisy trajectories and immutable run metadata.
