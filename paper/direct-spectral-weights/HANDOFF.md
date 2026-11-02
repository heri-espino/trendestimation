# AI agent handoff — theory draft

## Read-first sequence
1. Root README.md and available AGENTS.md at your branch.
2. paper/direct-spectral-weights/README.md and PROOF_AUDIT.md.
3. src/trendestimation/core.py and smoothness_weights.py.
4. tests/test_spectral_smoothness_weights.py.
5. notes/direct_spectral_weights.md,
   notes/smoothness_parameterization.md.
6. paper/csda-spectral-smoothness/sections/spectral_theory.tex.
7. paper/csda-computational-costs/sections/algorithms.tex.
8. The paper in main.tex and sections/*.tex.

## Current task and decisions
- Separate theory manuscript only; it does not reuse inaccurate
  performance claims from other studies.
- Elsevier CAS v2.4 two-column style, provisional authorship.
- Theorems and detailed proofs, no boxed results.
- Center the distinction between explicit lambda and implicit
  scalar logit weight root; they are mathematically equivalent.
- A new result to review especially carefully is the plug-in
  mean EDF correction. It is exact for s held fixed, but must not
  be interpreted as adaptive-selection EDF.
- The draft must not change the public solver API.
- Do not silently merge with previous paper work or experiment005.
- Preserve all sources and compile outputs on the branch.

## Next work
1. Confirm build and visually inspect every page and reference.
2. Independent coauthor proof audit, especially sensitivity
   bound and full plug-in trace.
3. Run a separately numbered Experiment006 comparing direct
   spectral weights, stable cached log-lambda and cached
   weight baseline with identical n,d,s,mu, data and precision.
4. Extend literature review to any directly equivalent
   constrained spectral-weight algorithms.
5. Update notes/README.md only when the work is accepted.
