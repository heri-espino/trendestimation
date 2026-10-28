# PLS solver backend study — machine-generated analysis

**Interpretation:** findings apply to the sampled series and recorded computing environment, not all machines or problem sizes.

## Pre-specified statistical design

- Methods: SVD of D, symmetric eigendecomposition of D.T @ D, and direct banded Cholesky for exactly the same full PLS trends.
- Primary outcome: wall-clock **setup plus M full fitted trends**, one measurement for each method within the same randomized block.
- Independent inferential unit: data seed. Repeated measurements for the same seed are summarized by their median; neither repeated time blocks nor the M individual penalties are treated as independent observations.
- Pairwise comparisons, for every pre-specified workload: SVD vs eigh, SVD vs Cholesky, eigh vs Cholesky.
- Effect: geometric mean of the per-seed **time(A)/time(B)** ratios. Values >1 indicate that method B is faster; values <1 indicate A is faster. Confidence intervals are seed-level paired percentile bootstrap intervals and are **pointwise, not family-wise adjusted**.
- Hypothesis H0: mean paired log time ratio equals zero. Two-sided paired sign-flip randomization test: exact for <=16 seeds, Monte Carlo otherwise (with plus-one p correction). It assumes exchangeable/symmetric paired log differences.
- Pre-specified family-wise level alpha=0.05; Holm adjustment across **every pair in every workload** for the primary outcome. Secondary timing metrics are descriptive.
- Missing blocks, failed numerical agreement, nonpositive times or incomplete data cause analysis to fail rather than quietly dropping observations.
- Statistical significance is not practical importance; small runtime differences may be irrelevant despite small p-values. Multiple machines, sessions, software versions and independent confirmation are needed for generalizable performance claims.

## Run characteristics

- Git revision: \`2530cf03d2d040b465d13a7e59eb4a8fad887f0d\`
- Preset: \`quick\`
- Data seeds: **20** per workload
- Timing blocks per seed: **5**
- BLAS threads requested: **1**
- Python: \`3.11.17\`, NumPy: \`2.4.6\`, SciPy: \`1.17.1\`

## Inferential results

Adjusted tests: **63**; Holm-significant: **57**. A low p-value describes evidence for these measured workloads, not a universal fastest default.

| n | d | M | mu | Comparison A / B | G-mean time ratio A/B | 95% CI (pointwise) | Holm p |
|---:|---:|---:|---:|---|---:|---|---:|
| 32 | 2 | 1 | 0 | svd / eigh | 1.003 | [0.991, 1.013] | 1 |
| 32 | 2 | 1 | 0 | svd / cholesky | 1.554 | [1.541, 1.568] | 0.00315 |
| 32 | 2 | 1 | 0 | eigh / cholesky | 1.550 | [1.533, 1.568] | 0.00315 |
| 32 | 2 | 1 | 0.15 | svd / eigh | 1.008 | [0.999, 1.017] | 0.5447 |
| 32 | 2 | 1 | 0.15 | svd / cholesky | 1.548 | [1.535, 1.561] | 0.00315 |
| 32 | 2 | 1 | 0.15 | eigh / cholesky | 1.535 | [1.517, 1.550] | 0.00315 |
| 32 | 2 | 16 | 0 | svd / eigh | 1.002 | [0.996, 1.009] | 1 |
| 32 | 2 | 16 | 0 | svd / cholesky | 0.678 | [0.676, 0.682] | 0.00315 |
| 32 | 2 | 16 | 0 | eigh / cholesky | 0.677 | [0.673, 0.682] | 0.00315 |
| 32 | 2 | 16 | 0.15 | svd / eigh | 1.002 | [0.995, 1.009] | 1 |
| 32 | 2 | 16 | 0.15 | svd / cholesky | 0.674 | [0.671, 0.678] | 0.00315 |
| 32 | 2 | 16 | 0.15 | eigh / cholesky | 0.673 | [0.667, 0.678] | 0.00315 |
| 32 | 2 | 64 | 0 | svd / eigh | 1.005 | [1.002, 1.008] | 0.0555 |
| 32 | 2 | 64 | 0 | svd / cholesky | 0.419 | [0.417, 0.421] | 0.00315 |
| 32 | 2 | 64 | 0 | eigh / cholesky | 0.417 | [0.416, 0.419] | 0.00315 |
| 32 | 2 | 64 | 0.15 | svd / eigh | 1.000 | [0.997, 1.004] | 1 |
| 32 | 2 | 64 | 0.15 | svd / cholesky | 0.418 | [0.416, 0.420] | 0.00315 |
| 32 | 2 | 64 | 0.15 | eigh / cholesky | 0.418 | [0.416, 0.419] | 0.00315 |
| 96 | 2 | 1 | 0 | svd / eigh | 1.321 | [1.317, 1.325] | 0.00315 |
| 96 | 2 | 1 | 0 | svd / cholesky | 4.221 | [4.198, 4.242] | 0.00315 |
| 96 | 2 | 1 | 0 | eigh / cholesky | 3.196 | [3.180, 3.211] | 0.00315 |
| 96 | 2 | 1 | 0.15 | svd / eigh | 1.324 | [1.320, 1.329] | 0.00315 |
| 96 | 2 | 1 | 0.15 | svd / cholesky | 4.238 | [4.225, 4.252] | 0.00315 |
| 96 | 2 | 1 | 0.15 | eigh / cholesky | 3.200 | [3.190, 3.211] | 0.00315 |
| 96 | 2 | 16 | 0 | svd / eigh | 1.294 | [1.289, 1.299] | 0.00315 |
| 96 | 2 | 16 | 0 | svd / cholesky | 2.093 | [2.084, 2.101] | 0.00315 |
| 96 | 2 | 16 | 0 | eigh / cholesky | 1.618 | [1.611, 1.625] | 0.00315 |
| 96 | 2 | 16 | 0.15 | svd / eigh | 1.304 | [1.300, 1.308] | 0.00315 |
| 96 | 2 | 16 | 0.15 | svd / cholesky | 2.103 | [2.097, 2.109] | 0.00315 |
| 96 | 2 | 16 | 0.15 | eigh / cholesky | 1.613 | [1.610, 1.616] | 0.00315 |
| 96 | 2 | 64 | 0 | svd / eigh | 1.234 | [1.230, 1.239] | 0.00315 |
| 96 | 2 | 64 | 0 | svd / cholesky | 0.965 | [0.961, 0.970] | 0.00315 |
| 96 | 2 | 64 | 0 | eigh / cholesky | 0.782 | [0.779, 0.786] | 0.00315 |
| 96 | 2 | 64 | 0.15 | svd / eigh | 1.235 | [1.231, 1.238] | 0.00315 |
| 96 | 2 | 64 | 0.15 | svd / cholesky | 0.964 | [0.962, 0.966] | 0.00315 |
| 96 | 2 | 64 | 0.15 | eigh / cholesky | 0.781 | [0.779, 0.783] | 0.00315 |
| 192 | 2 | 1 | 0 | svd / eigh | 1.420 | [1.405, 1.436] | 0.00315 |
| 192 | 2 | 1 | 0 | svd / cholesky | 10.107 | [10.024, 10.197] | 0.00315 |
| 192 | 2 | 1 | 0 | eigh / cholesky | 7.116 | [7.064, 7.178] | 0.00315 |
| 192 | 2 | 1 | 0.15 | svd / eigh | 1.414 | [1.411, 1.417] | 0.00315 |
| 192 | 2 | 1 | 0.15 | svd / cholesky | 10.000 | [9.951, 10.047] | 0.00315 |
| 192 | 2 | 1 | 0.15 | eigh / cholesky | 7.072 | [7.051, 7.093] | 0.00315 |
| 192 | 2 | 16 | 0 | svd / eigh | 1.390 | [1.381, 1.397] | 0.00315 |
| 192 | 2 | 16 | 0 | svd / cholesky | 5.685 | [5.651, 5.723] | 0.00315 |
| 192 | 2 | 16 | 0 | eigh / cholesky | 4.090 | [4.064, 4.120] | 0.00315 |
| 192 | 2 | 16 | 0.15 | svd / eigh | 1.398 | [1.392, 1.405] | 0.00315 |
| 192 | 2 | 16 | 0.15 | svd / cholesky | 5.715 | [5.674, 5.765] | 0.00315 |
| 192 | 2 | 16 | 0.15 | eigh / cholesky | 4.087 | [4.065, 4.112] | 0.00315 |
| 192 | 2 | 64 | 0 | svd / eigh | 1.351 | [1.346, 1.358] | 0.00315 |
| 192 | 2 | 64 | 0 | svd / cholesky | 2.558 | [2.541, 2.573] | 0.00315 |
| 192 | 2 | 64 | 0 | eigh / cholesky | 1.893 | [1.883, 1.901] | 0.00315 |
| 192 | 2 | 64 | 0.15 | svd / eigh | 1.347 | [1.340, 1.353] | 0.00315 |
| 192 | 2 | 64 | 0.15 | svd / cholesky | 2.562 | [2.549, 2.575] | 0.00315 |
| 192 | 2 | 64 | 0.15 | eigh / cholesky | 1.902 | [1.894, 1.910] | 0.00315 |
| 96 | 1 | 16 | 0 | svd / eigh | 0.731 | [0.729, 0.733] | 0.00315 |
| 96 | 1 | 16 | 0 | svd / cholesky | 2.205 | [2.193, 2.216] | 0.00315 |
| 96 | 1 | 16 | 0 | eigh / cholesky | 3.017 | [3.004, 3.030] | 0.00315 |
| 96 | 3 | 16 | 0 | svd / eigh | 1.275 | [1.270, 1.281] | 0.00315 |
| 96 | 3 | 16 | 0 | svd / cholesky | 1.731 | [1.723, 1.742] | 0.00315 |
| 96 | 3 | 16 | 0 | eigh / cholesky | 1.358 | [1.353, 1.363] | 0.00315 |
| 96 | 5 | 16 | 0 | svd / eigh | 1.250 | [1.245, 1.255] | 0.00315 |
| 96 | 5 | 16 | 0 | svd / cholesky | 1.168 | [1.163, 1.174] | 0.00315 |
| 96 | 5 | 16 | 0 | eigh / cholesky | 0.935 | [0.931, 0.939] | 0.00315 |

## Publication cautions

The unadjusted bootstrap intervals are provided as descriptive uncertainty summaries; **do not infer multiple-comparison-adjusted significance from whether they cover 1**. The predeclared Holm-adjusted p-values apply only to the primary total-time metric.
The comparisons use identical generated datasets but all timing trials ran on the same machine/session. The randomization test is model-dependent evidence, not a causal guarantee or cross-hardware generalization.
SVD currently remains the default for the original TrendSmoother/criterion-selection API. Backend choice and criterion selection are different computational problems.
