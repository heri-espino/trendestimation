# Elsevier CSDA paper — spectral smoothness

**Working research draft, not submitted.** This standalone manuscript is intentionally separate from the historical Springer working manuscripts. It uses Elsevier elsarticle with modular sections, author-year references, and five vector figures based entirely on archived Experiment004 outputs.

## Contents

- main.tex: manuscript entrypoint
- sections/: full mathematical theory, selection criteria, simulation and numerical validation, results and limitations
- references.bib: manuscript bibliography
- render_figures.py: regenerates figures directly from existing CSVs; does not repeat experiments
- figures/: PDF and SVG vector pairs
- main.pdf: compiled manuscript after successful GitHub Actions run
- publication_sha256.txt: input/output hashes written by workflow

## Rebuild in PowerShell from repo root

    conda activate trendestimation
    python -m pip install numpy scipy matplotlib
    python paper\csda-spectral-smoothness\render_figures.py
    Push-Location paper\csda-spectral-smoothness
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
    Pop-Location
    Start-Process ".\paper\csda-spectral-smoothness\main.pdf"

Automated build: .github/workflows/csda-spectral-paper.yml. It uses GitHub-hosted Linux, not PCAG103A-08, then commits PDF, SVG and output checksums on the research branch.

## Archived data

- Original RMSE pilot, 20 seeds: paper/benchmarks/experiment004/runs/pilot-hosted-40826487736/
- BIC and high-precision reference: paper/benchmarks/experiment004/runs/validation-hosted-40828581992/
- Nine implementations and BIC bounds: paper/benchmarks/experiment004/runs/stable-hosted-40830375100/

Every archived directory preserves original CSVs, exact-source hashes and environment metadata. Never overwrite or relabel these runs.

## Decision and limitations

Orders d=1 through d=6 only in Experiment004. Full singular-value decomposition of D is the chosen unified accuracy-oriented default, and shift-free spectral reconstruction avoids constructing a large polynomial reference for nonzero mean differences. Dense SVD is not claimed to be universally fastest. BIC's near-interpolation divergence is mathematically documented; Smin=0.10 and Smin=0.05 are restricted sensitivity checks, not a repaired universal model-selection criterion.

The observed-difference mean is an empirical conditional plug-in, not re-estimated leave-one-out CV or jointly estimated Gaussian MLE. The statistical pilot reports historical latent-trend recovery rather than future forecasting accuracy. Journal submission requires further coauthor approval, statistical validation and computational prior-art comparisons.
