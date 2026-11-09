# Unified CSDA theoretical manuscript: Paper A + Paper B

**Canonical source:** main.tex (Elsevier CAS v2.4 double-column).
**Status:** theoretical working draft, not submitted; coauthor approval required.
**Research branch:** paper/csda-unified-theory. Do not merge without author authorization.

## Purpose

The author requested that the spectral Paper A and amortized-complexity Paper B be combined into **one theoretical computational-methodology article**. It uses the **normalized smoothness index S in [0,1]** as the organizing parameter and keeps the fixed **nonzero difference mean mu** in the core mathematics. Contributions cover spectral/shift-free reconstruction for any integer order 1 <= d < n; normalization, unique mapping and exact endpoints; complete CV/GCV/AICc/BIC/ML diagnostics; banded Cholesky with selected inversion; work/memory bounds with reuse across grids and series; numerical failure mechanisms; and the public Python interface.

This paper does not claim invention of classical PLS, diagonalization, SVD, Cholesky, trace smoothness, or cross-validation. The proposed contribution is an integrated workload-aware computational and numerical framework.

## Previous work preserved

The original source trees remain unchanged:
- paper/csda-spectral-smoothness: Paper A multiprecision and exploratory simulations.
- paper/csda-computational-costs: Paper B proofs, original figures, timings, source audit, and shared BibTeX.
- paper/main.tex and paper/benchmarks/experiment011: independent Springer measured timing paper.
- paper/ngsim-jerk-case-study: physical extrapolation and forecast evaluation.

No original experiments, CSVs, figures, PDFs, workflows or branches are overwritten or rerun. No new benchmark measurements are claimed in this manuscript. The shared references come from paper/csda-computational-costs/references.bib.

## Reproduce the deterministic algebra checks

From the repository root with NumPy and SciPy installed:

    python paper/csda-unified-theory/verify_theory.py
    python paper/csda-computational-costs/verify_theory.py

These are small deterministic identity checks, not a benchmark campaign.

## Compile the PDF in PowerShell

From the repository root:

    Copy-Item paper\els-cas-templates\cas-dc.cls,paper\els-cas-templates\cas-common.sty,paper\els-cas-templates\cas-model2-names.bst -Destination paper\csda-unified-theory
    Push-Location paper\csda-unified-theory
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
    Pop-Location
    Start-Process ".\paper\csda-unified-theory\main.pdf"

The new workflow .github/workflows/csda-unified-theory.yml runs the checks and compiles the paper on GitHub-hosted Linux, without invoking the PC08 runner.

## Remaining acceptance gates

1. Independently review the mathematics and exact source priority against Guerrero (2007/2008), Cortes-Toto et al. (2017), Weinert (2007), Golub et al. (1979), Erisman--Tinney (1975), and Biessy (2026).
2. Audit selected inversion, likelihood normalization, conditional plug-in mean, and high-order conditioning claims.
3. Verify API calls against the intended release.
4. Confirm coauthor contributions, order, correspondence, affiliation, funding and conflicts.
5. Build, inspect, and freeze the final journal PDF with exact source SHA and input hashes. Do not submit or merge without explicit author approval.
