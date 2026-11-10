# Final scientific-methodology manuscript verification

Date: 2026-11-10. Scope: expanded first-order optimality/KKT
derivation and precise documentation of the finite-precision
acceptance test in the official Springer Computational Statistics
article, with current vector figures and publication-style tables.

## Exact source and compiled article

- Canonical LaTeX: paper/main.tex.
- Mathematical methods: paper/sections/experiment011_methods.tex.
- Empirical failure mechanism: paper/sections/experiment011_robustness.tex.
- Bibliography: paper/bibliografia.bib.
- New residual histogram and CSV:
  paper/benchmarks/experiment011/pc08_empirical/kkt001.
- Numerical diagnostic generation, no numerical experiment rerun:
  https://github.com/heri-espino/trendestimation/actions/runs/42768723043
- Successful final official PCAG103A-08 Windows Springer build:
  https://github.com/heri-espino/trendestimation/actions/runs/42769877846
- Immutable PDF artifact branch:
  artifacts/springer-empirical-pc08-42769877846.
- Run-specific compiled PDF:
  paper/builds/pc08/springer-empirical-42769877846/springer.pdf.
- Source revision used by the PDF:
  15349249c1f5bcf518a5e4fd0eabbdc9c79cb28e.
- PDF SHA-256:
  69e5dc84936e1c7a6db4690373cc982baa1e26d5afc614f8006dfa2525751c29.
- PDF size: 808912 bytes; 19 pages.

## Validation

1. Original KKT checker implementation read directly from
   paper/benchmarks/experiment006/selected_inverse.py: residual
   evaluation is after cholesky_banded/cho_solve_banded and before
   selected-inverse/criterion diagnostics. Zero/infinite endpoints
   have separate evaluation paths.
2. Independently established that strict convexity yields
   stationarity as a necessary/sufficient condition. Derived
   and tested r=b-A*tau=-grad(J)/2 and exact error/objective gap.
3. Corrected the term "backward error": the source calls the
   variable backward_error, but it measures a scaled
   first-order optimality residual, NOT the conventional normwise
   backward error. The paper spells out both expressions.
4. 10/10 source-only regression tests passed, including three
   new small deterministic algebra identities. One overstrict
   floating-point eigenvalue equality test was corrected to
   admit actual roundoff while checking positive definiteness.
5. Verified four primary external references and publication
   DOIs: Boyd--Vandenberghe (2004), Higham (2002),
   Golub--Van Loan (2013) and Stellato et al. (2020).
6. Citations rendered in conventional parenthetical author-year
   syntax, with no duplicate author-name strings.
7. Frozen residual figure generated from 92679 timing/status
   rows with 9096 recorded rejected banded cases:
   CV 3384, GCV 4160, MLE 1552; 1401 distinct case-seed
   groups. Min 1.0012664e-7, median 1.4078566e-7,
   max 1.0587341e-6. These are *rejected* method-level
   observations, not independent trials; accepted residual
   values were not collected.
8. Full official latexmk compilation completed, including
   BibTeX: 19 pages, no missing citations or references,
   no TeX errors and no overfull horizontal boxes.
   Three nonfatal underfull boxes were retained.
9. Downloaded the exact run-specific PDF, independently checked
   its SHA-256 against the build manifest and inspection JSON,
   extracted bibliographic citations, and rendered all 19 pages
   to PNGs. Reviewed the complete contact sheet and key KKT
   equations and figure pages; no material clipping or missing
   figure was detected.
10. Published all source changes, tests and derived evidence in
    draft manuscript PR #126, stacked on open handoff PR #124.
    No raw/backup file touched, no large empirical experiment
    restarted, no solver tolerance changed, no PR merged, and
    nothing submitted to the journal.

## Scientific boundaries retained

- Cholesky factorization is mathematically defined because
  A_lambda=I+lambda*D'D is SPD for finite lambda>=0.
  Failure of a *post-solve* acceptance check does not imply
  factorization impossibility.
- The implementation's tolerance 1e-7 is a study-specific
  policy and not a canonical cited numerical-analysis rule.
- Standard normwise backward error has denominator
  ||A|| ||tau|| + ||b||; the source does not use that denominator.
- Residual size alone is not a bound on relative forward
  error. The derived quadratic objective-gap bound uses
  the absolute unscaled residual under exact arithmetic.
- The SVD code does not undergo the identical Cholesky-specific
  KKT check, so status completion cannot demonstrate
  intrinsically better spectral numerical accuracy.
- High-order smoothness-to-lambda inversion can still fail
  for both methods and is a distinct failure stage.
- The spectral method remains recommended for repeated,
  complete-criterion searches within feasible dense-memory
  budgets, and banded methods remain competitive for
  single candidates and larger n.

## Before journal submission

Confirm the full actual author roster and contributions,
corresponding address, funding and competing-interest
declarations, raw experiment data permissions and
publisher submission details. PR #126 remains a draft
and must not be merged or submitted without authorization.
