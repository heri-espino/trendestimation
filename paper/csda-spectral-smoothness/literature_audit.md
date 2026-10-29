# CSDA bibliography expansion — provenance and scope

Date: 2026-10-29.

## Source

The expanded bibliography is drawn from the author's separate historical
repository, **heri-espino/Trend-Estimation** (not the publication repository
heri-espino/trendestimation), in:

- literature/INDEX.md — compact paper index
- literature/manifest.csv — DOI/title/author cross-reference
- literature/extracted/*.md — extracted paper text
- literature/dictionary/state_of_art_and_novelty.md — cautionary prior-art synthesis

The additions below were checked against the extracted abstracts/introduction
or relevant original-material excerpts. Because extraction is imperfect,
critical exact formulas and numerical claims should be verified against
the original PDFs before a final submission. No numerical results, estimates,
or significance claims have been inferred from OCR. The already-cited
Guerrero (2007, 2008), Cortés-Toto et al. (2017), Weinert (2007), and
Biessy (2026) remain the closest direct precedents.

## Literature mapped to manuscript claims

| BibTeX key | Extracted file in older repository | Supported use |
| --- | --- | --- |
| craven1979 | Craven-1979-smoothing_noisy_data_spline_functions.md | Historical smoothing-spline GCV, not new |
| golub1979 | Golub-1979-generalized_cross_validation_ridge.md | Rotation-invariant GCV and ridge penalty calibration |
| eilersmarx1996 | Eilers-1996-flexible_smoothing_b_splines.md | P-splines penalize *basis coefficients*, not the observation-grid operator used here |
| hodrickprescott1997 | Hodrick-1997-postwar_us_business_cycles.md | Economically familiar trend--cycle decomposition using quadratic penalty |
| kim2009 | Kim-2009-l1_trend_filtering.md | Distinct absolute-value trend-difference penalty, piecewise linear trends |
| kitagawa2003 | Kitagawa-2003-smoothness_prior_large_scale_time_series.md | State-space/smoothness-prior interpretation for time series; bibliographic metadata corrected to include Higuchi and Kondo |
| hart1994 | Hart-1994-time_series_cross_validation.md | Kernel smoother TSCV with serially dependent errors and one-step predictive selection, unlike retrospective LOOCV |
| burman1994 | Burman-1994-cross_validatory_dependent_data.md | Block/dependence-aware CV motivation |
| bergmeir2018 | Bergmeir-2018-cross_validation_ar_time_series.md | Conditions for CV with autoregressive time-series prediction |
| tashman2000 | Tashman-2000-out_of_sample_forecast_accuracy.md | Rolling-origin out-of-sample testing distinct from recovery of in-sample trend |
| franke2026 | Franke-2026-data_driven_hp_smoothing_parameter.md | Simulation using known latent trends and choice of HP penalty, not the same normalized spectral framework |
| islaszumaya2025 | Islas_Camargo-2025-exchange_rate_predictability_controlled_smoothness.md | Applied use of controlled-smoothness filtering in an exchange-rate forecasting framework; specifically a different filtering choice |

A strict boundary of relevance was applied. The historical corpus also
contains papers on cryptocurrency risks, equity-premium prediction,
Markov-switching and extensive band-pass filtering. They are not
automatically cited in this paper because the present manuscript is
about PLS trend recovery and numerical stability rather than their
respective empirical claims.

## Editorial decisions

- Avoid falsely claiming invention of GCV, CV, smoothness-index smoothing,
  data-driven HP calibration, structural break modeling, or forecasting
  from a smooth trend.
- Keep the current study's fixed-mean conditional CV separate from
  serial-dependence-aware forecast CV.
- Keep pilot true-trend RMSE separate from future prediction loss.
- Do not interpret restricted BIC as a statistically repaired criterion.
- Retain exact archived Experiment004 numbers; bibliography changes do
  not authorize recomputation or modification of the primary dataset.

All new bibliographic entries are cited in a specific manuscript paragraph,
rather than padding the reference section with uncited papers.
