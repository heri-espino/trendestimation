# Experiment004 — Smoothness-indexed trend selection, RMSE and numerical reliability

**Adopted research scope:** d = 1, 2, 3, 4, 5, 6. **No d=0 cases.**

**Research status (2026-10-29):** The 20-seed RMSE pilot and an independent BIC/high-precision numerical audit are completed and archived on GitHub-hosted Linux. The large computational factorial and the CSDA manuscript rewrite are **not yet authorized by numerical-validity review**. Never silently overwrite archived run directories, merge this draft PR, or run expensive jobs on PCAG103A-08 without clearing these gates.

## Question

When is it statistically and computationally useful to select a finite-difference penalized least-squares trend using normalized smoothness S rather than presenting its internal penalty lambda? Compare true trend-recovery error, criterion choice, robust computation and reuse of precomputed parameter grids. Do not claim that a monotone S reparameterization changes the underlying estimator, its exact optimum or automatically improves runtime.

For 1 <= d < n, the estimated trend minimizes

    ||y-tau||^2 + lambda ||D_d tau - mu 1||^2,

where D_d is the forward difference operator of order d and mu is its reference mean. With Q_d = D_d.T D_d, H=(I+lambda Q_d)^-1 and p_mu[t]=mu binom(t,d), the trend is tau_hat=p_mu+H(y-p_mu).

The normalized index is

    S_d(lambda) = [n - tr(H_lambda)]/(n-d)
                = mean_j lambda delta_j/(1+lambda delta_j).

The n-d positive eigenvalues delta_j depend on n and d. Smoothness targets S=0 and S=1 mean lambda=0 and lambda=infinity, respectively, and the latter is an **exact projection limit**. This index is a normalized version of Guerrero's earlier trace index, not an independently novel statistical estimator.

## RMSE pilot — completed

**Source:** paper/benchmarks/experiment004/run_pilot.py

**Verified GitHub Actions run:** https://github.com/heri-espino/trendestimation/actions/runs/40826487736

**Archived data:** paper/benchmarks/experiment004/runs/pilot-hosted-40826487736/

- n=64,128; d=1,...,6.
- 20 independent seeds for each combination of n, trend shape (smooth/kink), and noise model (iid Gaussian/AR(1)).
- Two reference-mean policies: fixed mu=0 and observed-difference plug-in mu_hat = mean(D_d y). This is not mean(y). Reusing fixed-mu CV/EDF/MLE equations for this observed mean is a **conditional plug-in analysis**, not exact mean-adaptive LOOCV or joint MLE.
- Five criteria: CV, GCV, AICc, RSS-based BIC, and profiled Gaussian marginal MLE.
- 110-point S grid: [0,.01,...,.99,.995,.999,.9995,.9999,.99999,.999999,1-1e-8,1-1e-10,1-1e-12,1].
- Response: **RMSE of fitted historical trend versus known latent truth**, not RSS and not future-forecast RMSE; also in-grid oracle RMSE and oracle S.
- 9,600 criterion-level rows, 12 mapping checks and 192 banded-versus-spectral numerical QA checks. The matched pipeline checks have not certified solver validity at all near-one S targets.

Hosted 192-case numerical QA: 112 agreed at the 1e-5 relative error tolerance, 50 disagreed and 30 Cholesky factorizations failed. These are platform-dependent observed counts, not inferential population proportions. The root-mapping error was ~2.13e-13 in its tested tail metric.

**Interpretation:** notes/experiment004_initial_pilot_findings_20261028.md

## Boundary and high-precision follow-up — completed

**Source:** paper/benchmarks/experiment004/verify_bic_precision.py

**Verified GitHub Actions run:** https://github.com/heri-espino/trendestimation/actions/runs/40828581992

**Archived data:** paper/benchmarks/experiment004/runs/validation-hosted-40828581992/

**Full analysis:** notes/experiment004_bic_highprecision_findings_20261029.md

The published Cortés-Toto et al. (2017) Eq. (21) and implemented BIC both equal

    log(RSS(lambda)/n) + tr(H_lambda)*log(n)/n.

For nondegenerate observations, RSS(lambda) scales as lambda squared near lambda=0 and BIC tends to -infinity. Thus unconstrained optimization has no finite interior global optimum. The original 0.01 winning grid point is a grid-boundary effect, not a generally meaningful optimality finding. A fixed numerical RSS cutoff in the package further alters the extreme near-zero numerical domain. Do not reinterpret the existing BIC score as an automatically well-posed selector over the whole positive penalty domain.

An independent 85-decimal-digit structured **dual** Cholesky solver evaluated 48 high-S cases with n=64,128; d=5,6; two reference-mean policies; and six S values from .9 through 1-1e-12. The reference was checked against the original KKT equations and re-evaluated at 55 and 110 digits on difficult cases. The largest relative error of the standard float64 primal banded Cholesky was ~681.39, with 18 factorization failures; full SVD error was <=3.8e-6 in these *tested configurations*. The outcomes are numerical problem-specific, not general solver rankings.

The independent hosted job stored 224 BIC evaluation rows, 48 high-precision comparison rows, three multiprecision convergence checks, full environment metadata and source checksums. It passed all scientific-quantity assertions. Neither job used the dedicated self-hosted PCAG103A-08 runner.

## Still-open scientific review gates

1. **Criterion interpretation:** characterize any admissible restrictions or substitute model-based information criterion for the degenerate RSS-BIC near interpolation, with an explicit statistical justification. Do not silently change the library's public BIC formula without discussion and tests.
2. **Mean estimation:** distinguish fixed numeric mu from observed-difference plug-in and mathematically derived re-estimated-mu CV or joint MLE. In particular, conditional EDF is not automatically the correct adaptive EDF.
3. **Numerical stability:** test scaled or dual/orthogonalized float64 strategies against independent high-precision references, including d=5,6 and very high S; preserve failures and assess conditioning.
4. **Paired simulation inference:** use independent seeds as sampling units. Assess RMSE uncertainty over new truth/noise scenarios only after the above issues are addressed.
5. **Algorithmic prior-art fairness:** for performance claims include specialized GCV-trace/selected-inverse methods rather than treating a dense identity-column solve as state of the art. Weinert (2007) is indispensable; Garcia (2010) uses different boundary conditions, so a DCT comparison is not automatically the same estimator.

## Deferred performance factorial

After review, compare SVD, dense symmetric eigendecomposition, dense Cholesky at manageable n, general banded, banded Cholesky, and special-purpose structured GCV; n up to 2048 where feasible, d=1,...,6, M=110 S points, and R=1,4,16,64 independent observed series. Separately time cold setup, shared solver, S-to-lambda mapping, reused mapped grid, cached factors and end-to-end whole-workflow cost. The lambda and S comparisons must receive the **same candidate penalties** when claiming matched statistical performance. An independently spaced lambda grid constitutes a different search policy, not a pure implementation benchmark.

Score CV using correctly computed leverage diagonals; GCV, BIC and AICc using EDF and RSS; MLE using its own correctly justified determinant/quadratic or spectral method. Do not charge MLE for unneeded CV operations or allow a failed solver to appear faster because it evaluated fewer candidates. Report measured timings and CPU/BLAS metadata, complete input hashes, data CSVs, numerical validity, paired-seed uncertainty, and AwesomeFigures source with PDF/SVG outputs.

## Existing literature and historical archives

- Prior 17-point grid, 7 solvers, 5 criteria: notes/experiment002_full_s_factorial.md. Its historical d=0 records are **not** part of this Experiment004.
- The 80,640-record Windows benchmark: paper/sections/windows_full_s_results.tex, separate from GitHub-hosted and local studies.
- Experiment003 large-series/cached S workflow: separate PR #82 and experiment003/windows-local branch. Historical results cannot be silently pooled.
- Weinert, H. L. (2007), Efficient computation for Whittaker-Henderson smoothing. https://doi.org/10.1016/j.csda.2006.11.038
- Cortés-Toto, D., Guerrero, V. M. and Reyes, H. J. (2017), Trend smoothness achieved by penalized least squares with the smoothing parameter chosen by optimality criteria. https://doi.org/10.1080/03610918.2015.1005236
- Biessy, G. (2026), Whittaker-Henderson smoothing revisited. https://doi.org/10.1017/asb.2025.10061
- Garcia, D. (2010), Robust smoothing of gridded data in one and higher dimensions with missing values. https://doi.org/10.1016/j.csda.2009.09.020 and 2012 corrigendum https://doi.org/10.1016/j.csda.2011.12.001

**No new manuscript rewrite or larger runner launch before the review gates.**


## 2026-10-29 update — numerical-stability study completed

The **576-case** d=5,6, high-S study is complete and independently reproduced on GitHub-hosted Linux; see
[run 40830375100](https://github.com/heri-espino/trendestimation/actions/runs/40830375100)
and the exact source/data under
paper/benchmarks/experiment004/runs/stable-hosted-40830375100/.
The new note
notes/experiment004_stable_solvers_and_bic_sensitivity_20261029.md
is the authoritative interpretation.

**Adopted default for Experiment004 high-d/high-S numerical validation:**
full spectral SVD **of D itself**, with **shift-free reconstruction** that
avoids materializing the high-degree polynomial reference. Across 576 matched
fits versus the 85-digit independent reference, it completed all comparisons
with maximum relative fit error **5.52e-9**. Scaled QR also completed all 576
cases with maximum error **3.10e-9**. Standard primal banded Cholesky failed in
**216/576** cases and exceeded 1e-5 error in **294 of its 360 completed**
cases. This is a targeted accuracy default, **not** a change to the package's
global fit-only backend or proof of faster runtime.

**BIC methodology:** Retain the mathematical near-S=0 boundary pathology
explicitly. Two descriptive 20-seed restricted searches (identical score,
eligible candidates only) gave mean true-trend RMSE **0.290446** at Smin=0.05
(all 1,920 searches chose that lower bound) and **0.245280** at Smin=0.10
(1,535/1,920 chose the bound). For subsequent **sensitivity analyses**, treat
Smin=0.10 as the provisional restricted BIC configuration, with Smin=0.05 as
a declared sensitivity check. Neither solves the unrestricted BIC pathology.

The large self-hosted-runner factorial remains deferred pending a fair
specialized structured-GCV competitor, explicit conditional-mu conventions,
and a cross-workload backend selection policy.
