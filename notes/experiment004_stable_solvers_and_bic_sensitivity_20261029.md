# Experiment004 — Stable double precision and restricted BIC sensitivity

**Completed on 2026-10-29. Difference orders d=1,...,6 only; d=0 excluded.**

This is a reproducible **numerical-correctness** and constrained-criterion study. It is not the expensive solver-runtime factorial, and the CSDA manuscript remains unchanged.

## Reproduction and archived evidence

- Program: paper/benchmarks/experiment004/verify_stable_solvers.py
- High-precision reference: paper/benchmarks/experiment004/verify_bic_precision.py, implementing an 85-decimal-digit dual Toeplitz banded-Cholesky solve
- Original seeded series and mapped S grid: paper/benchmarks/experiment004/run_pilot.py
- **Successful GitHub-hosted run:** https://github.com/heri-espino/trendestimation/actions/runs/40830375100
- **Immutable run-specific directory:** paper/benchmarks/experiment004/runs/stable-hosted-40830375100/
- The directory includes stable_solver_precision.csv (5,184 backend-level comparisons), restricted_bic_rmse.csv (3,840 constrained-BIC selector observations), summary.json with machine metadata and SHA256 hashes, and input/source revision markers.
- The GitHub-hosted Linux job completed its QA assertions and committed all raw data to this isolated research branch. It did **not** run on PCAG103A-08.

## A. BIC small-smoothness issue: retain as scientific observation

Cortés-Toto, Guerrero & Reyes (2017), equation (21), and the existing implementation use the same expression:

    BIC(lambda) = log(RSS(lambda)/n) + EDF(lambda)*log(n)/n.

For fixed mu and nondegenerate observations, RSS(lambda) is asymptotic to lambda² times ||Q(y-p_mu)||² as lambda tends to zero. Consequently, BIC tends to minus infinity for S approaching zero from above; unconstrained global selection has no finite optimum. The library's small-RSS numerical cutoff also restricts the effective numerical search domain. Neither is a reason to silently rename or replace the published formula.

**Sensitivity study, unchanged BIC expression:** keep only S candidates at or above each stated bound, using the same 110-point grid and synthetic series as the original 20-seed pilot. n=64/128; d=1..6; smooth/kink trends; iid/AR(1) noise; 20 seeds per data-generating configuration; mu=0 or conditional observed-difference plug-in mean(D_d@y).

| BIC candidate restriction | Selection rows | Mean historical-trend RMSE | Winners at lower bound | Fixed-mu RMSE | Plug-in mu RMSE |
| --- | ---: | ---: | ---: | ---: | ---: |
| S >= 0.05 | 1,920 | 0.290446 | 1,920 | 0.290446 | 0.290447 |
| S >= 0.10 | 1,920 | 0.245280 | 1,535 | 0.234217 | 0.256343 |

These are **exploratory restricted-BIC policies** and **not** a mathematically repaired, unrestricted BIC. The better average result for 0.10 is specific to this simulation, and 80% of its candidates still choose the imposed lower boundary. The 1,920 records per bound are **paired and correlated**, because many rows reuse the same observed series across difference orders and mean policies. Do not interpret them as 1,920 independent sampling units.

**Provisional choice for the next statistical sensitivity experiment:** report restricted BIC at Smin=0.10 with Smin=0.05 as a control; retain the pathological near-zero behavior explicitly.

## B. 85-digit numerical truth versus nine double-precision solvers

For every tested case we freeze the same float64 observed y, difference reference mean mu and penalty lambda. The independent dual high-precision computation solves:

    (D_d D_d.T + lambda^(-1)*I) u = D_d*y - mu*1,
    tau_ref = y - D_d.T*u.

The Toeplitz dual operator is assembled with exact integer binomial coefficients and solved with 85-decimal-digit banded Cholesky, then checked against the **original PLS optimality equations**. Previous experiments confirmed convergence at 55, 85 and 110 digits.

Factor levels: n={64,128}, d={5,6}, two synthetic truth shapes, iid or AR(1) noise, three independently seeded series per data-generating cell, fixed mu=0 versus observed-difference plug-in, and S={.9,.99,.999,.999999,1-1e-8,1-1e-12}.

This gives **576 matched fits per method**, or **5,184 backend-level numerical observations**. The relative error is ||tau_float64 - tau_high_precision|| / max(1,||tau_high_precision||), **not statistical true-trend RMSE**.

| Double-precision fit procedure | Completed / 576 | Numerical errors > 1e-5 | Largest relative fit error |
| --- | ---: | ---: | ---: |
| Existing full SVD using polynomial reference | 576 | 0 | 3.85e-6 |
| **Full SVD using shift-free spectral evaluation** | **576** | **0** | **5.52e-9** |
| Full SVD using minimum-norm reference | 576 | 0 | 5.52e-9 |
| **Scaled augmented QR (gelsy)** | **576** | **0** | **3.10e-9** |
| Dual SVD | 576 | 0 | 3.69e-8 |
| Scaled augmented SVD (gelsd) | 576 | 12 | 1.57e-5 |
| Dual banded Cholesky | 576 | 302 | 0.122 |
| Primal banded Cholesky | 360 (216 failures) | 294 of completed | 681.39 |
| Symmetric diagonalization of D.T@D | 576 | 484 | 144.55 |

These observations are host-, grid- and data-dependent, not universal algorithm rankings. Numerical failures and wrong finite results are both reported rather than removed.

### Why shift-free SVD is more accurate

Let D=U diag(sigma) V.T denote a full or thin SVD on the n-d positive singular modes, and w=lambda sigma²/(1+lambda sigma²). The same trend estimator can be evaluated as

    tau_hat = y - V [
        w*(V.T@y) - mu*(w/sigma)*(U.T@ones(n-d))
    ].

This is algebraically equivalent to p_mu + H(y-p_mu), but it **does not construct** the potentially enormous polynomial reference p_mu[t]=mu binom(t,d). It also avoids explicitly forming the ill-conditioned Gram matrix D.T@D, which squares the operator singular values. Stable logistic attenuation prevents overflow/underflow in the weight calculation.

For the same high-S cases, an independent alternative solves the **scaled, stacked least-squares** problem

    minimize_tau ||D*tau - mu*1||² + lambda^(-1)*||tau-y||²

by QR factorization of the rectangular matrix [D ; sqrt(1/lambda)*I]. This produced very accurate solutions at the cost of repeating a dense solve for each lambda. It corroborates the SVD result without using the same numerical factorization.

## C. Backend decision — precise scope

**For Experiment004 validation at high d=5,6 and high S, choose FULL SVD of D with the shift-free reconstruction as the default double-precision accuracy baseline.** Keep augmented QR as a second independent stable double-precision comparator and the 85-digit dual solve as the external numerical reference.

**Do not silently change the universal production fit-only library default** from banded Cholesky. For ordinary lower-d or short fit-only workloads banded Cholesky may be much faster, whereas full SVD has O(n³)-class preparation and O(n²) storage. The present study measures numerical accuracy, **not** wall-clock rankings. Future condition-aware fallback rules need independent correctness tests across a broader domain and measured amortized costs.

The trend-recovery RMSE conclusions from Experiment004 remain separate from these solver numerical errors. The observed-difference mu is a conditional plug-in, not correct joint marginal likelihood or exact refitted-mu LOOCV.

## D. Remaining research

- Implement/validate a condition-aware production high-S strategy separately from the research validation baseline.
- For the large factorial, compare matched candidate grids and real complete-workflow timing, including a specialized Weinert (2007) structured GCV-trace baseline; do not promote an incomplete-grid solver as a speed winner.
- Preserve all source revisions, random seeds, true-trend RMSE, numerical failures, scientific criterion definitions, and environment metadata.
- Do not merge PR #83 or rewrite the Elsevier CSDA manuscript merely because these exploratory correctness checks succeeded.

**Primary references:** Cortés-Toto et al. (2017), DOI 10.1080/03610918.2015.1005236; Weinert (2007), DOI 10.1016/j.csda.2006.11.038; Biessy (2026), DOI 10.1017/asb.2025.10061. Prior detailed derivation and KKT checks: notes/experiment004_bic_highprecision_findings_20261029.md.
