# Experiment005 — completed paired pilot

These results are from a **new experiment** on one hosted Linux environment. Fit error and timing were measured for the **same numerical outputs**. 85-digit references were computed outside the measured runtime.

- 3,264 individual fitted-curve observations.
- 960 complete-grid criterion-selection attempts.
- 1,088 matched reference records.
- Grid: 17 exact normalized smoothness levels including both endpoints and values near one.
- n=32,64; d=2,3,5,6; two reference-mean policies; CV/GCV/AICc/restricted-BIC/marginal ML.

## Complete-workload status

| Backend | Valid selections | Numerically invalid grids | Selected fit inaccurate | Failures |
|---|---:|---:|---:|---:|
| Shift-free SVD | 320 | 0 | 0 | 0 |
| Gram eigendecomposition | 252 | 63 | 5 | 0 |
| Banded Cholesky | 0 | 120 | 0 | 200 |

The failures are **not** included as fast algorithms in any accuracy–time ranking. Full-grid near-one smoothing is a demanding numerical regime.

Across 252 paired, complete, accurate SVD/eigh selections, the median ratio of eigendecomposition to SVD warm time was **1.062**. Ratios are descriptive because the pilot uses one independent seed per scenario and times are host-specific.

Maximum selected-s difference within that paired valid set: 1e-12. Maximum selected true-trend RMSE gap: 1.41e-07.

## Methods and qualifications

The first figure shows reference error against the elapsed time of the same fit. The second counts complete-grid validity, not individual successful candidate values. The third compares latencies only for matched SVD/eigh cases where both are numerically admissible; Cholesky is not ranked because it has no admissible complete-selection cases in this pilot.

This is **historical latent-trend recovery** rather than forecast accuracy. BIC is restricted to S>=0.10 without claiming that this resolves the criterion's statistical pathology. The empirical reference mean is a conditional plug-in, not reestimated LOOCV or joint maximum likelihood.

No confidence intervals are justified by the timing repeats, which are nested within observations. A follow-up with multiple independent random seeds, broader n and additional numerically stable structured algorithms is needed before a publication-quality global accuracy–cost frontier.

## Reproduction

Source: \`paper/benchmarks/experiment005/run_joint.py\`. Raw data are archived under \`paper/benchmarks/experiment005/runs/\` and are not overwritten by this analysis. Rebuild these plots from \`analyze_joint.py\` with the explicit \`--input\` and \`--out\` arguments.
