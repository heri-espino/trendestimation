# Completed observed-study evidence snapshot — 3 November 2026

This is the provenance ledger for the Elsevier working manuscript at **paper/csda-computational-costs/main.tex**, especially **sections/experiment010_observed.tex**. It freezes observed results; it is not a claim that the entire proposed factorial was executed. Historical measurements and figures are separately preserved in **SOURCE_AUDIT.md**.

## Mathematical contract

The estimator minimizes the sum of squared observations-to-trend residuals plus lambda times the squared d-th differences around a reference mean. Smoothness S is the normalized trace index, S=(n-tr[(I+lambda D_d^T D_d)^(-1)])/(n-d). It is strictly increasing from zero to one. Exact S=1 means the constrained infinite-penalty limit, not an arbitrary huge finite lambda. All compared methods evaluate the *same* S candidates.

The three mean policies are fixed zero; sample-derived mean(D_d y) recomputed for each input series, which is conditional plug-in rather than jointly estimated; and fixed nonzero 0.15. The five selection scores are CV, GCV, BIC, AICc, and Gaussian marginal likelihood. The full-criterion methods include diagnostics and preprocessing. Guarded SVD/Cholesky is a composite policy rather than a new factorization.

## Corrected Windows results, no fabricated timings

Each branch below is a permanently archived independent GitHub results branch, named by prefix **results/experiment010-** plus the suffix in the first column. All eight outputs ran on Windows university PCAG103A-08 with the existing non-administrator Conda environment. Each result has its source SHA, exact run configuration, original raw time CSVs, status masks, and batch summary.

| Archived suffix | Method–case attempts | OK raw timing rows | Score-only matches | Disagreements | Missing spectral comparator | Failed/partial records |
|---|---:|---:|---:|---:|---:|---:|
| 41587467639-a1-smoke | 30 | 420 | 420 | 0 | 0 | 30 |
| 41587467639-a1-pilot | 60 | 720 | 704 | 16 | 0 | 180 |
| 41587723422-a1-pilot-offset60 | 60 | 680 | 680 | 0 | 0 | 208 |
| 41587723422-a1-pilot-offset120 | 60 | 840 | 840 | 0 | 0 | 60 |
| 41587723422-a1-pilot-offset180 | 60 | 840 | 840 | 0 | 0 | 60 |
| 41587723422-a1-pilot-offset240 | 60 | 840 | 840 | 0 | 0 | 60 |
| 41642508020-a1-frontier-offset0 | 60 | 666 | 664 | 2 | 0 | 222 |
| 41642508020-a1-frontier-offset60 | 60 | 564 | 492 | 0 | 72 | 282 |
| **Total** | **450** | **5570** | **5480** | **18** | **72** | **1102** |

A successful raw time row is a **method/workload/coordinate/repeat observation**, not an independent benchmark problem. Score-only agreement with spectral criteria is not an independent high-precision accuracy certificate. The failure statuses, including missing optional packages and incomplete search grids, have no inferred timing. The comprehensive 50,400-method–case / 403,200-workload planning manifest is not a measured dataset. The corrected pilot cursor is only 300/1800 method–case attempts. The historical 80,640-row Windows corpus is distinct, and its times should not be indiscriminately pooled with these.

Archived first corrected smoke:
https://github.com/heri-espino/trendestimation/tree/results/experiment010-41587467639-a1-smoke

Archived first corrected pilot:
https://github.com/heri-espino/trendestimation/tree/results/experiment010-41587467639-a1-pilot

Four continuation archives: substitute each continuation suffix from the table after the path:
https://github.com/heri-espino/trendestimation/tree/results/experiment010-

Frontier n=256:
https://github.com/heri-espino/trendestimation/tree/results/experiment010-41642508020-a1-frontier-offset0

Frontier n=512:
https://github.com/heri-espino/trendestimation/tree/results/experiment010-41642508020-a1-frontier-offset60

## All ten actual numerical policies, directly comparable example

**n=256, d=1, GCV, mu=0, high amplitude, mapped-lambda from exactly the same S values, one series, median total cold milliseconds, two recorded repetitions.** All values are from the immutable n=256 frontier archive above, in the per-method **summary.csv** of case **n256_d1_gcv_b2ec525e804e**, with original individual **raw_times.csv** alongside.

| End-to-end policy | One S | 100 S |
|---|---:|---:|
| naive_inverse | 9.74 | invalid / not a complete timing |
| spectral_svd | 13.80 | 26.68 |
| banded_cholesky | 8.13 | 61.31 |
| guarded_svd_cholesky | 8.26 | 58.85 |
| banded_lu_banded_trace | 8.55 | 63.38 |
| sparse_lu_banded_trace | 9.71 | 72.89 |
| sparse_cholesky_banded_trace | optional CHOLMOD unavailable | optional CHOLMOD unavailable |
| pcg_fft_banded_trace | 9.09 | 73.63 |
| pcg_dst_banded_trace | 8.30 | 79.87 |
| pcg_jacobi_banded_trace | 8.39 | 147.84 |

The reported winner reversal, Cholesky for one S versus spectral SVD for 100 S, was also observed at fixed mu=0.15 and the sample-derived mu policy at n=256,d=1 and GCV. These two-repetition results do not establish a universal or statistically calibrated crossover.

## Initial likelihood error and independently archived correction

Original pre-correction pilot:
https://github.com/heri-espino/trendestimation/tree/results/experiment010-41586066141-a1-pilot

Initial selected-score disagreements: 104, of which 100 were n=64,d=5, mu=data, MLE. Missing finite-penalty banded/hybrid/naive normalization term: logdet(D_d D_d^T). That term was retained by spectral likelihood and exact S=1, so comparing endpoints and finite penalties used inconsistent scales. Fixed scoring and analytic log-gamma determinant identity are committed on the Experiment010 branch. Corrected pilot disagreements: 16, all involving high-order naive inversion. Preserve pre- and post-correction archives independently; never pool their MLE criterion values as though they were identical.

Mathematical and numerical audit:
https://github.com/heri-espino/trendestimation/blob/research/experiment010-multibackend-frontier-design/notes/experiment010_mle_normalization_audit.md

## Separate 85-digit fitted-trend accuracy evidence

Experiment006 independent n=128, d=5/6, mu=0.15, 28 tests per method: shift-free spectral SVD 28/28 accurate; banded Cholesky 16/28; sparse LU 22/28; FFT-PCG 14/28 accepted and 14 convergence rejects. This is a different fit-only high-precision audit: it does not automatically certify Experiment010 full-criterion rows or establish runtime rankings. Experiment006 high-d source branch: **results/experiment006-highd-41439239921**.

## What remains unestablished

This snapshot does not prove an all-method machine-calibrated theoretical runtime frontier; held-out balanced crossover prediction; selected-method regret; fallback costs; exact re-estimated-mean CV; a high-precision certificate for every high-order complete-grid criterion; nor feasible dense computation at n=16384 or 131072. The sample-derived mean is a plug-in. Classical CV is not rolling-origin forecasting. The Gaussian marginal likelihood has assumptions and residual BIC has an interpolation-boundary issue. Optional CHOLMOD was unavailable on the university runner.

The empirical study is complete **within the observed scope** for an honest, traceable research manuscript, not ready for journal submission until source PDF validation and both authors approve declarations and authorship.

## Reproduction without rerunning expensive Windows experiments

The paper uses the existing author-provided Elsevier CAS v2.4 template and existing AwesomeFigures PDF/PGF/SVG assets. Compile paper/csda-computational-costs/main.tex after copying CAS template files from paper/els-cas-templates. The hosted paper workflow compiles LaTeX and BibTeX only, archives the resulting PDF and source SHA, and **does not rerun Experiment010 computations**. All numerical evidence remains in immutable results branches; no measured timing exists solely in a VM.
