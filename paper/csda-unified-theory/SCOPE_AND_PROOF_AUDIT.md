# Scientific scope and proof audit — unified theoretical CSDA paper

Date: November 9, 2026. Status: theory-first draft, not submitted.

## Author's five priorities

1. Spectral diagonalization to compute PLS trends **using the normalized smoothness index**.
2. Working directly in bounded S, rather than only searching log lambda.
3. Interpretability and normalization of the original trace-based index to [0,1].
4. Exact endpoint limits S=0 and S=1.
5. A public Python API with nonzero fixed reference mean and selection criteria.

Paper B adds algorithmic families, complete scoring, time/memory complexity, reuse, numerical risk and conditional algorithm selection. The article intentionally does not center on newly collected benchmark timings.

## Source lineage

- Paper A original: paper/csda-spectral-smoothness/sections/spectral_theory.tex, criteria.tex, introduction.tex, experiments.tex, discussion.tex; numerical 85-digit data archived in experiment004.
- Paper B original: paper/csda-computational-costs/sections/foundations.tex, algorithms.tex, structured_criteria.tex, amortized_frontier.tex, decision_examples.tex, theory_discussion.tex; proof program verify_theory.py.
- Source audit: paper/EDITORIAL_LITERATURE_AUDIT.md and the predecessor papers' bibliography audits.
- Complexity source audit: paper/csda-unified-theory/COMPLEXITY_REFERENCE_LEDGER.md and the **in-manuscript** sections/algorithm_provenance.tex. Both an algorithm's original scientific source (Golub--Kahan 1965, Golub--Reinsch 1970, Cholesky/Benoit 1924, Francis 1961, Takahashi 1973, Erisman--Tinney 1975, Markowitz 1957, Hestenes--Stiefel 1952) and later complexity reference (Golub--Van Loan 2013, LAPACK Users' Guide 1999, Davis 2006, Saad 2003, Weinert 2007) are cited. Exact textbook pages remain a pre-submission verification gate. Takahashi 1973 conference name variants are flagged rather than silently normalized.
- Actual library API: src/trendestimation/core.py and README.md.
- Separate empirical companion: paper/main.tex and Experiment011 on the current independently active Springer PR.

## Proof and identity ledger

| Statement | Source in this draft | Deterministic check |
| --- | --- | --- |
| dim ker D=d, rank D=n-d | Model, Lemma | Matrix rank and polynomial differences |
| Shift-free nonzero-mu spectral reconstruction | Model, Proposition | Affine, direct solve and SVD equality |
| Polynomial constrained limit | Model, Corollary | Direct constrained projection |
| S and trace relationship, strict monotonicity | Smoothness, Theorem | Direct trace and spectral sums |
| CV leverage preserves nullspace | Criteria, Eq. leverage | Explicit inverse diagonal |
| Residual-BIC boundary divergence | Criteria, Proposition | Analytic series proof; no statistical benchmark |
| Gaussian quadratic and determinant identity | Criteria, Proposition | Two independent algebraic computations |
| Selected inverse, O(nd^2) arithmetic | Algorithms | Original Paper B verify_theory.py |
| Amortized SVD / banded upper bounds | Complexity, Theorems | Counting argument, assumptions explicit |
| Affine M crossover | Complexity, Proposition | Algebraic sign argument |
| Kappa(A)=1+lambda delta_max<=1+lambda 4^d | Stability, Proposition | Spectral test, operator norm bound |

Independent line-by-line journal-level referee assessment remains pending. Small deterministic float64 tests do not establish forward-error reliability under all high orders.

## Priority and limitation ledger

- Established prior art: Whittaker, Guerrero 2007/2008, Cortes-Toto 2017, Weinert 2007, Golub et al. 1979, Erisman--Tinney 1975, Biessy 2026, plus Golub--Van Loan (2013) for dense factorization, Davis (2006) for sparse/direct factorization and Saad (2003) for iterative methods. Claim only the integrated computational treatment pending a fuller novelty audit.
- The original index divided by n reaches **1-d/n**, not 1-n/d. Current index divided by n-d reaches exactly one.
- Fixed mu=0 is only a special case; prescribed nonzero mu is core. Data-derived mu and joint unknown-mu selection require changed statistical accounting.
- Residual BIC has no finite unrestricted interior optimum near exact interpolation for nondegenerate samples.
- Cholesky is mathematically feasible for SPD A but finite-precision factorization or subsequent KKT checks may fail. Do not conflate these with spectral inversion errors, missing dependencies, policy skips or actual OOM.
- No measured universal winner is claimed. Exact CV and scalar GCV have different spectral candidate costs.
- Complete native S search and once-pretranslated S->lambda search have matching candidates; independently spaced log lambda does not.
- The Springer paper owns measured hardware timings; the NGSIM paper owns physical forecast performance.
- No new experiments were executed. The manuscript relies on inherited citations and old verified algebra; coauthor declarations remain unconfirmed.

## Before final submission

Review publisher originals, validate references and author information, run both identity scripts and the CAS build, visually inspect every PDF page, freeze commit/hash provenance and obtain coauthor signoff. The PR is not an authorization to merge or submit.
