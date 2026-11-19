# Agent instructions: unified CSDA theoretical manuscript

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
