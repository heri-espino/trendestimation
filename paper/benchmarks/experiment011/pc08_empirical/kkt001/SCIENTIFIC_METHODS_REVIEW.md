# Scientific KKT-methodology revision and provenance

Date: 2026-11-10. Scope: publication-facing mathematical
methods and scientific audit only; no rerun of large experiments.

## Repository source examination

Mandatory original numerical implementation:
paper/benchmarks/experiment006/selected_inverse.py

- The routine fit_stats(y, lam, mu, criterion) builds the finite
  positive-penalty banded Cholesky factor and solves the system.
- After the solve it computes the optimality residual
  r = (y-tau) - lam*D.T*(D*tau-mu), then
  eta = ||r|| / max(1, ||y||, ||y+lam*mu*D.T*1||).
- Rejects on eta>1e-7 or nonfinite solution/diagnostic.
- Its exception calls the scalar "backward_error", but that is
  an implementation variable name: the denominator is NOT
  the normwise linear-system backward-error denominator.
- Only afterward do the selected inverse, effective degrees of
  freedom, leverage deficits and full CV/GCV/AICc/BIC/MLE
  computations occur.
- lambda=0 and lambda=infinity are separate limit cases; the
  1e-7 test concerns finite positive lambda.
- Invalid smoothness-to-lambda inversion is a separate stage.
- The spectral scorer does NOT apply an identical KKT gate.
  Banded failures therefore cannot be used to prove that
  spectral forward accuracy is superior.

## Mathematical basis verified

Define A=I+lambda*D.T*D and b=y+lambda*mu*D.T*1.
The gradient of J is 2(A*tau-b), so the residual in the
source is r=b-A*tau=-grad(J)/2. With n>d and finite
lambda>=0, D has rank n-d, hence A is SPD with
smallest eigenvalue 1. KKT/first-order stationarity is
necessary and sufficient for unique minimization:
  tau* = A^{-1} b.

For any computed tau~:
  e = tau~-tau* = -A^{-1}r,
  J(tau~)-J(tau*) = e' A e = r' A^{-1}r <= ||r||^2,
  ||e|| <= ||r|| (exact arithmetic).
The bounds depend on the absolute/unscaled residual;
eta's implementation-specific denominator does not itself
provide a relative forward-error certificate.

For comparison, a conventional normwise linear-system backward
error takes the form:
  ||b-A*tau~|| / (||A||*||tau~||+||b||).
This is NOT the diagnostic in the recorded experiment.
Do not mislabel the latter as a standard Higham normwise
backward error. The 1e-7 threshold is a reproducible
engineering acceptance policy, not an established default
of the literature. Relative residuals can be affected by
finite-precision cancellation and numerical scaling.

## External references independently checked

- Boyd, S. and Vandenberghe, L. (2004),
  Convex Optimization, Cambridge University Press,
  DOI 10.1017/CBO9780511804441: strictly convex,
  differentiable unconstrained minimization and stationarity.
- Higham, N. J. (2002), Accuracy and Stability of Numerical
  Algorithms, second edition, SIAM, DOI
  10.1137/1.9780898718027: residual size, perturbation theory
  and distinct normwise backward and forward errors.
- Golub, G. H. and Van Loan, C. F. (2013),
  Matrix Computations, fourth edition, Johns Hopkins
  University Press, DOI 10.1137/1.9781421407944:
  linear-system residual, stability and accuracy assessment.
- Stellato, B. et al. (2020), OSQP: an operator splitting
  solver for quadratic programs, Mathematical Programming
  Computation 12:637-672, DOI 10.1007/s12532-020-00179-2:
  examples of thresholded primal/dual optimality residuals.
  Constrained OSQP and our unconstrained PLS use related
  validation principles but DO NOT have identical residuals,
  tolerances or guarantees.

Bibliography entries are included in paper/bibliografia.bib.

## Frozen empirical evidence

KKT figure generator:
paper/benchmarks/experiment011/pc08_empirical/kkt001/render.py

Successful PC08 figure generation:
https://github.com/heri-espino/trendestimation/actions/runs/42768723043

Immutable evidence branch:
results/experiment011-kkt001-42768723043

The renderer read the frozen timing tensor, verified original
hash a25f674981b1c20df678638287df289c4d888ae62417a3f58ed8a6b2a08fce13,
and derived histogram plus count table:
  total timing/status rows: 92,679
  KKT-rejected banded timing rows: 9,096
  CV: 3,384; GCV: 4,160; MLE: 1,552
  distinct failing case-seed groups: 1,401
  eta minimum: 1.0012664e-7
  eta median: 1.4078566e-7
  eta maximum: 1.0587341e-6
  threshold: 1.0e-7 (exact original source)
All these are correlated timing-level observations; the histogram
is conditional on rejection and cannot reveal accepted residuals.
No raw report or original Windows backup has been touched.

## Regression and build

New deterministic source-only unit tests verify the stationarity
identity, objective gap identity and distinction between eta
and conventional normwise backward error:
paper/benchmarks/experiment011/pc08_empirical/test_kkt_methodology.py.

The official PC08 Springer build workflow additionally checks
the new figure, summary, and criterion-level table and runs
all existing and new analysis tests before latexmk. The target
article is the canonical paper/main.tex using sn-jnl.

After the new build, archive and independently verify the
source SHA, PDF SHA-256, new citations, missing references,
overfull boxes, and final rendered pages. The prior compiled
16-page PDF from Actions run 42720035896 does not contain
this methodology expansion. No merge or submission is
authorized; draft PR #126 remains stacked on unmerged #124.
