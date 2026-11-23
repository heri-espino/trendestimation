# Paper C — lossless reconciliation of PR #152 and merged PR #156

**Date:** 2026-11-22. **Repository:** heri-espino/trendestimation.
**Purpose:** integrate overlapping independent scientific/editorial improvements without dropping the older manuscript, figures, results or historical research notes.

## Merge ancestry and ownership

- Older PR #152 original head: `ae0f946666e2e09e03fff7c3784d866035556a09`. It contains the 17-page source-matched November 19 Paper C alternative, preserving the full historical Guerrero/Cortés-Toto original-versus-rank normalization, the six qualified PLS design properties, the original source audit, algebra tests, and edits to the abstract, Introduction, Methods and Discussion.
- Merged PR #156 mainline parent: `aa12b52c719002934a659c6c91fa4f417ea40ae4`. It includes a previously verified 16-page Paper C PDF with the conditional posterior-jerk covariance, revised Springer 20-page PDF, revised unified CSDA 19-page PDF, new algebraic tests and provenance documents.
- The reconciliation is a **real two-parent merge commit** on PR #152, preserving both commit histories. Its tree is based on the up-to-date `main` tree: all current Springer, CSDA, research data, figures, frozen experiments, source code, documents and current compiled PDFs remain present.
- The Paper C abstract, Introduction, Discussion, source audit and historical regression test come in full from PR #152. Methods retain PR #152's original index and design-property treatment and incorporate PR #156's additional conditional Gaussian precision, posterior covariance and physically scaled jerk-covariance identity, without duplicated/contradictory definitions.
- The two historical AGENTS.md and Paper C README addenda from PR #152 are prepended to the mainline documents, rather than replacing new mainline material with an old snapshot. The November 20 continuation and newer PR #156 notes remain untouched.

## Historical manuscript binaries and source preservation

- PR #152 validated 17-page PDF is retained by [PC08 Actions #44490200179](https://github.com/heri-espino/trendestimation/actions/runs/44490200179) and the immutable `results/paper-c-pdf-pc08-44490200179-a1` archive, SHA-256 `409096cb0a9d75195c60da263070a27ec109db779b8f3d007a84ae77ca0357c3`.
- PR #156 validated 16-page PDF is retained by [PC08 Actions #45002709460](https://github.com/heri-espino/trendestimation/actions/runs/45002709460) and `results/precision-springer-ngsim-pc08-45002709460-a1`, SHA-256 `da2a8ffa747a98bef9d7d3ea690b425aa2631d6e06bcd30f050f1db7e7d3a5f3`.
- The previously verified 15-page Paper C and 12-page AwesomeFigures atlas are preserved in the November 19 archive; frozen Experiments004--008, original synthetic results, and real NGSIM records are never regenerated.

## Verification and remaining release gates

This manuscript-only integration does **not** introduce an experiment. It must pass both existing Paper C normalizations/trace tests and the cross-paper covariance tests, repository CI on Python 3.10/3.12 and Sphinx, a source-matched Windows PC08 TeX rebuild, and the 16-file SHA-256 ledger updated from **Git LF blobs**, not a Windows CRLF checkout. The historical 17-page and 16-page PDFs cannot be substituted for the integrated build. The rebuilt PDF is archived under a fresh results branch with its source commit, build log, hash manifest and publication checksum. Human page-by-page typography review remains a separate final editorial gate if not performed.

No coauthor approval or journal submission is implied. The source and verified historical PDFs remain available regardless of any compile issue.


## Integrated 17-page PDF verification (2026-11-22)

**Integrated Paper C source-matched release (2026-11-22):** [Actions #45088143254](https://github.com/heri-espino/trendestimation/actions/runs/45088143254) compiled the combined manuscript on PCAG103A-08 as **17 pages, 908993 bytes**, PDF SHA-256 `9a41b321d80a79621ee54dac5fa82bb88c82c76982dd6147ae10d7517348f8a5`; all scoped numerical identity tests passed. [Immutable complete build log/PDF/source fingerprints](https://github.com/heri-espino/trendestimation/tree/results/paper-c-integrated-precision-45088143254-a1/paper/builds/paper-c-integrated-precision-45088143254-a1). Its canonical 16-file checksum ledger has been regenerated using Git LF source bytes and passed to repository CI for final confirmation. Original 17-page PR #152 and 16-page PR #156 PDFs, Figure Atlas and all experiments are retained. No new simulation, independent true NGSIM jerk, validated interval coverage, journal submission or new page-by-page visual review is claimed.

The compiled source commit is `4e9a3a18fefeebfa0113094a75b7ebba2d2b0c73` and the output commit is `1f84beb7dbaaff1e0f058c08a1b4766a6f5173e6`. The paper remains an unsubmitted draft. The previous alternate 17-page PDF was produced by different original source and remains separately immutable; equal page counts do **not** imply identical source or output.
