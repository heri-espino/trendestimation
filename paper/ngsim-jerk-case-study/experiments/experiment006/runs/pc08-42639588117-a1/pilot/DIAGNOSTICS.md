# Experiment006 synthetic: selection and jerk diagnostics

**Models:** 5. **Inner-CV groups:** 6.
**Historical jerk summaries:** 11.

## Smoothing selection and boundaries

| Method | n | lambda→0 | lambda→infinity | Median S |
| --- | ---: | ---: | ---: | ---: |
| fixed_zero_continuous | 96 | 0 | 13 | 0.9594 |
| joint_reml_continuous | 96 | 0 | 30 | 0.9781 |
| joint_reml_grid | 96 | 0 | 30 | 0.975 |
| plugin_global_ols_continuous | 96 | 0 | 61 | 1 |
| plugin_sample_continuous | 96 | 0 | 0 | 0.8523 |

## True historical finite-difference jerk RMSE

| Method | Horizon (when shrinkage varies) | RMSE (m/s³) |
| --- | --- | ---: |
| plugin_global_ols_continuous | all | 0.179006 |
| shrink_tscv_guerrero_last3 | 5 | 0.190159 |
| shrink_tscv_local25 | 5 | 0.190629 |
| shrink_tscv_guerrero_last3 | 10 | 0.190799 |
| shrink_tscv_guerrero_last3 | 20 | 0.191284 |
| shrink_tscv_local25 | 20 | 0.191649 |
| shrink_tscv_local25 | 10 | 0.192065 |
| joint_reml_continuous | all | 0.195855 |
| fixed_zero_continuous | all | 0.203147 |
| joint_reml_grid | all | 0.214658 |
| plugin_sample_continuous | all | 6.845206 |

## Nested training-only forecast-shrinkage choices

| Rule | Horizon | alpha=0 | alpha=.5 | alpha=1 |
| --- | ---: | ---: | ---: | ---: |
| shrink_tscv_guerrero_last3 | 5 | 25 | 13 | 58 |
| shrink_tscv_guerrero_last3 | 10 | 28 | 12 | 56 |
| shrink_tscv_guerrero_last3 | 20 | 32 | 10 | 54 |
| shrink_tscv_local25 | 5 | 15 | 15 | 66 |
| shrink_tscv_local25 | 10 | 18 | 13 | 65 |
| shrink_tscv_local25 | 20 | 29 | 8 | 59 |

## Interpretation limits

- Mean-adjusted REML is an *in-sample Gaussian* criterion, not a guarantee
  of the smallest future prediction or known-jerk error.
- Lambda=0 is a boundary covariance-model limit; historical trend
  equals raw observations and has no smoothing. An observed frequency
  of zero-boundary selections is substantive, not a numerical omission.
- Exact 15-value grid REML excludes lambda=0 unless explicitly listed;
  continuous REML checks both ends. Inspect both to isolate search effects.
- Nested alpha uses past validation frames only; it changes the
  extrapolation target and is not itself a restricted likelihood.
- Monte Carlo uncertainty is conditional on the frozen synthetic DGP.
- Real NGSIM has no measured true jerk and only five coarse session blocks.
