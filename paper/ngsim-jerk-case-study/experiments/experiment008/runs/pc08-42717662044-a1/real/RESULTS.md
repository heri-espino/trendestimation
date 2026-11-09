# Experiment008: TSVD is a smoothing method, not an SVD solver timing benchmark

**Mode:** real; **matched source windows:** 200.
Every numeric candidate used only the first 80 historical positions.

| Method | Target | Continuation | Horizon (frames) | RMSE | Units |
| --- | --- | --- | ---: | ---: | --- |
| cubic_spline_gcv | future_recorded_position | guerrero_last3 | 5 | 0.139289 | m |
| cubic_spline_gcv | future_recorded_position | guerrero_last3 | 10 | 0.494562 | m |
| cubic_spline_gcv | future_recorded_position | guerrero_last3 | 20 | 1.796524 | m |
| cubic_spline_gcv | future_recorded_position | local25 | 5 | 0.340638 | m |
| cubic_spline_gcv | future_recorded_position | local25 | 10 | 0.618417 | m |
| cubic_spline_gcv | future_recorded_position | local25 | 20 | 1.344658 | m |
| pls_profileml_cubic_ols | future_recorded_position | guerrero_last3 | 5 | 0.143409 | m |
| pls_profileml_cubic_ols | future_recorded_position | guerrero_last3 | 10 | 0.514386 | m |
| pls_profileml_cubic_ols | future_recorded_position | guerrero_last3 | 20 | 1.882939 | m |
| pls_profileml_cubic_ols | future_recorded_position | local25 | 5 | 0.354794 | m |
| pls_profileml_cubic_ols | future_recorded_position | local25 | 10 | 0.653222 | m |
| pls_profileml_cubic_ols | future_recorded_position | local25 | 20 | 1.480573 | m |
| savitzky_golay_21_3 | future_recorded_position | guerrero_last3 | 5 | 0.346441 | m |
| savitzky_golay_21_3 | future_recorded_position | guerrero_last3 | 10 | 0.818773 | m |
| savitzky_golay_21_3 | future_recorded_position | guerrero_last3 | 20 | 2.282152 | m |
| savitzky_golay_21_3 | future_recorded_position | local25 | 5 | 0.323725 | m |
| savitzky_golay_21_3 | future_recorded_position | local25 | 10 | 0.593895 | m |
| savitzky_golay_21_3 | future_recorded_position | local25 | 20 | 1.300576 | m |
| tsvd_gcv_cubic_ols | future_recorded_position | guerrero_last3 | 5 | 0.151241 | m |
| tsvd_gcv_cubic_ols | future_recorded_position | guerrero_last3 | 10 | 0.533672 | m |
| tsvd_gcv_cubic_ols | future_recorded_position | guerrero_last3 | 20 | 1.933911 | m |
| tsvd_gcv_cubic_ols | future_recorded_position | local25 | 5 | 0.354797 | m |
| tsvd_gcv_cubic_ols | future_recorded_position | local25 | 10 | 0.653236 | m |
| tsvd_gcv_cubic_ols | future_recorded_position | local25 | 20 | 1.480588 | m |
| tsvd_matched_edf | future_recorded_position | guerrero_last3 | 5 | 0.142340 | m |
| tsvd_matched_edf | future_recorded_position | guerrero_last3 | 10 | 0.511776 | m |
| tsvd_matched_edf | future_recorded_position | guerrero_last3 | 20 | 1.878666 | m |
| tsvd_matched_edf | future_recorded_position | local25 | 5 | 0.354794 | m |
| tsvd_matched_edf | future_recorded_position | local25 | 10 | 0.653223 | m |
| tsvd_matched_edf | future_recorded_position | local25 | 20 | 1.480579 | m |

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
