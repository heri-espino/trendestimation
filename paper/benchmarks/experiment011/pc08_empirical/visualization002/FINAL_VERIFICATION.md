# Final AwesomeFigures publication and integration QA

Verified on 14 November 2026 against immutable Experiment011 results.

## Source and reproducibility

- Feature branch: `paper/experiment011-awesomefigures-gallery`
- Draft visualization integration PR: https://github.com/heri-espino/trendestimation/pull/135
- Intended integration base: `paper/springer-empirical-tensor-pc08` (manuscript draft PR #126); NOT `main`
- Original 2813 case-seed jobs and frozen sparse timing tensor remain unchanged.
- Tensor SHA-256: `a25f674981b1c20df678638287df289c4d888ae62417a3f58ed8a6b2a08fce13`
- 92,679 timing/status rows, 76,220 accepted, 9,096 banded post-solve KKT rejections, 6,336 smoothness inversion-error rows, 970 work-policy exclusions, 57 original job failures.
- The chart scripts read existing derived CSV/JSON and never fit a model, select another smoothing parameter, resample synthetic data, rerun a benchmark or change numerical tolerances.
- Seed-level paired log ratios are reduced within independent seeds. The old 700-resample independent seed-cluster confidence intervals are reused unchanged. Failed or incomplete grids never win comparisons.
- Explicit scientific distinctions: SVD does not execute the same banded KKT gate; memory curves are code-defined allocation estimates, not measured RSS; different worker concurrency phases are not interchangeable isolated latencies.

## Generated deliverables

- 42 AwesomeFigures figure sets, each with a vector PDF, SVG and PNG preview.
- Nine primary paper figures use the real AwesomeFigures 0.1.0 `latex_style` API, pdfLaTeX+PGF and the canonical Springer `sn-jnl` text-width of 372pt, with font sizes vetted at full insertion width.
- 33 additional supplementary vector figures in a standalone 33-page combined figure gallery.
- Every figure retains title, scientific caption/description and SHA-256 in `figure_manifest.json`.
- **All nine primary typographic audit sidecars report `exact_tex_preamble=true` and empty `audit_warnings=[]`.** The first generation was explicitly revised after finding physically oversize canvases; print-width rescaling and targeted visual fixes eliminated those warnings.
- The existing three evidence-derived LaTeX tables remain unchanged; no new numerical measurements were invented.

## Exact runner verification

Final successful Windows action:
https://github.com/heri-espino/trendestimation/actions/runs/43630631770

- Self-hosted Windows 11 runner: `PCAG103A-08`; Conda `trendestimation`.
- All existing Experiment011/KKT source-only numerical unit tests passed (10/10).
- AwesomeFigures figures generated and original input hash asserted.
- Canonical Springer PDF rebuilt using existing `scripts/build_papers_pc08.py --paper springer --require-runner` with new nine figures; no LaTeX errors, missing citations/references or overfull boxes.
- PDF source commit: `2f70f4349a0623b21308062e3ad4c54164ccb486`.
- New Springer PDF: 19 pages, 868,088 bytes, SHA-256 `3c9b1e7a8359e0970678fd8d9f271da4e05729d5b7876f69ba3c21426a258471`.
- Immutable archive ref: `artifacts/springer-awesomefigures-43630631770`
- PDF path in archived repository: `paper/builds/pc08/springer-awesomefigures-43630631770/springer.pdf`
- Figure gallery: `paper/benchmarks/experiment011/pc08_empirical/visualization002/supplementary_figure_gallery.pdf`
- Downloaded and independently verified the source-run PDF by SHA-256 and 19-page PyMuPDF count; supplementary gallery has exactly 33 pages.
- Rendered and reviewed the manuscript contact sheet and pages containing the final full-grid completion, fourth-order reliability, single-to-grid crossover and memory graphics. All updated main figure typography sidecars have no remaining audit warnings.
- Original raw checkout and backup unchanged, unrelated manuscripts and concurrent branches untouched.

## State and next actions

The user explicitly requested merging the visualizations into the repo. Merge only scoped PR #135 into the existing Springer manuscript branch after verifying its current head SHA and mergeability. Manuscript PR #126 and handoff PR #124 remain separate and MUST NOT be merged or submitted merely because the figure-only sub-PR was integrated. Authors, declarations and raw-data permissions still require verification before publication.
