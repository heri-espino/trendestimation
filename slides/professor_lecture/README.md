## Latest: complete Windows study and local paper + Marp rebuild

**New chapter X-D:** The professor's Marp research notebook now includes
the **80,640-cell author-run Windows experiment** rather than relying only
on early Linux quick runs or the incomplete 3×4×3 classroom factorial.

The new module covers $n=24,48$, $d=0,\ldots,5$, fixed reference-difference
means 0 and .15, all seven numerical backends, five statistical criteria,
17 smoothness targets including the exact $S=1$ limit, $R=1,3,8$,
cold and shared preprocessing, and bounded local continuous optimization.

It uses **five measured AwesomeFigures vectors** from
`paper/figures/windows_full_s_*.svg` copied deterministically to
`figures/60_windows_*.svg` through `windows_full_results.py`.
The generated figure manifest records the original path and SHA-256.
The lecture generator **does not recompute** any of the 80,640 measured
searches; it simply uses already published vectors and other existing
figure recipes.

The experimental methods have distinct interpretation:
**native S and pretranslated S-to-lambda** score identical candidates;
**independently log-spaced lambda** has different interior targets;
bounded minimizers in either coordinate are **local**, not certified
global. The Windows-host times must not be pooled with the earlier
GitHub-Linux quick reference.

### Compile paper and lecture locally (Windows, repository root)

```powershell
git switch main
git pull --ff-only origin main
conda activate trendestimation
python -m pip install -e ".[dev,docs,plot]"
python -m pip install -r paper/requirements.txt

# Uses committed Windows raw CSV: does NOT rerun the full experiment
python paper/benchmarks/report_windows_full_s.py
python paper/build.py --figures --pdf --package

# Requires Node.js; PDF requires Chrome or Chromium
powershell -ExecutionPolicy Bypass -File slides/professor_lecture/build.ps1
```

**Local requirements:** MiKTeX/TeX Live, latexmk and pdflatex for the
paper and exact AwesomeFigures Springer font layout; Node.js and
Chrome/Chromium for Marp PDF. If TeX is installed in a conda
environment, activate that environment before running the commands.

Results are `paper/main.pdf`, `paper/computational-statistics-submission.zip`,
`slides/professor_lecture/main.pdf` and `main.html`.
The PDF is already committed in the repository, but to publish a
*newly compiled local* copy, use a separate generated-output branch
via `python scripts/publish_generated_outputs.py --publish`
(the script checks for uncommitted tracked edits), or explicitly
stage just those generated files and push after review.

```powershell
git add -f paper/main.pdf paper/computational-statistics-submission.zip slides/professor_lecture/main.pdf slides/professor_lecture/main.html
git commit -m "docs: refresh local Springer and Marp compiled publications"
git push
```

The two pdfs should not require rerunning any heavy experiment.
See `notes/experiment002_full_s_factorial.md` and
`docs/windows_full_s_results.rst` for scientific provenance.

---


# Professor research lecture — trendestimation

An extensive, mathematical **Marp research notebook**, not a short conference
presentation. The approximately 130 slides cover PLS foundations, the
difference-order nullspace proof, fixed and plug-in means, spectral
computation and fair banded baselines, conditional EDF, Guerrero and
normalized smoothness, direct versus bounded-S searches, exact gradients,
CV/GCV/AICc/BIC, conditional marginal MLE, **deferred** joint mu profiling,
numerical inversion, stability, synthetic and Mauna Loa examples,
reproducibility, novelty boundaries, and future research.

## The central bounded-smoothness story

The lecture now foregrounds a first-pass narrative around
**why search using normalized smoothness `s=S(lambda)` rather than only
the unbounded PLS penalty**. Section V includes a concrete
`EDF=n-(n-d)S` interpretation (for `n=100, d=2, S=.8`, conditional
EDF is 21.6). Section VI compares the two numerical coordinates,
displays their monotone inverse and exact derivative, and provides
self-contained Python examples for both `select_lambda(...,
search_space="lambda"|"smoothness")` options, mapped-candidate
score equivalence, and direct smoothing targets via
`TrendSmoother.lambda_for_smoothness`.

The website has a matching introductory explanation at
[docs/smoothness_coordinate.rst](../../docs/smoothness_coordinate.rst).
A published URL is
https://trendestimation.github.io/trendestimation/smoothness_coordinate.html
**after the separate manual GitHub Pages deployment**.

The normalized index is conditional trace smoothness, **not**
forecast confidence or a percentage of noise removed. Neither
bounded coordinates nor numerical inversion establish faster
optimization. That original module predates the independently measured full Windows
search-coordinate study now included in **chapter X-D**; the complete
author-run data and their figures are archived and verified. All 49 figure recipes and existing measured
data remain unchanged.

## Factorial computational comparison: 3 × 4 × 3, plus released selectors

The extended lecture now adds a substantial **research-oriented factorial
module** (over 160 slides overall) to the original historical and mathematical
story. It includes **paired lambda / normalized-S objective plots for all
four criteria**, the SVD/eigh/banded-Cholesky numerical distinctions,
the complete 36-cell (3 solvers × 4 criteria × 3 search policies)
experimental design, host-measured timing and optimum-quality plots,
and a separate study of the actual public `select_lambda` default.

**Two complementary studies, not one combined speed ranking:**

1. `benchmarks/criterion_coordinate_matrix.py`: controlled grid search
   cross-product. `lambda` computes S *once after selecting lambda*;
   `s_mapped` uses the identical penalties after independent
   backend-specific inverse S; `s_uniform` changes which candidates
   are evaluated while keeping the candidate **count** fixed.
2. `benchmarks/public_coordinate_optimizer_benchmark.py`: times the
   released `select_lambda(..., method="auto")` with
   `search_space="lambda"` versus `"smoothness"`, including setup,
   actual candidate counts, and selected scores. The CV derivative
   searches have **different** default grids and budgets.

For reproducible smoke runs from the root:

```bash
python -m pip install -e ".[plot]" threadpoolctl
python benchmarks/criterion_coordinate_matrix.py --preset smoke --seeds 1 --repeats 2
python benchmarks/public_coordinate_optimizer_benchmark.py --preset smoke --seeds 1 --repeats 2
python slides/professor_lecture/make_figures.py
bash slides/professor_lecture/build.sh --html-only
```

For a larger research run, use `--preset quick --seeds 3 --repeats 4`
on both benchmark scripts (or `full` after reviewing numerical
conditioning). The two scripts produce raw and summarized CSVs with
environment metadata in `build/criterion-coordinate-study/`.
**Timing figures 54–59 are generated only from those measured CSVs**
and explicitly display missing-measurement panels otherwise.
Figures 50–53 are seeded deterministic criterion transformations,
not speed measurements.

A precise mathematical and experimental protocol, plus limitations and
future spline comparisons, is in
[notes/criterion_coordinate_factorial.md](../../notes/criterion_coordinate_factorial.md).
The extant original paper timing suite is untouched: its
`solve_banded` results must not be described as specific Cholesky
factorization measurements.

The repository stores the **source** of approximately 49
publication-style SVG figures and exports to both **HTML and PDF**.
The figure generator creates figures/manifest.json with provenance.

## VM setup

From the repository root:

~~~powershell
conda activate trendestimation
python -m pip install -e ".[plot]"
python -m pip install statsmodels
npm install --global @marp-team/marp-cli
~~~

On Windows 11 PowerShell:

~~~powershell
# From the repository root; no editable package installation is required
# for the slide builder to locate the local src/trendestimation sources.
conda activate trendestimation
powershell -ExecutionPolicy Bypass -File .\slides\professor_lecture\build.ps1
~~~

The Windows builder temporarily places the local ``src`` directory on
``PYTHONPATH`` and restores the previous value afterward, so it works
with a src-layout checkout even if ``pip install -e .`` was missed.
NumPy, SciPy, Matplotlib, Marp/Node.js and optional statsmodels are still
required. The direct Python command ``python slides/professor_lecture/make_figures.py``
still requires an editable installation or an explicit ``PYTHONPATH``.


On Ubuntu/Linux VM:

~~~bash
bash slides/professor_lecture/build.sh
~~~

Headless VM without Chromium (HTML only):

~~~bash
bash slides/professor_lecture/build.sh --html-only
~~~

This emits slides/professor_lecture/main.html and main.pdf alongside
main.md and theme.css, with local SVGs under figures/. PDF export requires
Chrome/Chromium and its OS libraries. HTML export works without PDF.
The generated HTML/PDF and figures are normally Git-ignored by default,
but reviewed publication outputs can be explicitly force-added and committed.
The relative SVG paths mean that when sharing main.html, you must also
copy the figures/ folder.

## Host benchmark evidence

The two timing figures read actual, host-specific CSVs:

- paper/benchmarks/results/full_fit_timings.csv
- paper/benchmarks/results/trace_timings.csv

When absent, the generator produces **explicitly labeled missing-data
panels**. It never substitutes invented timing measurements.
Before rendering on the VM, you may **explicitly** benchmark:

~~~powershell
python -m pip install threadpoolctl
python paper/benchmarks/run_all.py --preset quick --repeats 5
python slides/professor_lecture/make_figures.py
~~~

The original solver benchmark does not measure end-to-end lambda/S selection.
The two new experiments described above measure controlled grid-selection
work and real public auto selectors, respectively, once executed manually.

The CO2 figure uses statsmodels' weekly CO2 dataset aggregated to
monthly observations in 1990–1999. Install statsmodels to enable it.
If it is unavailable the generator displays a missing-data panel.

## Important scientific boundaries

The objective with arbitrary difference order d and reference mean mu
is **established**. The current library implements fixed mu, empirical
plug-in mu, conditional Gaussian MLE and bounded-S criterion searches;
a validated joint (lambda,mu) likelihood optimizer is **future research**.
Normalized S is not a probability, confidence measure or a guarantee
of faster optimization. LOOCV is not chronological forecasting validation.

The lecture is intentionally more extensive than the focused
Springer *Computational Statistics* article, but should **never**
misrepresent its empirical claims.

## Source references

- paper/main.tex and paper/sections — current manuscript and results.
- notes/smoothness_parameterization.md — mathematical coordinate change.
- src/trendestimation/core.py — spectral smoothing implementation.
- src/trendestimation/criteria.py — CV derivatives and S search.
- src/trendestimation/likelihood.py — conditional Gaussian likelihood.
- paper/benchmarks/ — independent dense, spectral and banded baselines.
- docs/handbook/ — detailed derivations and assumptions.
- paper/bibliografia.bib — publication citations.

## Validation and iteration

~~~powershell
python slides/professor_lecture/make_figures.py --smoke
python -m pytest tests/test_professor_lecture.py -q
~~~

For the complete deck, rerun the builder without --smoke.
The final HTML/PDF must be visually inspected for equation overflow.
Figures have distinct metadata categories: deterministic, observed,
analytical illustration, complexity schematic, host measured, or missing.
Changing the script, not hand-editing SVG output, is the reproducible
way to change a figure.
