# Experiment007 — Data-derived difference means and solver switching

Research pilot. Full fit-only wall-clock times and numerical forward-error diagnostics; NOT an optimality-criterion benchmark.

## Mean of differences

Primary model policy is mu='data', exactly mean(np.diff(observed_y,n=d)).
The mean of d-th differences of the true, unobserved trend is only an oracle diagnostic in these synthetic experiments; it is NEVER supplied to the fitting solver.
Under zero-mean observation errors, the observed-difference mean is unbiased for the true-trend difference mean, but it can have high variance for higher d.
The old tests used fixed mu=0 or 0.15 for controlled mathematical comparisons. That was useful to isolate the effect of the mean, but not the preferred practical policy.

**Different model:** If mu is defined jointly as mean(D*tau_hat) and optimized along with tau, eliminating mu gives a centered penalty D.T (I-11.T/(n-d)) D, with null-space dimension d+1 instead of d. Its normalized smoothness index would need a new derivation. Do not silently identify this estimator with mu='data'.

## Switching analysis

n = 64,128,256; d = 1,...,6; low and high observation magnitudes; mu='data' primary with mu=0 control; 2 seeds; target S = .2,.5,.75,.9,.95,.99,1. The workflows cross one vs many S with one vs three independently observed series. Methods: spectral SVD, banded Cholesky, sparse LU, FFT-preconditioned PCG.

Every method receives the SAME penalty lambda generated from S. Per-series mu_data is recomputed from that series. Each measured cold time includes backend preparation and all requested fits. This first pilot intentionally excludes S-grid inversion and all CV/GCV/BIC/AICc/MLE diagnostics from fitted-curve timings. A complete criterion timing crossover needs separate correct mu_data-dependent hat matrix definitions.

For n<=128,d>=5,S>=.9 and the first series in each cell, we use an independent 85-digit Python Decimal dual solution and 55-digit precision agreement check. Elsewhere, spectral SVD agreement is only labeled svd_proxy: it is NOT independent numerical truth. No method may be claimed the best based on invalid or proxy-only evidence.

Old evidence: paper/benchmarks/solver_study_runs/pilot-01/analysis/results.md finds n=96,d=2,M=1 SVD/Cholesky timing ratio 4.259, while M=64 ratio 0.959; these were fixed-mu fit-only workloads. The previous small-n high-order 85-digit audit was for a fixed nonzero mu, not actual mu_data. Both show the d-only guarded switch was a provisional safety fallback, NOT an empirically optimized rule.

## Reproduce without administrator privileges

Windows runner: PCAG103A-08, environment trendestimation (NOT trend-estimation), Conda binary under C:\Users\175199\AppData\Local\miniconda3\Scripts\conda.exe. No setup-python, pip install or conda create in the workflow.

Workflow: .github/workflows/experiment007-data-mu-pilot.yml. Run sources: paper/benchmarks/experiment007/run.py; test: tests/test_experiment007_data_mu.py. Seeded outputs raw_times.csv, forward_accuracy.csv, metadata.json are committed automatically on a unique results-only branch when successfully completed.

## Open research questions

1. Is the true-trend difference mean assumed known, estimated from y, or optimized jointly? These are distinct assumptions.
2. Compare measured paired times only among complete numerically valid methods at a given n,d,S,mu and reuse workload. One small pilot cannot certify a global switching boundary.
3. Repeat with >=3 series sizes per fixed factor cell, larger S grids, multiple hardware sessions, independently verified forward errors, and explicit cache/memory accounting before selecting a production auto backend.
4. For data-derived means, classic fixed-mu LOOCV/GCV/AICc/BIC are conditional plug-in scores, not exact refitted-mean criteria. Derive and validate the appropriate data-dependent smoother first.
5. Preserve all experimental evidence and update AGENTS.md and AI_HANDOFF.md after results are reviewed.
