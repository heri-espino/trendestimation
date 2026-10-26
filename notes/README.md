# Mathematical research notes

This directory records derivations, mathematical assumptions, boundary cases,
computational decisions, and reproducibility checks for methods explored in
`trendestimation`. Notes do not necessarily imply release-quality implementation
or inclusion in a scientific manuscript.

- [Normalized smoothness as an optimization coordinate](smoothness_parameterization.md):
  proof of monotonicity, inverse map, selection-score chain rule,
  boundary conventions, and a separate joint-likelihood research outlook.

- [Cholesky and banded PLS: provenance and scope](cholesky_prior_art_cortes2017.md):
  what Cortes-Toto et al. (2017) actually say about Weinert's Cholesky
  algorithms, the cited 2012 book, and the distinction between the
  paper's generic banded timing baseline and the library's Cholesky backend.

- [Factorial solver × criterion × search-coordinate study](criterion_coordinate_factorial.md):
  mathematical equivalence of lambda/S search, distinct Cholesky/SVD/eigh
  score workloads, fair matched-candidate design, the actual public
  selector experiment, scripts, statistical cautions and spline outlook.

When changing code or Sphinx documentation, preserve an explanation here
of the underlying mathematical relationship and its limitations.
