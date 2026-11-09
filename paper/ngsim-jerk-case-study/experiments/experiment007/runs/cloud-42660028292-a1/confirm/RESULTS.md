# Experiment007 confirm: Does PLS smoothness indicate relative noise?

**Cases:** 1944; **selected S values:** 7776;
**invalid selections:** 0.
**Paired interventions:** 6048, clustered at parent innovations.

## Calibration when Gaussian iid jerk and iid measurement assumptions hold

| Selector | Spearman(selected S, theoretical noise fraction) | MAE(S) | Zero-boundary share |
| --- | ---: | ---: | ---: |
| gcv_zero_mu | 0.901 | 0.0249 | 0.0% |
| global_ols_plugin_mle | 0.966 | 0.0143 | 0.0% |
| joint_reml | 0.965 | 0.0115 | 0.0% |
| known_mu_reml | 0.967 | 0.0107 | 0.0% |

## Paired interventions under the model-correct Gaussian iid case

| Selector | Intervention | Mean estimated ΔS | Cluster bootstrap 95% interval | Mean true ΔS |
| --- | --- | ---: | --- | ---: |
| gcv_zero_mu | jerk_variability_increase | -0.1503 | [-0.1691, -0.1325] | -0.1337 |
| gcv_zero_mu | noise_increase | +0.1556 | [+0.1382, +0.1740] | +0.1451 |
| gcv_zero_mu | same_ratio_precision_change | +0.0000 | [+0.0000, +0.0000] | +0.0000 |
| global_ols_plugin_mle | jerk_variability_increase | -0.1457 | [-0.1492, -0.1420] | -0.1337 |
| global_ols_plugin_mle | noise_increase | +0.1568 | [+0.1530, +0.1607] | +0.1451 |
| global_ols_plugin_mle | same_ratio_precision_change | +0.0000 | [-0.0000, +0.0000] | +0.0000 |
| joint_reml | jerk_variability_increase | -0.1387 | [-0.1428, -0.1345] | -0.1337 |
| joint_reml | noise_increase | +0.1498 | [+0.1454, +0.1544] | +0.1451 |
| joint_reml | same_ratio_precision_change | +0.0000 | [-0.0000, +0.0000] | +0.0000 |
| known_mu_reml | jerk_variability_increase | -0.1368 | [-0.1404, -0.1331] | -0.1337 |
| known_mu_reml | noise_increase | +0.1480 | [+0.1436, +0.1519] | +0.1451 |
| known_mu_reml | same_ratio_precision_change | -0.0000 | [-0.0000, +0.0000] | +0.0000 |

## Interpretation

The reference theory is the unconditional covariance-trace fraction.
When both observation and jerk innovation disturbances are iid and Gaussian,
this agrees exactly with Guerrero-style normalized S at the TRUE variance ratio.
Estimated S comes from likelihood/GCV selection and is not guaranteed
unbiased or monotone in finite samples. Results must report departures.
Increasing measurement noise at fixed latent jerk SD should increase true S;
increasing latent jerk variability at fixed observation noise should decrease it.
Scaling BOTH observation and jerk SD by the same factor leaves true S unchanged,
even though absolute observation precision changes. Hence S cannot on its own
measure sensor precision. Correlated noise, endpoint contamination and
nonstationary jerk are deliberately included as model stress tests.

All individual known true jerk, position, observation errors, selected
penalties, lambda, mu, component variance estimates and treatment seeds
are archived with independent source commit, configs and hashes.
