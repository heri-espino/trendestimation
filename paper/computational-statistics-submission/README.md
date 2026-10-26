# October 2026 empirical examples for Computational Statistics

This **standalone submission directory** modernizes the archived
`1990–1999` Mauna Loa example. It deliberately does **not** modify
the separate, active `paper/main.tex` research draft.

## Frozen sources, date boundaries

- **NOAA GML Mauna Loa CO2**, monthly mean (ppm), 1990-01 to
  **2026-09**, 441 complete months. September 2026 is **426.07 ppm**.
  Original publisher: https://gml.noaa.gov/ccgg/trends/data.html .
  Frozen source: `data/noaa_mlo_monthly_1990_2026_09.csv`.
  NOAA can revise data; this is an auditable snapshot, not a live feed.
- **US effective federal funds rate (FEDFUNDS)**, monthly not seasonally adjusted
  (%), 2010-01 to **2026-09**, 201 months; September 2026 is **3.75%**.
  Underlying publisher Federal Reserve, distributed by FRED:
  https://fred.stlouisfed.org/series/FEDFUNDS .
  Source CSV URL:
  https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS .
  Frozen source: `data/fred_fedfunds_2010_2026_09.csv`. The first
  creation of this snapshot requires access to the FRED URL
  (`--fetch-fred`), then a normal reproduction uses committed data.

No October 2026 monthly observations are invented or substituted.

## Questions answered

At fixed reference difference mean \(\mu=0\), compare
`d = (1,2,3,4)` and CV / GCV / AICc / BIC selectors plus the
**pre-specified** normalized trace smoothness `S=0.86`.
All four classical selectors use the *same* 29 candidate penalties,
constructed by inverting a common normalized-smoothness grid in
`[0.10, 0.98]`. Store **both** selected \(\lambda\) and \(S\).

Three data configurations are shown: full 441-month CO2 series;
last 120 CO2 months; 201-month effective federal funds rate series.
Every case generates a four-criterion overlay, a controlled-S
order comparison, an \(\lambda/S\) selection-coordinate chart,
a 12-month future *trend-only extrapolation* plot and an
honest fixed-origin 12-month historical holdout plot.

**Forecasting caveat:** extrapolated values are local least-squares
polynomials of degree `min(d-1,2)` fitted on the last 36
*smoothed* months, shifted to pass through the final PLS fitted value,
with no explicit seasonal/noise model. They
are **not** the PLS method's intrinsic future forecast (PLS is a
two-sided smoother) and do not include calibrated intervals.
All time-origin holdout fits/penalties use training data only.
One holdout is an illustrative diagnostic, not a statistically
valid ranking of forecasting methods.

## Windows 11 PowerShell reproduction

From the repository root with a conda environment:

~~~powershell
conda activate trendestimation
python -m pip install -e ".[plot]"
# Uses frozen committed NOAA + FRED data, no network needed
python paper\computational-statistics-submission\make_current_examples.py

# OPTIONAL ONLY to fetch a new FRED snapshot after verifying the cutoff
python paper\computational-statistics-submission\make_current_examples.py --fetch-fred

# Compile the standalone Springer paper (requires latexmk and TeX Live / MiKTeX)
Push-Location paper\computational-statistics-submission
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
Pop-Location
Start-Process .\paper\computational-statistics-submission\main.pdf
~~~

**Output contracts:** `figures/{co2_full,co2_recent,fedfunds_full}_*.pdf`
(and PNG/SVG companions), `current_examples_table.tex`,
`data/*_results.json`, `data/provenance.json`.

The manual-reproduction output is deliberately allowed to be large;
plot PDFs/SVG/PNGs and dated source snapshots are suitable for
committing so the coauthors can inspect identical figures.
Do not regenerate the source snapshot silently: any data vintage
update must be an explicit manuscript revision.

The accompanying CI workflow regenerates snapshots/figures and
compiles the standalone Springer PDF on a disposable Linux runner;
the source snapshot, checksums, execution evidence and PDF remain
reviewable on the PR before merging.

## Scope and later extensions

A genuine forecasting analysis needs repeated chronological
origins, appropriate seasonal models for CO2, uncertainty
calibration, and comparison with additional forecast models.
No new contribution is claimed solely from fitting higher
difference orders or interpolating the same optimal penalty
using the \(\lambda\) vs \(\ S\) coordinates.
