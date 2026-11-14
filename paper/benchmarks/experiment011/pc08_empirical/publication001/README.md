# Springer journal-language revision — publication001

## Purpose
Replace development-chronology and internal-run nomenclature in the
canonical Springer *Computational Statistics* article with conventional,
publication-facing scientific exposition, while retaining transparent
numeric status qualifications and the audited computational evidence.

**The principal interpretation is deliberately conditional:**
spectral SVD is the preferred default for complete, repeated smoothing-
parameter searches when its dense matrix workspace is feasible.
Banded Cholesky remains attractive for isolated valid evaluations
and for memory-limited large series.

## Manuscript modifications
- \`paper/main.tex\`: journal-style title, concise self-contained
  abstract, sharpened contribution and reference to repeated spectral
  criterion evaluation. Remove internal campaign and runner titles.
- \`paper/sections/experiment011_methods.tex\`: introduction, formal
  PLS estimator, finite-difference spectral representation,
  normalized smoothness, complete CV/GCV formulas, numerical
  acceptance criterion and statistically faithful matched design.
- \`paper/sections/experiment011_results.tex\`: full performance and
  reliability study; pairwise matched grid comparisons; cached mapping;
  figures; evidence-bound selected-method recommendation.
- \`paper/sections/experiment011_robustness.tex\`: precise KKT post-solve
  failure, shared coordinate inversion failures, candidate-count
  crossover, memory-policy model.
- This folder's \`render.py\` transforms the frozen \`paired_backend_seed_bootstrap.csv\`
  into a publication-facing, numerically checked table and vector forest
  plot labeled exclusively by criterion, n, d and reference mean.
  It replaces internal case labels in the published table/figure.
- The original first four figures and four follow-up figures remain
  preserved. No new benchmark, changed solver tolerance or synthetic
  observation generation is permitted.

## Reproduction
Within a checkout that contains the frozen audited results, run:

    python paper/benchmarks/experiment011/pc08_empirical/publication001/render.py

The predeclared eight display configurations are a presentation
subset of the full auditable timing table. The full measurement
tensor and paired raw/bootstrap datasets are not reduced, replaced
or silently filtered.

For a fresh Springer build on PC08:

    python -m unittest discover -s paper/benchmarks/experiment011/pc08_empirical -p "test_*.py" -v
    python scripts/build_papers_pc08.py --paper springer --output-dir paper/builds/pc08/springer-publication001 --require-runner

## Author-review conditions
An earlier draft added a second named coauthor who has not been
independently verified as having participated in this study. This
publication-language revision conservatively lists the verified
project author alone until the actual author approves any coauthor
attribution and confirms eligibility/consent. This is **not** a
decision to exclude a verified collaborator. Funding, conflicts,
contributorship and corresponding contact must be approved by the
author before journal submission. The word "publication-ready"
here describes scholarly writing/format, not a claim that these
required personal disclosures have been legally/ethically signed.

Numerical constraints persist:
- Successful spectral execution does not pass the same banded
  implementation-specific KKT gate and is not independent
  high-precision evidence.
- Large-n fourth-order inverse-smoothness mappings can fail for
  both methods.
- Valid paired 100-candidate grid timings support SVD speed
  advantages in the displayed configurations, not universally.
- 2 GiB memory cap and 40n²-byte SVD admission are formulas,
  **not measured peak RSS**.
- Parallel worker phase limits are not constant instantaneous
  CPU occupancy; uncertainty uses independent seed clusters.
- Raw experimental measurements remain unpublished in author-
  owned storage and must not be represented as downloadable.

Keep this document in the repository; do not insert implementation
handoff terms or internal experiment numbers in the publication
manuscript.
