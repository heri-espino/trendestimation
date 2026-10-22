# SMCCA manuscript — trendestimation

**Status: research-software submission draft, not yet author-approved.**

- Manuscript: main.tex
- Journal class: smcca.cls (copied unchanged from the already-used SMCCA
  numerical paper template in heri-espino/Trend-Estimation)
- Bibliography: bibliografia.bib
- Numerical illustration: figures/make_figures.py
- Reproducible outputs (generated, not necessary to version): figures/cortes_toto_synthetic.dat,
  criteria_table.tex, results_summary.json
- First author: Heriberto Espino-Montelongo
- Second author: Daniela Cortés-Toto
- Affiliation for the second author: **requires confirmation by coauthor**.
  Her 2017 affiliation is not assumed to remain current.

## Scientific position

This is a short computational/scientific-software article implementing
**published** finite-difference penalized least squares (Guerrero 2007;
Cortés-Toto, Guerrero, Reyes 2017), not a new smoothing estimator. It
supports orders 1<=d<n (the package also defines d=0), fixed difference
means, Guerrero's observed-difference plug-in for fitting, fixed-mu
CV/GCV/AICc/BIC, an SVD-based solver and exact infinite-penalty limits.

The two articles from this same journal used as contextual examples are:

- R. Balam, L. Valencia, M. Zapata, R. Balam (2025),
  *A Simple Overview of Least Squares*:
  https://www.scipedia.com/public/Balam_et_al_2025a
- D. Azofeifa, M. Moreles (2025),
  *Hybrid Discontinuous Galerkin method for perturbations of the modified
  Helmholtz equation*:
  https://www.scipedia.com/public/Azofeifa_Moreles_2025a

The manuscript adopts their compact motivation/method/numerical-results/
conclusions progression without implying that their mathematical problems
are the same.

## Build instructions

From the **repository root**:

\`\`\`bash
python -m pip install -e ".[plot]"
python paper/figures/make_figures.py
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
\`\`\`

A complete TeX distribution with BibTeX and pgfplots is needed.
Alternatively, run \`make -C paper pdf\` after Python installation.
Heavy figure and PDF builds remain **manual**; they must not be run
automatically on each push or PR.

Outputs are deterministic for the declared seeds. Selected-lambda values
depend on the current software's finite candidate grid, and the BIC near-zero
boundary requires explicit interpretation. The numerical parity experiment
is not a universal stability result.

**Runtime measurements on the user's own computer have not been added.**
Any end-to-end speedup statement would require warm-up protocol, repeated
runs, hardware and thread information, and a banded-solver comparator.
The paper therefore reports algorithmic complexity, not invented speedups.

## Before submission

- Confirm the second author's affiliation and any desired contact email,
  authorship approval, and institutional information.
- Review the article's novelty and suitability for SMCCA with both authors.
- Check current SMCCA requirements and the exact LaTeX class before final
  submission. The class here is copied from the existing project template.
- Verify simulation/metrics against the released \`trendestimation\` version,
  and reproduce figures and numerical checks in the tagged release.
- Benchmark on the actual reference machine if making runtime claims.
- Inspect the compiled PDF, line breaks, bibliography and page count.
- Cite the release and archive its DOI when available.
