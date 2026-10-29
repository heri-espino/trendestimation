# Computational costs of smoothness-indexed PLS

**Independent, pre-submission computational companion** to the separate
numerical-reliability paper under \`paper/csda-spectral-smoothness/\`.

## Contribution

The paper compares the arithmetic and memory costs, original measured
runtime and amortized search costs for full SVD, eigendecomposition, dense
solves, dense Cholesky, general banded solves and banded Cholesky. It
distinguishes one fit, one CV/GCV/AICc/BIC/ML evaluation, full 17-point
grid search, continuous local minimization and reuse across independent
series. It uses the interpretable normalized coordinate \`S in [0,1]\`
for any \`1 <= d < n\` and any fixed reference mean of differences,
including nonzero means. It makes the distinction between fixed nonzero
mu and sample-derived mu explicit.

## Source data

See \`SOURCE_AUDIT.md\` and the original committed timing CSVs in
\`paper/benchmarks/results/full_s_search_modes\` and
\`paper/benchmarks/solver_study_runs/pilot-01\`. Existing
\`paper/sections/windows_full_s_generated.tex\` is a source for
cross-checking the five-criterion case. All primary data remain
unchanged. The original Windows full run has 80,640 records, but
covers **d=0,...,5**, not d=6; and mu=0/0.15 is **fixed**,
not the observed-difference mean.

## Build locally (PowerShell)

From the repository root:

\`\`\`powershell
conda activate trendestimation
python -m pip install -r paper/requirements.txt
Copy-Item paper\els-cas-templates\cas-dc.cls,paper\els-cas-templates\cas-common.sty,paper\els-cas-templates\cas-model2-names.bst -Destination paper\csda-computational-costs
python paper\csda-computational-costs\render_figures.py
Push-Location paper\csda-computational-costs
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
Pop-Location
Start-Process ".\paper\csda-computational-costs\main.pdf"
\`\`\`

Requires the full pdflatex/BibTeX installation and the pinned
AwesomeFigures package. The GitHub Actions workflow
\`.github/workflows/csda-computational-costs.yml\` performs the complete
CAS double-column compilation and saves the PDF, editable TeX/PGF
figures, SVG previews and SHA256 provenance in the repo.

## Figures

The main comparison now uses **d=3** and only two statistically matched policies
on the *same complete* 17-point S grid: native repeated inversion and
one cached S-to-lambda mapping. The conventional independently sampled
log-lambda grid remains as a diagnostic in the raw benchmark archive,
but is not presented as an equivalent or equally interpretable grid.

1. Normalized smoothness versus internal lambda across d=1,...,6.
2. Analytical physical-derivative interpretation at S=1: d=1,...,4,
   including d=3 with fixed zero versus nonzero third differences.
3. Five criterion timings from original Windows data at d=3,
   displaying matched full-S grids only. The paired timing table
   is generated automatically into sections/generated_d3_timings.tex.
4. One GCV evaluation, full grid and eight independent grids at d=3,
   across numerically valid solver implementations.
5. Cold/shared spectral reuse across the archived d=1,...,5 orders.
6. Independent paired 20-seed SVD versus banded-Cholesky full-fit study
   across measured d=1,2,3,5 at n=96, M=16. No d=4 interpolation.

The Gaussian likelihood criterion profiles observation-error variance
under a Gaussian model of the dth differences. It is a reduced-coordinate
marginal variance-component likelihood, not maximum likelihood of tau
at a given lambda, nor joint ML estimation of mu when mu='data'.

## Scientific boundaries

- These are machine-specific timings, not proofs of which method is
  always fastest.
- S and lambda label the **same estimator** at corresponding penalties;
  measured speedups arise from caching.
- Independently sampled log-lambda grids are not statistically matched
  to a uniform S grid. Continuous optimizers are local.
- For a fair full-criterion backend comparison, EDF and LOOCV leverage
  work must be included. Fit-only banded Cholesky is not an exact trace
  implementation by itself.
- BIC's mathematical interpolation-boundary issue remains documented
  in the numerical companion.
- The next joint accuracy-versus-time paper needs actual d6 and
  data-derived mu timing, broader series lengths and a specialized
  structured selected-inverse baseline.
