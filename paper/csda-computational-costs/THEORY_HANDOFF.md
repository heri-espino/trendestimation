# CSDA Paper B — theoretical computational complexity handoff

## Manuscript objective and scope

**Primary manuscript:** `paper/csda-computational-costs/main.tex`.

**Working title:** *Amortized complexity of smoothness-indexed
penalized least squares*.

This is now a **theoretical computational paper**, not a manuscript
claiming that historical Windows timing plots establish general runtime
rankings. The canonical mathematical object is

```math
A_lambda = I + lambda D_d^T D_d,
T_A(n,d,M,R,C; epsilon, theta),
```

with `C` the set of requested criteria and `A` the complete
criterion-evaluation pipeline. The contribution is a careful
workload-aware cost accounting, not a new PLS penalty, Whittaker
algorithm, selected inverse or new likelihood model.

Read source in this order:
1. `main.tex` and `sections/foundations.tex`;
2. `sections/algorithms.tex` and `structured_criteria.tex`;
3. `sections/amortized_frontier.tex` (formal propositions/proofs);
4. `sections/theory_discussion.tex` (workflow, limits, prior art);
5. `references.bib`, `SOURCE_AUDIT.md`, `verify_theory.py`;
6. root `AGENTS.md` and `AI_HANDOFF.md`.

## Results actually proved

- The normalized smoothness-to-penalty inverse is a data-independent
  bijection for a fixed n,d, so an identical S grid maps once and
  can be shared across criteria, reference means and observed series.
- The forward-difference normal matrix is SPD for finite lambda>=0
  and has half-bandwidth d; banded Cholesky plus the classical
  selected-inverse recurrence provides exact conditional EDF and CV
  leverages in O(n d^2) arithmetic per positive finite candidate.
- New explicit derivation in this manuscript: under the stated
  reduced-coordinate Gaussian model, a banded factor and solved
  trend determine the profile quadratic J_lambda, while
  `logdet(C_lambda) = logdet(A_lambda) - (n-d)*log(lambda)
     - logdet(D_d D_d^T)`. The final determinant depends only
  on n,d and can be cached. This is an algebraic identity, not a
  claim of algorithmic novelty over preexisting WH literature.
- Full retained spectral basis work is bounded by
  `O(n r^2 + M I r + R n r + M R c r + CVflag*M R n r)`,
  memory O(nr), r=n-d.
- Banded + selected-inverse work is bounded by
  `O(n d^2 + M I n d^2 + M n d^2 + M R n d + M R c n)`,
  with streamed O(nd+M+Rn) memory.
- For d=1, positive penalty eigenvalues follow the path-graph
  Laplacian cosine formula `2-2cos(pi*j/n)`. This is known
  numerical linear algebra, not a new transform method.
- A calibrated affine cost ansatz has a positive M-crossover
  only when setup and marginal-work slopes satisfy the
  explicit sign assumptions. Constants, numerical validity,
  memory and contention must be measured before claiming
  specific optimal thresholds.

These are arithmetic upper bounds under the assumptions in the
paper, not claims of lower bounds or a measured universal winner.

## Deterministic verification, no timings

```powershell
python paper/csda-computational-costs/verify_theory.py
```

Checks banded Cholesky vs dense solve, selected-inverse diagonal,
smoothness identity, exact profile quadratic and determinant
identity in multiple small deterministic cases. It **does not**
repeat expensive benchmark experiments. The dedicated
`.github/workflows/csda-computational-theory.yml` compiles using
the exact existing Elsevier CAS Bundle v2.4, validates cross-references
and archives PDF plus source provenance.

## Historical empirical material is preserved, not discarded

The following existing files remain tracked in the same directory
but are **no longer included by the theoretical main.tex**:

- `sections/benchmarks.tex`, `sections/results.tex`,
  `sections/experiment006_design.tex`,
  `sections/experiment006_status.tex`,
  `sections/discussion.tex`;
- `render_figures.py`, figure PDF/PGF/SVG outputs and the
  archived generated timing tables.

They belong to the implementation / measured-runtime companion
(anticipated as a distinct Springer paper, pending author
submission decision).

### Latest matched Windows pilot — archived result branch

The user's completed three-method, `Workers=1` replication
is stored separately and must not be overwritten:

`results/experiment010-uncapped-PCAG103A-08-20261103T222938857Z-shard0-offset20`
(commit `8d8ac0aff0e585343b37865bdbb9b47bbc7d730d`).

Provenance: Windows 11 PCAG103A-08, conda Python 3.11.17,
one worker, one BLAS thread, source SHA
`f16f2bab6cfa37c6423c7f2d4554208efa9f683a`,
seed 20261102, two repeat seeds, n=64, d=1,
`mu=mean(D_d y)` conditional plug-in,
residual BIC, M=100000 candidates. Three selected methods,
seven explicitly excluded slots, **48 valid result rows**, and
48 selected-score parity records (not an independent high-precision
certification). Total process batch elapsed time 525.55s is
not the elapsed time of any one score.

Representative `mapped_lambda` cold medians in **seconds**,
copied from the original result branch (NOT included in Paper B):

| Workload | SVD | Naive inverse | CHOLMOD + banded trace |
|---|---:|---:|---:|
| one S, one series | 0.002130 | 0.001932 | 0.002606 |
| 100000 S, one series | 8.625016 | 11.602875 | 32.003494 |
| one S, two series | 0.002150 | 0.001955 | 0.002676 |
| 100000 S, two series | 9.262217 | 15.384171 | 37.602602 |

This is a **fairer isolated one-worker comparison** than earlier
mixed-concurrency samples, but still only a single n,d,criterion
configuration with two repeats, not a universal scaling law.
A positive CHOLMOD runtime here includes the extra banded selected
inverse diagnostic; do not label it a pure factorization timing.

Prior mixed-concurrency data remain in the main Springer manuscript
(available on GitHub); do not mix the two sources without a new
documented statistical analysis.

## Distinct publication plan

1. **Paper B, theoretical CSDA**: this directory's `main.tex`.
   Mathematical results, proofs, complexity accounting, no timing
   figures as inferential evidence.
2. **Implementation/runtime Springer manuscript**: keep the existing
   `paper/main.tex` and `paper/computational-statistics-submission/`
   working drafts. The new matched 3-method run can be incorporated
   there after independent validation, reproducible reporting,
   and coauthor approval.
3. **Paper A, numerical-reliability CSDA** remains in
   `paper/csda-spectral-smoothness/`. Avoid publication overlap.

Potential journal novelty caveat: classical WH factorizations, selected
inversion and trace smoothing already exist. A CSDA theory submission
requires editorial assessment of whether the *integrated*
workload-aware analysis is sufficiently original; this draft
does not automatically establish that claim.

Correspondence, coauthor order, disclosures and final submission
approval remain unverified and must not be fabricated.
