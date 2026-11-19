# Paper C: second selective methodological reference pass (2026-11-19)

**Status:** Research bibliography proposal and source-to-claim map. **Not yet inserted into the compiled manuscript, not a new estimator, and not a new experiment.** This review is based on the current post-PR-144 `main` source (parent commit `a04387ad0b574837a567f417130e804c2a435d28`), its 42-entry bibliography, the six manuscript sections, and publisher/author bibliographic metadata checked on 2026-11-19.

## Why another search, and what to prioritize

Paper C already cites classical Whittaker--Henderson PLS, Guerrero, classical spline smoothing, the REML origin Patterson--Thompson, AICc/GCV, TSVD, noise differentiation, and NGSIM measurement-error studies. Blindly adding citations to each paragraph would be redundant. The major remaining inferential risks are:

1. **Dependence:** Independent Gaussian observation errors underpin the covariance interpretation of normalized smoothness `S`; the completed calibration experiment explicitly finds substantial miscalibration under serial correlation.
2. **Estimated nuisance reference:** The fixed-`mu` profile likelihood is not unknown-`mu` joint REML. General restricted likelihood needs a proper reference for treating fixed-effect estimation, not merely a variance ratio.
3. **Sampling unit:** There are 200 recorded NGSIM episodes but only five coarse recording-time blocks. Their dependence is not solved by increasing the row count or by naive iid episode resampling. The 72 *independent synthetic parent draws* in Experiment007 are an entirely different inferential setting.

## Ranked primary references

### Priority 1: cite when the manuscript source can be recompiled

| Rank | Source | Verified bibliographic locator | Exact claim this supports in Paper C | Important limit |
| --- | --- | --- | --- | --- |
| 1 | Yuedong Wang (1998), *Smoothing Spline Models with Correlated Random Errors*, JASA 93(441), 341--348 | [Publisher DOI 10.1080/01621459.1998.10474115](https://doi.org/10.1080/01621459.1998.10474115); [author's publication list](https://yuedong.faculty.pstat.ucsb.edu/research.html) | Correlated errors affect smoothing-parameter methods; alternative models jointly estimate dependence and smoothness. Add to `precision_calibration.tex` at the transition to Eq. `eq:noise-cov-fraction`, and optionally to `discussion.tex` at the AR(1) calibration limitation. | Wang's model is a **smoothing spline**, not our exact third-difference PLS or an implemented covariance-aware version of `S`. Do **not** claim the covariance-trace formula was derived by Wang. |
| 2 | David A. Harville (1977), *Maximum Likelihood Approaches to Variance Component Estimation and to Related Problems*, JASA 72(358), 320--338 | [Publisher DOI 10.1080/01621459.1977.10480998](https://doi.org/10.1080/01621459.1977.10480998) | Historical theoretical context for *restricted* ML correcting for estimation of nuisance fixed effects. Add next to `patterson1971` in `methods.tex` (smoothing/reference estimation). | The exact unknown-`mu` covariance likelihood in Paper C is separately derived and validated in-repository; do **not** attribute it to Harville. |
| 3 | A. Colin Cameron & Douglas L. Miller (2015), *A Practitioner's Guide to Cluster-Robust Inference*, Journal of Human Resources 50(2), 317--372 | [Publisher DOI 10.3368/jhr.50.2.317](https://doi.org/10.3368/jhr.50.2.317); [university-hosted article](https://escholarship.org/uc/item/1jq5d0pq) | Supports why within-recording dependence and *few effective clusters* restrict generalizable uncertainty. Cite in `real_case.tex` after the five-block statement and in `discussion.tex` when qualifying cross-driver population inference. | Principally regression inference; it **does not** supply valid confidence intervals for the specific 200-episode NGSIM RMSE estimand, especially with only five coarse blocks. Do not report a new p-value or cluster-robust interval. |

### Priority 2: valuable but conditional on how much scope the paper has

| Source | Verified locator | Possible placement | Constraint |
| --- | --- | --- | --- |
| Hans R. Künsch (1989), *The Jackknife and the Bootstrap for General Stationary Observations*, Annals of Statistics 17(3), 1217--1241 | [DOI 10.1214/aos/1176347265](https://doi.org/10.1214/aos/1176347265) | Future-work paragraph on block-aware resampling of genuinely dependent time series | Moving-block bootstrap is built for stationary dependence under conditions; **not** a justification to bootstrap five possibly nonstationary recording blocks, nor a description of the **already completed** Monte Carlo resampling over independent synthetic parents. |
| Paul H. C. Eilers (2003), *A Perfect Smoother*, Analytical Chemistry 75(14), 3631--3636 | [Publisher DOI 10.1021/ac034173t](https://doi.org/10.1021/ac034173t) | Historical finite-difference PLS and Whittaker baseline in `methods.tex`, if a broader origin narrative is wanted | This is established penalized smoothing, not prior evidence about nonzero jerk reference, NGSIM accuracy or the paper's normalized `S` calibration. |

## Publication-ready BibTeX candidates (not in canonical references.bib yet)

```bibtex
@article{wang1998correlated,
  author = {Wang, Yuedong},
  title = {Smoothing Spline Models with Correlated Random Errors},
  journal = {Journal of the American Statistical Association},
  year = {1998}, volume = {93}, number = {441}, pages = {341--348},
  doi = {10.1080/01621459.1998.10474115}
}
@article{harville1977reml,
  author = {Harville, David A.},
  title = {Maximum Likelihood Approaches to Variance Component Estimation and to Related Problems},
  journal = {Journal of the American Statistical Association},
  year = {1977}, volume = {72}, number = {358}, pages = {320--338},
  doi = {10.1080/01621459.1977.10480998}
}
@article{cameronmiller2015,
  author = {Cameron, A. Colin and Miller, Douglas L.},
  title = {A Practitioner's Guide to Cluster-Robust Inference},
  journal = {Journal of Human Resources},
  year = {2015}, volume = {50}, number = {2}, pages = {317--372},
  doi = {10.3368/jhr.50.2.317}
}
@article{kunsch1989,
  author = {K{\"u}nsch, Hans R.},
  title = {The Jackknife and the Bootstrap for General Stationary Observations},
  journal = {The Annals of Statistics},
  year = {1989}, volume = {17}, number = {3}, pages = {1217--1241},
  doi = {10.1214/aos/1176347265}
}
@article{eilers2003,
  author = {Eilers, Paul H. C.},
  title = {A Perfect Smoother},
  journal = {Analytical Chemistry},
  year = {2003}, volume = {75}, number = {14}, pages = {3631--3636},
  doi = {10.1021/ac034173t}
}
```

## Two disciplines, one conceptual warning

**Smoothing / Gaussian covariance estimation:** Independence is a *model assumption*, not a physical property of camera-derived positions. Under the current independent-`epsilon` model, `lambda = sigma_epsilon^2 / sigma_u^2`, and normalized `S` has a relative **spectral covariance-fraction** meaning. Correlated `epsilon` generally changes the covariance eigenstructure and invalidates a scalar-ratio interpretation of arbitrary real error structures. Wang (1998) supports the broad statistical relevance of covariance modeling, **not** a numerical correction within our frozen results.

**Econometrics / hierarchical sampling:** An episode's measurement errors may be serially correlated and episodes sharing the same recording block may be cross-correlated. Even if every episode has an observed forecast loss, an observational count of 200 does not imply 200 iid units. Cameron--Miller (2015) supports the inferential caution, **not** a demonstrated valid 5-cluster method. The synthetic Experiment007 *does* have 72 independent parent draws, correctly preserving 27 paired treatments per parent. That synthetic independence does not transfer to NGSIM.

## Thesis / counterargument / conclusion

- **Thesis:** These primary citations are much more defensible than adding generic recent filtering articles, because each connects to a specific assumption or limitation already discussed.
- **Counterargument:** Citations do not repair model misspecification, establish latent real jerk, guarantee generalizability of the five recording blocks, or transform descriptive RMSE comparisons into population confidence intervals.
- **Conclusion:** Incorporate the top three as *support for model assumptions and limitations*. Reserve Künsch (1989) for a precisely scoped future-evaluation paragraph and Eilers (2003) for historical context only if desired. No new experimental superiority claims.

## Next manuscript-source release procedure

1. Rebase a fresh scoped Paper C branch on live `main`; recheck `AGENTS.md`, `paper/AGENTS.md`, the comprehensive handoff, and open PRs.
2. Add the **three priority** records to `references.bib` and insert carefully limited `\\citep{}` calls in the indicated source paragraphs. Add the two conditional references *only* if corresponding text is genuinely included.
3. **Do not** run Experiments004--008 or regenerate source-backed AwesomeFigures assets for this citation change.
4. Use the **existing guarded, manual-only** `.github/workflows/paper-c-manuscript-pc08.yml` on the scoped branch. It creates an immutable results archive without silently changing `main`. Do not add automatic push triggers.
5. Inspect every updated PDF page and the BibTeX log. Ensure zero undefined citations, and explicitly check the new line/page wrapping.
6. Commit the actual source-matched compiled `main.pdf`; update the 16-entry `publication_sha256.txt` using the *canonical committed file bytes*, not Windows CRLF working-tree hashes. Preserve the pre-atlas historical checksum inventory.
7. Run the SHA checker and Paper C publication-maintenance regression tests, Python 3.10/3.12 CI and docs checks. Merge only a conflict-free, verified PR; confirm post-merge CI.

## Provenance boundaries

Source titles, DOIs, dates and the scoped abstracts/conclusions were checked against publisher, university author, institutional or scholarly bibliographic metadata on 2026-11-19. **This is not a full-text systematic review.** No PDF was copied, redistributed or committed. No numeric experiment, simulation seed, data, figure, renderer, manuscript or active published-source checksum was changed in this documentation-only step. The finished first citation pass remains [PR #144](https://github.com/heri-espino/trendestimation/pull/144).
