# Unified CSDA theoretical manuscript: Paper A + Paper B

## November 23, 2026: state-of-the-art and editorial positioning

The abstract, Introduction, direct-SVD discussion, algorithm provenance table and conclusion now explain the **integrated** contribution more assertively while preserving every mathematical claim, equation, experiment and figure. Added historical Demmler--Reinsch (1975) and contemporary Biessy (2026, Section 6.4) **use-site** comparisons: the paper factors the original rectangular difference matrix using a retained full SVD, versus a Gram-penalty eigenbasis and possible low-rank approximation. Also added Eilers (2003) for cross-disciplinary use, Tibshirani (2014) for the distinct L1 alternative and Hamilton (2018) for HP-filter interpretation cautions. The audit and reproduction gate are in [notes/STATE_OF_ART_POSITIONING_20261123.md](notes/STATE_OF_ART_POSITIONING_20261123.md). The new citations have not yet passed a source-matched PDF build, and no benchmark, journal submission, or merge occurred.


## November 23, 2026: explicit paper contributions and novelty boundaries

The abstract, Introduction and conclusion now foreground **six concrete
contributions**: (1) the rank-normalized $S\in[0,1]$ index with
$d$-independent endpoints and invertible mapping, (2) arbitrary-order
shift-free spectral reconstruction for specified nonzero $\mu$,
(3) **selection of the established variance ratio**
$\lambda=\sigma_\varepsilon^2/\sigma_u^2$ using **existing profiled
Gaussian restricted/marginal likelihood** in the normalized
$S$ coordinate, (4) complete statistical-criterion diagnostics,
(5) amortized spectral versus banded pipeline costs and numerical
admissibility, and (6) the reproducible software/figure illustration.

This work does not claim that either the historical n-normalized
Theil--Guerrero precision index, the original PLS variance ratio,
Gaussian marginal likelihood, REML or SVD was invented here.
The rank denominator $n-d$ rather than $n$ gives exact
$S=1$ at the polynomial limit for every order; the original
finite-n bound $1-d/n$ is explicitly stated in Cortés-Toto
et al. (2017). The Gaussian profile likelihood selects a
variance ratio **under fixed numeric $\mu$ and Gaussian
assumptions**, not a guaranteed globally best forecast.

Source-based priority, equations, boundaries and reproduction:
[notes/CONTRIBUTION_PRIORITY_AUDIT_20261123.md](notes/CONTRIBUTION_PRIORITY_AUDIT_20261123.md).
No new numerical experiment or independent paper changed.



## November 22, 2026: one simple AwesomeFigures figure after the code

The paper's software section now demonstrates
`select_lambda(..., criterion="mle", search_space="smoothness")`
with a **fixed numeric reference `mu`** and shows one two-panel
illustration immediately after the code: noisy synthetic positions
and the true/fitted trend, followed by the profiled Gaussian
contrast across normalized smoothness `S`.
The synthetic trajectory has a cubic nonzero-jerk baseline plus a
small sinusoidal perturbation. Nothing is estimated from real
trajectory data; no forecasting or method-comparison claim is made.

Reproduction, fixed seed and full parameters:
[figures/README.md](figures/README.md).
Figure generation uses the **existing pinned** AwesomeFigures revision
from `paper/requirements.txt`. The paper-only GitHub Actions workflow
renders the vector PDF and PNG/SVG previews, preserves numerical
CSV/JSON sources with hashes, and compiles the canonical CAS PDF
using its existing landscape-table checks.



## November 19, 2026: primary-paper citation verification

All **eleven original PDFs supplied by the author** have now been
checked for actual titles, publication years, DOI/volume/pages,
and relevance to particular algorithmic claims. The audit
`notes/PRIMARY_REFERENCE_AUDIT_20261119.md` maps each
publication to the manuscript's exact citation purpose.

Five genuinely missing works were added to the local BibTeX
(Reinsch 1967, Cornea-Madeira 2017, Lin et al. 2011,
Hutchinson **1990**, Ubaru et al. 2017). Six original
algorithm/GCV papers were already in the bibliography and
received stronger contextual or page-specific attribution
rather than redundant entries. The 1990 Hutchinson print
year and DOI correct an earlier informal 1989 suggestion.

A new subsection distinguishes stochastic approximate
trace/log-determinant methods from our exact leverage/trace
calculations. No external paper is represented as the
source of our composite time bound or a proof of universal
SVD superiority. Primary licensed PDFs are **not** copied
into Git. The source-only CI now validates all citation
keys and preserves the audit alongside PDF provenance.

## November 19, 2026: explained Gaussian REML and mathematical reading guide

The former short "Gaussian reduced-coordinate likelihood" subsection has
been replaced by a **full theorem with proof** identifying the exact
Gaussian mixed-effects assumptions, nuisance polynomial coefficients,
orthogonal error contrasts, covariance diagonalization, and
closed-form profiling of the observation noise variance. We now call
the resulting criterion **profiled Gaussian marginal / restricted
likelihood in penalized spectral coordinates**, not a new
likelihood method. Original sources Patterson--Thompson (1971),
Wahba (1985), Wood (2011), and especially Biessy (2026),
Section 5.3, are cited directly beside the theorem and its formula.

New mathematical explanations include a notation/roadmap section,
the derivation of the PLS normal equations by differentiating,
positive definiteness and inverse-free solutions,
the interpretation of each SVD component and pointwise multiplication,
effective degrees of freedom and normalized smoothness, individual
CV leverages versus average GCV leverages, and the likelihood/Cholesky
determinant equivalence.

Small deterministic tests in tests/test_reml_contrast.py independently
check the spectral and direct differenced-data Gaussian quadratic
forms, determinant identity, unpenalized beta invariance, nonzero mu,
profile noise variance, and original penalized objective equality.
No new data, numerical benchmark or statistical novelty is implied.

Primary-source audit and proof details:
[notes/GAUSSIAN_LIKELIHOOD_PROVENANCE.md](notes/GAUSSIAN_LIKELIHOOD_PROVENANCE.md).



## November 18, 2026: Weinert and the third-difference example

The revised article compares Weinert (2007), whose principal solver uses banded LDL^T of alpha I + M^T M, to our reusable SVD of D_d. It documents lambda=1/alpha for mu=0 and explains why neither method is universally faster. Weinert's fixed-p=2 GCV computation is linear in n per penalty, not exponential in the number of trial penalties.

New sections give an exact d=3, n=6 D3/Q3 example and H_1[1,6]=11/195, link third differences to discrete jerk with correct sampling units and nonzero mu, and discuss validated selection of (d,S) as model hyperparameters without claiming any new empirical result.

Read notes/WEINERT_PRIMARY_SOURCE_D3_REVIEW.md for the page- and equation-specific source audit. Run all source-only deterministic tests:

    python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_*.py' -v

## November 18, 2026: readable landscape tables and clear SVD-cost explanation

The canonical Elsevier CAS paper now places the algorithm-provenance and
per-penalty-computational-cost tables on dedicated sideways pages.
The source uses the rotating package and a post-compilation
PDF metadata correction (rotate_landscape_tables.py, pypdf 5.9.0)
to give the two float pages native landscape orientation in PDF viewers.
No table text is rasterized or clipped.

The model section states explicitly that the single reusable
reduced SVD is computed on D_d, of shape (n-d) by n, not on
H_lambda. The algorithms section distinguishes the equivalent
Gram eigendecomposition of D_d^T D_d from decomposing the
penalty-dependent dense smoother H_lambda, with exact
equivalence and conditioning caveats. The complexity section
explains a workload of 11 DISTINCT smoothness levels: one
spectral decomposition followed by 11 mappings/scorings,
not 11 matrix inversions and not 11 repeats of the same
penalty.

Reproducible local build from paper/csda-unified-theory,
after copying the official CAS templates:

    python -m pip install pypdf==5.9.0
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
    python rotate_landscape_tables.py main.pdf
    python rotate_landscape_tables.py main.pdf --check

The GitHub Actions workflow carries out the same source-only
mathematical checks, CAS build, native page rotation,
page-presence verification, artifact preservation,
and SHA-256 logging automatically. No Experiment011 run,
new optimization sweep, or Paper C dataset is touched.

## SVD versus Gram eigendecomposition clarification (2026-11-16)

The canonical `sections/algorithms.tex` now states and proves exact spectral equivalence and the positive-spectrum identity `kappa_+(D_d^T D_d) = kappa_+(D_d)^2`. The `sections/stability.tex` discussion derives the partial sensitivity of the inverse smoothness-to-penalty map to a positive penalty eigenvalue. These are established algebraic/numerical-analysis observations, **not** claimed novel decomposition algorithms or measured SVD-versus-eigen runtime/accuracy results. They explain why the Python library uses SVD of `D_d` as an accuracy-oriented reference while symmetric eigendecomposition of `Q_d` is also mathematically valid. Banded solvers remain appropriate at larger n.

Reproducible, deterministic checks (no benchmarks or source data changed):

```bash
python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_svd_gram_equivalence.py' -v
```

That November 16 note referred to the earlier paper state. The November 18 source-only GitHub-hosted workflow recompiles and archives the revised PDF without running empirical benchmarks.

**Canonical source:** main.tex (Elsevier CAS v2.4 double-column).
**Status:** theoretical working draft, not submitted; coauthor approval required.
**Research branch:** paper/csda-unified-theory. Do not merge without author authorization.

## Purpose

The author requested that the spectral Paper A and amortized-complexity Paper B be combined into **one theoretical computational-methodology article**. It uses the **normalized smoothness index S in [0,1]** as the organizing parameter and keeps the fixed **nonzero difference mean mu** in the core mathematics. Contributions cover spectral/shift-free reconstruction for any integer order 1 <= d < n; normalization, unique mapping and exact endpoints; complete CV/GCV/AICc/BIC/ML diagnostics; banded Cholesky with selected inversion; work/memory bounds with reuse across grids and series; numerical failure mechanisms; and the public Python interface.

This paper does not claim invention of classical PLS, diagonalization, SVD, Cholesky, trace smoothness, or cross-validation. The proposed contribution is an integrated workload-aware computational and numerical framework. The Algorithms section includes a table separating the **original publication of each numerical algorithm** from **published cost analyses** and **our derived PLS workload bounds**; details are in `COMPLEXITY_REFERENCE_LEDGER.md`. The added primary references are local to `algorithmic_references.bib`.

## Previous work preserved

The original source trees remain unchanged:
- paper/csda-spectral-smoothness: Paper A multiprecision and exploratory simulations.
- paper/csda-computational-costs: Paper B proofs, original figures, timings, source audit, and shared BibTeX.
- paper/main.tex and paper/benchmarks/experiment011: independent Springer measured timing paper.
- paper/ngsim-jerk-case-study: physical extrapolation and forecast evaluation.

No original experiments, CSVs, figures, PDFs, workflows or branches are overwritten or rerun. No new benchmark measurements are claimed in this manuscript. Historical citations are reused from paper/csda-computational-costs/references.bib; the new local algorithmic_references.bib gives authoritative standard complexity references without editing the predecessor bibliography. See COMPLEXITY_REFERENCE_LEDGER.md for the precise source-to-bound map and attribution of the newly combined workload theorems.

## Reproduce the deterministic algebra checks

From the repository root with NumPy and SciPy installed:

    python paper/csda-unified-theory/verify_theory.py
    python paper/csda-computational-costs/verify_theory.py

These are small deterministic identity checks, not a benchmark campaign.

## Compile the PDF in PowerShell

From the repository root:

    Copy-Item paper\els-cas-templates\cas-dc.cls,paper\els-cas-templates\cas-common.sty,paper\els-cas-templates\cas-model2-names.bst -Destination paper\csda-unified-theory
    Push-Location paper\csda-unified-theory
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
    Pop-Location
    Start-Process ".\paper\csda-unified-theory\main.pdf"

The new workflow .github/workflows/csda-unified-theory.yml runs the checks and compiles the paper on GitHub-hosted Linux, without invoking the PC08 runner.

## Remaining acceptance gates

1. Independently review the mathematics and exact source priority against Guerrero (2007/2008), Cortes-Toto et al. (2017), Weinert (2007), Golub et al. (1979), Erisman--Tinney (1975), Biessy (2026), Golub--Van Loan (2013), Davis (2006), and Saad (2003). Verify exact textbook section citations before submission.
2. Audit selected inversion, likelihood normalization, conditional plug-in mean, and high-order conditioning claims.
3. Verify API calls against the intended release.
4. Confirm coauthor contributions, order, correspondence, affiliation, funding and conflicts.
5. Build, inspect, and freeze the final journal PDF with exact source SHA and input hashes. Verify original algorithm citations (Golub--Kahan, Golub--Reinsch, Cholesky/Benoit, Francis, Takahashi, Erisman--Tinney, Markowitz, Hestenes--Stiefel), as distinct from later complexity references (Golub--Van Loan, LAPACK, Davis, Saad, Weinert). The original Takahashi conference bibliographic record has variants in secondary citations that require checking against its proceedings.
6. Do not submit or merge without explicit author approval.
