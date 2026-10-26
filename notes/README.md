# Mathematical research notes

This directory records derivations, mathematical assumptions, boundary cases,
computational decisions, and reproducibility checks for methods explored in
`trendestimation`. Notes do not necessarily imply release-quality implementation
or inclusion in a scientific manuscript.

- [Experiment002: full S=[0,1] × seven solvers × five criteria](experiment002_full_s_factorial.md):
  mathematical endpoint treatment, fixed mu, all difference orders d=0..5,
  numerical stability and undefined-score audits, raw results,
  vector PDF/SVG figures, and future-agent reproduction instructions.

- [Experiment001: solver studies, MLE, and publication figures](experiment001_solver_selection_figures.md):
  central onboarding map of all measured benchmarks, PR history,
  six numerical solvers versus five selection criteria, conditional MLE,
  matched S/lambda grids, reproducible AwesomeFigures vectors, defaults,
  scientific limitations, Windows result provenance and next steps.

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
