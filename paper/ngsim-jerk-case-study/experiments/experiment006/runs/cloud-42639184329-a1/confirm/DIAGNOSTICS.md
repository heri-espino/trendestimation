# Experiment006 synthetic: selection and jerk diagnostics

**Models:** 5. **Inner-CV groups:** 6.
**Historical jerk summaries:** 11.

## Smoothing selection and boundaries

| Method | n | lambda→0 | lambda→infinity | Median S |
| --- | ---: | ---: | ---: | ---: |
| fixed_zero_continuous | 1296 | 0 | 97 | 0.9421 |
| joint_reml_continuous | 1296 | 0 | 304 | 0.9552 |
| joint_reml_grid | 1296 | 0 | 307 | 0.95 |
| plugin_global_ols_continuous | 1296 | 0 | 644 | 0.9745 |
| plugin_sample_continuous | 1296 | 0 | 0 | 0.849 |

## True historical finite-difference jerk RMSE

| Method | Horizon (when shrinkage varies) | RMSE (m/s³) |
| --- | --- | ---: |
| plugin_global_ols_continuous | all | 2.441257 |
| fixed_zero_continuous | all | 2.587379 |
| shrink_tscv_guerrero_last3 | 20 | 3.291527 |
| shrink_tscv_guerrero_last3 | 10 | 3.291671 |
| shrink_tscv_guerrero_last3 | 5 | 3.291746 |
| shrink_tscv_local25 | 20 | 3.291818 |
| shrink_tscv_local25 | 10 | 3.292112 |
| shrink_tscv_local25 | 5 | 3.292494 |
| joint_reml_continuous | all | 3.294994 |
| joint_reml_grid | all | 4.101415 |
| plugin_sample_continuous | all | 7.707732 |

## Nested training-only forecast-shrinkage choices

| Rule | Horizon | alpha=0 | alpha=.5 | alpha=1 |
| --- | ---: | ---: | ---: | ---: |
| shrink_tscv_guerrero_last3 | 5 | 525 | 106 | 665 |
| shrink_tscv_guerrero_last3 | 10 | 575 | 111 | 610 |
| shrink_tscv_guerrero_last3 | 20 | 599 | 113 | 584 |
| shrink_tscv_local25 | 5 | 323 | 172 | 801 |
| shrink_tscv_local25 | 10 | 368 | 189 | 739 |
| shrink_tscv_local25 | 20 | 476 | 178 | 642 |

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
