# Computational-cost companion — archived evidence audit

This manuscript is a **separate companion** to
\`paper/csda-spectral-smoothness/\` (the numerical reliability and
statistical recovery study). No numerical data are recomputed.

## Primary complete timing corpus

Original source (author's Windows host):

- \`paper/benchmarks/results/full_s_search_modes/search_mode_timings.csv\`
- \`paper/benchmarks/results/full_s_search_modes/search_grid_preparation.csv\`
- \`paper/benchmarks/results/full_s_search_modes/environment.json\`

Original reporting and validation:

- \`paper/benchmarks/report_windows_full_s.py\`
- \`paper/benchmarks/windows_full_s_analysis/validation.json\`
- \`paper/benchmarks/windows_full_s_analysis/paired_grid_costs.csv\`
- \`paper/sections/windows_full_s_generated.tex\`

**Actual axes:** n = 24, 48; difference order d = 0,1,2,3,4,5;
two **fixed** reference means mu = 0, 0.15; criteria CV/GCV/AICc/BIC/
conditional marginal ML; seven backend implementations;
R = 1, 3, 8 independent series; eight search policies; cold/shared
preparation; two source seeds, seven timing repeats, single-thread BLAS.
The source has **80,640 records**, corresponding to **40,320** design
cells with two seed records, not 80,640 independent datasets.

Numerical-validity audit: 4,484 matched successful native-s versus
once-premapped penalty grid seed pairs; max observed difference in
selected s and criterion value = 0.

**One reported five-criterion case:** n=48, d=2, mu=0, R=1, SVD.
The original generated results state native s 11.234 ms versus
shared once-premapping plus five backend-only searches 3.980 ms;
ratio 2.823. The figure script recomputes these from original CSVs and
asserts agreement with those archived numbers.

**Important fairness limitations:**

- Native s and premapped s->lambda use identical seventeen penalties.
  Independently spaced log-lambda has different interior candidates.
- Bounded s/loglambda optimization is local and need not share the
  same sequence or objective optimum.
- A numerically invalid complete grid cannot win on elapsed time.
  BIC's unrestricted interpolation-limit pathology is statistical, not
  a runtime benefit.
- These timings were **not** produced on the newer GitHub runner or
  regenerated in this work.

## Independent secondary timing datasets

- \`paper/benchmarks/solver_study_runs/pilot-01/analysis/paired_comparisons.csv\`
  is the 20-independent-seed, five timing-block study of **full fitted
  trends** for SVD, eigendecomposition and banded Cholesky.
  These are not CV/GCV/ML selection times. Plot only matched
  mu=0, d=2, n=32/96/192, M=1/16/64.
- \`paper/benchmarks/results/full_fit_speedups.csv\` and
  \`full_fit_timings.csv\` include earlier complete-fit sweeps for
  n up to 400 and M up to 256, with multiple distinct backends.
- \`paper/benchmarks/results/grid_reuse/gcv_grid_timings.csv\`
  documents a separate six-solver GCV-only reuse experiment.
- \`paper/benchmarks/results/full_s_search_modes/\` is the primary
  machine's full multi-criterion and multi-policy record; the
  \`paper/benchmarks/full_s_search_reference/\` hosted quick pilot must
  **never be substituted** for its Windows timings.

These sources were produced on different systems/presets. Their raw
milliseconds are not pooled to infer a cross-host speedup.

## Missing design factors for a later combined paper

1. **d=6 comprehensive runtime**: not measured by the Windows factorial.
   The high-precision Experiment004 study covers d=5,6 for accuracy, not time.
2. **Data-dependent mu=mean(D_d y) timing**: not separately timed by
   the Windows factorial; its mu=.15 is a fixed nonzero input.
3. **Wider n and independent machine sessions** for the full seven-method,
   five-criterion matched-grid factorial.
4. **Specialized exact EDF/LOOCV computation using the selected inverse**
   to compare with Weinert-style structured GCV on equivalent candidates.
5. **Numerical accuracy versus wall time** for the same end-to-end
   selection workflows. Current high-S numerical failures are from a
   different validation experiment, not directly comparable timings.

## Bibliography

The document cites the foundational Whittaker/Guerrero smoothness
literature, Cortes-Toto et al. for criteria, Weinert for structured
Whittaker-Henderson algorithms, and Biessy for a modern treatment. The
bibliography is shared with the numerical companion to facilitate the
eventual combined paper.

## Rebuild

\`python paper/csda-computational-costs/render_figures.py\` reads the
original raw CSVs but **does not execute numerical experiments**.
Figure PDFs are generated using the exact CAS template's measured fonts,
and the original \`paper/csda-spectral-smoothness/publication_style.py\`
as a starting point, adapted to this companion. TeX PDF + editable PGF
+ SVG previews and hashes are archived by GitHub Actions.
