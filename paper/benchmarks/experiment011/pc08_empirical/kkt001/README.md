# Numerical optimality-residual audit: scientific-methods supplement

The article uses the phrase *scaled first-order optimality residual*
for the diagnostic recorded in the banded Cholesky implementation.
Its internal variable name "backward_error" is historical:
the denominator is max(1, norm(y), norm(y+lambda*mu*D'1)),
not the standard normwise linear-system backward-error denominator
(norm(A)*norm(tau)+norm(b)). The paper explicitly distinguishes the
two concepts and cites Boyd--Vandenberghe (stationarity for strictly
convex problems), Higham and Golub--Van Loan (linear algebra
residual/backward-error analysis), and Stellato et al. (residual-based
acceptance in practical quadratic programming).

## Reproduction

    python paper/benchmarks/experiment011/pc08_empirical/kkt001/render.py

The only data input is the version-locked, immutable long-form
timing tensor (92,679 method-level records). The renderer parses
error strings *as saved* in the original experiment; it does not
evaluate any new smoothing penalties, refit a trend, run a numerical
benchmark, or modify the user’s original and backup source data.

Requirements checked:
- Exactly 9,096 rows have a banded Cholesky post-solve KKT
  exception. The recorded distribution is conditional on failure.
- 3,384 CV, 4,160 GCV, and 1,552 marginal-likelihood failed
  timing observations. They are correlated repeats, not independent
  case-seed observations.
- The saved diagnostic values are all finite and exceed the
  implementation-specific acceptance threshold 1e-7.
- Rejected-row median is ~1.408e-7, maximum ~1.059e-6.
- This does not measure accepted evaluations' residuals or
  establish forward-error superiority of spectral SVD. The
  implementations do not execute identical acceptance gates.

## Outputs

kkt_rejection_distribution.pdf and PNG: stacked histogram of
logged, rejected scaled optimality residuals, colored by
selection criterion (CV/GCV/MLE), with a dashed vertical
acceptance threshold; conditional on rejection only.

criterion_residual_summary.csv: count, median, minimum and maximum
for each criterion. summary.json: source hash, counts,
summary statistics, disclaimer and analysis provenance.

The article must remain focused on scientific methodology,
not Windows VM, internal GitHub Actions jobs, experiment
directory names or agent handoffs. The raw data and all
derived outputs are preserved in the repository, with an
immutable results branch and independent-qa PDF branch.

## Numerical derivation

For fixed mu and lambda, define
A=I+lambda*D'D, b=y+lambda*mu*D'1.
The gradient of J is 2(A*tau-b). Thus the recorded residual
r=b-A*tau is -1/2 of the gradient, and strict convexity makes
its zero necessary and sufficient for optimality.

The exact error is e=-A^{-1}r. Because lambda_min(A)=1
when 1<=d<n, ||e||_2<=||r||_2 and the objective gap equals
r'A^{-1}r<=||r||_2^2. These statements use the *unscaled*
residual and exact arithmetic; the recorded scaled threshold
does NOT by itself certify small relative forward error.

The acceptance test runs after the banded factorization and
linear solve and before selected-inverse calculation and score
evaluation, at finite lambda>0. Endpoints 0 and infinity
are handled via separate branches; smoothness-to-lambda
inversion accuracy and leverage/numerical score validation
are separate failure stages.

## Follow-up

Compile the updated canonical Springer sn-jnl article after
this figure and expanded citation-backed methodology are
committed, run the seven existing tests, inspect rendered
pages and logs, confirm bibliography citations resolve, then
update draft PR #126 without merging or submitting.
