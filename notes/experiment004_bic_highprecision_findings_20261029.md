# Experiment004 — BIC boundary pathology and high-precision reference fits

**Date:** 2026-10-29. **Scope:** targeted verification only, n=64/128, d=1,2,5,6 for the BIC audit and d=5,6 for high-precision numerical QA. **No d=0. No self-hosted runner. No new manuscript claims.**

## Research question 1 — is the BIC result a mistake?

No mismatch was found between the **formula implemented** and Cortés-Toto, Guerrero and Reyes (2017), Eq. (21), on PDF page 7:

    BIC(lambda) = log(RSS(lambda)) - log(n) + EDF(lambda)*log(n)/n
                = log(RSS(lambda)/n) + EDF(lambda)*log(n)/n.

The score in `src/trendestimation/criteria.py` evaluates the same mathematical expression, apart from an implementation safeguard for sufficiently small RSS.

For the conditional smoother, write c=y-p_mu, H=(I+lambda Q)^-1, and tau_hat=p_mu+Hc, so

    y-tau_hat = (I-H)c = lambda*Q*c + O(lambda^2),

and, provided Qc != 0,

    RSS(lambda) = lambda^2 ||Q c||^2 + O(lambda^3).

Consequently

    BIC(lambda) = 2 log(lambda) +
                  log(||Q c||^2/n) + log(n) + o(1)
                -> -infinity as lambda -> 0+.

With positive Q spectral eigenvalues, S(lambda) ~ lambda*mean(delta), so equivalently

    BIC(S) = 2 log S + constant + o(1) -> -infinity as S -> 0+.

Thus on an unrestricted positive domain the score does **not** have a finite global minimizer: its infimum is -infinity at the near-interpolation boundary. At the exact S=0 the zero RSS gives log(0), which has no finite BIC value. Assigning +infinity there in the implementation is a pragmatic exclusion, **not** the continuous limiting score.

The package additionally implements an `rss<=eps` cutoff that returns +infinity, creating an artificial numerical exclusion zone. Together with a coarse S grid whose first interior target is .01, this explains the earlier universal BIC selection of S=.01 in the 20-seed pilot. Never infer that this is BIC's intrinsic statistical superiority or inferiority.

**Source nuance:** Cortés-Toto et al. report empirical BIC selection outcomes on their particular numerical optimization setup; they do not provide a global guarantee over arbitrarily small positive penalties. The presence of a published formula does not eliminate the mathematical boundary problem of its unrestricted extension.

## BIC numerical check

A verified seeded synthetic smooth-trend plus iid-noise example, identical to Experiment004's first pilot seed, was evaluated at S values 1e-12, 1e-10, 1e-8, 1e-6, 1e-4, .001, .005, .01, .02, .05, .1, .2, .5, .9. RSS was computed in positive-eigenmode coordinates, avoiding catastrophic subtraction y-tau near interpolation.

| n | d | fixed mu=0: BIC(S=.01) | fixed mu=0: BIC(S=1e-12) |
| ---: | ---: | ---: | ---: |
| 64 | 1 | -7.242 | -53.250 |
| 64 | 2 | -7.047 | -53.054 |
| 64 | 5 | -6.685 | -52.690 |
| 64 | 6 | -6.612 | -52.617 |
| 128 | 1 | -6.197 | -52.196 |
| 128 | 2 | -5.874 | -51.871 |
| 128 | 5 | -5.431 | -51.427 |
| 128 | 6 | -5.348 | -51.344 |

The difference in log score is roughly -46 for a 10^10 decrease in smoothness, consistent with the leading 2 log S term.

**Publication implication:** For reliable selection comparisons, either (a) explicitly constrain the admissible S range and treat its boundary as design-dependent, or (b) replace the BIC specification with a *separately derived* statistically valid marginal-likelihood/model-comparison formulation. A plain RSS-based BIC criterion optimized without restriction must not be treated as a well-posed global smoothing-parameter selection method. Do not silently modify the public BIC API to hide this issue.

## Research question 2 — which solver is wrong near S=1?

Using the same seeded observations as the original pilot, a separate script solves the **dual problem in high precision**:

    (D_d D_d.T + lambda^(-1)I)u = D_d y - mu*1
    tau_ref = y - D_d.T u,

with the exact Toeplitz band identity

    (D_d D_d.T)[i,i+k] = (-1)^k * binom(2d,d-k),

for 0<=k<=d. The reference uses `mpmath` arithmetic with 85 decimal digits, an independently implemented banded Cholesky recursion, and a high-precision KKT residual check for

    tau_ref - y + lambda*D_d.T(D_d*tau_ref - mu*1) = 0.

The float64 S-to-lambda grid and the mean value (including observed difference mean) are frozen at the values actually supplied to the pilot, so this test concerns the **fit for the same inputs**, not the independent accuracy of fitted mu or S inversion.

### Local 48-case numerical verification

48 cases: n=64/128 × d=5/6 × mu in {fixed_zero, observed_difference} × S in {.9,.99,.999,.999999,1-1e-8,1-1e-12}.

| Measure | Full SVD | Ordinary double-precision banded Cholesky |
| --- | ---: | ---: |
| Largest finite relative fit error vs independent high precision | 3.79e-6 | 681.39 |
| Tested fits with relative error >1e-5 | 0 | 24 (of 30 completed) |
| Factorization failures | 0 | 18 |

The high-precision KKT absolute residuals in the original local run were below approximately 3e-47 in these 48 cases. For three difficult (n=128, d=5/6, observed-difference mu) configurations, independently repeating the high-precision solve at 55, 85 and 110 digits produced the same **float64-roundoff-level output**; KKT residuals decreased with the precision.

**Particular outlier:** n=128, d=6, data plug-in mean, S=.99: float64 banded-Cholesky relative error vs the independent reference was about **557.95**, while full SVD error was about **5.66e-7**. This strongly implicates the ordinary primal normal-equation factorization at severe conditioning. Nevertheless, the SVD is not exact at all scales, especially with high-order plug-in reference means; the independent reference is essential.

### Why the reference-mean policy matters

The observed-difference mean is

    mu_hat = mean(D_d y),

not mean(y). For high d, even modest mu_hat multiplies a rapidly growing polynomial reference `mu_hat*binom(t,d)`. Large true high-S fitted values can be **genuine consequences of the statistical model**, not only numerical artifacts. Report scale-invariant relative errors alongside physical fit magnitudes and the true-trend RMSE.

The finding does **not** imply that banded Cholesky is inappropriate in general. It establishes that some direct **primal float64 normal-equation implementations** fail at the tested extreme finite lambda. Specialized scaled/dual methods, suitable factorization strategies, and conditioning-aware fallbacks merit further testing against the high-precision reference.

## Executable reproduction, provenance and next decision

- Earlier 20-seed pilot source: `paper/benchmarks/experiment004/run_pilot.py`, results: `paper/benchmarks/experiment004/runs/pilot-hosted-40826487736/`.
- New source: `paper/benchmarks/experiment004/verify_bic_precision.py`. It writes `bic_small_s.csv`, `high_precision.csv`, `precision_convergence.csv`, and `metadata.json` to a unique run directory.
- Workflow: `.github/workflows/experiment004-validation.yml` uses a **GitHub-hosted** Linux runner, never PCAG103A-08. It checks record counts, BIC boundary behavior, high-precision KKT residuals, and multi-precision reference convergence before committing raw output to the isolated research branch.

**Next scientific gate:** Derive an appropriate restricted or alternative BIC statistical comparison, inspect classical CV with estimated mean (not the fixed-mu shortcut), and add stable high-S solver strategies. Only then benchmark complete score selection and run the large factorial.

**References:** Cortés-Toto, Guerrero and Reyes (2017), https://doi.org/10.1080/03610918.2015.1005236; Weinert (2007), https://doi.org/10.1016/j.csda.2006.11.038; Biessy (2026), https://doi.org/10.1017/asb.2025.10061; Garcia (2010), https://doi.org/10.1016/j.csda.2009.09.020 and associated corrigendum https://doi.org/10.1016/j.csda.2011.12.001.
