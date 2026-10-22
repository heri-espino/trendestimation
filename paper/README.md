# SMCCA scientific-computing manuscript

**Draft, not approved for journal submission.**

- First author: **Heriberto Espino-Montelongo**.
- Second author: **Daniela Cortés-Toto**.
- Affiliation for **both**: Universidad de las Américas Puebla (UDLAP).
- Officially styled with the available SMCCA `smcca.cls` class already used in the research repo.
- Main document: `main.tex`; sections of the extended mathematical derivation are in `sections/`.
- Bibliography: `bibliografia.bib`, including the two other SMCCA articles previously identified.
- Synthetic replication: `figures/make_figures.py` (Cortés-Toto et al. scenario).
- **Observed-data example:** `figures/make_extended_figures.py` uses the historical Mauna Loa weekly CO2 measurements bundled with `statsmodels.datasets.co2`; aggregates the 1990–1999 measurements to 120 monthly averages, compares d=2,3,4,5 at normalized smoothness 0.86, and exports the plot data.
- Independent mathematical test: the same script computes the closed-form conditional GLS/likelihood profile estimator of `mu`, then checks it against a direct joint normal-equation solver for d=1,2,3,5.

## Build the entire paper with one command

`paper/build.py` is the canonical command-line interface. It resolves paths
relative to its own location, so it works whether you launch it from the
repository root or elsewhere. The current SMCCA PDF is compiled with
`latexmk`; PDF compilation requires an installed TeX distribution
(including the journal class's packages, BibTeX and PGFPlots).

Install the scientific dependencies, then run:

```sh
python -m pip install -e .
python -m pip install statsmodels pandas threadpoolctl
python paper/build.py
```

The **default build** generates the synthetic plot and CV/GCV/AICc/BIC
table, the historical Mauna Loa plot and the high-order numerical plot,
then compiles `paper/main.pdf`. It does **not** run slow timing benchmarks
implicitly. All generated figures, tables, results and PDF remain inside
`paper/`.

### CLI flags

| Command | Effect |
| --- | --- |
| `python paper/build.py --help` | Show all options. |
| `python paper/build.py --figures` | Generate all required figures and the synthetic-criteria table, without compiling PDF. |
| `python paper/build.py --tables` | Rebuild benchmarking LaTeX tables from **existing** raw timing CSVs. |
| `python paper/build.py --benchmarks --benchmark-preset quick --repeats 5` | Run timed comparisons and automatically produce tables. No PDF compilation. |
| `python paper/build.py --pdf` | Recompile from **existing** figure and table files; fail with an explanation if required inputs are missing. |
| `python paper/build.py --all --benchmark-preset full --repeats 7` | Regenerate all figures and benchmark results, then compile the full SMCCA PDF. May be expensive. |
| `python paper/build.py --dry-run --all` | Inspect the exact commands without running or writing anything. |
| `python paper/build.py --clean` | Clean LaTeX auxiliary files and the compiled PDF, preserving results and figures. |

Optional controls: `--blas-threads N` (benchmark parallelism;
default 1), `--latex-engine pdflatex|xelatex|lualatex` (default
pdfLaTeX), `--benchmark-preset smoke|quick|full`, and `--repeats N`.
The usual build uses existing measured benchmark tables if they are
present; check their recorded machine and revision to avoid mixing
results. To update tables from raw data without rerunning measurements,
use `--tables --pdf` (after figures are already generated).

A successful non-dry-run build also writes
`paper/build_manifest.json` with executed commands, durations,
Python/platform details and Git revision. The manifest is ignored by
Git; do not present measurements from another computer as your own.

The Makefile delegates to the same interface, for example:

```sh
make -C paper pdf
make -C paper figures
make -C paper pdf-with-benchmarks
```

The GitHub Actions manuscript workflow is **manual only**. It uses this
builder for figure generation and the LaTeX action for compilation in an
isolated TeX environment; it does not run large benchmarks on pushes.
The manual benchmark workflow produces downloadable raw timing artifacts.

## Scientific boundaries

The long-known PLS estimator, arbitrary finite-difference order and polynomial
nullspace, nonzero reference-difference mean, spectral decomposition,
smoothing splines, and Gaussian marginal likelihood are not claimed as novel.
The package integrates these methods with an illustrative gallery.

- The correction maps Guerrero's index `[0, 1-d/n]` to `[0,1]`. Do not
  write `1-n/d`.
- The reviewed base package uses **SciPy/NumPy on CPU**, not a verified GPU
  backend. No runtime/GPU speedup has been measured for the paper.
- The other agent's MLE branch implements Gaussian marginal likelihood with
  fixed or plugged-in `mu`. The new analytical **joint profile formula for mu**
  is research code under `figures/make_extended_figures.py`; it is **not**
  yet a public package API and must not be presented as one.
- The real CO2 observations include seasonality, not merely measurement error.
  The visualization is two-sided descriptive smoothing, not future forecasting.
- Large difference orders may be poorly conditioned. A bounded reproducible d=1..10 experiment reports the condition ratio of the positive penalty spectrum and direct-versus-spectral disagreement.
- All coauthor approvals, affiliation presentation, author contribution statements,
  manuscript novelty review and release tagging remain to be completed.

## Context in this journal

The prior SMCCA articles cited are Balam et al. (2025),
*A Simple Overview of Least Squares*, and Azofeifa and Moreles (2025),
*Hybrid Discontinuous Galerkin Method for Perturbations of the Modified
Helmholtz Equation*. The exposition mirrors their compact numerical-analysis
structure without claiming a directly shared mathematical method.

## Paper-only timing comparisons

The scripts under `paper/benchmarks/` compare naive fresh dense solves,
cached dense solves, a reusable spectral decomposition, and a directly
banded penalty solver. A separate test compares full matrix EDF/trace
computation against summing spectral attenuation factors. All numerical
parity checks are separated from timed regions; one-time SVD setup is
included. No library API or `src/` file is modified.

Run from the repository root:

```sh
python -m pip install -e .
python -m pip install threadpoolctl
python paper/benchmarks/run_all.py --preset smoke --repeats 2
python paper/benchmarks/run_all.py --preset quick --repeats 5
# Longer study, explicitly manual:
python paper/benchmarks/run_all.py --preset full --repeats 7
```

Raw CSV files, hardware information, relative speedups, and optional
PGFplots timing data and publication-style LaTeX summary tables are generated in the **ignored** directory
`paper/benchmarks/results/`. The SMCCA manuscript imports **actual measured timing tables, numerical parity
and host metadata automatically** when those files exist. Without them it
prints a missing-results notice; preliminary pilot timings are not silently
published as measurements from another computer.

**Do not claim universal spectral superiority or GPU acceleration.** The
banded baseline may be faster than spectral fitting. The numbers must be
measured on a named host, repeated, and associated with a source revision.
See `paper/benchmarks/README.md` for the operation model, input grid,
numerical tolerances and detailed interpretation.
