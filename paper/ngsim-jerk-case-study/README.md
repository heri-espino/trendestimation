# NGSIM real-vehicle jerk and trend forecasting case study

Separate third manuscript in paper/ngsim-jerk-case-study.

## Public real measurements

FHWA / US Department of Transportation NGSIM US-101, DOI
10.21949/1504477. Official source:
https://data.transportation.gov/d/8ect-6jqj

The official dataset labels the license CC BY-SA 3.0. Its 10-Hz
camera-derived raw longitudinal positions are preserved, with exact
feet-to-meters conversion, original times, identifiers and a SHA256
record. See data/provenance.json and fetch_ngsim.py for the original
query, deterministic track selection and audit rules. Five real tracks
are recorded, never simulated, ranked or fabricated.

## Design

80 points per training window; 3 chronological origins per track;
3 future horizons (0.5, 1, 2 seconds). Orders d=1,2,3,4 and
five selectors (CV, GCV, AICc, restricted BIC and marginal Gaussian
ML) on a common full S-grid in [0,1]. Mean of differences is
fixed zero or a training-only observed-difference plug-in.
Plug-in CV is conditional, not exact leave-one-out refitting.

The PLS estimator does NOT natively forecast. The application
explicitly appends a local degree-(d-1) polynomial extension of
the last 25 fitted observations, with the particular solution
mu * binomial(t,d) added for nonzero third differences.
That is a heuristic, not a state-space or predictive distribution.

The third difference of a position series approximates jerk times
the cube of the sampling interval. No independently measured jerk
ground truth exists for these traces.

Three physical prediction baselines are evaluated on the same
future observed positions: constant velocity, constant acceleration,
and Savitzky-Golay smoothing plus velocity extension.
Seven fit-only numerical backends at d=3, S=0.90 provide separate
runtime and numerical-discrepancy diagnostics.

## Reproduce on Windows PowerShell

From the repository root:

    conda activate trendestimation
    python -m pip install -e .
    python -m pip install -r paper/requirements.txt
    python paper/ngsim-jerk-case-study/run_case.py
    Copy-Item paper/els-cas-templates/cas-dc.cls,paper/els-cas-templates/cas-common.sty,paper/els-cas-templates/cas-model2-names.bst -Destination paper/ngsim-jerk-case-study
    python paper/ngsim-jerk-case-study/render_paper.py
    Push-Location paper/ngsim-jerk-case-study
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
    Pop-Location
    Start-Process "./paper/ngsim-jerk-case-study/main.pdf"

To redownload a possible newer source revision, run fetch_ngsim.py
before the study and audit the new hash; do not silently overwrite
the frozen dataset used for this paper.

The GitHub Actions analysis and paper workflows preserve all raw
data subsets, selection rows, forecast holdouts, plots, editable PGF
sources and the compiled two-column Elsevier CAS manuscript.
Results are illustrative, not a physical safety prediction.
