**2026-11-24 CSDA author/typography/numbering contract:** Read [notes/AUTHORS_TYPOGRAPHY_EQUATIONS_20261124.md](notes/AUTHORS_TYPOGRAPHY_EQUATIONS_20261124.md) before editing the unified CSDA paper. Author-supplied metadata identifies Heriberto Espino-Montelongo as corresponding author (ORCID 0009-0009-1230-2931, heriberto.espinomo@udlap.mx), Daniela Cort\'es-Toto (ORCID 0000-0003-0893-6455, daniela.cortes@udlap.mx; Departamento de Actuar\'ia, F\'isica y Matem\'aticas, UDLAP, San Andr\'es Cholula, Puebla 72810, Mexico). Preserve native CAS author/ORCID/corresponding-author markup. The old PDF showed a fallback Computer Modern font family, so the dedicated CAS workflow now explicitly installs/checks `charis.sty` plus `stix.sty`; verify actual embedded text/math fonts in the next PDF. All DISPLAY mathematics must be numbered with `equation` or equivalent unstarred environments. Inline math remains inline. No boxed formulas, bordered Python listing, or decorative boxes. Keep theorem statements and numerical results unchanged; run deterministic unit tests, font inspection, rotated-table and hard-margin QA. This branch is **not authorized for automatic merge or journal submission**.

**2026-11-23 CSDA layout/disclosure contract:** Read
[notes/SUBMISSION_LAYOUT_AND_DECLARATIONS_20261123.md](notes/SUBMISSION_LAYOUT_AND_DECLARATIONS_20261123.md)
before modifying the paper's formatting or author declarations.
The VS Code Light+ `listings` theme is intentionally bounded by
`\\linewidth`; `microtype` and the paragraph emergency stretch
guard against two-column bleed. The CSDA workflow must pass
`python verify_layout.py main.log` with no body paragraph overflow
above 0.5 pt, retain both native landscape tables, resolve citations,
and archive the compiled source-matched PDF. The funding, conflict and
individual CRediT statements are *unconfirmed*: never replace them with
fabricated claims. AI use is disclosed before references; all journal
declarations need authors' sign-off before any submission. Mathematical
models, figures and experiments remain unchanged.

**2026-11-23 CSDA state-of-the-art editorial handoff:** Read [notes/STATE_OF_ART_POSITIONING_20261123.md](notes/STATE_OF_ART_POSITIONING_20261123.md) before rewriting the abstract, Introduction, SVD model, algorithm provenance or conclusion. The retained full direct SVD of the rectangular `D_d` is framed against **Demmler--Reinsch (1975)** and **Biessy (2026) Section 6.4** Gram-eigenbasis/rank-reduced WH, preserving `W=I` and fixed numeric `mu`. Eilers 2003, Tibshirani 2014 and Hamilton 2018 provide applications, alternative penalties and interpretational cautions. No theorem, benchmark, figure, code or publication track was changed by that edit. Existing deterministic checks plus a source-matched Elsevier CAS PDF/citation build remain required before merge; no journal submission.

## November 22, 2026 precision-matrix extension

The smoothness subsection now derives the intrinsic-Gaussian fixed-reference
precision matrix `J = sigma_e^(-2)I + sigma_u^(-2)Q`, the posterior
conditional covariance `J^(-1)`, and the rank-normalized
relative-precision trace `tr(P J^(-1))/(n-d)`.
The original Guerrero index divides by `n`, not `n-d`.
This is established mathematics, cited to Guerrero (2007) and
Cortés-Toto et al. (2017), not a new algorithm. Preserve the
separate Gaussian restricted-likelihood theorem and its handling
of the `d` fixed-effect/nullspace directions.
New test: `tests/test_precision_matrix.py`.
See [the cross-manuscript audit](../PRECISION_MATRIX_CROSS_MANUSCRIPT_2026-11-22.md).
Existing PDF must be rebuilt/verified; no numerical experiments or
journal submission.


# Agent instructions: unified CSDA theoretical manuscript

## November 23, 2026 contribution-positioning contract

Read notes/CONTRIBUTION_PRIORITY_AUDIT_20261123.md before
editing introduction/conclusion novelty claims. Six concrete
contributions (rank-normalized S, shift-free fixed-mu spectral
formula, prior-art Gaussian REML variance-ratio selection,
complete criteria, workload/accuracy trade-offs, reproducible
code/figure) must be distinguished from previously known
PLS, Guerrero variance ratio, Theil relative precision,
Gaussian marginal likelihood, REML and SVD.

Do not call elementary n/(n-d) trace rescaling a new
statistical estimator or a demonstrated global priority.
Original Guerrero (2007) printed p.1229 Eq.(23) uses n
denominator; Cortés-Toto et al. (2017) Sec.2.1
explicitly note upper bound 1-d/n. The present paper
uses denominator r=n-d to reach exactly 1 at infinite
penalty for any d. It gives normalized relative precision
tr(P J^-1)/r conditional on fixed variance parameters.

A finite positive Gaussian REML optimum estimates
lambda=sigma_obs²/sigma_difference², and S(lambda).
The REML construction is established prior art
(Patterson--Thompson, Wahba, Wood, Biessy).
A finite S grid only yields a grid optimum; unknown
mu changes the inferential problem. Preserve the
single AwesomeFigures demonstration and the
two native landscape tables. Do not modify
independent sources or rerun historical benchmarks.



## November 22, 2026 single AwesomeFigures illustration

The software section includes **one** d=3 synthetic position/jerk
illustration directly after the profile Gaussian MLE example code.
Its renderer is `figures/render_gaussian_jerk.py`, with exact fixed
seed/parameters/selection grid documented in
`figures/README.md`. Use genuine AwesomeFigures, pinned in
`paper/requirements.txt`, to regenerate PDF/PNG/SVG, and retain
the CSV samples, criterion profile and JSON/hash manifest in the
research branch. This is an illustrative in-sample fit, not
physical jerk observations, a forecast, model comparison or
Gaussian-model calibration study.

Keep `mu` a known fixed numeric third-difference reference,
derived from the cubic baseline. Do NOT select `mu="data"`
while describing the existing fixed-mean likelihood theorem.
Do not mention other manuscripts within the CSDA paper.
Keep the two native-landscape provenance/cost tables intact.
Do not rerun any existing experiments.



## November 19, 2026 original-reference source audit

Before altering the algorithm provenance or BibTeX, read
notes/PRIMARY_REFERENCE_AUDIT_20261119.md. The author
supplied 11 primary PDFs and their metadata/claim relevance
were verified. Do not duplicate the six existing citations;
the five new keys reside in algorithmic_references.bib.
Hutchinson's printed journal paper is **1990**, not 1989,
and its DOI is 10.1080/03610919008812866. Lin's SelInv
article is **February 2011**, not the 2010 ACM sample
citation template. The Cornea-Madeira published year is
**2017**, not its 2016 manuscript draft.

Reinsch (1967) treats a continuous spline derivative
penalty, distinct from our discrete D; Cornea-Madeira
(2017) treats finite-sample HP d=2; Lin (2011) is a
general sparse selected-inverse implementation, not
the original inverse recursion. Hutchinson (1990) and
Ubaru et al. (2017) provide **approximate**, not exact,
trace/logdet methods; exclude them from the exact
cost theorem and use explicit stochastic error caveats.
Golub--Reinsch (1970) p.404 directly documents numerical
loss from forming the Gram matrix, but not blanket
SVD runtime superiority.

Do not commit copyrighted source scans. Re-run
tests/test_reference_provenance.py and deterministic
algebra tests and archive the fully compiled PDF.

## November 19, 2026 likelihood and pedagogy contract

Before editing the Gaussian subsection read
notes/GAUSSIAN_LIKELIHOOD_PROVENANCE.md. The source of the
Gaussian restricted/error-contrast likelihood is *established* REML/GML
(Patterson--Thompson 1971, Wahba 1985, Wood 2011);
Biessy 2026 Section 5.3 provides directly relevant Gaussian WH
marginal-likelihood prior art. The manuscript proves an algebraic
specialization, NOT the invention of likelihood or REML.

Keep mu a fixed prespecified numeric difference reference,
unpenalized polynomial W beta as fixed effects, theta and epsilon as
independent Gaussian terms, lambda as the variance ratio, and exactly
r=n-d independent error-contrast coordinates. z=0 causes a
zero-variance profile degeneracy; jointly estimated or plug-in mu is
NOT handled by this theorem.

Preserve the full explanatory proof (projection, variance, profiling,
determinant, connection to banded calculation). Do not alter
SVD/Gram or D3 matrix examples, source provenance, existing
landscape table orientation, or unrelated research branches.
Run tests/test_reml_contrast.py alongside existing suites
before compiling the journal PDF. No novel performance claims.



Read repository README.md, AGENTS.md, AI_HANDOFF.md, paper/AGENTS.md, paper/PUBLICATION_MAP.md and paper/SESSION_HANDOFF.md before modifying this manuscript. Also read this directory's README, all its sections and deterministic checks, both source CSDA papers, and the editorial literature audit.

## Weinert/third-difference editorial contract (November 18, 2026)

Read notes/WEINERT_PRIMARY_SOURCE_D3_REVIEW.md. Weinert (2007, pp. 959-963) defines M as a difference matrix but factorizes alpha I + M^T M by banded LDL^T, not SVD(M). His p=2 fit/GCV is O(n) per trial. Never imply that many lambdas make banded work exponential or that retained dense SVD of D is always faster. For mu=0 lambda=1/alpha.

Keep the exact d=3, n=6 D3/Q3 illustration, sparse Q versus dense H at lambda=1, the physical units of sampled jerk, the difference between mu=0 and mu=j*h^3, and honest chronological validation when treating d as a hyperparameter. Tests live under tests/test_d3_weinert_comparison.py. Preserve Springer benchmarks, Paper C work, prior papers and source histories.

## November 18, 2026 editorial contract
Keep the two algorithm tables as full-width sideways LaTeX floats,
not compressed two-column small-font tables. For distribution,
the reproducible rotate_landscape_tables.py script sets the corresponding
PDF pages to native 90-degree landscape orientation; the source must
still compile under Elsevier CAS. If table numbering or wording changes,
update the script's extraction markers and verification together.

State that the reusable SVD is of D_d (shape (n-d) by n);
H_lambda is derived from it rather than diagonalized anew. Exact
Gram/SVD spectral equivalence, the square-positive-conditioning
identity, and the distinct role of H_lambda eigendecomposition must
all be explained without claiming universal SVD runtime superiority.
When reporting 11 smoothing candidates, distinguish one-time
factorization, 11 different smoothness-to-penalty maps,
11 scores, LOOCV/full trend extra work, and caching for
repeated IDENTICAL candidates. A successful proof check is not
an empirical benchmark.

## Ownership and concurrency
Work only in an independent feature branch and an appropriate PR. This folder is the new theoretical canonical source; preserve all material under paper/csda-spectral-smoothness, paper/csda-computational-costs, paper/benchmarks, paper/main.tex and paper/ngsim-jerk-case-study. Separate agents own the Springer timing tensor and the applied vehicle paper. Do not rerun Experiment011 or any large prior benchmark. Do not merge without explicit author approval.

## Mandatory scientific contracts
- Objective: squared residuals + lambda times squared order-d differences centered on fixed numeric mu.
- Fixed nonzero mu is an established Guerrero feature, not a newly invented penalty. Mu=data is conditional plug-in; it is not a jointly estimated mean in the core proofs.
- Conditional normalized S=(n-tr(H))/(n-d), with exact 0/interpolation and 1/constrained-polynomial endpoints. Old trace/n index has upper bound 1-d/n.
- The eigenvalues, inverse S map and H depend only on n,d,lambda, not a fixed mu or observed series.
- Do not report an independently spaced log-lambda grid as the same candidate search as an S grid.
- Fixed-mu leverage and EDF do not give exact foldwise refit for a data-dependent mean.
- Keep exact CV/GCV/AICc/residual BIC/likelihood definitions. Disclose residual BIC's interpolation pathology.
- Include every mapping, factorization, selected inverse, determinant, projection and scoring cost before identifying a cheap pipeline.
- Cite the original algorithm literature *and separately* the later complexity sources using algorithmic_references.bib and the inherited references; read COMPLEXITY_REFERENCE_LEDGER.md. Original algorithms include Golub--Kahan, Golub--Reinsch, Cholesky documented by Benoit, Francis, Takahashi, Erisman--Tinney, Markowitz and Hestenes--Stiefel. Do not imply that the originals stated our derived complexity formulas or that generic books introduced the algorithms. The direct source citation table is sections/algorithm_provenance.tex.
- Arithmetic O bounds are not measured runtime. SPD existence does not guarantee finite-precision correctness. Distinguish factorization, KKT, S-inversion, memory and undefined-score failure mechanisms.
- The Python package does not implement every proposed theoretical auto-dispatch policy.

Preserve all TeX source, scripts, tests, PDF, compilation logs and checksums. Name new experiments sequentially and include purpose, methodology, outputs, reproduction, findings and next steps if a new experiment is authorized. Never delete prior numerical evidence or overwrite other agents' work. Before publication verify all proofs and citations directly against original papers; obtain coauthor approval.
