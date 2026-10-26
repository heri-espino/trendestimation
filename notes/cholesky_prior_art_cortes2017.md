# Cholesky prior work in discrete PLS and spline smoothing

## Question

Did Cortés-Toto, Guerrero and Reyes (2017) themselves benchmark or use
Cholesky factorization to select the PLS penalty, and which Weinert work
did they cite?

## Source-grounded answer

The article **mentions** Cholesky in its introduction (page 4 of the
paper; extraction section surrounding equation (6)). It attributes
Cholesky-based spline algorithms to **Weinert (2012)** and identifies
the second-difference, zero-reference-mean PLS problem as a discrete
analogue of the continuous cubic-spline problem.

**It does not establish that the authors' own R simulations used a
Cholesky factorization.** Section 3 says the simulations were
implemented in R, and Section 3.2 explicitly states that the authors
implemented CV, GCV, AICc and BIC in the PLS setting, using the
smoothing-matrix trace. That discussion names Weinert's separate
MATLAB implementations and spline routines as background, explaining
why those existing routines were not directly appropriate to the
authors' analysis. Thus a claim that the 2017 experiment measured
Cholesky speed or selected Cholesky as its underlying factorization is
not supported by the cited article.

### Original source

- Daniela Cortés-Toto, Víctor M. Guerrero and Hortensia J. Reyes (2017),
  *Trend smoothness achieved by penalized least squares with the
  smoothing parameter chosen by optimality criteria*,
  **Communications in Statistics – Simulation and Computation** 46(2),
  1492–1507. DOI:
  <https://doi.org/10.1080/03610918.2015.1005236>.
- Author-maintained full-text extraction:
  <https://github.com/heri-espino/Trend-Estimation/blob/main/literature/extracted/Cortes_Toto-2017-trend_smoothness_optimality_criteria.md>.
- Its extracted reference list identifies: **Weinert, H. (2012).**
  *Fast Compact Algorithms and Software for Spline Smoothing*.
  SpringerBriefs in Computer Science, Springer.

### Verified Weinert sources

1. Howard L. Weinert (2012 electronic publication, Springer copyright
   2013), *Fast Compact Algorithms and Software for Spline Smoothing*.
   SpringerBriefs in Computer Science, Springer.
   DOI: <https://doi.org/10.1007/978-1-4614-5496-0>.
   The Springer catalog lists publication of the electronic edition on
   12 October 2012 and copyright 2013. Its chapters explicitly cover
   Cholesky (pp. 5–18), QR (pp. 19–28), FFT (pp. 29–35), and discrete
   spline smoothing (pp. 37–45). The abstract describes MATLAB
   implementations and comparison of runtime, memory, and accuracy.
2. Howard L. Weinert (2007), *Efficient computation for
   Whittaker–Henderson smoothing*,
   **Computational Statistics & Data Analysis** 52(2), 959–974.
   DOI: <https://doi.org/10.1016/j.csda.2006.11.038>.
   It develops structured computation of smoothing estimates and
   GCV quantities, predating the 2017 comparison.

**Do not conflate** the two Weinert references: Cortés-Toto et al.
explicitly cite the *2012 book*, while the 2007 journal article is
separate relevant prior art. Neither provides evidence that our
implementation invented Cholesky smoothing.

## Algebra and reproducible implementation distinction

Let `D_d` be the order-`d` forward-difference matrix,
`Q_d = D_d.T @ D_d`, `lambda >= 0` finite, and a fixed `mu`.
Then the normal equations for the same PLS estimator are

```text
A_lambda = I + lambda * Q_d
A_lambda * tau = y + lambda * mu * D_d.T @ ones(n-d)
```

For nonzero `x`,

```text
x.T @ A_lambda @ x = ||x||_2^2 + lambda * ||D_d @ x||_2^2 > 0.
```

Hence `A_lambda` is symmetric positive definite, and its band
half-width is `d`. A banded Cholesky method can factor
`A_lambda = L_lambda @ L_lambda.T`, then solve triangular systems.
For a changed positive `lambda`, the factor generally changes.
This differs from the reusable SVD projection used for evaluating
many candidates.

The paper's **four-way measured timings** live in
`paper/benchmarks/run_benchmarks.py` and
`paper/benchmarks/trace_benchmarks.py`, where the `banded`
baseline calls **`scipy.linalg.solve_banded`**; it does *not*
call the Cholesky routines. Meanwhile
`src/trendestimation/solvers.py` implements a distinct genuine
Cholesky backend (`PreparedPLSSolver(method="cholesky")`) through
`scipy.linalg.cholesky_banded` and
`scipy.linalg.cho_solve_banded`. That backend is a correct
object for future matched-workload Cholesky benchmarks, but it
is not the method measured by the four-way paper tables.

Consequently:

- Cite both Weinert (2007) and the exact Weinert (2012) book.
- State accurately what Cortés-Toto et al. actually report.
- Retain the word *banded* for existing paper timing data,
  and reserve *Cholesky* for results that explicitly time that factorization.
- Do not retroactively relabel measurements or claim faster optimization.
- Any new Cholesky comparison needs separate measurements, error checks,
  recorded machine/BLAS details, and identical workloads.

This note records literature and implementation provenance, not new
experimental observations or a new estimator.
