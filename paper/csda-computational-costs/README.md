> **Current source:** `main.tex` and `main.pdf` are CSDA Paper B theory from PR #109.
> The older empirical manuscript from PR #100 is retained in Git at
> `5eb5b30ae8a172dc1d56f2d46f1024c6ce9370ab`; its sections and evidence are
> historical material for the Springer track, not a replacement for Paper B.
> Read `../PUBLICATION_MAP.md` and `../SESSION_HANDOFF.md` first.

## Revised research article with four verified figures

Paper B remains **theory-first**, with two carefully bounded illustrations.
The main draft now includes `sections/decision_examples.tex`:
a plain-language solver-regime comparison with exact CV versus scalar
criterion distinctions; compact exact-solver and hybrid tables; and
two theoretical work-count figures (NOT calibrated runtimes).
It also includes one reproducible, matched, one-worker BIC example and
one real FHWA NGSIM vehicle trajectory illustrating $d=3$,
training-only `mu='data'`, a fitted trend and a **separate**
local-polynomial forecast. The latter is not a native PLS forecast,
does not measure ground-truth jerk, and does not substitute for the
independent NGSIM application study.

Run `python paper/csda-computational-costs/render_theory_figures.py`
with the pinned AwesomeFigures dependency and original CAS class.
It produces `theory_regime_map`, `theory_cost_curves`,
`matched_bic_timings` and `ngsim_jerk_application` in PDF/PGF/SVG
plus `theory_awesomefigures_manifest.json` and
`theory_figure_sources.json`. The GitHub Actions workflow runs
this exact script, validates 48 archived rows and all source
provenance, and commits the compiled manuscript and vector figures.

All 48 records were copied, without timing recomputation, from
`results/experiment010-uncapped-PCAG103A-08-20261103T222938857Z-shard0-offset20`
to `data/experiment010_matched_three_methods.csv`.
The values represent **one worker, one BLAS thread**, two repeats
per workload and method, and only n=64/d=1/BIC/mu=data.
These outcomes do not identify a universal SVD/Cholesky crossover.

The independent NGSIM source in
`paper/ngsim-jerk-case-study/` selects, by training-only GCV,
`S=0.40` for the illustrated track and origin; use the already
archived real track, never fabricated observations or future leakage.
This Paper B illustration is not a substitute for the third paper.

# Current Paper B — theoretical computational analysis (November 2026)

**Entry point:** `main.tex`, title *Amortized complexity of smoothness-indexed
penalized least squares*. This is a **theoretical
CSDA working manuscript**. Read [THEORY_HANDOFF.md](THEORY_HANDOFF.md)
for the full proof/validation contract.

The principal contribution is the workload-dependent mathematical model

\[
T_{\mathcal A}(n,d,M,R,\mathcal C;\varepsilon,\theta),
\]

and its proof-based decomposition into mapping preparation, factorization,
conditional criterion diagnostics and reuse across smoothing candidates
and independent observed series. The paper proves a banded
Gaussian likelihood log-determinant identity, gives full-SVD versus
banded-selected-inverse arithmetic and memory bounds, an exact
first-difference cosine-eigenvalue formula, and the sign conditions for
a conditional calibrated crossover. These are not machine timings.

**The original empirical manuscript sections and all six AwesomeFigures
figure families remain in the repository unchanged**, but the
theoretical `main.tex` no longer inputs the historical
`sections/benchmarks.tex`, `sections/results.tex`,
`sections/experiment006_design.tex` or
`sections/experiment006_status.tex`.
The newly completed three-backend, one-worker Windows comparison is
preserved on the user's timestamped GitHub results branch and documented
in THEORY_HANDOFF.md as evidence for a **different implementation/runtime
Springer manuscript**. No new benchmark is needed to compile Paper B.

## Reproduce theory checks and the PDF

From the repository root:

```powershell
conda activate trendestimation
python paper/csda-computational-costs/verify_theory.py
Copy-Item paper\els-cas-templates\cas-dc.cls,paper\els-cas-templates\cas-common.sty,paper\els-cas-templates\cas-model2-names.bst -Destination paper\csda-computational-costs
Push-Location paper\csda-computational-costs
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
Pop-Location
Start-Process ".\paper\csda-computational-costs\main.pdf"
```

The dedicated [CSDA theory build](../../.github/workflows/csda-computational-theory.yml)
verifies mathematical identities and compiles the Elsevier CAS PDF
without rerunning statistical simulations, benchmark workflows or
the historical timing renderers. Its committed PDF and SHA256 input
manifest remain on the paper branch.

The author metadata and disclosures remain provisional. A mathematical
theory paper still requires novelty assessment against Weinert (2007),
Erisman--Tinney (1975), and Biessy (2026) before journal submission.

---

## Preserved historical computational-timing manuscript documentation

The remainder of this file documents the **prior empirical draft**,
whose sources and figures are retained for reproducibility but are
no longer input by the current theoretical `main.tex`.

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


## Expanded four-workload CSDA research draft — November 2026

The **paper/csda-four-workload-20261102** branch develops this existing
two-column Elsevier manuscript into a broader computational-methods paper.
The original historical figures and raw timing files are kept unchanged;
the expanded manuscript is **not** a claim that the new 7-length ×
6-difference-order × four-smoothness-grid factorial has been measured.

New LaTeX material:
- \`sections/structured_criteria.tex\`: banded selected inverse,
  exact fixed-mean CV leverages, EDF, direct nonzero-mean RHS,
  honest sparse and PCG hybrid costs, theoretical complexity.
- \`sections/experiment006_design.tex\`: the four crossed workloads,
  7 sample lengths, d=1..6, zero/nonzero fixed mu, low/high magnitude,
  all 5 criteria, all 4 S grids (including exact S=1), matched
  direct-S versus once-translated-lambda candidate comparisons.
- \`sections/experiment006_status.tex\`: evidence matrix clearly
  separating measured historical d<=5/n<=48 results from
  pending Experiment006 computational measurements.
- \`main.tex\`, \`discussion.tex\`, \`references.bib\`: revised
  title, abstract, interpretation and verified selected-inverse
  reference (Erisman and Tinney, 1975).

**Historical status, superseded by the newer completed bounded Experiment010 results reported below:** the 80,640 original historical rows remain independently archived.
The initial PCAG103A-08 pilot from separate Experiment006 PR #95 is not
promoted into a publication result without its raw data and validation.
Fast fit-only timing is not substituted for complete CV/GCV/AICc/BIC/MLE
pipeline costs.

The original six AwesomeFigures TeX-native PDF/PGF/SVG figure families
are reused without re-running experimental simulations or drawing
invented timing plots. \`csda-four-workloads-paper.yml\` compiles
the same author-supplied Elsevier CAS double-column template and
archives the revised paper PDF/source as an independent branch artifact.

The primary unresolved publication steps are: complete matched
factorial measurements and quality gates, paired CPU timing analysis
with confidence intervals, high-order/nonzero-mean S=1 numerical
validation, cached S-grid mapping at large n, and author approval.


## Completed bounded empirical manuscript — November 2026

The paper now incorporates the real Experiment010 ten-policy numerical
comparison, rather than describing it only as a planned factorial.
The LaTeX section is sections/experiment010_observed.tex, with
a revised title, abstract, discussion and historical-status bridge.
The current immutable evidence ledger is OBSERVED_RESULTS_SNAPSHOT.md.

**Observed corrected-source study:** 450 method–case attempts, 5,570
successful raw timing records, 5,480 selected-criterion score
agreements, 18 disagreements, 72 without a valid spectral reference,
and 1,102 failed/partial records. These are related timing observations,
not independent problems or universally precision-certified solutions.
Original and corrected MLE results remain separate.

The manuscript includes all ten existing complete-criterion policies
(guarded is composite; optional CHOLMOD was unavailable), uses matched
S candidates under three reference-mean policies (zero, empirical
mean of observed differences, fixed 0.15), and presents the measured
n=256 one-S vs 100-S GCV winner reversal. The independent 85-digit
Experiment006 fit audit remains distinct from full-criterion timing.
No automatic solver dispatcher, empirically calibrated cost surface
or full 50,400-case factorial completion is claimed.

**Status:** completed, reproducible research snapshot; not
journal-submission ready. Both authors must approve author order,
declarations and interpretation. The existing historical figures
and raw sources are retained and no numerical benchmarks are rerun
for this paper build. PDF generation uses the same author-supplied
Elsevier CAS template on GitHub-hosted Linux; no university Windows
installation or administrator access is needed.
