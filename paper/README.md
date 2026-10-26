# Computational Statistics manuscript — Springer Nature

This directory contains an **unsubmitted working draft** of the scientific
paper describing the `trendestimation` Python library. The intended venue
is **Computational Statistics** (Springer Nature, ISSN 0943-4062).
This is distinct from *Computational Statistics & Data Analysis* (Elsevier).

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
