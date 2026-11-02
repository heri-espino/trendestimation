# Direct spectral-weight reconstruction — theoretical manuscript

**Status:** independent theorem-driven *working draft*, not a submission.
The mathematical PLS estimator is not new and no direct-weight speedup
has been demonstrated. The paper is distinct from:
- numerical accuracy: paper/csda-spectral-smoothness/
- computational costs: paper/csda-computational-costs/
- paired existing-estimator experiment: paper/benchmarks/experiment005/

**Title:** Direct Smoothness-Constrained Spectral Reconstruction for
Penalized Least-Squares Trends: Exact Equivalence, Endpoint Geometry,
and Nonzero Difference Means.

## Source and authorship

This project builds on the current main-branch implementation
src/trendestimation/smoothness_weights.py and its equivalence tests,
notes/direct_spectral_weights.md, Guerrero (2007, 2008),
Cortés-Toto et al. (2017), and structured smoothing prior art.
Authorship and order are *provisional*; please obtain explicit
coauthor approval before submission. No unpublished licensed PDF
is redistributed.

## Theorems, with proof

1. Full row rank and polynomial nullspace of the forward difference.
2. Strict convexity, unique PLS fit and conditional affine hat matrix.
3. Normalized trace smoothness and monotone penalty bijection.
4. Odds-ratio characterization of all admissible PLS spectral weights.
5. Unique scalar direct-S log-odds root with an analytical finite bracket.
6. Exact full-SVD shift-free fit and both endpoint projections.
7. Sensitivity bounds with exact smoothness-derivative formula.
8. Penalty endpoint asymptotics.
9. Full data-dependent smoother/EDF for observed-difference plug-in mu:
   trace n-rs + sum(w_j * (U.T 1)_j^2)/r.
10. Degenerate r=1 data-mean case (fit is exactly y at all S).
11. A posteriori scalar-root residual bound on fitted-trend error.

Each result is carefully scoped to exact arithmetic, finite full-row-rank
differences and a *fixed* target s. The code may use empirical
mu=mean(D_d y), but the conditional S interpretation and full-data EDF
are different; the draft derives the correction explicitly.

## Build locally

From the repository root (Windows PowerShell):

~~~powershell
Copy-Item paper\els-cas-templates\cas-dc.cls,paper\els-cas-templates\cas-common.sty,paper\els-cas-templates\cas-model2-names.bst -Destination paper\direct-spectral-weights
Push-Location paper\direct-spectral-weights
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
Pop-Location
Start-Process ".\paper\direct-spectral-weights\main.pdf"
~~~

The independent GitHub Actions paper workflow compiles against the
user-provided CAS v2.4 template, archives the PDF and references,
and verifies there are no undefined citations. Edit source in
sections/*.tex; main.tex holds the structure and front matter.

## Novelty and peer-review guardrails

- User-chosen percentage smoothness is prior art (Guerrero).
- The weight/root equation is algebraically a reparameterized
  log-lambda solve, not a closed-form or inversion-free procedure.
- The plug-in EDF theorem is an algebraic identity and is not yet
  claimed as historically novel.
- The a posteriori error certificate only accounts for exact
  scalar-root residual, not inexact SVD, floating-point multiplication,
  or data-dependent selection of S.
- No statistical/physical observations, runtime measurements or
  confidence intervals are reported in this theory-only draft.
- Before considering publication: run distinct Experiment006,
  review direct-weight prior art, verify all numerical corner cases,
  obtain coauthor review, and ensure bibliography is current.

See PROOF_AUDIT.md for checked assumptions and deferred claims.
