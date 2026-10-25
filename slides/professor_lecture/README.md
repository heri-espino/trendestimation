# Professor research lecture — trendestimation

An extensive, mathematical **Marp research notebook**, not a short conference
presentation. The approximately 130 slides cover PLS foundations, the
difference-order nullspace proof, fixed and plug-in means, spectral
computation and fair banded baselines, conditional EDF, Guerrero and
normalized smoothness, direct versus bounded-S searches, exact gradients,
CV/GCV/AICc/BIC, conditional marginal MLE, **deferred** joint mu profiling,
numerical inversion, stability, synthetic and Mauna Loa examples,
reproducibility, novelty boundaries, and future research.

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

On Windows PowerShell:

~~~powershell
powershell -ExecutionPolicy Bypass -File slides/professor_lecture/build.ps1
~~~

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
Files are Git-ignored so commits contain editable Markdown, CSS, Python
figure recipes, and build instructions — not opaque exports.
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

The existing solver benchmarks do NOT measure end-to-end optimization
speed of searching in S versus log(lambda). That is a future experiment.

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
