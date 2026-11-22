# Precision-matrix interpretation across the three active PLS papers

**Date:** 2026-11-22. **Scope:** Source-based mathematical/editorial update only. The three canonical active articles are the Springer empirical complete-criterion paper (\`paper/sections/experiment011_methods.tex\`), unified CSDA theory (\`paper/csda-unified-theory/sections/smoothness.tex\`), and the third-order vehicle-jerk/NGSIM Paper C (\`paper/ngsim-jerk-case-study/sections/methods.tex\`). The independent historical CSDA A/B, SNCS draft and the direct-weights paper were **not** revised.

## Literature and original source checks

Original author-provided full PDFs were inspected (not merely abstract/search results):

- **V. M. Guerrero (2007)**, *Time series smoothing by penalized least squares*, *Statistics & Probability Letters* **77**, 1225–1234, pp. 1229–1230, equations **(21)–(23)**: the fitted trend's precision is the sum of observational and roughness contributions, and Theil's trace provides a *relative* smoothness-precision measure.
- **D. Cortés-Toto, V. M. Guerrero and H. J. Reyes (2017)**, *Trend smoothness achieved by penalized least squares with the smoothing parameter chosen by optimality criteria*, *Communications in Statistics—Simulation and Computation* **46**, 1492–1507, printed pp. **1495–1496**, equations **(9), (13)–(16)**: variance-ratio trend fit, covariance/precision matrices, original normalized-by-\`n\` index and its finite-\`n\` limit. The trace construction derives from earlier work; no novelty is claimed for it.
- The already checked-in BibTeX keys are \`guerrero2007penalized\` / \`cortes2017smoothness\` in Springer and \`guerrero2007\` / \`cortes2017\` in CSDA and Paper C. The original Theil source has **not** been independently checked: attribute it as *Theil-inspired* **through Guerrero and Cortés-Toto**, without introducing an unsupported new citation.

## Mathematical contract and derivation

Let \`1 <= d < n\`, \`r = n-d\`, \`D = D_d\` be full row rank, \`Q=D^T D\`, \`H=(I+lambda Q)^{-1}\` and \`mu\` a specified fixed difference-reference mean. Assume independent Gaussian observation errors \`epsilon\` and difference innovations \`u\` with strictly positive variances \`sigma_e^2\` and \`sigma_u^2\`, such that \`y=tau+epsilon\`, \`D tau=mu 1+u\`, and \`lambda=sigma_e^2/sigma_u^2\`.

The *intrinsic Gaussian* roughness distribution is improper along \`ker D\`; the full data-conditional quadratic form is strictly positive definite:

\`\`\`text
J = sigma_e^(-2) I + sigma_u^(-2) Q = sigma_e^(-2)(I+lambda Q)
P = sigma_u^(-2) Q >= 0
Cov(tau | y, fixed variance parameters and mu) = J^(-1) = sigma_e^2 H
tr(P J^(-1)) / r = [n - tr(H)] / r = S(lambda)
tr(sigma_e^(-2) J^(-1)) + tr(P J^(-1)) = n
S_Guerrero = tr(P J^(-1))/n = (r/n) S
\`\`\`

This is a conditional **posterior** covariance under the intrinsic Gaussian model, not automatically the frequentist covariance of \`tauhat\` for a deterministic unknown trend; estimated \`mu\`, selected \`lambda\`, covariance misspecification, and systematic motion constraints are excluded.

With positive eigenvalues \`delta_j\` of \`Q\`, the spectrum of \`J\` is \`sigma_e^(-2)\` (multiplicity \`d\`) and \`sigma_e^(-2)(1+lambda delta_j)\` (\`j=1,...,r\`). Hence \`kappa_2(J)=1+lambda max(delta_j)\`, and the normalized relative precision is \`r^(-1) sum lambda delta_j/(1+lambda delta_j)\`. The standard historical trace is normalized by \`n\` and tends to \`r/n\` at infinite penalty; the project's rank-normalized trace tends to \`1\`. Scaling **both** standard deviations by the same factor changes absolute precision but not \`S\`.

For physical third differences \`D_3 tau\` sampled at \`Delta t\`, \`j=D_3 tau/(Delta t)^3\` is an approximation of jerk in \`m/s^3\`. The conditional model implies:

\`\`\`text
Cov(j | y, lambda, mu, sigma_e^2, sigma_u^2)
    = D_3 J^(-1) D_3^T / (Delta t)^6
\`\`\`

This does **not** claim that uncertainty bands were computed or empirically calibrated. The real NGSIM data lack independently observed physical jerk, and Paper C's Experiment007 reports correlated-noise misspecification; interval coverage requires a separate study. Do not mix this model-based uncertainty with the observed holdout-position RMSE.

## Manuscript-specific additions

1. **Springer Computational Statistics:** One concise paragraph and two displayed formulas after the PLS/S definition connect \`A_lambda\` to scaled \`J\`, place the original trace normalization next to the normalized coordinate, and explain SVD versus banded factorization. Does not reproduce CSDA's proof or change any Experiment011/013 performance results.
2. **Unified CSDA:** New proposition and proof establish positive definiteness, intrinsic-prior interpretation, conditional covariance, relative-precision and conservation traces. Separate paragraphs describe the spectral eigenvalues and matrix conditioning versus existing computational algorithms; no new algorithms or performance claims.
3. **Paper C:** Concise conditional precision subsection explains the rank-three nullspace, historical normalization, and physically scaled jerk covariance. It explicitly disclaims interval validation and absolute camera sensor precision; keeps 1,296 synthetic jerk cases, 1,944 calibration cells/72 parents, 200 real NGSIM episodes and all negative baseline findings unchanged.

## Verification and handoff

- A **new deterministic regression test** at \`paper/csda-unified-theory/tests/test_precision_matrix.py\` checks arbitrary-order difference matrices, exact normalization, Gaussian posterior/PLS mean equivalence at fixed \`mu\`, trace conservation, physically scaled \`d=3\` jerk covariance symmetry and positive definiteness, and the absolute-precision-vs-relative-smoothness scaling counterexample.
- Run: \`python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_*.py' -v\`; \`python paper/csda-unified-theory/verify_theory.py\`; \`python -m pytest -q\` as available. Existing repository CI should also pass on the PR.
- **PDF status:** The pre-existing tracked compiled manuscripts, visual galleries, source/hash manifests and immutable archive branches remain preserved, but are **not newly compiled by these text commits**. To update distributed PDFs, compile all three *from the exact revised branch SHA* using the established source-only workflow on PCAG103A-08 (or approved comparable journal toolchain); check every PDF page, bibliography, source SHA, and archived checksums. No numerical experiment should rerun.
- **Concurrent PR:** Paper C PR [#152](https://github.com/heri-espino/trendestimation/pull/152) already includes a broader historical normalization/relative-precision treatment, passes its prior checks, but is unmerged and conflicted against contemporary \`main\`. **Do not replace or merge it blindly.** Reconcile its wording and tests with this concise cross-manuscript update, retaining its verified 17-page draft separately until a new source-matched compiled release is approved.
- No journal submission, coauthor approval, new experiment or independent data analysis took place.
