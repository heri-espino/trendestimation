# Proposed SMCCA manuscript refocus (2026-10-21)

**Suggested title:** trendestimation: Spectral Computation of Penalized Least-Squares Trends Across Difference Orders

**Candidate abstract.** We present trendestimation, a Python implementation
of established finite-difference penalized least-squares smoothers. The
package supports admissible differencing orders, zero and nonzero reference
means of the differences, classical CV/GCV/AICc/BIC parameter selection
for fixed means, and visualization of estimated trends. A reusable spectral
factorization permits efficient repeated evaluation of smoothing-dependent
quantities, while the exact infinite-penalty limit is represented by a
nullspace projection. We describe computational complexity and numerical
conditioning, test against direct linear solves, and illustrate linear
and nonlinear scenarios from Cortés-Toto, Guerrero, and Reyes (2017).
The research contribution is software integration, verified implementation,
and measured performance, not a newly discovered smoothing estimator.

## Proposed article structure

1. Background/provenance: Whittaker-Henderson, Guerrero (2007),
   Cortés-Toto et al. (2017), Weinert (2007), existing Python and R tools.
2. Published PLS problem for any admissible integer order d, fixed
   nonzero mu, and Guerrero observed-difference plug-in.
3. SVD diagonalization, nullspace, normalized smoothness, and exact
   infinite-penalty endpoint. Distinguish fixed versus estimated mu.
4. Classical CV/GCV/AICc/BIC criteria and their exact domain of validity;
   no forecast-horizon-based tuning or future-observation CV.
5. Scientific software design, package API, Sphinx docs, reproducibility.
6. Correctness checks versus direct normal equations, plus predeclared
   time and memory comparisons with BANDed factorization, across n,
   orders and numbers of requested lambda values.
7. Simulation illustrations from the published 2017 paper: linear
   4t/N and nonlinear beta-density mixture; n=50 or 200, Gaussian
   noise sd=0.5 or 2, and optional quarterly seasonality. Label
   all simulated examples honestly.
8. Limitations: equally spaced inputs, high-order conditioning,
   no universal runtime advantage, boundary effects, no forecasting
   performance claims, no exact CV for re-estimated mu.

## Deliberate manuscript boundary

The current numerical-methods paper in
working_papers/Working Paper - Numerical Methods/main.tex
studies forecast-validation objectives, adaptive derivative searches,
Brent, and Sturm root isolation. It was inspected, **not overwritten**.
This software-and-benchmark emphasis is a change in publication
direction and belongs in a separately reviewed manuscript revision.

Published diagonalization, arbitrary d and Guerrero's nonzero mu
are NOT new mathematical discoveries. The reusable package and fair
empirical computation study can be a useful scientific-software
contribution, subject to a literature/software novelty audit.

## Release gate

- Confirm authorship, license, package name on PyPI and version.
- Run the full correctness and conditioning suite on supported Python
  versions and OS environments; build wheel and sdist.
- Benchmark against specialized banded solvers, not just dense inverse.
- Build and inspect Sphinx output; choose Read the Docs or GitHub Pages.
- Keep heavy paper builds and package publishing MANUAL, not push-triggered.
- Do not publish PyPI or deploy public documentation from this draft PR.
