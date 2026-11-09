# Experiment006 real: selection and jerk diagnostics

**Models:** 5. **Inner-CV groups:** 6.
**Historical jerk summaries:** 0.

## Smoothing selection and boundaries

| Method | n | lambda→0 | lambda→infinity | Median S |
| --- | ---: | ---: | ---: | ---: |
| fixed_zero_continuous | 200 | 161 | 0 | 0 |
| joint_reml_continuous | 200 | 161 | 0 | 0 |
| joint_reml_grid | 200 | 0 | 0 | 0.05 |
| plugin_global_ols_continuous | 200 | 161 | 0 | 0 |
| plugin_sample_continuous | 200 | 161 | 0 | 0 |

## Nested training-only forecast-shrinkage choices

| Rule | Horizon | alpha=0 | alpha=.5 | alpha=1 |
| --- | ---: | ---: | ---: | ---: |
| shrink_tscv_guerrero_last3 | 5 | 164 | 3 | 33 |
| shrink_tscv_guerrero_last3 | 10 | 167 | 5 | 28 |
| shrink_tscv_guerrero_last3 | 20 | 169 | 12 | 19 |
| shrink_tscv_local25 | 5 | 87 | 36 | 77 |
| shrink_tscv_local25 | 10 | 92 | 35 | 73 |
| shrink_tscv_local25 | 20 | 105 | 48 | 47 |

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
