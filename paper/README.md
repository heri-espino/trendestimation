## Archived Windows full preset: 80,640 search records

The author's original 80,640-cell Windows benchmark (n=24,48,
d=0..5, both fixed mu, five criteria, seven solvers, R=1/3/8,
8 search policies, two seeds, seven timing repeats) is preserved under
`benchmarks/results/full_s_search_modes/`. It is **different from the
Linux-hosted quick reference** and is never silently pooled with it.

`python paper/benchmarks/report_windows_full_s.py` verifies the
Windows dataset, generates median two-seed tables, parity and
provenance records, five Springer-width AwesomeFigures PDF+SVG pairs,
and the manuscript/web tables. The paper includes
`sections/windows_full_s_results.tex`; Sphinx includes
`docs/windows_full_s_results.rst`. Rebuilding does **not** require
rerunning the 80,640-cell experiment.

## Full S-domain seven-backend × five-criterion factorial

The manuscript additionally includes `sections/full_s_factorial.tex`
and source-traceable PDF figure pairs rendered by
`figures/render_full_s_factorial.py`. The experiment
`benchmarks/full_s_backend_criteria.py` covers S=0,
the complete decile grid, six near-one points through
S=0.999999999999 and the exact S=1 limit. For every supported
criterion, it compares seven methods including eigendecomposition,
both Cholesky variants and both reference-mean scenarios,
d=0..5. MLE d0 is deliberately labeled not applicable.
The zero/infinite endpoints are analytic and are not timed as
finite matrix factorizations. Raw invalid-criterion and numerical
instability statuses are archived instead of fabricated scores.

Run the `full` preset on Windows and archive those measurements in
a separate results branch; do not overwrite Linux reference timings.
See `notes/experiment002_full_s_factorial.md` and the website page
`docs/full_s_factorial.rst`.

## AwesomeFigures and five-criterion selection (including conditional MLE)

`sections/selection_visuals.tex` now includes five PDF charts with
identical SVG counterparts linked from the Sphinx website. The
figure generator uses the pinned `awesomefigures` package and the
measured official Springer Nature typography; raw benchmarking CSVs
are not rewritten by the renderer.

The added `paper/benchmarks/selection_coordinate_mle.py` experiment
compares **five criteria** (CV/GCV/AICc/BIC/conditional Gaussian MLE),
two fixed numeric reference means (0 and 0.15), normalized-S candidate
targets mapped once into lambda, native-S selectors that invert on each
call, and a separate log-penalty grid with the same candidate count.
Mapped lambda and native-S candidates are required to give identical
criterion scores. Scores **cannot be compared across different criteria**;
only within-criterion profiles, optimum locations and observed time
are compared. The conditional MLE is not joint estimation of mu.

```powershell
python paper\benchmarks\selection_coordinate_mle.py --preset quick --repeats 5
python paper\figures\render_awesomefigures.py --benchmarks-only
python paper\build.py --pdf --package
```

For an independent full Windows run, pass
`--preset full --output-dir paper/benchmarks/results/selection_coordinate_mle`
and keep its CSVs separate from the GitHub reference data. Archived
GitHub quick timings are labeled with their own machine metadata.
See `notes/experiment001_solver_selection_figures.md` for the full
research handoff and limitations.

## October 2026: six-solver GCV grid search included in paper

The manuscript now includes `sections/gcv_grid_reuse.tex` with numerical
tables derived from the archived **GitHub-hosted Linux quick-preset**
reference CSVs under `benchmarks/grid_reuse_reference/`. These give
actual GCV selection timings for six methods (including dense and banded
Cholesky), `d=1,2,3,4`, fixed `mu=0` and `mu=.15`, log-penalty
versus normalized-S candidate grids, and repeated independent series
with cold vs reused preprocessing. It distinguishes true GCV grid search
from the earlier fitted-trend-only and trace-only benchmarks.

These numbers are NOT the author's Windows VM full-preset run and are
not claims of universally optimal solver choices. The Windows-generated
`paper/benchmarks/results/grid_reuse/` CSVs need to be committed under
their own provenance-preserving results branch or attached for a separate
author-run revision before manuscript submission. The finite grid
endpoints in the GCV runtime comparison exclude S=0/1; other notebook
tests exercise those exact theoretical endpoints.

**Fit-only public backend default:** `fit_penalized` and
`PreparedPLSSolver` now use banded Cholesky by default, with explicit
`method="svd"` and `method="eigh"` options. The SVD-based
`TrendSmoother` and `select_lambda` remain unchanged to provide
efficient EDF, smoothness, CV/GCV/AICc/BIC, and MLE spectral computation.

Run `python paper/build.py --pdf --package` to regenerate the
actual manuscript PDF and submission ZIP from these sources after
checking the host timing labels and coauthor approvals.

# Computational Statistics manuscript — Springer Nature

This directory contains an **unsubmitted working draft** of the scientific
paper describing the `trendestimation` Python library. The intended venue
is **Computational Statistics** (Springer Nature, ISSN 0943-4062).
This is distinct from *Computational Statistics & Data Analysis* (Elsevier).

## Newly proposed factorial selection study (not yet manuscript results)

The research lecture and `notes/criterion_coordinate_factorial.md` now
specify a reproducible **3 solver × 4 criterion × 3 search-policy**
factorial benchmark, plus a separate benchmark of the public default
lambda/S selectors. The three independent backends are full SVD of
the difference matrix, symmetric eigendecomposition of `Q=D.T@D`,
and genuine banded Cholesky. Four fixed-mu criteria are CV, GCV,
AICc and BIC. The search policies use original geometric lambda
candidates, the *same* candidates reached through smoothness
inversion, and a *different* uniform smoothness grid.

**This is planned numerical evidence, not a new measured result of
the submitted working manuscript.** The new timing CSVs live under
`build/criterion-coordinate-study/` and remain host-dependent.
The current manuscript's existing tables are unchanged, as are its
careful distinctions between an exact reparameterization and
measured optimization runtime. The follow-up should be incorporated
into the manuscript only after end-to-end timings, score parity,
selected-score quality and statistical uncertainty have been
reviewed. See
[the lecture](../slides/professor_lecture/README.md) and
[experimental protocol](../notes/criterion_coordinate_factorial.md).

## Scope of the Computational Statistics paper

**Research question:** Can the normalized conditional smoothness index
`s=S(lambda)` in `[0,1]` serve as an interpretable parameter-search
coordinate for established finite-difference penalized least-squares
trends without changing their selection criteria, and what numerical
trade-offs arise from spectral inversion and repeated solver work?

**Both options are available in the library:**

```python
from trendestimation import TrendSmoother, select_lambda

solver = TrendSmoother(len(y), order=2)
by_lambda = select_lambda(solver, y, criterion="cv", mu=0.0,
                          search_space="lambda")
by_s = select_lambda(solver, y, criterion="cv", mu=0.0,
                     search_space="smoothness")
# Either result reports .lambda_ and .smoothness.
# With grid=..., entries represent the selected search coordinate.
```

The paper presents the invertible map, chain-rule CV derivative and
mapped-grid agreement tests, then studies the related computational
question through independent four-solver timings and numerical
conditioning. It **does not** claim that optimizing in `s` is faster:
end-to-end optimization times in the two search coordinates are not
part of the currently reported benchmark series.
The manuscript reports only existing and reproducible evidence:

- the established affine PLS estimator, its polynomial null space and
  normalized trace-based smoothness coordinate;
- four end-to-end solver implementations under matched workloads,
  separating full fitted curves from scalar EDF/trace evaluations;
- deterministic numerical agreement and high-order conditioning checks;
- one fixed-mean, second-order nonlinear synthetic illustration of
  **CV/GCV/AICc/BIC**, without claiming a general ranking;
- a descriptive NOAA Mauna Loa CO2 monthly-mean illustration from
  **January 1990 through September 2026** (`n=441`), comparing orders
  at the same **prescribed smoothness** (not a forecast test).

**New bounded-parameterization subsection:**
`paper/sections/smoothness_coordinate_search.tex` explains how the
existing criteria can be searched either over `lambda` or over
`s=S(lambda)` in `[0,1]`, without changing their definitions.
It includes the monotone inverse, analytical chain rule
`dC/ds=(dC/dloglambda)/(dS/dloglambda)`, CV refinement strategy,
exact endpoints and numerical inversion limitations. The paper
mentions the deterministic library regression tests that compare
mapped candidate scores and derivatives across orders, but makes
**no new runtime or predictive-performance claim** for S-space search.
The existing timing tables measure solver workloads, not an
end-to-end comparison of lambda-space and S-space optimizers.
The manuscript still retains the joint `(lambda, mu)` profile only
as an explicitly deferred theoretical extension.

For the mathematical derivation and all boundary assumptions see
[notes/smoothness_parameterization.md](../notes/smoothness_parameterization.md).
Existing numerical CSVs, vector figures, and benchmark scripts are
intentionally unchanged. After pulling the update, compile with:

```powershell
python paper/build.py --pdf --package
```

**Equations intentionally retained in the manuscript:** the full
PLS objective (Eq. `eq:objective`), affine spectral solution, normalized
smoothness index, and the mathematical identities for a possible
joint Gaussian likelihood extension: `J(lambda;mu)`, the explicit
conditional `mu_hat(lambda)`, and the scalar profile optimization for
`lambda_hat`. Those identities are visibly labelled as a **deferred
theoretical extension**, not an evaluated method in this submission.

**Not part of the current experiments or contribution claim:** a new
arbitrary-order PLS family; a validated joint `(lambda, mu)` MLE
algorithm; MLE-vs-CV/GCV/AICc/BIC comparisons; inference with a
data-dependent plug-in mean; forecast-optimal selection; GPU/energy
benchmarks. The longer `paper/sections/likelihood_mu.tex` stays in the
repository for later work but is deliberately **not included** by
`main.tex`. The public Gaussian marginal-likelihood selector is
not benchmarked or presented as a principal contribution.

An earlier version mixed a profiled-mean likelihood derivation into the
numerical benchmarking paper. This revision changes **manuscript scope
and exposition only**: no measured CSVs, fixed seeds, simulation code,
published figures, original sources, or library APIs are altered.

Submission still requires author approval of the experimental conclusions,
benchmarks' provenance, correspondence details and editorial declarations.

## Updated NOAA Mauna Loa experiment — October 25, 2026 cutoff

The primary observed-data figure now uses monthly-mean observations from
NOAA Global Monitoring Laboratory over 1990-01 to 2026-09 (441 months).
The last released complete monthly value as of the cutoff is **426.07 ppm**
for September 2026; NOAA published the update October 9, 2026.

The 441 values are frozen in `paper/figures/noaa_mlo_monthly_1990_2026_09.csv`.
First 440 months (through August 2026) follow the public
[datasets/co2-ppm NOAA mirror](https://github.com/datasets/co2-ppm/blob/main/data/co2-mm-mlo.csv).
The September 2026 value was independently checked against
[NOAA GML](https://gml.noaa.gov/ccgg/trends/). This is a pinned **derived
snapshot**, not a byte-identical reproduction of NOAA's complete 2026-10
CSV; it may require deliberate revision when NOAA updates its values.

The current example preserves `mu=0`, `S=0.86`, and difference orders
`d=2,3,4,5`. Parameters are freshly computed for 441 months, not reused
from the older 120-month experiment. Results are written by
`paper/figures/make_updated_mauna_loa.py` to
`paper/real_data_2026_summary.json` and
`paper/figures/mauna_loa_1990_2026_09.dat`, then rendered as
`paper/figures/mauna_loa_1990_2026_09.pdf`.

The old 1990–1999 example aggregated historical weekly observations from
a `statsmodels` dataset. Its data, PDF, and generator remain archived
separately. The two series are **not identical measurement inputs**, so
changes in the fitted curve must not be attributed to time extension alone.

From a fresh checkout, regenerate the data and vector figure, compile
the Springer draft, and package its sources with:

```powershell
python paper/build.py --figures --pdf --package
```

This does not rerun heavy measured timing benchmarks. For a quick
input-only check, use `python paper/figures/make_updated_mauna_loa.py
--validate-only`. A bare `--pdf` requires the new figure to have
already been rendered.

The experiment produces two-sided historical smoothing curves, not
forecasts. Annual seasonality, observation uncertainty, the 2022 eruption
site changes, and later NOAA revisions remain domain limitations.
## Cholesky and banded-solver prior art

Cortés-Toto, Guerrero and Reyes (2017, Sections 1 and 3.2) cite
Weinert's 2012 book for Cholesky-based spline algorithms but report
implementing their own PLS criterion-selection study in R. The source
does not establish which factorization their R implementation used.
The bibliography now also includes Weinert, *Fast Compact Algorithms
and Software for Spline Smoothing* (electronic edition 2012,
Springer copyright 2013; DOI
[10.1007/978-1-4614-5496-0](https://doi.org/10.1007/978-1-4614-5496-0)).
That work compares Cholesky, QR and FFT algorithms; this manuscript
does not introduce those methods.

**Benchmark naming:** the four-way comparison in
`paper/benchmarks/run_benchmarks.py` times general
`scipy.linalg.solve_banded`, *not* Cholesky. The separately
implemented full-trend `PreparedPLSSolver(method="cholesky")`
uses `cholesky_banded` and `cho_solve_banded`, but its timing results
are not part of the paper's four-way tables. See
[the provenance note](../notes/cholesky_prior_art_cortes2017.md).
Do not relabel the existing measurements as Cholesky benchmarks.

## Official December 2024 template

- `main.tex` uses `\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}`.
- `sn-jnl.cls` and `sn-mathphys-ay.bst` were checked against the author's
  uploaded December 2024 Springer Nature ZIP, **byte-for-byte** by Git blob hash:
  `d25f07cb51c685e90a4ab97e95479826289486d4` and
  `35533152b3a21c47815f2fe194fef46285c4ccd8` respectively.
- The style is **author–year**, consistent with the journal's instructions.
- The scientific model, mathematics, figures and experiments are inherited
  from the earlier paper; no new measurements were invented in changing venue.
- Previous SMCCA-specific entrypoint: `legacy_smcca_main.tex`. Original
  documentation: `README_SMCCA.md`; old `smcca.cls` is untouched.

Journal instructions: https://link.springer.com/journal/180/submission-guidelines

## Build

From repository root with your existing `trendestimation` conda environment:

```powershell
python -m pip install -e .
python -m pip install -r paper/requirements.txt
python paper/build.py
```

This creates `paper/main.pdf` using Springer Nature's `sn-jnl` class. It
generates deterministic synthetic, observational and higher-order data and
uses [AwesomeFigures](https://github.com/awesomefigures/awesomefigures) to
render standalone vector PDFs. Its `af.latex_style()` probes **the current
paper/main.tex**, not the old SMCCA document, so figure text sizes and
fonts follow the new class's physical layout. Requires `latexmk`,
`pdflatex`, and `bibtex` (e.g. MiKTeX).

To reuse results from an existing Windows benchmark run:

```powershell
python paper/build.py --render-figures --pdf --package
```

For a full fresh run, including costly benchmarks and packaging:

```powershell
python paper/build.py --all --benchmark-preset full --repeats 7
```

Additional steps:

| Flag | Effect |
| --- | --- |
| `--figures` | Regenerate deterministic data and publication figures. |
| `--render-figures` | Redraw using existing data; do not rerun experiments. |
| `--benchmarks` | Run full-fit and trace performance comparisons. |
| `--tables` | Regenerate benchmark tables from measured CSVs. |
| `--pdf` | Compile PDF from existing data/figures. |
| `--package` | Produce a **flat** Springer submission ZIP using existing PDF and LaTeX sources. |
| `--all` | Full reproducible figures + benchmarks + PDF + submission ZIP. |
| `--dry-run` | Show commands without writing files. |
| `--clean` | Clean LaTeX outputs, preserve experimental results. |

## Switching from the previous SMCCA / Boletín build

PR #29 already merged the Springer Nature `sn-jnl` manuscript into `main`.
If you still see a Boletín header, update your *local checkout*:

```powershell
git switch main
git pull --ff-only origin main
Select-String -Path paper/main.tex -Pattern 'documentclass'
python paper/build.py --pdf
```

The correct class declaration is
`\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}`.

When switching from `smcca.cls` and the old numeric `abbrv` bibliography,
the old `paper/main.aux` can contain `\NAT@force@numbers{}`. Springer
uses the author--year `sn-mathphys-ay` bibliography, so that stale auxiliary
file makes `pdflatex` fail *before* BibTeX can refresh citations.
The compiler now detects this mismatch automatically and removes only
the obsolete LaTeX/BibTeX auxiliary files. It preserves all numerical data,
benchmarks, figures and the previous PDF until the next successful compile.
You do not need to rerun `--all` merely to switch journal format.

If you inspect an old PDF after a successful build, ensure you open
`paper/main.pdf` (not an old downloaded copy of the SMCCA manuscript).

## Springer float and generated-table compatibility

The old SMCCA manuscript used forced `[H]` placement for tables and figures
and embedded a generated `tabular` source inside `\\resizebox{...}{...}{\\input{...}}`.
Both patterns can fail with the official Springer Nature `sn-jnl.cls`
(`Extra }, or forgotten \\endgroup` at `\\end{table}`).

The Springer version uses standard `[tbp]` placement and inputs
`full_fit_table.tex` and `trace_table.tex` directly. Their measured
numerical values, generated CSVs, and caption text are unchanged.
A regression test checks both the LaTeX source and (when available)
a minimal real `pdflatex` compile against the official class.

To resume after updating `main`:

```powershell
git switch main
git pull --ff-only origin main
python paper/build.py --pdf --package
```

The `--pdf` step reuses existing vector figures, benchmark tables,
and measured data. Undefined-citation warnings on the *first* LaTeX pass
are expected; `latexmk` runs BibTeX and the subsequent LaTeX passes.

## Windows CRLF and official template integrity

The official December 2024 `sn-mathphys-ay.bst` uses LF line endings.
With Windows Git `core.autocrlf=true`, the working-tree copy may contain
CRLF. A strict byte hash of that copy differs despite identical BibTeX
contents, and previously blocked `--package` after PDF compilation.

The packager now validates the original template hash, trying only a
CRLF-to-LF normalization if the raw hash does not match. The output ZIP
contains the **original verified Springer bytes**, not locally converted
lines. Substantive template modifications still fail verification.
The repository `.gitattributes` also requests LF for the `.bst` on
future checkouts and preserves the CR-only `.cls` without Git conversion.
Existing Windows checkouts are supported without discarding experiments.

To regenerate just the submission package after a successful PDF build:

```powershell
git switch main
git pull --ff-only origin main
python paper/build.py --package
```

## Flat submission source ZIP

The journal explicitly states: **do not upload LaTeX sources in subfolders**.
Running

```powershell
python paper/build.py --package
```

produces `paper/computational-statistics-submission.zip`. It includes
`main.tex`, `main.pdf`, `bibliografia.bib`, the official `.cls`
and `.bst`, referenced `sections/*.tex`, optional generated LaTeX timing
tables, and referenced vector `.pdf` figures, all **flattened at ZIP root**.
A reference-rewriting pass makes the flattened sources self-contained.
The packager checks template blob hashes, missing files and potentially
stale PDF outputs. It does **not** include ignored numeric benchmark CSVs
or private/local data by default. Consider archiving verified raw benchmark
results separately for research reproducibility.

## Journal requirements and remaining author approvals

Computational Statistics' online instructions request a 150–250 word
abstract, 4–6 keywords, author–year citations and editable LaTeX source.
The current paper includes an abstract and five keywords, and introduces
a `Declarations` section.

**Before any submission, the authors must verify and complete:**
corresponding-author email; affiliations; funding; competing interests;
author contributions; research data and code availability, ideally with
an archived code release and stable DOI; publication ethics statements;
permissions if any third-party figure is reused; novelty and statistical
significance relative to recent work. Placeholders have intentionally
not been filled with unverified statements.

The **computational** focus is critical: assess numerical stability,
setup vs repeated-use costs, scaling and hardware effects carefully.
Specialized banded solvers often outperform SVD for full fitted curves.
The work should not claim that existing Whittaker--Henderson methods,
penalized least squares, or standard cross-validation are newly invented.

The existing timing data generated by the author are in the ignored
`paper/benchmarks/results/`. Use `paper/benchmarks/README.md` for
experiment methodology and provenance. Heavy GitHub Actions continue to
run **only via manual workflow_dispatch**; regular CI is limited to tests.

Original template readme and full article authoring manual are supplied
in the uploaded Springer Nature December 2024 ZIP; the manuscript
repository stores the verified build-critical `.cls` and `.bst`.



### Experiment002 continuation: one score vs 17-point search, direct S/lambda and repeats

The full S=0..1 numerical factorial now has an additional paired
search-mode benchmark at
`paper/benchmarks/full_s_search_modes.py`.
It times one evaluation, one 17-point grid search, and the
same grid reused over independent series; compares cold vs
shared backend preparation, native S inversion on every scored
candidate, translating the S grid once, direct log-lambda
grid candidates, and *bounded local* continuous optimization
over S or log-lambda. The local optimizer is not a global
optimizer and independent grids can select different minima.
Five additional AwesomeFigures PDF/SVG charts are included in
the manuscript and Sphinx site's full-S experiment page.

The benchmark's Python/scientific outputs, validity flags,
candidate-evaluation counts and hardware provenance are
stored in `paper/benchmarks/full_s_search_reference/`
(Linux GitHub runner). Windows full runs must be committed
with separate metadata, never mislabeled as hosted results.

~~~powershell
python paper/benchmarks/full_s_search_modes.py --preset full --repeats 7
~~~
