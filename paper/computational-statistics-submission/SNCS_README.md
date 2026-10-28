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

# Compile the shorter manuscript (MiKTeX and latexmk needed)
Push-Location paper/computational-statistics-submission
latexmk -pdf -interaction=nonstopmode -halt-on-error sncs_main.tex
Pop-Location
Start-Process .\paper\computational-statistics-submission\sncs_main.pdf

# Commit paper, figures, dashboard code, provenance, and compiled PDF.
git add .
git commit -m "paper: render concise SNCS article and cached-data dashboards"
git push
~~~

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
