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

- Git revision: \`bc5fc3e40f13a469cd772eba623d7d6de8ba481e\`
- Preset: \`quick\`
- Data seeds: **20** per workload
- Timing blocks per seed: **5**
- BLAS threads requested: **1**
- Python: \`3.11.17\`, NumPy: \`2.4.6\`, SciPy: \`1.17.1\`

## Inferential results

Adjusted tests: **63**; Holm-significant: **57**. A low p-value describes evidence for these measured workloads, not a universal fastest default.

| n | d | M | mu | Comparison A / B | G-mean time ratio A/B | 95% CI (pointwise) | Holm p |
|---:|---:|---:|---:|---|---:|---|---:|
| 32 | 2 | 1 | 0 | svd / eigh | 1.005 | [0.996, 1.012] | 1 |
| 32 | 2 | 1 | 0 | svd / cholesky | 1.552 | [1.541, 1.563] | 0.00126 |
| 32 | 2 | 1 | 0 | eigh / cholesky | 1.545 | [1.533, 1.557] | 0.00126 |
| 32 | 2 | 1 | 0.15 | svd / eigh | 1.004 | [0.997, 1.012] | 1 |
| 32 | 2 | 1 | 0.15 | svd / cholesky | 1.535 | [1.523, 1.548] | 0.00126 |
| 32 | 2 | 1 | 0.15 | eigh / cholesky | 1.529 | [1.516, 1.542] | 0.00126 |
| 32 | 2 | 16 | 0 | svd / eigh | 1.002 | [0.996, 1.008] | 1 |
| 32 | 2 | 16 | 0 | svd / cholesky | 0.672 | [0.669, 0.675] | 0.00126 |
| 32 | 2 | 16 | 0 | eigh / cholesky | 0.670 | [0.667, 0.674] | 0.00126 |
| 32 | 2 | 16 | 0.15 | svd / eigh | 1.001 | [0.995, 1.008] | 1 |
| 32 | 2 | 16 | 0.15 | svd / cholesky | 0.681 | [0.678, 0.685] | 0.00126 |
| 32 | 2 | 16 | 0.15 | eigh / cholesky | 0.680 | [0.676, 0.685] | 0.00126 |
| 32 | 2 | 64 | 0 | svd / eigh | 1.004 | [0.999, 1.009] | 0.9912 |
| 32 | 2 | 64 | 0 | svd / cholesky | 0.421 | [0.419, 0.424] | 0.00126 |
| 32 | 2 | 64 | 0 | eigh / cholesky | 0.420 | [0.418, 0.422] | 0.00126 |
| 32 | 2 | 64 | 0.15 | svd / eigh | 0.996 | [0.990, 1.001] | 0.9912 |
| 32 | 2 | 64 | 0.15 | svd / cholesky | 0.416 | [0.415, 0.418] | 0.00126 |
| 32 | 2 | 64 | 0.15 | eigh / cholesky | 0.418 | [0.416, 0.420] | 0.00126 |
| 96 | 2 | 1 | 0 | svd / eigh | 1.333 | [1.328, 1.339] | 0.00126 |
| 96 | 2 | 1 | 0 | svd / cholesky | 4.259 | [4.242, 4.275] | 0.00126 |
| 96 | 2 | 1 | 0 | eigh / cholesky | 3.194 | [3.182, 3.205] | 0.00126 |
| 96 | 2 | 1 | 0.15 | svd / eigh | 1.321 | [1.314, 1.328] | 0.00126 |
| 96 | 2 | 1 | 0.15 | svd / cholesky | 4.225 | [4.206, 4.244] | 0.00126 |
| 96 | 2 | 1 | 0.15 | eigh / cholesky | 3.198 | [3.185, 3.211] | 0.00126 |
| 96 | 2 | 16 | 0 | svd / eigh | 1.295 | [1.289, 1.300] | 0.00126 |
| 96 | 2 | 16 | 0 | svd / cholesky | 2.083 | [2.071, 2.094] | 0.00126 |
| 96 | 2 | 16 | 0 | eigh / cholesky | 1.609 | [1.599, 1.617] | 0.00126 |
| 96 | 2 | 16 | 0.15 | svd / eigh | 1.299 | [1.294, 1.304] | 0.00126 |
| 96 | 2 | 16 | 0.15 | svd / cholesky | 2.099 | [2.090, 2.108] | 0.00126 |
| 96 | 2 | 16 | 0.15 | eigh / cholesky | 1.616 | [1.611, 1.621] | 0.00126 |
| 96 | 2 | 64 | 0 | svd / eigh | 1.217 | [1.212, 1.223] | 0.00126 |
| 96 | 2 | 64 | 0 | svd / cholesky | 0.959 | [0.955, 0.964] | 0.00126 |
| 96 | 2 | 64 | 0 | eigh / cholesky | 0.788 | [0.785, 0.791] | 0.00126 |
| 96 | 2 | 64 | 0.15 | svd / eigh | 1.216 | [1.210, 1.223] | 0.00126 |
| 96 | 2 | 64 | 0.15 | svd / cholesky | 0.959 | [0.955, 0.963] | 0.00126 |
| 96 | 2 | 64 | 0.15 | eigh / cholesky | 0.788 | [0.786, 0.791] | 0.00126 |
| 192 | 2 | 1 | 0 | svd / eigh | 1.429 | [1.414, 1.443] | 0.00126 |
| 192 | 2 | 1 | 0 | svd / cholesky | 10.146 | [10.050, 10.248] | 0.00126 |
| 192 | 2 | 1 | 0 | eigh / cholesky | 7.102 | [7.055, 7.163] | 0.00126 |
| 192 | 2 | 1 | 0.15 | svd / eigh | 1.409 | [1.404, 1.414] | 0.00126 |
| 192 | 2 | 1 | 0.15 | svd / cholesky | 9.933 | [9.909, 9.958] | 0.00126 |
| 192 | 2 | 1 | 0.15 | eigh / cholesky | 7.050 | [7.025, 7.076] | 0.00126 |
| 192 | 2 | 16 | 0 | svd / eigh | 1.398 | [1.388, 1.408] | 0.00126 |
| 192 | 2 | 16 | 0 | svd / cholesky | 5.666 | [5.638, 5.699] | 0.00126 |
| 192 | 2 | 16 | 0 | eigh / cholesky | 4.053 | [4.037, 4.070] | 0.00126 |
| 192 | 2 | 16 | 0.15 | svd / eigh | 1.389 | [1.384, 1.392] | 0.00126 |
| 192 | 2 | 16 | 0.15 | svd / cholesky | 5.640 | [5.618, 5.663] | 0.00126 |
| 192 | 2 | 16 | 0.15 | eigh / cholesky | 4.061 | [4.047, 4.076] | 0.00126 |
| 192 | 2 | 64 | 0 | svd / eigh | 1.344 | [1.330, 1.359] | 0.00126 |
| 192 | 2 | 64 | 0 | svd / cholesky | 2.614 | [2.595, 2.635] | 0.00126 |
| 192 | 2 | 64 | 0 | eigh / cholesky | 1.945 | [1.928, 1.962] | 0.00126 |
| 192 | 2 | 64 | 0.15 | svd / eigh | 1.342 | [1.332, 1.354] | 0.00126 |
| 192 | 2 | 64 | 0.15 | svd / cholesky | 2.574 | [2.553, 2.599] | 0.00126 |
| 192 | 2 | 64 | 0.15 | eigh / cholesky | 1.918 | [1.904, 1.933] | 0.00126 |
| 96 | 1 | 16 | 0 | svd / eigh | 0.730 | [0.724, 0.738] | 0.00126 |
| 96 | 1 | 16 | 0 | svd / cholesky | 2.194 | [2.172, 2.218] | 0.00126 |
| 96 | 1 | 16 | 0 | eigh / cholesky | 3.006 | [2.988, 3.023] | 0.00126 |
| 96 | 3 | 16 | 0 | svd / eigh | 1.258 | [1.249, 1.267] | 0.00126 |
| 96 | 3 | 16 | 0 | svd / cholesky | 1.704 | [1.689, 1.717] | 0.00126 |
| 96 | 3 | 16 | 0 | eigh / cholesky | 1.354 | [1.349, 1.361] | 0.00126 |
| 96 | 5 | 16 | 0 | svd / eigh | 1.232 | [1.224, 1.241] | 0.00126 |
| 96 | 5 | 16 | 0 | svd / cholesky | 1.159 | [1.153, 1.167] | 0.00126 |
| 96 | 5 | 16 | 0 | eigh / cholesky | 0.941 | [0.936, 0.946] | 0.00126 |

## Publication cautions

The unadjusted bootstrap intervals are provided as descriptive uncertainty summaries; **do not infer multiple-comparison-adjusted significance from whether they cover 1**. The predeclared Holm-adjusted p-values apply only to the primary total-time metric.
The comparisons use identical generated datasets but all timing trials ran on the same machine/session. The randomization test is model-dependent evidence, not a causal guarantee or cross-hardware generalization.
SVD currently remains the default for the original TrendSmoother/criterion-selection API. Backend choice and criterion selection are different computational problems.
