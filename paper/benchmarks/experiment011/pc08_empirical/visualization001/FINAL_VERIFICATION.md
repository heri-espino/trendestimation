# Springer visual redesign: final compilation and PDF verification

Date: November 9, 2026. The official Springer Nature sn-jnl
Computational Statistics draft has been rebuilt with the eight revised
figures and three improved LaTeX tables. This is a source-and-figure
editorial revision, **not** a rerun of numerical experiments.

## Authoritative builds and source provenance

- Frozen Experiment011 empirical data source:
  results/experiment011-springer-derived-42636962129
- Frozen original final numerical report SHA-256:
  c5d4898c83c731ada23a10957f80adc43616200206dc76573f365d38ba37f723
- Visual postprocessing script:
  paper/benchmarks/experiment011/pc08_empirical/visualization001/render.py
- Successful figure/table generation:
  https://github.com/heri-espino/trendestimation/actions/runs/42719614790
- Immutable figure/table archive:
  results/experiment011-visualization001-42719614790
- **Successful fresh Springer compilation**:
  https://github.com/heri-espino/trendestimation/actions/runs/42720035896
- Exact manuscript source SHA used in this compile:
  632a32300435348c3af1c351273d760f8da66f7a
- Immutable compiled artifact branch:
  artifacts/springer-empirical-pc08-42720035896
- Final compiled PDF on this branch:
  paper/builds/pc08/springer-empirical-42720035896/springer.pdf
- Final PDF SHA-256:
  d2a91de05c4399560efab435804ade3373900d2f39c18be18374452054b84044
- Final PDF size: 702,329 bytes.
- Final PDF pages: 16.
- Draft PR: #126, base docs/experiment011-completion-handoff;
  still unmerged and no journal submission.

## Acceptance and graphical QA

1. Figure generation used the independent frozen numerical tensor
   and pairwise timing evidence, not new benchmark trials.
2. The figure-derivation job verified 92,679 timing/missingness rows,
   76,220 complete outcomes, 9,096 banded post-solve KKT rejection
   rows, 6,336 smoothness-inversion failure rows, 970 work-budget
   exclusions, and 57 unavailable job records.
3. All eight vector PDF figures and PNG previews and three numerical
   LaTeX tables were generated, committed and archived.
4. The tables use valid LaTeX double-backslash row endings and retain
   sample sizes, random-seed clusters, geometric time ratios and
   their original 95% cluster-bootstrap intervals.
5. The workflow inspected that all new figure, TeX table and
   evidence-manifest files existed before compiling.
6. Seven source-only numerical-ingestion regression tests passed.
7. A fresh source-SHA-bound Springer sn-jnl build succeeded
   with no TeX fatal errors, undefined references/citations or
   overfull horizontal boxes. Two harmless underfull-line
   warnings remain in the final TeX log.
8. Downloaded the new run-specific PDF, independently recomputed
   its SHA-256 and confirmed agreement with the build manifest.
9. Rendered all **16 pages** using the PDF rendering tool, assembled
   a complete contact sheet, and visually inspected the graphics
   and tables at individual-page resolution. All displayed
   figures and tables were present and readable, with no missing
   figures, obvious overflow, or material clipping.
10. The article retains the rigorous conditional recommendation
    that spectral decomposition is preferred for repeated full
    smoothing-criterion searches at memory-feasible lengths;
    banded computation remains advantageous for isolated
    evaluations or large memory-constrained problems.

## Scientific reporting details

- Stacked bars are method-colored; patterns separate post-solve
  KKT rejection, smoothness-inversion failure and work-budget
  exclusions. An SVD inversion error is not relabeled as a
  Cholesky KKT error merely because its code status says
  numerical_failed.
- Full-grid timing distributions first average paired log time
  ratios within the independent random-seed cluster. Violin
  densities are descriptive, not independent repeated trials.
- The figure depicting coordinate-reuse distributions pools
  heterogeneous admissible configurations and is not a
  randomized method-level effect estimate.
- The workload decomposition stacks component **medians**
  and does not claim their sum is the median total cold time.
- The memory figure depicts conservative code-defined storage
  allowances, **not** observed peak resident memory or
  memory failures.
- A completed SVD criterion does not imply independent
  high-precision forward-error certification. The spectral
  and banded implementations do not execute identical
  KKT rejection gates.

## Reproduction and future-agent handoff

From the repository root (existing Conda trendestimation environment):

    python paper/benchmarks/experiment011/pc08_empirical/visualization001/render.py

    python -m unittest discover -s paper/benchmarks/experiment011/pc08_empirical -p "test_*.py" -v

On the scoped PCAG103A-08 Windows runner:

    python scripts/build_papers_pc08.py --paper springer --output-dir paper/builds/pc08/verification003 --require-runner

Read the existing AGENTS.md, paper/AGENTS.md, paper/SESSION_HANDOFF.md,
AI_HANDOFF.md and prior numerical-source documentation before future
modification. Retain original numerical experiments and their archived
figures for reproducibility. Do not merge the PR or submit the paper
without explicit author approval of authorship and declarations.
