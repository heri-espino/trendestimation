# Final Experiment011 Springer empirical publication verification

Verified on 9 November 2026. This file records the reproducible build and
independent manual PDF review and does not authorize journal submission.

## Data audit

Canonical original report SHA-256:
c5d4898c83c731ada23a10957f80adc43616200206dc76573f365d38ba37f723

Read-only original location:
C:\Users\175199\trendestimation-PC08_add97svd_20261105_025108

Same-disk backup:
C:\Users\175199\experiment011-backups\experiment011_20261109_072910742

The preflight verified RUNNER_NAME=PCAG103A-08, correct Windows user,
original-vs-backup report checksum, all 2813 recorded jobs, 29 selected
cases, candidate run folders, file inventory and tools. The authoritative
six-stage lineage and 21 derived data/figures are archived on a permanent
source-controlled branch. GitHub actions jobs:
- Preflight: https://github.com/heri-espino/trendestimation/actions/runs/42633415411
- Initial audit (provenance; superseded Figure 2): https://github.com/heri-espino/trendestimation/actions/runs/42634293076
- Repaired audit (figures, tables, tensor): https://github.com/heri-espino/trendestimation/actions/runs/42636962129
- Repaired artifact recovery to Git: https://github.com/heri-espino/trendestimation/actions/runs/42637443986

Approved repaired derived folder:
paper/benchmarks/experiment011/pc08_empirical/derived/42636962129/

Immutable branch:
https://github.com/heri-espino/trendestimation/tree/results/experiment011-springer-derived-42636962129

Scheduling completion: 2813 distinct recorded case-seed jobs.
Process exit failures: 57.
Sparse timing cells (including explicit masked cells): 92,679.
Valid full-search status-admissible cells: 76,220.
Invalid/missing cells: 16,459.
Missing source files: 60 paths over 57 failed jobs.
Phases: 24-worker/2231 jobs, one-worker/52, 12-worker/530.
Candidate search incompleteness is not treated as success. Numeric pair
matching uses recorded double-precision selected-criterion parity only.
No large numerical experiments were repeated.

## New Springer manuscript PDF

New successful build:
https://github.com/heri-espino/trendestimation/actions/runs/42638070663

Permanent PDF/artifacts branch:
https://github.com/heri-espino/trendestimation/tree/artifacts/springer-empirical-pc08-42638070663

New PDF path in that branch:
paper/builds/pc08/springer-empirical-42638070663/springer.pdf

Canonical tracked source-branch PDF:
paper/main.pdf

Build source revision:
41e876224db79b79684df7bd9bbcf3a9fa6acb8c

Fresh PDF SHA-256:
7027b90867aad9bbeb431e9a4c6cb23ec79c26092686c4ea89e3dce9f27fee44

PDF bytes: 409,890.
PDF pages: 11.
Builder and template: scripts/build_papers_pc08.py --paper springer
using official Springer's sn-jnl class on PC08, existing Conda
trendestimation and MiKTeX. The builder forced -g compilation, not an
old tracked PDF. The manifest identifies the exact requested source
revision and its SHA-256; archived PDF binary independently matched
the manifest SHA-256 after downloading the Actions artifact.

Automated source regression tests: seven passed.
New PDF inspector: final TeX pass had no fatal errors, no overfull
horizontal boxes, no unresolved citations or references; all main
sections and references extracted, 11 pages validated. A few harmless
underfull-line warnings and Springer-class duplicate PDF destination
warnings may remain in the full log and should be reviewed by authors
before submission.

Independent manual PDF review:
- Downloaded the NEW successful Actions artifact, not the old main.pdf.
- Extracted and SHA-256 verified its PDF against the manifest.
- Rendered all 11 pages locally to PNG and inspected a complete
  contact sheet, including all figures, references and declarations.
- Inspected the empirical table page and the repaired case-level
  CV/GCV forest plot at page resolution; neither is blank or clipped.
- Confirmed four included empirical figures, readable 10-row
  matched-pair table and visible references.
- No material layout defect, clipping, black-square glyphs, missing
  citations or broken figure references detected on the final build.
- First draft's blank comparison plot and interim false positive
  citation checker were found and corrected before this build.

The new PDF was not submitted or merged. Funding, conflicts,
contributions, corresponding-author details and coauthor approvals
remain unverified; journal submission requires explicit author review.

## Exact reproduction without numerical reruns

From the repository root on the specified PC08 Windows runner in the
existing trendestimation Conda environment:

    python -m unittest discover -s paper/benchmarks/experiment011/pc08_empirical -p test_*.py -v

    python scripts/build_papers_pc08.py --paper springer --output-dir paper/builds/pc08/springer-rebuild001 --require-runner

For renewed derived tables and figures, first inspect the source
preflight.py and analyze_campaign.py, then invoke the analysis with
--original, --backup and a NEW nonexistent --out folder. Never clean,
reset or overwrite the author raw checkout or backup. Do not invoke
campaign.py or the numerical Experiment006 benchmark as part of paper
reproduction. Archive all new outputs with a new immutable run-specific
branch and preserve prior snapshots.
