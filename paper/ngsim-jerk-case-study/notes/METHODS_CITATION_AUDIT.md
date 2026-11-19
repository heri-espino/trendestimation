# Paper C — methodological literature and citation audit

**Research-only revision:** 18 November 2026. Manuscript: `paper/ngsim-jerk-case-study/main.tex` and six included sections. Starting source: `main` commit `6502ed5444242a955dfead5c6976cff99676211c`. The purpose is to strengthen *claim-level citations* in the existing 14-page research draft, not to change model definitions, numerical results, experimental datasets, figures, author status or journal submission.

## Diagnostic on the pre-revision paper

- The original bibliography contained **31 BibTeX records** but very few method-section citation commands.
- The original introduction included foundational references; the synthetic, calibration, and NGSIM results sections contained **no formal \cite commands**, despite invoking established statistical and vehicle-data methodologies.
- Retain cited original sources (Guerrero 2007/2008, Cortés-Toto et al. 2017, Weinert 2007, Craven and Wahba 1979, Savitzky--Golay 1964, Biessy 2025 online/2026 volume), and cite them *at the particular claims they support*. Do not erase historical bibliography entries merely because the article has a narrow focus.
- The prior source-backed scientific corrections (conditional plug-in TSVD-GCV, nominal fixed-reference EDF, pooled cumulative forecast RMSE, dependent Experiment007 parents and NGSIM episodes) remain unchanged.

## Added verified bibliographic records and justified uses

| Citation | Primary or bibliographic verification | Legitimate Paper C use | Important limit |
| --- | --- | --- | --- |
| Reinsch (1967), `reinsch1967` | [DOI:10.1007/BF02162161](https://doi.org/10.1007/BF02162161), *Numerische Mathematik* 10:177--183; [Netlib bibliographic record](https://netlib.org/bibnet/authors/r/reinsch-christian-h.html) | Classical smoothing-spline foundation and distinction from third-difference PLS | Does not validate the particular Experiment008 spline penalty tuning or forecast results |
| Wahba (1990), `wahba1990` | [SIAM book DOI:10.1137/1.9781611970128](https://doi.org/10.1137/1.9781611970128) | Observational smoothing splines and smoothing-parameter framework | No assertion that this source investigated NGSIM |
| Hansen (1990), `hansen1990tsvd` | [DOI:10.1137/0911028](https://doi.org/10.1137/0911028), *SIAM Journal on Scientific and Statistical Computing* 11:503--518 | Established TSVD versus Tikhonov-type spectral filtering | Classical inverse-problem TSVD is not the same estimator-selection experiment as our right-singular-vector cutoff of $D_3$ |
| Ye (1998), `ye1998` | [DOI:10.1080/01621459.1998.10474094](https://doi.org/10.1080/01621459.1998.10474094), *JASA* 93(441) | Degrees of freedom and selection-induced adaptivity, conceptual context | Fixed-$\lambda$/rank plug-in trace identities are derived and tested in this repository, not attributed as Ye's formula |
| Efron (2004), `efron2004` | [DOI:10.1198/016214504000000692](https://doi.org/10.1198/016214504000000692), *JASA* 99(467):619--642 | Prediction-error penalties, covariance/df and cross-validation | No suggestion that classical covariance penalties automatically account for all data-dependent tuning |
| Hurvich, Simonoff and Tsai (1998), `hurvich1998` | [DOI:10.1111/1467-9868.00125](https://doi.org/10.1111/1467-9868.00125), *JRSS B* 60(2):271--293 | Corrected Akaike information criterion for smoothing | Does not certify the exact historical Paper C AICc implementation |
| Patterson and Thompson (1971), `patterson1971` | [DOI:10.1093/biomet/58.3.545](https://doi.org/10.1093/biomet/58.3.545), *Biometrika* 58(3):545--554 | Historical restricted likelihood and variance-component estimation | Paper C's joint unknown-$\mu$ REML is a separate derivation for $Dy$ and $DD^T$ |
| Coifman and Li (2017), `coifman2017` | [DOI:10.1016/j.trb.2017.09.018](https://doi.org/10.1016/j.trb.2017.09.018), *Transportation Research B* 105:362--377 | Camera-tracking and NGSIM measurement/data-quality caveats | Does not give independently observed true physical jerk for our 200 episodes |
| Montanino and Punzo (2015), `montanino2015` | [DOI:10.1016/j.trb.2015.06.010](https://doi.org/10.1016/j.trb.2015.06.010), *Transportation Research B* 80:82--106 | Vehicle trajectory reconstruction and traffic-level validation precedent | No implication that a reconstructed trajectory is observed latent ground truth |
| Cerqueira, Torgo and Mozetič (2020), `cerqueira2020` | [DOI:10.1007/s10994-020-05910-7](https://doi.org/10.1007/s10994-020-05910-7), *Machine Learning* 109:1997--2028 | Respecting time series evaluation design when assessing future forecasting | Not a justification for treating repeated NGSIM scenes as independent observations |
| Chartrand (2011), `chartrand2011` | [DOI:10.5402/2011/164564](https://doi.org/10.5402/2011/164564), *International Scholarly Research Notices* | Numerical differentiation under noisy, nonsmooth signals | Does not imply that Experiment008 tested Chartrand's TV regularizer |

The existing bibliography also contained **previously underused relevant sources** that have now been placed near the corresponding discussion: Craven and Wahba (1979) for GCV; Weinert (2007) for discrete Whittaker--Henderson smoothing; Punzo, Borzacchiello and Ciuffo (2011) for NGSIM accuracy; Tashman (2000) for out-of-sample forecasting; Zhu et al. (2024) for alternative event-preserving trajectory processing; and Savitzky--Golay (1964) for local polynomial differentiation.

## Source-to-claim rationale

1. **Introduction:** Cite primary empirical critiques of raw NGSIM positions rather than claiming that withheld camera frames constitute latent physical truth.
2. **PLS equations and normalized $S$:** Cite established regularizers, while explicitly deriving the exact $D_3$ spectral formulas within Paper C.
3. **Gaussian REML versus conditional profile ML:** Cite the general restricted-likelihood precedent, but preserve the crucial distinction between fixed-mean Guerrero-style PLS and a jointly profiled Gaussian nuisance reference.
4. **Effective degrees of freedom and TSVD:** Cite classical df/data selection and inverse-problem spectral filtering, with explicit notice that *conditional* and *plug-in* degrees of freedom are not the complexity of the complete fitted-and-selected algorithm.
5. **Cubic smoothing splines, Savitzky--Golay and noisy derivatives:** Cite original statistical methods rather than relying solely on generic modern comparisons.
6. **Synthetic and calibration experiments:** Cite external theory as methodological context only; the generated trial counts, comparative losses and covariance-based $S$ calibration remain original empirical results.
7. **Real-data evaluation and discussion:** Cite observational-data validation precedents and chronological forecast evaluation without implying independent vehicle-population significance.

## Scientific non-changes and remaining work

**Unchanged:** Experiments004--008; original simulated parent draws, 1,296 synthetic known-jerk trajectories, 1,944 calibration treatments from 72 independent parents, 200 NGSIM episodes, model comparisons, AIC/GCV/REML/TSVD selection implementations, source manifests, figure suite, and frozen original result refs. No parameter was reselected. The spline-Taylor result of 0.3480 m first-second recorded-position window RMSE remains an adverse comparison and is preserved.

**Future checks:** A compiled PDF should be source-matched and visually inspected after LaTeX citation changes. Final claims and citations require coauthor review, bibliographic rights checks if reproducing any external figure (none is added here), venue-specific format and explicit author authorization before journal submission. Additional sources alone cannot fix weak independence, missing physical jerk truth, or inadequate model comparisons.

**Mechanical verification:** Check that every `\citep{...}`, `\citet{...}` and `\citealp{...}` key exists in `references.bib`; check for duplicate BibTeX keys; run paper-related tests and compiled-PDF/reference audits. Do not run any frozen numerical simulation just to test bibliography edits.
