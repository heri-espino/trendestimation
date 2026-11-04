# Short SN Computer Science article and cached-data dashboards

This is a **separate, concise ORIGINAL RESEARCH manuscript** targeting
SN Computer Science. The full Computational Statistics draft remains at
`main.tex`, unchanged, with all derivations, 80,640-search figures,
case dashboards, and archived experiments. `sncs_main.tex` selects
only the most informative results.

## Based on three published SN Computer Science papers

These examples were inspected as journal-specific communication
references, **not** as direct prior art for PLS theory:

- Berns, Hüwel and Beecks (2022), `10.1007/s42979-022-01186-x`:
  runtime and error together, compact algorithm comparison tables
  and explicit experimental conditions. It is a review article.
- Gauss, Brandin, Heberle and Löwe (2021),
  `10.1007/s42979-021-00814-2`: a smoothing problem, alternative
  filters, quantitative trade-offs and practical illustration.
- Cardoso, Hart and Pitt (2025), `10.1007/s42979-025-04056-4`:
  explicit algorithmic workflow and coherent baseline comparisons.
  Its domain is classifiers rather than numerical smoothing.

The short article retains four results: (i) the mathematical
normalization and inversion of S(lambda), (ii) paired solver-speed
uncertainty, (iii) float64 inversion algorithms, and (iv) one compact
real-data dashboard across selectors and difference orders.

The original 24-panel CO2/FEDFUNDS dashboards for each mean specification
are **supplementary**; the main article contains a single 2x2 summary.

## Windows PowerShell — run the code, NOT the experiments

In the repo root, after checking out this PR branch:

~~~powershell
conda activate trendestimation
python -m pip install -e ".[dev,plot]"
python -m pip install -r paper/requirements.txt
python -m pip install streamlit

# Generate publication-size figures from ONLY SAVED result JSON.
python paper/computational-statistics-submission/sncs_dashboard.py
python paper/computational-statistics-submission/sncs_dashboard.py --mu data

# Interactive supplementary research browser
streamlit run paper/computational-statistics-submission/sncs_dashboard_app.py

# Compile the shorter manuscript and ASSERT the PDF exists.
# Works with MiKTeX + pdflatex/BibTeX; latexmk+Perl is optional.
powershell -ExecutionPolicy Bypass -File .\paper\computational-statistics-submission\build_sncs.ps1

# Commit paper, figures, dashboard code, provenance, and compiled PDF.
git add .
git commit -m "paper: render concise SNCS article and cached-data dashboards"
git push
~~~

### If the PDF did not appear

Earlier Windows runs showed `latexmk` returning **no visible output**,
even though `sncs_main.pdf` did not exist; checking only `$LASTEXITCODE`
was therefore insufficient. The new `build_sncs.ps1`:

1. Checks all required figures, Springer class, BibTeX file and tables.
2. Displays exactly which `pdflatex`, `bibtex`, `latexmk`, and `perl`
   binaries are found in PATH.
3. By default uses `pdflatex`, `bibtex`, and two further LaTeX passes
   directly, bypassing potentially silent `latexmk` Windows wrappers.
   An explicit `-UseLatexmk` switch is available when latexmk and Perl work.
4. **Fails if the PDF does not exist or is empty**, prints the last 55
   lines of `sncs_main.log`, and opens the PDF only after success.

No admin rights are required to install MiKTeX for the current Windows
user. If needed, install Perl into Conda with
`conda install -c conda-forge perl`, but it is **not needed** for the default direct build. When diagnosing TeX PATH, run:

~~~powershell
Get-Command latexmk,pdflatex,bibtex,perl -All -ErrorAction SilentlyContinue |
    Select-Object Name,CommandType,Source
Test-Path .\paper\computational-statistics-submission\sncs_main.pdf
~~~

Only compile/render code runs; the completed benchmarks remain untouched.

`sncs_dashboard.py` produces `figures/sncs_compact_dashboard.pdf`,
SVG and PNG, and the supplementary `sncs_tradeoff_*.{pdf,svg,png}`.
The app reads `data/{co2_full,co2_recent,fedfunds_full}_dashboards.json`,
selects an already archived `lambda` and `mu`, and performs *only a
deterministic trend reconstruction* for the selected case. It never
calls the method-selection criteria, optimizers, root-inversion
benchmarks, random simulations, or data downloaders.

We deliberately do **not** import experimental functions from
`run_final_vm_study.py` or `make_selection_dashboards.py` for
selection. Numerical inputs are verified with SHA-256 digests before
and after figure generation. The complete original experiments and
corresponding timestamps remain under `research/final_vm/` and
`paper/benchmarks/`; do not rerun them to revise graphics.

## Editorial checks before submission

- Confirm author emails, final author order, affiliations, funding,
  contributions and competing-interests declarations.
- Verify the interpretation and limitations of the reported
  sign-flip/Holm tests and pointwise bootstrap intervals.
- Check that chosen solvers/methods and all figure/table captions
  correspond to **archived, measured** results.
- Agree with both coauthors on originality and correct attribution
  to Guerrero, Cortés-Toto, Weinert and other prior literature.
- Obtain a versioned DOI for the code/benchmark archive.
- Check the latest official SN Computer Science author instructions;
  the shorter format is an **editorial target**, not a claimed page limit.


## Expanded journal paper: code, results, and new trend figures

The shorter SNCS draft was too compressed to explain the numerical
contributions. The expanded `sncs_main.tex` now has dedicated sections:

1. Guerrero's $S_G=1-\mathrm{tr}(H)/n$ and the rescaled
   $S=nS_G/(n-d)$, the difference-order null space, and nonzero mu.
2. Root inversion and exact equivalence of criterion optimization in
   lambda versus S; unmatched finite log-lambda candidate grids are
   explicitly distinguished from a pure reparameterization.
3. Reusable Python API, seven solver implementations, preparation
   caching, pretranslation of candidate grids, and different timing
   workloads.
4. The archived 80,640-record Windows factorial over five criteria,
   orders d=0,...,5, reference means mu=0 and mu=0.15, and seven
   computational backends; real search-mode timings and selected S.
5. Independent-seed paired solver confidence intervals and Holm tests
   by order and computational workload; four smoothness-inversion
   algorithms and numerical validity.
6. Actual monthly CO2 and FEDFUNDS series with selected PLS trends,
   same-S/different-d trend comparisons, and selected penalty,
   smoothness and single-origin holdout tables.

**Important:** Both the theoretical index and the algorithmic
implementations build on prior literature. What is emphasized as a
software contribution is the reusable, auditable smoothness-first
Python interface and its documented numerical trade-offs, not a
claim of inventing the PLS smoother or CV/GCV/AICc/BIC.

All NEW tables and charts are generated from **archived** data by:

~~~powershell
conda activate trendestimation
python -m pip install -e ".[dev,plot]"
python -m pip install -r paper/requirements.txt

python paper/computational-statistics-submission/sncs_expand_results.py

# Compile via verified Windows direct-pdflatex/BibTeX build:
powershell -ExecutionPolicy Bypass -File .\paper\computational-statistics-submission\build_sncs.ps1
~~~

The renderer writes `sncs_coordinate_methods_table.tex`,
`sncs_solver_orders_table.tex`, `sncs_realdata_table.tex`,
plus PDF/SVG/PNG figures for (i) matched native/mapped versus
unmatched log-lambda, (ii) observed series over selected trends,
(iii) controlled S=0.86 over d=1,...,4, and
(iv) archived S↔lambda curves across orders. It checks SHA-256
of the nine original numeric source files before and after.
The compiled article uses these new figures alongside preexisting
archived Windows workload, mu, solver uncertainty, and inversion
figures. It does **not** rerun CV, GCV, AICc, BIC, likelihood,
root-inversion timings or any stochastic benchmark.

The renderer and paper PDF may also be generated by the
`sncs-expanded.yml` GitHub Actions workflow; its artifacts
are committed to the research branch for durable reuse.

### Save edits after updating the manuscript or figures

~~~powershell
git add .
git commit -m "paper: expand SN Computer Science computational results and smoothness-first software description"
git push
~~~

The complete original manuscript, raw numerical results,
dashboards and experimental matrices are retained separately.


## Rebuild the paper figures with the actual AwesomeFigures library

Source: https://github.com/awesomefigures/awesomefigures

We use the **immutable AwesomeFigures Git commit**
54c8bf2374551fa39428f47f69580b4822d4b938 pinned by
paper/requirements.txt, rather than a moving master branch.
The shared contrast_theme.py now invokes the real public plotting
functions: af.set_style("elegante", palette="okabe-ito"),
af.plot_scheme, af.named_colormap and af.save_figure.
The original seven solver colors and six criterion labels remain
consistent throughout the manuscript. Styles also provide distinct
linestyles and markers to distinguish series in grayscale.

On Windows, with an up-to-date checkout of the publication branch:

~~~powershell
conda activate trendestimation
python -m pip install -e ".[dev,plot]"
python -m pip install -r paper/requirements.txt
Get-Command pdflatex -All  # TeX is required even for journal-only exports

# All figures cited by the SN Computer Science paper, including
# full 4-by-6 supplementary dashboards. NO EXPERIMENTS RERUN.
python paper/computational-statistics-submission/rerender_awesomefigures.py

# Include older full-manuscript figure families too (also needs TeX).
python paper/computational-statistics-submission/rerender_awesomefigures.py --scope all

# Build the expanded SN Computer Science manuscript
powershell -ExecutionPolicy Bypass -File .\paper\computational-statistics-submission\build_sncs.ps1

# Persist all new PDFs, SVGs, PNGs and source-hash evidence
git add .
git commit -m "paper: regenerate publication figures with pinned AwesomeFigures"
git push
~~~

The command verifies all original observations, per-method selectors,
numerical inversion trials and paired solver timings using SHA-256 before
and after drawing. A manifest at awesomefigures_render_manifest.json
records the exact plotting library commit, method, palette and all source
checksums and figure paths. The diagrams, trend curves, confidence
intervals, 4-by-6 heatmaps, numerical-order comparisons and S/lambda
coordinate comparisons are generated from frozen observations and
archived results. Trend lines are reconstructed only at **already saved**
lambda and mu. The renderer neither downloads data nor optimizes CV,
GCV, AICc, BIC or MLE, performs Monte Carlo simulations or reruns any
timing benchmarks.

A GitHub Actions workflow on the publication PR automatically
regenerates and commits the figure assets and an updated SNCS manuscript
PDF. Core tests may use a simple preview when AwesomeFigures is not
installed, but the dedicated publication pipeline explicitly requires
the pinned AwesomeFigures release and fails if it is absent.


### Exact Springer Nature fonts and physical figure dimensions

The native publication renderer now uses **af.inspect_latex(sncs_main.tex)**
and **af.latex_style** to measure the official text width, body font
size, and TeX font identity from the actual Springer document class.
It then uses **PublicationStyle.fit** and **audit** to size every PDF
in its final printed dimensions. The manuscript includes four Windows
benchmark panels at 48% of text width and two numerical comparisons at
86%; the other figures use the full text width. Rebuilding at those
widths avoids shrinking an 11-point plot into illegible small text.

For the actual manuscript PDF, **PublicationStyle.savefig(backend="pgf")**
runs pdfLaTeX and embeds TeX-native fonts in the vector figures.
Matplotlib/DejaVu font matching alone is not sufficient. The SVG/PNG
previews are the same physical layout but are not guaranteed to contain
the exact TeX font outlines. Per-figure *.typography.json files record
the measured document font, actual export widths, minimum label sizes,
and publication audit warnings. All 11 figures referenced by the
SNCS manuscript must have a successful typography audit.

This now requires MiKTeX/TeX Live **even for --scope journal**; if
pdflatex is not found, rendering stops rather than silently using the
wrong font. From a Conda PowerShell in the repository root:

~~~powershell
Get-Command pdflatex -All
python -m pip install -r paper/requirements.txt
python paper\computational-statistics-submission\rerender_awesomefigures.py
powershell -ExecutionPolicy Bypass -File .\paper\computational-statistics-submission\build_sncs.ps1

git add .
git commit -m "paper: export SNCS figures at exact Springer LaTeX font and page dimensions"
git push
~~~

This step renders from archived numerical CSV/JSON only; it performs no
parameter retuning, new simulation, or timing experiment.

## 2026-10-28 — document-aware AwesomeFigures regeneration

The pinned AwesomeFigures revision is
`a9760351c1f72ccf7a1a2ef2ff14136d6e280d88`
(merged upstream PR #4). Paper rendering now uses the high-level
`af.paper(sncs_main.tex)` interface, rather than manually coordinating
`latex_style`, PGF backend settings, and physical document-width fitting.

Run from the repository root in PowerShell (MiKTeX/pdflatex required):

~~~powershell
git fetch origin
git switch feature/sncs-awesomefigures-auto-publication
git pull --ff-only
conda activate trendestimation
python -m pip install -r paper/requirements.txt
python paper/computational-statistics-submission/rerender_awesomefigures.py --scope journal
powershell -ExecutionPolicy Bypass -File .\paper\computational-statistics-submission\build_sncs.ps1
Start-Process .\paper\computational-statistics-submission\sncs_main.pdf
~~~

Each PDF cited by the manuscript must have `exact-tex-preamble`
provenance and an embedded-font audit in `figures/*.typography.json`.
The `*.pgf` intermediates are archived. SVG and PNG are preview-only.
See `awesomefigures_render_manifest.json` for source-file SHA-256
verification and figure-coverage results.

Only archived data and fixed saved parameters are used. No statistical
experiments, model selections, optimizations, simulations, or benchmark
timings are rerun. Multi-panel figures still merit visual inspection.
