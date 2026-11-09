# Experiment008: TSVD is a smoothing method, not an SVD solver timing benchmark

**Mode:** synthetic; **matched source windows:** 1296.
Every numeric candidate used only the first 80 historical positions.

| Method | Target | Continuation | Horizon (frames) | RMSE | Units |
| --- | --- | --- | ---: | ---: | --- |
| cubic_spline_gcv | future_clean_position | guerrero_last3 | 5 | 0.869489 | m |
| cubic_spline_gcv | future_clean_position | guerrero_last3 | 10 | 2.134574 | m |
| cubic_spline_gcv | future_clean_position | guerrero_last3 | 20 | 6.596934 | m |
| cubic_spline_gcv | known_jerk |  |  | 60.913063 | m/s^3 |
| cubic_spline_gcv | future_clean_position | local25 | 5 | 0.308191 | m |
| cubic_spline_gcv | future_clean_position | local25 | 10 | 0.461424 | m |
| cubic_spline_gcv | future_clean_position | local25 | 20 | 0.941606 | m |
| pls_profileml_cubic_ols | future_clean_position | guerrero_last3 | 5 | 0.330927 | m |
| pls_profileml_cubic_ols | future_clean_position | guerrero_last3 | 10 | 0.604215 | m |
| pls_profileml_cubic_ols | future_clean_position | guerrero_last3 | 20 | 1.541937 | m |
| pls_profileml_cubic_ols | known_jerk |  |  | 2.441257 | m/s^3 |
| pls_profileml_cubic_ols | future_clean_position | local25 | 5 | 0.272800 | m |
| pls_profileml_cubic_ols | future_clean_position | local25 | 10 | 0.435296 | m |
| pls_profileml_cubic_ols | future_clean_position | local25 | 20 | 1.010690 | m |
| savitzky_golay_21_3 | future_clean_position | guerrero_last3 | 5 | 0.754425 | m |
| savitzky_golay_21_3 | future_clean_position | guerrero_last3 | 10 | 1.427232 | m |
| savitzky_golay_21_3 | future_clean_position | guerrero_last3 | 20 | 3.509015 | m |
| savitzky_golay_21_3 | known_jerk |  |  | 36.829147 | m/s^3 |
| savitzky_golay_21_3 | future_clean_position | local25 | 5 | 0.322056 | m |
| savitzky_golay_21_3 | future_clean_position | local25 | 10 | 0.482451 | m |
| savitzky_golay_21_3 | future_clean_position | local25 | 20 | 0.977509 | m |
| tsvd_gcv_cubic_ols | future_clean_position | guerrero_last3 | 5 | 2.864762 | m |
| tsvd_gcv_cubic_ols | future_clean_position | guerrero_last3 | 10 | 8.069491 | m |
| tsvd_gcv_cubic_ols | future_clean_position | guerrero_last3 | 20 | 26.541590 | m |
| tsvd_gcv_cubic_ols | known_jerk |  |  | 250.718104 | m/s^3 |
| tsvd_gcv_cubic_ols | future_clean_position | local25 | 5 | 0.311336 | m |
| tsvd_gcv_cubic_ols | future_clean_position | local25 | 10 | 0.488903 | m |
| tsvd_gcv_cubic_ols | future_clean_position | local25 | 20 | 1.088313 | m |
| tsvd_matched_edf | future_clean_position | guerrero_last3 | 5 | 0.377840 | m |
| tsvd_matched_edf | future_clean_position | guerrero_last3 | 10 | 0.717041 | m |
| tsvd_matched_edf | future_clean_position | guerrero_last3 | 20 | 1.859503 | m |
| tsvd_matched_edf | known_jerk |  |  | 2.941621 | m/s^3 |
| tsvd_matched_edf | future_clean_position | local25 | 5 | 0.283124 | m |
| tsvd_matched_edf | future_clean_position | local25 | 10 | 0.450206 | m |
| tsvd_matched_edf | future_clean_position | local25 | 20 | 1.033189 | m |

## Interpretation and limitations
- PLS smoothing and TSVD spectral truncation use the SAME d=3 difference basis.
- SVD full factorization alone is NOT a method; hard spectral truncation is.
- TSVD-GCV selects retained rank from training-only in-sample GCV.
- TSVD-matched-EDF uses the PLS archived EDF, so it is NOT an independently
  optimized alternative; it isolates soft versus hard shrinkage at matched complexity.
- The cubic reference mean and PLS lambda were frozen in Experiment006; they
  were NOT re-estimated here. Other methods see the same historical observations.
- True physical jerk is known only for synthetic clean trajectories.
- Real NGSIM future camera-recorded positions are not independent clean truth.
- Same-trajectory overlapping horizons and five coarse recording-session blocks
  do not support population-level independent-sample claims.
- Do not use this as a computational backend/time comparison.
