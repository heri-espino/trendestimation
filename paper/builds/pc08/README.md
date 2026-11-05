# Verified PC08 manuscript compilation — 5 November 2026

The original university workstation `PCAG103A-08` compiled **seven distinct
LaTeX manuscript entrypoints** using the existing `trendestimation` Conda
environment and its installed MiKTeX / latexmk toolchain. This directory
preserves the **unaltered** build manifests, logs, and archived PDF copies.

| GitHub Actions run | Manuscripts | Result |
| --- | --- | --- |
| [41985165397](https://github.com/heri-espino/trendestimation/actions/runs/41985165397) | CSDA A, CSDA B, NGSIM, direct spectral weights, historical Springer and historical SNCS | 6 passed; canonical Springer failed |
| [41991642006](https://github.com/heri-espino/trendestimation/actions/runs/41991642006) | Canonical Springer retry after missing-input restoration | 1 passed |

## Why the first Springer compilation failed

The first log identifies missing `paper/criteria_table.tex` in
`paper/main.tex` around line 242. A complete review of the manuscript
entrypoint and section inputs also identified missing
`paper/figures/mauna_loa_1990_2026_09.pdf`. The fixed builder restores
the numerical table from its tracked `.example.tex` and reconstructs
the NOAA figure from a frozen 441-month CSV only when these inputs
are absent. The recorded original results were not remeasured.

## Validity and source provenance

- The seven canonical manuscript PDFs are committed at their original
  locations under `paper/`. The `paper/builds/pc08` folders additionally
  retain the exact per-run PDF copies, logs, and hash manifests.
- The first manifest **correctly retains its one failed Springer attempt**;
  its failure has not been rewritten to success. The second manifest
  documents the successful replacement independently.
- Only the canonical Springer table, NOAA vector figure, derived `.dat`,
  and source-summary JSON were added to restore reproducible compilation.
- The two historical Springer manuscripts are retained archives; they
  must not be conflated with new submissions.
- The numerically heavy Experiment011 or other benchmark runs were
  **not** executed by either compilation.

Review the fix separately in [PR #116](https://github.com/heri-espino/trendestimation/pull/116).
Do not merge its temporary one-shot workflow triggering branches into
`main`. Generated PDFs and checksums do not certify scientific claims
or manuscript readiness for journal submission.
