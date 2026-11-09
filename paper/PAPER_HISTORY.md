# Paper history: manuscript versions and verified PDF builds

This record tracks research-paper **versions**, not only journal publications. It retains source lineage, archived PDFs, compilation jobs, and the difference between a completed LaTeX build and a reviewed manuscript.

Last updated: **November 9, 2026**. Compilation only: no benchmark reruns, synthetic experiments, FHWA downloads, journal submissions, or research PR merges.

## Current compilation record

### 1. Combined CSDA theory manuscript (the successor to Papers A + B)

**Title:** *Spectral and structured algorithms for smoothness-indexed penalized least-squares trend estimation*.

**Scope:** prescribed nonzero mean of order-d differences, shift-free SVD, normalized smoothness \(S\in[0,1]\), exact endpoints, CV/GCV/likelihood, banded Cholesky and selected inversion, time and memory complexities, algorithm decision policy, and Python library interface.

**Source:** [manuscript tree](https://github.com/heri-espino/trendestimation/tree/paper/csda-unified-theory/paper/csda-unified-theory), exact source commit [9863fd0dc8e0de48e3212cc8fce95d18bd24339d](https://github.com/heri-espino/trendestimation/commit/9863fd0dc8e0de48e3212cc8fce95d18bd24339d), [draft PR #129](https://github.com/heri-espino/trendestimation/pull/129).

**PDF:** [compiled 10-page paper](https://github.com/heri-espino/trendestimation/blob/paper/csda-unified-theory/paper/csda-unified-theory/main.pdf), [successful compile and proof-check run #42663001195](https://github.com/heri-espino/trendestimation/actions/runs/42663001195). PDF SHA-256: **ba774cc3bedd1938771fa08604c47a972dffe7e377378954b3dcc1b9b142bf6f**. Build log, source commit and checksums reside beside the PDF. A previous compiled version was also preserved in the branch history.

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
- All three newer PDFs are on their respective branch histories with reproducibility metadata; **none was merged into main by these compilation workflows**.
- Successful LaTeX builds do not certify statistical claims, typography, novelty, authorship, or journal submission readiness.

## Reproducible continuation

For the original paper-only Windows build catalogue see [BUILD_ON_PC08.md](BUILD_ON_PC08.md). For scientific ownership see [PUBLICATION_MAP.md](PUBLICATION_MAP.md). For the combined manuscript, use its dedicated README, scoped AGENTS.md, proof audit and verification script.

When a paper changes, append a new dated record preserving its previous entry, source branch and exact commit, latest PDF and SHA-256, build log/artifact location, journal or intended venue, verification scope, and whether the scientific manuscript or only its experiments changed. Do not replace historical PDFs or mistake a successful build for publication.
