# Experiment004 — First RMSE and numerical-validity pilot (2026-10-28)

**Status:** Locally executed 20-seed exploratory pilot. No self-hosted runner job launched, no main-paper rewrite, no timing claims. **d=0 excluded** by author decision. The ZIP with the exact execution script and raw result CSVs is presently a conversation attachment and is **not yet committed to this branch**; this distinction is intentional. The local script SHA256 is `25429a88ea98c993f07c64913cd18bfb7c60326082d5d9b9a9a4ce219b229899`.

## Design

- n in {64, 128}, d in {1,2,3,4,5,6}, 2 true-trend shapes (smooth nonlinear; piecewise-linear with kinks), 2 error models (iid Gaussian; AR(1), phi=.65), 20 seeds per (n,shape,noise) combination, 2 mean policies (fixed 0; observed mean of **d-th differences**).
- 5 criteria: conditional LOOCV, GCV, the library's AICc and BIC score formulas, Gaussian profiled marginal likelihood.
- 110 normalized S targets: 0,.01,...,.99,.995,.999,.9995,.9999,.99999,.999999,1-1e-8,1-1e-10,1-1e-12,1. Mapping cached per (n,d); true endpoints handled analytically. Oracle trend RMSE computed on this same grid.
- Historical-trend recovery metric: RMSE against the **known latent trend**. Not residual RMSE, not out-of-sample forecast RMSE.
- 9,600 criterion-level rows; 12 mapping QA cases; 192 numerical QA comparisons (8 selected S targets per n,d,mean). All methods share the same observed y per (n,shape,noise,seed), including across d.

## Exploratory mean latent-trend RMSE

These are descriptive means of correlated and paired observations, **not independent samples for statistical significance** or universal criterion rankings.

| Criterion | mu=0 | mu_hat=mean(D_d y) |
|---|---:|---:|
| CV | 0.174451 | 0.193489 |
| GCV | 0.176647 | 0.194667 |
| AICc | 0.157946 | 0.177608 |
| BIC | 0.297390 | 0.297390 |
| Profiled Gaussian marginal MLE | 0.140633 | 0.178623 |

With fixed zero mu in these simulations, MLE has the lowest average, but the conclusion is scenario- and model-dependent. The plugin mu policy is **conditional**: LOOCV does not refit mu on deletion, EDF does not account for fitting mu, and MLE is not joint mean estimation.

## Numerical validity: important failures

- Max relative tail error in the scalar S-to-lambda inversion: **2.13e-13** (rounded). Scalar inversion accuracy does **not** establish stable trend calculation.
- **192** targeted banded-Cholesky vs full-SVD curve QA checks at S=.01,.5,.9,.99,.999,.999999,1-1e-8,1-1e-12, across n,d,mean. With a 1e-5 relative curve error tolerance: **110 ok, 56 disagreements, 26 factorization failures**.
- For n=128,d=6, plug-in mu and S=.99, spectral vs banded fitted curves differed by ~**558** relative norm; banded factorization failed at S=.999. Near-one validation needs an independent higher-precision reference before attributing error to only one solver. High order and plug-in mean can produce huge polynomial reference values mu_hat*binom(t,d).
- A direct determinant-based marginal likelihood computation showed nontrivial numerical disagreement from the spectral calculation for the difficult d=6, data-plug-in mean cases even for moderate S.
- **BIC audit blocker:** under the current expression log(RSS/n)+EDF*log(n)/n, BIC selected the smallest positive candidate **S=.01 in all 1,920 BIC searches**. The near-interpolating RSS->0 behavior means we must verify the criterion and admissible search domain against Cortés-Toto et al. before using this result as a statement about BIC's statistical merits.

## Interpretation and next gate

This pilot supports studying **numerical conditioning, criterion-domain definitions, and conditional-vs-adaptive mean estimation** before a large timing factorial. It suggests, but does not establish, a CSDA narrative centered on numerical reliability and statistical tradeoffs, with amortized computational costs as a separate contribution.

**Required next actions:** (1) commit/expose the exact runnable source and raw CSV/JSON provenance in a unique GitHub results directory, ideally using a small GitHub-hosted pilot job; (2) reproduce independent formula parity against the package and review the BIC formula; (3) isolate reliable high-S/high-d reference fits before ranking solver timings; (4) review differences between fixed and plug-in mu under exact CV and likelihood assumptions. **Do not start the full self-hosted-runner factorial yet.**

## Literature/precedent

Weinert (2007), DOI 10.1016/j.csda.2006.11.038; Cortés-Toto et al. (2017), DOI 10.1080/03610918.2015.1005236; Biessy (2026), DOI 10.1017/asb.2025.10061; Garcia (2010), DOI 10.1016/j.csda.2009.09.020 and 2012 corrigendum 10.1016/j.csda.2011.12.001.
