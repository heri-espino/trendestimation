# AwesomeFigures empirical visualization atlas: visualization002

## Purpose
Generate a comprehensive supplementary gallery and replace all nine
main manuscript graphics with the *actual*, pinned AwesomeFigures
publication style. This extends, but does not overwrite,
the earlier visualization001 results. Nothing in this step executes
a numerical smoother, selects parameters, changes a criterion,
modifies acceptance tolerances, or reruns the experiment.

## Frozen sources and validity
The immutable results are read from the neighboring
derived/42636962129 directory. The canonical timing tensor
SHA-256 must equal a25f674981b1c20df678638287df289c4d888ae62417a3f58ed8a6b2a08fce13.
The validated original sample has 2813 scheduled case-seed jobs,
92679 timing/status records, 76220 complete records, 9096 banded
post-solve KKT rejections, 6336 mapping failures and 970 budget
exclusions. All skipped/incomplete/missing observations remain
in reliability analyses and are never counted as fast timings.

Runtime-ratio violins and confidence summaries are constructed
from full, numerically admissible **matched** method pairs.
Repeated observations are combined within independent seed
clusters before kernel-density estimation. Bootstrap intervals
are reused from the original 700-resample seed-cluster analysis,
not recomputed or falsely applied to row-level pseudoreplicates.

Worker execution phases 24, 12, 1 are separate observational
conditions, not controlled isolated latencies. The memory policy
curve is an analytical code-defined workspace allowance and not
measured RSS. SVD lacks the identical banded-specific KKT test,
so numerical acceptance differences do not certify universal
spectral forward-error superiority. All these qualifications
remain explicit in manuscript prose and metadata.

## Publication style
Use the existing library revision pinned in paper/requirements.txt:
AwesomeFigures at a9760351c1f72ccf7a1a2ef2ff14136d6e280d88.

APIs: awesomefigures.set_style('elegante'),
awesomefigures.color_palette('okabe-ito'),
awesomefigures.save_figure, and, for the nine main PDFs,
awesomefigures.paper with the canonical Springer paper/main.tex
preamble. Manuscript figures must have embedded TeX fonts
and a typography sidecar. Every chart also includes SVG
vectors and PNG previews. Color choices are identical
for methods across all plots.

## Reproduction on PCAG103A-08
From the repository root:

    conda run -n trendestimation python paper/benchmarks/experiment011/pc08_empirical/visualization002/render.py --tex-core
    conda run -n trendestimation python -m unittest discover -s paper/benchmarks/experiment011/pc08_empirical -p test_*.py -v

The output comprises:
- figures: at least thirty vector PDF/SVG/PNG figure sets;
- figure_manifest.json: per-figure provenance, input hashes and caveats;
- supplementary_figure_gallery.pdf: all supplementary vector pages,
  distinct from the nine main journal figures;
- existing evidence-preserving LaTeX summary tables generated
  by visualization001, without numerical re-analysis.

Primary visualization families: method-colored reliability stacks;
candidate-grid distributions and uncertainty forests; n-by-d
completion heatmaps; mapped penalty/direct-S time distributions;
paired raw-time scatter plots; single-vs-grid comparisons;
component-wise runtime allocation; high-order inversion failures;
case/seed completion masks; deterministic worker coverage,
cold/warm accounting, candidate-count summaries, and the
KKT rejection residual distribution and empirical CDF.

## Windows CI and merged scientific scope
The scoped new workflow springer-awesomefigures-gallery.yml
runs only on branch paper/experiment011-awesomefigures-gallery
when the triggering commit includes [awesomefigures-render].
It requires AwesomeFigures and actual pdflatex; no silent
matplotlib-only fallback. It renders the atlas from frozen data,
tests all source-only numerical identities, rebuilds the canonical
Springer manuscript, uploads PDF artifacts, and commits all figure
and PDF results back to the branch and an immutable artifact ref.

The feature branch is based on the manuscript PR #126 branch,
which remains stacked on PR #124. Integration means merging
the validated visualization PR into that existing manuscript
branch, not merging unrelated research papers into main.
All original experiment files and other articles are unchanged.

## Scientific review
The aim is wide *coverage*, not redundant displays or false
precision. Additional charts are supplementary; main paper
figures should each answer a distinct scientific question.
The publisher declarations, author approvals and raw-data
distribution permissions still require explicit verification
before journal submission.


## AwesomeFigures API compatibility on the verified Windows runner
The installed library reports version 0.1.0 and provides
awesomefigures.latex_style as its publication interface;
awesomefigures.paper is not exposed by this installation.
The renderer uses the library's established latex_style
context with PDF/PGF output and an audit sidecar, consistent
with the existing paper/figures/render_awesomefigures.py
Springer export. This is actual AwesomeFigures, not an
invented compatibility package. The no-fallback renderer
requires the installed AwesomeFigures version and exact
Springer pdflatex typography for the nine main figures.
