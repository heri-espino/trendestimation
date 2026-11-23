# Contribution and priority audit — unified CSDA theory (2026-11-23)

Purpose: distinguish **what this article concretely supplies** from
the established results that make it possible. The description below
governs the abstract, Introduction §Contributions, smoothness/likelihood
sections and conclusion. This is a source/text revision, not a new
numerical experiment or novelty certification.

## Primary sources directly checked

- Victor M. Guerrero, *Time Series Smoothing by Penalized Least Squares*,
  *Statistics & Probability Letters* 77 (2007), 1225–1234:
  the uploaded original PDF, printed p. 1229 (Section 3,
  Eqs. (21)–(23)) gives Theil-type relative precision and the
  **n-normalized trace** index. The text says that the index tends to 1
  even for d≥1, but its displayed formula and the nullspace dimension d
  imply the exact finite-sample upper limit **1−d/n**. The same work
  supplies nonzero reference differences and variance-ratio modeling.
- Daniela Cortés-Toto et al., *Trend Smoothness Achieved by Penalized
  Least Squares with the Smoothing Parameter Chosen by Optimality Criteria*,
  *Communications in Statistics—Simulation and Computation* (2017):
  uploaded original PDF, Section 2.1 and Eq. (9) explicitly state
  the **1−d/N** finite-n limit, and Eqs. (10)–(16)
  describe observation noise, difference-innovation variance and
  λ as the ratio of those two variances. They compare classical criteria,
  not the current paper's entire S-based multi-criterion computation.
- Guillaume Biessy, *Whittaker–Henderson Smoothing Revisited: A Modern
  Statistical Framework for Practical Use*, *ASTIN Bulletin* (2026):
  uploaded original, §5.3 (printed p. 12) explicitly uses Gaussian
  **marginal likelihood** for smoothing-parameter estimation with the
  minimized quadratic and determinant correction. It is prior art for
  likelihood-based tuning, not evidence that this manuscript created REML.
- Patterson–Thompson (1971), Wahba (1985), Wood (2011):
  established REML/GML and computation, cited in manuscript. Read
  original-source ledger notes/GAUSSIAN_LIKELIHOOD_PROVENANCE.md before
  adding any claim of priority.

## Concrete contributions with boundaries

| Manuscript component | Contribution in *this treatment* | Not claimed as invented |
|---|---|---|
| Rank-normalized S | S=(n−tr H)/(n−d) = [1/(n−d)]Σ λδ/(1+λδ), exact 0/1 endpoints for any 1≤d<n, monotone inverse S↔λ, comparability as *fraction* of penalizable directions, ν=n−(n−d)S | Original n-normalized trace/relative precision; PLS estimator; global priority for a simple arithmetic rescaling |
| Precision interpretation | S = tr(P J⁻¹)/(n−d) under fixed variance components, connecting the rescaled trace to normalized relative precision | Guerrero/Theil variance and precision decomposition |
| Variance-ratio selection | Under a specified **fixed numeric μ** and Gaussian observation/difference errors, derive the penalized-coordinate **existing profiled Gaussian REML** criterion and use it to estimate λ=σ²_obs/σ²_diff, then S(λ); estimate σ²_obs=J_λ/(n−d) and σ²_diff=σ²_obs/λ at a finite positive optimum | Original stochastic PLS variance-ratio identity, Gaussian marginal likelihood, REML, or general uniqueness/global optimization |
| SVD representation | Reusable SVD of **D_d**, shift-free nonzero-μ reconstruction, conditioning/endpoint checks | SVD itself, nonzero-mean PLS, numerical linear algebra |
| Full criterion workload | Complete CV/GCV/AICc/BIC/REML diagnostics; show roles of leverages, trace, log determinants; derive setup/mapping/criterion/series-specific operation and memory terms | The named criteria and selected-inverse algorithms |
| Admissibility and reproducibility | Numerical validity conditions, fixed-/estimated-μ boundaries, code example and reproducible synthetic third-difference illustration via AwesomeFigures | Benchmarked superiority, actual physical jerk measurements, new forecasting results |

## Statistical caveats

The scalar \`lambda\` is called an "optimal" variance ratio **only
relative to the assumed Gaussian likelihood and the stated search
domain**. It is not universally optimal for trend recovery or
out-of-sample forecasts. The 91-point illustrative S grid yields a
finite-grid minimum, not a certified continuous global optimum. Jointly
estimating μ changes the contrast space/degrees of freedom and
requires another likelihood derivation. The deterministic PLS solution
requires no Gaussian assumption.

The rank normalization is a useful explicit parameterization; by itself
it is the elementary multiplicative factor n/(n−d) and does **not**
generate a different trend family. Readers should not infer that all
the listed components are first occurrences worldwide.

## Reproducibility

Review and run existing checks:

    python paper/csda-unified-theory/verify_theory.py
    python paper/csda-computational-costs/verify_theory.py
    python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_*.py' -v

The single AwesomeFigures example and exact source/output metadata are
in \`paper/csda-unified-theory/figures/\`. Recompile with the paper-only
GitHub Actions workflow, verify two native landscape tables, PDF text
and figure placement, and record the exact source/PDF hashes.

PR #157 was merged before this revision. Do not rewrite its figure,
data or tests. This contribution-positioning follow-up is scoped to
the unified CSDA manuscript and its notes, not a journal submission.
