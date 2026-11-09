# Fresh Springer PDF requested for the reviewed visual-redesign manuscript

Date: 2026-11-09. Source branch: paper/springer-empirical-tensor-pc08,
draft manuscript PR #126, stacked on still-open handoff PR #124.

This is a manuscript-only compile request, not a new experiment.

The article in paper/main.tex now uses the figure/table outputs from the
audited visualization001 source. Eight original and follow-up plots were
replaced with method-colored stacked reliability and runtime decomposition,
distribution-aware violin/box/raw paired seed evidence, detailed failure
mode bars, and an analytical memory-model graphic. Three TeX tables are
derived from the original complete-criterion tensor, including a
comment-classified Cholesky KKT and shared S-to-lambda inversion audit.

Frozen measurements: 2,813 case-seed jobs, 92,679 method/status rows, 76,220
complete rows, 9,096 banded KKT rejections, 6,336 inversion-error rows
(both backends), 970 work-budget exclusions and 57 missing jobs. No
numerical parameter searches or large experiments should be rerun.

Figures and LaTeX tables have passed PCAG103A-08 rendering,
source-count assertions and permanent branch publication:
https://github.com/heri-espino/trendestimation/actions/runs/42719614790

Build the official Springer sn-jnl manuscript on PCAG103A-08 using
the existing scripts/build_papers_pc08.py --paper springer builder.
The workflow additionally checks all new figure files and TeX
table files before compilation, executes seven regression tests,
creates a new PDF from the current exact git commit, and uploads
the PDF/log/inspection manifest into an immutable artifact branch.

Following the build, obtain the new run-specific PDF from the
artifact, check SHA-256, render and visually inspect every page.
A new PDF is required; the older 16-page PDF from previous
Actions run 42654369909 does NOT include the updated displays.
Do not merge PRs, submit to the journal, alter raw Windows
measurements/backup or modify numerical tolerances.
