# Editorial and literature claim audit — 2026-11-04

## Scope and authority

This review polishes the current LaTeX sources of the four primary publication tracks (CSDA spectral accuracy; CSDA computational-cost theory; Springer *Computational Statistics* implementation; and the NGSIM vehicle case study), plus the additional direct-spectral-weights theory draft. It preserves all prior benchmark tables, raw data, figures, experiments, bibliography keys and journal templates. The older SN Computer Science draft is historical and was **not** rewritten.

The companion literature corpus is [heri-espino/Trend-Estimation/literature/extracted](https://github.com/heri-espino/Trend-Estimation/tree/main/literature/extracted), with an index, bibliographies and original PDF locations under `literature/`. The extracted folder currently lists **40 Markdown items**. This pass examined source excerpts and relevant historical audits for the papers directly implicated in the edited claims; it was **not** a line-by-line verification of all 40 extractions. OCR-derived formulas and precise quotations require checking against the original published PDF. No licensed PDFs have been copied into this repository.

## Mathematical corrections applied

| Manuscript | Previous issue | Correction | Validation |
| --- | --- | --- | --- |
| CSDA A, `sections/introduction.tex` | The $S=1$ limit was described universally as a degree-$(d-1)$ polynomial. | For fixed $\mu=0$ the limiting fit has degree at most $d-1$; if $\mu\ne0$ is fixed, the affine constraint $D_d\tau=\mu\mathbf1$ admits degree-$d$ polynomials. | Follows from $D_d\binom{t-1}{d}=\mathbf1$ and the $d$-dimensional nullspace. |
| CSDA B, `sections/decision_examples.tex` | The stated spectral CV leverage $h_i=\sum_k v_{ik}^2/(1+\lambda\delta_k)$ omitted the unpenalized nullspace projector. | $h_i=(H_\lambda)_{ii}=1-\sum_k v_{ik}^2\lambda\delta_k/(1+\lambda\delta_k)$. | $H_\lambda=I-V\operatorname{diag}(w)V^\top$; see `paper/tests/test_spectral_leverage_identity.py`. |
| CSDA A, `sections/introduction.tex` and `sections/discussion.tex` | Unqualified BIC divergence near interpolation. | State the nondegeneracy condition $Q_d(y-p_\mu)\ne0$, under which $\mathrm{RSS}(\lambda)=\lambda^2\|Q_d(y-p_\mu)\|^2+O(\lambda^3)$ and the reported residual-based BIC tends to $-\infty$. | Proof retained in `sections/criteria.tex`; no numerical values changed. |

The CV leverage identity is also important for scientific interpretation: for finite $\lambda$, the $d$ unpenalized polynomial directions are preserved by the smoother. Simply summing the penalized spectral eigenvalues misses those directions.

## Prior art checked against the literature corpus

| Source (extracted filename) | Supported claim | Required limitation |
| --- | --- | --- |
| `Guerrero-2007-time_series_smoothing_penalized_least_squares.md` | Classical PLS and nonzero mean-of-differences formulation; end adjustment and smoothness index. | Do not claim the PLS model itself is new. |
| `Guerrero-2008-estimating_trends_percentage_smoothness.md` | Prescribing percentage smoothness and trace-based interpretation predates these drafts. | The papers' unit-interval normalization is a reparameterization, not an invented smoothing family. |
| `Cortes_Toto-2017-trend_smoothness_optimality_criteria.md` | Study of CV, GCV, AICc and BIC in finite-difference PLS, and the resulting smoothness. | This is not evidence that predictive rolling-origin CV was introduced in the new manuscripts. Extracted mathematical scores should be checked against the original pages before submission. |
| `Weinert-2007-efficient_whittaker_henderson_smoothing.md` | Structure-exploiting fitted-trend and GCV algorithms with favorable computational and memory characteristics. | Do not claim novelty for banded structure or efficient GCV alone. |
| `Biessy-2025-whittaker_henderson_smoothing_revisited.md` | Bayesian/statistical WH framework, marginal-likelihood parameter selection, faster computation and extrapolation; the source discusses GCV profiles with multiple local minima. | First published online 2025; the version supplied for review is identified with the 2026 *ASTIN Bulletin* volume. Avoid claiming the mere existence of multiple minima is new. |
| `Hart-1994-time_series_cross_validation.md` | Kernel bandwidth selection using one-step-ahead time-series cross-validation under dependent errors. | It is a **different** smoothing and forecasting formulation, but predictive smoothing-parameter selection is not new in general. |
| `Islas_Camargo-2019-forecasting_remittances_mexico_rjef.md` | Controlled-smoothness trend filtering followed by a Markov-switching forecasting model for Mexican remittances. | A smoothed trend is not itself a forecasting model. |
| `Islas_Camargo-2025-exchange_rate_predictability_controlled_smoothness.md` | Another application of controlled-smoothness filtering with a separate exchange-rate model. | This paper discusses exponential-smoothing filtering rather than treating every instance as an HP or generic high-order PLS application. |
| `Franke-2026-data_driven_hp_smoothing_parameter.md` | Monte Carlo calibration of HP smoothing against known simulated trends. | Such recovery-error calibration is distinct from forecast-horizon validation. |

Other corpus items and prior repository reviews discuss GCV, smoothing splines, dependent-data CV, forecast evaluation, trend filters and HP alternatives. Their presence in the index is useful for follow-up, but this pass does not certify every individual assertion or bibliographic field.

## Selection-score notation checked against the extracted Cortés-Toto text

The extraction of Cortés-Toto et al. (2017) presents
$\mathrm{AICc}(\lambda)=\log\mathrm{RSS}(\lambda)+(2\nu+1)/(n-\nu-2)$
and $\mathrm{BIC}(\lambda)=\log\mathrm{RSS}(\lambda)-\log n+\nu\log n/n$,
using $\nu=\operatorname{tr}(H_\lambda)$. CSDA A writes AICc with
$\log(\mathrm{RSS}/n)$ instead: this is a $-\log n$ additive constant
independent of $\lambda$, so the selected optimum is unchanged at fixed
$n$. Its residual-BIC expression is algebraically identical to the
extracted formula. Score values may differ across implementations that
use different constants, even when minimizers agree. The publisher PDF
remains the final authority where the extraction may be imperfect.

## Editorial changes

- Replaced grand or unnatural formulations with direct statements of the scientific question, method and limits.
- Reduced repetitions of “we do not claim” without weakening novelty boundaries.
- Separated statements about **arithmetic work**, **measured execution time**, **numerical precision**, **historical trend recovery** and **actual future-position forecasting**.
- Retained the existing numerical values, experimental conditions, formula numbering and citation keys.
- Clarified that Springer timing evidence under different worker contention cannot support an uncontrolled backend ranking.
- Described NGSIM third differences as **estimated jerk proxies** and the fitted local polynomial as an independently appended **forecasting heuristic**.

## Outstanding before submission

1. **Scientific audit, not just copyediting:** Independently verify key derived results and implementation details (especially selected inversion, the Gaussian marginal likelihood normalization, conditional plug-in CV and all endpoint conventions). The small leverage identity test cannot certify the rest of the paper.
2. **Primary-source checks:** Recheck all exact formula references, publication dates and bibliographic fields against publisher PDFs. OCR or text extraction is not sufficient to resolve disputed equations. Visually verify the precise AICc/BIC equations in the publisher PDF; the extracted formulas and their additive normalization relation have now been checked as described above.
3. **Numerical evidence:** CSDA A's 85-digit precision, BIC sensitivity and pilot RMSE numbers remain archived claims. This copyedit did not rerun or independently certify their full original provenance. The CSDA B 48-row BIC illustration has only two repeats.
4. **Springer:** Experiment011's 29-case Windows data are not established by the handoff. Do not publish a cross-criterion performance frontier until matched real observations, numerical checks and independent blocks are archived. Existing Springer text is preliminary and will require a results-driven rewrite.
5. **NGSIM:** Five vehicles and overlapping forecast origins provide a descriptive application, not independent population-level confidence intervals, measured ground-truth jerk or validated vehicle safety predictions.
6. **Direct spectral weights:** The proposed spectral-weight representation is algebraically equivalent to a log-penalty inverse. A distinct novelty search and matched high-precision/runtime experiments are needed before claiming superior numerical performance.
7. **Author/editorial approval:** Verify coauthor order, affiliations, correspondence, contributions, acknowledgments, journal declarations, cover letters and intended submission venue. None is inferred or submitted by this audit.
8. **Publication overlap:** Keep the numerical paper, computational theory, measured Springer implementation and physical application scientifically distinct. Reusing the same estimator is permissible; repeating the same novelty claim across independent submissions is not.

## Reproduction and review

Use the dedicated source branch for editorial changes, compare its diff against `main`, and run:

```powershell
conda activate trendestimation
python -m pytest paper/tests/test_spectral_leverage_identity.py -q
python paper/csda-computational-costs/verify_theory.py
```

Rebuild papers through their existing Elsevier CAS or Springer `sn-jnl` workflows, without silently regenerating benchmark results or rewriting frozen figures. Compare resulting PDFs visually for typographic regressions.

Editorial pass status: **changes proposed for review, not an assertion that all scientific claims across the repository are verified or that any paper is ready to submit**.
