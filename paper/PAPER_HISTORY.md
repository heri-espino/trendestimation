# Paper history: manuscript versions and verified PDF builds

This record tracks research-paper **versions**, not only journal publications. It retains source lineage, archived PDFs, compilation jobs, and the difference between a completed LaTeX build and a reviewed manuscript.

Original archive compiled **November 9, 2026**; historical note reconciled **November 18, 2026**. These are historical snapshots, not a claim that November 9 PDFs are the newest current manuscripts. No historical benchmarks, raw experiments or journal submissions were rerun or rewritten by the original compilation.

## Current integrated manuscripts (updated November 23, 2026)

The live current-manuscript index is
[LATEST_PAPERS.md](LATEST_PAPERS.md), not the historical
November 9 PDFs below. By November 14 the unified CSDA
theoretical manuscript (including algorithm provenance),
the 19-page Springer empirical manuscript with AwesomeFigures,
and the 14-page Paper C applied manuscript were integrated
in main, with original sources and historical releases retained.
See that live index for the newest checked-in PDF, LaTeX source,
and source-specific visualization galleries.

The **November 9 section below preserves the historic versions**.
Any references to latest or current within that section refer
to the earlier compilation date.

### November 23, 2026 — explicit normalization and variance-ratio contributions

**Current unified CSDA manuscript: 21 pages.** The authors requested that
the paper's actual contribution set be identified more precisely, rather
than described only as a unified computational framework. The revised
abstract, Introduction (six numbered contributions) and conclusion
emphasize the $S=(n-\operatorname{tr}H)/(n-d)$ **rank-normalized** unit
interval with its exact endpoints, invertible penalty mapping and
conditional relative-precision interpretation. Guerrero (2007) used
the original $n$-normalization; Cortés-Toto et al. (2017) explicitly
recognized its $1-d/n$ finite-n ceiling. The rescaling is an
operational contribution, **not** invention of the trace index or PLS.

The statistical contribution is stated accurately as **using** the
established profiled Gaussian restricted/marginal likelihood to choose
the *previously known* variance ratio
$\lambda=\sigma_\varepsilon^2/\sigma_u^2$ and corresponding
$S(\lambda)$, under fixed numeric $\mu$ and Gaussian assumptions.
The theorem's variance profiles, fixed-effect contrasts, deterministic
endpoints, finite-grid limitations and original REML citations are
preserved. Other named contributions: shift-free nonzero-$\mu$ SVD($D$)
reconstruction, full CV/GCV/IC/likelihood diagnostic costs, memory and
numerical admissibility, and reproducible AwesomeFigures code/figure.

**Verification:** [Merged figure PR #157](https://github.com/heri-espino/trendestimation/pull/157)
and [merged contribution PR #158](https://github.com/heri-espino/trendestimation/pull/158).
Verified source pre-archive SHA
\`91893454dd53cdc67cbaf32582b32ac61d5ba0c1\`;
merged contribution commit
\`43e97807f9c49c457aa60e4c288358e91f54567f\`.
Successful [Actions #45242845352](https://github.com/heri-espino/trendestimation/actions/runs/45242845352)
ran all deterministic math/citation checks, regenerated the existing
AwesomeFigures plot, compiled Elsevier CAS, and archived source+PDF.
**PDF SHA-256**:
\`538cf94310e21582912295f5c509ae8acb1a3337ac3ace76cd76b25b790e5772\`.
The 21-page searchable PDF's contribution list is legible on p. 2,
variance-ratio derivation on p. 8, and conclusion on p. 19; the two
native-landscape algorithm tables are on pp. 11 and 14. The direct
original-paper priority assessment is
[CONTRIBUTION_PRIORITY_AUDIT_20261123.md](csda-unified-theory/notes/CONTRIBUTION_PRIORITY_AUDIT_20261123.md).
No fresh benchmarking, changed estimator, or journal submission.

### November 19, 2026 — profiled Gaussian REML theorem and original-paper citation audit

**Current unified CSDA theory manuscript: 19 pages.** The Gaussian reduced-coordinate likelihood is now rigorously described as **profiled Gaussian marginal/restricted likelihood (REML) in penalized spectral coordinates**, and shown to be established methodology rather than a newly invented likelihood. A complete theorem derives the orthogonal error contrasts, fixed-effect polynomial nullspace, independent Gaussian spectral variances, the profiled observation-noise variance, and the banded determinant identity. The manuscript also explains PLS normal equations, positive definiteness, the shift-free SVD reconstruction, normalized smoothness and LOOCV-versus-GCV leverages.

**Original references:** Eleven user-supplied PDF originals audited for actual claims, years, publication metadata and exact-versus-approximate algorithm status. Five new local BibTeX entries are Reinsch 1967, Cornea-Madeira 2017, Lin et al. 2011, Hutchinson **1990** (corrected from previously suggested 1989), and Ubaru et al. 2017. Six already-present originals received precise in-text attribution. The shared Golub--Heath--Wahba (1979) reference now has its original **Technometrics 21(2), 215–223** volume, issue and pagination. Stochastic trace/logdet approximations are not confused with exact CV leverages or exact banded selected-inverse computations. Original copyrighted PDFs are not stored in the repository. See [complete eleven-source audit](csda-unified-theory/notes/PRIMARY_REFERENCE_AUDIT_20261119.md), [Gaussian original-source audit](csda-unified-theory/notes/GAUSSIAN_LIKELIHOOD_PROVENANCE.md), and [citation integrity test](csda-unified-theory/tests/test_reference_provenance.py).

**Reproducibility:** [Merged manuscript PR #147](https://github.com/heri-espino/trendestimation/pull/147), merged commit [da87f3b1](https://github.com/heri-espino/trendestimation/commit/da87f3b10d243f2ca07e3c1a4a741a4123a83c9f); authored source `1d354e1c9e30c18d30bb90f947b19689ca38541f`; successful source-only [Elsevier CAS build #44490243522](https://github.com/heri-espino/trendestimation/actions/runs/44490243522); [current PDF on main](csda-unified-theory/main.pdf). Repository PDF **SHA-256: 845f7ed58d2f805dca81ddcfc0b677040b00419ced7db3b391331e785d783898**. All manuscript algebra and bibliography tests passed; PDF has 19 pages, with native landscape tables on pages 9 and 13 and no unresolved citations or LaTeX errors. Existing overfull-box warnings remain for later typography review.

**Boundaries:** No numerical benchmarks, data, algorithm implementations, paper submissions or independent scientific manuscripts changed as part of this citation/proof revision (apart from a bibliographic metadata correction in the inherited Paper B references file). The article remains an author-reviewed draft, not a submitted journal paper.

### November 18, 2026 — Weinert original-source audit and third-difference revision

**Current CSDA theory draft: 15 pages.** The user requested a closer comparison with Weinert's original algorithm, exact illustrative order-three matrices, interpretation of third differences, and honest computational-crossover statements.

**Original-source finding:** Weinert (2007, published pp. 959--963, Eqs. 1.1--1.8 and 2.1--2.14) defines a rectangular difference matrix $M$ but **factorizes $\alpha I+M^\top M$ into banded $LDL^\top$**, not an SVD of $M$. His main order-two fit/GCV method is $O(n)$ for a known parameter; $M$ distinct candidate penalties cost $O(Mn)$, not exponentially increasing time. In the common zero-reference formulation, our $\lambda=1/\alpha$. His state-space alternative is also acknowledged. New article passages distinguish this prior method from the retained SVD of $D_d$ and explain when SVD preparation can or cannot be amortized.

**Worked example and interpretation:** A fully specified $n=6,d=3$ matrix figure presents the exact $D_3$ and $Q_3=D_3^\top D_3$, establishes that $Q_3$ is singular while $A_\lambda=I+\lambda Q_3$ is SPD and banded, and verifies $(H_1)_{1,6}=11/195$. For equally spaced position data, third differences divided by $h^3$ approximate jerk; $\mu=jh^3$ corresponds to a constant-jerk cubic limit, while $\mu=0$ favors a quadratic limit. Selecting $(d,S)$ via held-out validation is discussed as a prospective methodology, not an experimentally verified forecasting result.

**Reproducible source:** [merged PR #143](https://github.com/heri-espino/trendestimation/pull/143), [authored source SHA 306a775b](https://github.com/heri-espino/trendestimation/commit/306a775b7c563bb9771b37a17f5e8a362e7ec4bc), [successful journal build and deterministic checks #44457005132](https://github.com/heri-espino/trendestimation/actions/runs/44457005132), and [PDF in main](csda-unified-theory/main.pdf). The final **15-page PDF SHA-256** is **6f567dffe2d6cab0b5ec5a1df2a7fa4725210c61a48e931d43947e2985517b84**. The exact research source/equation audit is [WEINERT_PRIMARY_SOURCE_D3_REVIEW.md](csda-unified-theory/notes/WEINERT_PRIMARY_SOURCE_D3_REVIEW.md); the test suite includes [test_d3_weinert_comparison.py](csda-unified-theory/tests/test_d3_weinert_comparison.py).

**Verified presentation:** d=3 mathematical matrices are legible on page 3; both existing algorithm tables remain native landscape on pages 7 and 10. Mathematical checks and LaTeX compilation passed, with no undefined citations or LaTeX errors. Six existing/minor overfull-box warnings remain for final typography review. No experiments or statistical results rerun, no other paper changed and no journal submission.

### November 18, 2026 — CSDA landscape-table and SVD rationale revision

**Title:** Spectral and structured algorithms for
smoothness-indexed penalized least-squares trend estimation.

**Change:** Two formerly cramped tables have been rebuilt as
full-page, native landscape-orientation PDF pages (5 and 8).
The model now explicitly decomposes the rectangular difference
matrix D_d, not the smoothing matrix H_lambda. The algorithm
discussion compares SVD(D_d), eigenanalysis(D_d^T D_d), and
eigenanalysis(H_lambda), including their exact shared basis,
Gram-matrix conditioning and dense-factorization trade-offs.
The complexity section separates a one-time decomposition
from evaluating 11 distinct smoothness levels, including
S-to-lambda mapping, projected scalar scoring and optional
full-fit or exact CV work.

**Source:** [research commit 88b00739](https://github.com/heri-espino/trendestimation/commit/88b0073910a8822e8c63292a28168de632f85108),
[merged editorial PR #138](https://github.com/heri-espino/trendestimation/pull/138),
and [source/compiled PDF in main](csda-unified-theory/).
Source-only [Actions build #44448096253](https://github.com/heri-espino/trendestimation/actions/runs/44448096253)
passed deterministic algebra checks and generated a **14-page**
Elsevier CAS PDF. The preserved manuscript PDF SHA-256 is
**fa7b6fd4f663e3b3f71507693e15624afbc021758cf2252f2e040a3873892d7d**.

**Layout verification:** Both table PDF pages are marked
native rotation 90 degrees; page text and citations remain
selectable, and the rotated PNGs were inspected. The exact
rotation protocol is [rotate_landscape_tables.py](csda-unified-theory/rotate_landscape_tables.py).
Existing CAS front-matter and minor paragraph overfull-box
warnings remain for subsequent copy-editing.

**Boundaries:** This is a mathematical clarification and
publication-layout revision; it did not repeat any empirical
timing experiment, change solver behavior or submit the
manuscript to a journal.


## November 9, 2026 compilation archive (historical, preserved)

### 1a. Citation-audited CSDA theory build as of November 9

**Revision (November 9, 2026):** After the original A+B theoretical compilation, the author requested explicit published references supporting the individual algorithms' time and memory complexities. The manuscript now cites Golub--Van Loan (2013), Davis (2006), Saad (2003), and the existing Erisman--Tinney (1975) and Weinert (2007) sources. The new [complexity source-to-claim ledger](https://github.com/heri-espino/trendestimation/blob/paper/csda-unified-theory/paper/csda-unified-theory/COMPLEXITY_REFERENCE_LEDGER.md) separates established factorization/selected-inverse bounds from the authors' composite smoothness-grid workload theorems. All original Paper A/B materials remain preserved.

**Source:** [citation revision 970ad820](https://github.com/heri-espino/trendestimation/commit/970ad820de9a5b635caa2cb0ed1dc3dfb1b593c4), [draft PR #129](https://github.com/heri-espino/trendestimation/pull/129). **PDF:** [verified 10-page PDF, frozen at archival commit c69ae8c](https://github.com/heri-espino/trendestimation/blob/c69ae8c37a3963b25a59cbcb26c1958bf3c8c25d/paper/csda-unified-theory/main.pdf); [successful source-only build #42744452605](https://github.com/heri-espino/trendestimation/actions/runs/42744452605). PDF SHA-256: **bcfd91c8cacd489462448e47e17244d782dc5fb20d3ae45fc4969bc8da9b7aac**. Both deterministic algebra checks passed and no final unresolved citations or LaTeX references were reported. CAS front-matter/paragraph overfull-box warnings remain for typography review.

### 1b. Original combined CSDA theory manuscript (preserved predecessor)

**Title:** *Spectral and structured algorithms for smoothness-indexed penalized least-squares trend estimation*.

**Scope:** prescribed nonzero mean of order-d differences, shift-free SVD, normalized smoothness \(S\in[0,1]\), exact endpoints, CV/GCV/likelihood, banded Cholesky and selected inversion, time and memory complexities, algorithm decision policy, and Python library interface.

**Source:** [manuscript tree](https://github.com/heri-espino/trendestimation/tree/paper/csda-unified-theory/paper/csda-unified-theory), exact source commit [9863fd0dc8e0de48e3212cc8fce95d18bd24339d](https://github.com/heri-espino/trendestimation/commit/9863fd0dc8e0de48e3212cc8fce95d18bd24339d), [draft PR #129](https://github.com/heri-espino/trendestimation/pull/129).

**PDF:** [compiled 10-page paper](https://github.com/heri-espino/trendestimation/blob/9bac744996e092f649a0a1f100fca70bc5450cfe/paper/csda-unified-theory/main.pdf), [successful compile and proof-check run #42663001195](https://github.com/heri-espino/trendestimation/actions/runs/42663001195). PDF SHA-256: **ba774cc3bedd1938771fa08604c47a972dffe7e377378954b3dcc1b9b142bf6f**. Build log, source commit and checksums reside beside the PDF. A previous compiled version was also preserved in the branch history.

**Quality status:** compilable draft with deterministic algebra checks passed. The CAS log still has overfull-box warnings; it needs typographic and independent scholarly review. The author lists and journal declarations are provisional.

### 2. Springer Computational Statistics empirical manuscript

**Title:** *Spectral decomposition for efficient smoothing-parameter selection in penalized least squares: an empirical study of complete-criterion computation*.

**Scope:** numerical performance, actual complete-criterion evaluation, one-candidate versus grid workload, SVD-versus-banded reliability, and archived Experiment011 evidence. Not a duplication of the CSDA theoretical proof.

**Source:** research branch [paper/springer-empirical-tensor-pc08](https://github.com/heri-espino/trendestimation/tree/paper/springer-empirical-tensor-pc08), exact original source commit [d2158e065a070aa270ae866e9127b13ef4acad34](https://github.com/heri-espino/trendestimation/commit/d2158e065a070aa270ae866e9127b13ef4acad34), [draft PR #126](https://github.com/heri-espino/trendestimation/pull/126).

**PDF:** [freshly compiled 16-page PDF](https://github.com/heri-espino/trendestimation/blob/artifacts/manuscript-compile-springer-20261109/paper/builds/history/springer-20261109/main.pdf). [Successful standalone compile #42664292757](https://github.com/heri-espino/trendestimation/actions/runs/42664292757). PDF SHA-256: **1502c8f5d3172b55f3aed0fa055ce772d11de2b5622fca060acf1f8ca3bb9017**. [Persistent archival folder, log and manifest](https://github.com/heri-espino/trendestimation/tree/artifacts/manuscript-compile-springer-20261109/paper/builds/history/springer-20261109).

**Quality status:** journal LaTeX built successfully without running, repeating or modifying Experiment011. The current empirical content still requires author approval and independent statistical review.

### 3. Paper C: NGSIM vehicle-trajectory application

**Title:** *Smoothness-indexed penalized trend estimation on measured vehicle trajectories: jerk, conditional extrapolation and selection-method comparison*.

**Scope:** physical interpretation of third-difference trend estimates, chronological held-out vehicle positions, and separate polynomial extrapolation.

**Source:** [Paper C latest research branch](https://github.com/heri-espino/trendestimation/tree/research/paper-c-experiment007-smoothness-precision-calibration), original source commit [46adc304fd5a9be874239dc24f979fa03a6fa420](https://github.com/heri-espino/trendestimation/commit/46adc304fd5a9be874239dc24f979fa03a6fa420), [PR #128](https://github.com/heri-espino/trendestimation/pull/128), stacked on related Paper C PRs.

**PDF:** [freshly compiled 7-page PDF](https://github.com/heri-espino/trendestimation/blob/artifacts/manuscript-compile-ngsim-20261109/paper/builds/history/ngsim-20261109/main.pdf). [Successful standalone compile #42664361469](https://github.com/heri-espino/trendestimation/actions/runs/42664361469). PDF SHA-256: **356410c4e7e83d038a3829a68250a5e43753c399a61991b65c77a4f0402057bd**. [Persistent archival folder, log and manifest](https://github.com/heri-espino/trendestimation/tree/artifacts/manuscript-compile-ngsim-20261109/paper/builds/history/ngsim-20261109).

**Quality status:** compilable draft with overfull-box warnings. The current source also repeats one sentence about seven numerical implementations in the abstract (in paper/ngsim-jerk-case-study/main.tex); this should be corrected in the active manuscript branch before submission, not silently edited in a compilation archive. Although the branch contains later experiments, its manuscript main.tex is identical in Experiment001, 004, 005, 006 and 007 branches; newer experimental results were not silently inserted into the manuscript.

## Earlier research-paper versions (preserved, not recompiled in this batch)

| Version and role | Historical PDF | Original source |
|---|---|---|
| **CSDA Paper A:** spectral smoothness, numerical accuracy and 85-digit validation | [Existing A PDF](https://github.com/heri-espino/trendestimation/blob/main/paper/csda-spectral-smoothness/main.pdf) | [A original source](https://github.com/heri-espino/trendestimation/tree/main/paper/csda-spectral-smoothness) |
| **CSDA Paper B:** amortized algorithm complexity and selected-inverse theory | [Existing B PDF](https://github.com/heri-espino/trendestimation/blob/main/paper/csda-computational-costs/main.pdf) | [B original source](https://github.com/heri-espino/trendestimation/tree/main/paper/csda-computational-costs) |
| **Prior NGSIM application:** original five-track manuscript | [Existing earlier C PDF](https://github.com/heri-espino/trendestimation/blob/main/paper/ngsim-jerk-case-study/main.pdf) | [Main-branch source](https://github.com/heri-espino/trendestimation/tree/main/paper/ngsim-jerk-case-study) |
| **Direct spectral weights:** experimental mathematical draft | [Existing weights PDF](https://github.com/heri-espino/trendestimation/blob/main/paper/direct-spectral-weights/main.pdf) | [Draft source](https://github.com/heri-espino/trendestimation/tree/main/paper/direct-spectral-weights) |
| **Historical SN Computer Science / computational manuscripts:** preserve rather than count as approved separate submissions | [Historical full PDF](https://github.com/heri-espino/trendestimation/blob/main/paper/computational-statistics-submission/main.pdf) and [concise SNCS PDF](https://github.com/heri-espino/trendestimation/blob/main/paper/computational-statistics-submission/sncs_main.pdf) | [Historical source](https://github.com/heri-espino/trendestimation/tree/main/paper/computational-statistics-submission) |

These historical PDFs already existed in the repository. Their presence is **not** evidence of a fresh November 9 build, journal submission, independent publication, or final author approval.

## Scientific and archival boundaries

- The unified CSDA paper is a proposed theoretical consolidation, not the automatic deletion or merging of original Paper A/B histories. Its emphasis is the fixed, possibly nonzero reference mean, bounded normalized smoothing index, spectral and structured algorithms, and complete mathematical complexity.
- The Springer paper reports a separate empirical question. This compilation **did not** recompute experimental timing or publish new raw timing data.
- Paper C has a stacked history of research branches and experiments. Manuscript text remains a separately versioned object; the latest branch snapshot does not prove those later findings are in the PDF.
- All three November 9 PDFs were preserved on their respective branch histories with reproducibility metadata; **none was merged into main by the original compilation workflows**. The later integrations into main on November 14 are listed separately above.
- Successful LaTeX builds do not certify statistical claims, typography, novelty, authorship, or journal submission readiness.

## Reproducible continuation

For the original paper-only Windows build catalogue see [BUILD_ON_PC08.md](BUILD_ON_PC08.md). For scientific ownership see [PUBLICATION_MAP.md](PUBLICATION_MAP.md). For the combined manuscript, use its dedicated README, scoped AGENTS.md, proof audit and verification script.

When a paper changes, append a new dated record preserving its previous entry, source branch and exact commit, latest PDF and SHA-256, build log/artifact location, journal or intended venue, verification scope, and whether the scientific manuscript or only its experiments changed. Do not replace historical PDFs or mistake a successful build for publication.
