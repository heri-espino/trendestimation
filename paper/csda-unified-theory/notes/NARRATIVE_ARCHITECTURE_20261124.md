# Unified CSDA narrative architecture — 2026-11-24

## Why this edit exists

The previous manuscript repeatedly alternated among history, mathematical
derivation, novelty qualification, algorithm comparison and general implications.
This diluted the central question: **what does it take to select smoothness
efficiently, rather than merely fit a PLS trend for one penalty?**

The new narrative is an actual source-only organization revision, **not**
a new model, derivation or experiment. Preserve the complete previous
mathematical results, equations, proofs, author ORCIDs/emails, official
Elsevier CAS class, STIX font selection, unboxed numbered equations,
reproducible synthetic figure, tables, code, declarations and references.

## Seven principal sections

1. **Introduction:** motivated by complete-criterion workload, concise
   historical context, three integrated contributions, and assumptions.
2. **Finite-difference PLS and smoothness parameterization:** concise
   notation; the existing fixed-nonzero-reference PLS solution and SVD
   formulas; derivative-order interpretation; rank-normalized smoothness,
   Gaussian precision, bijection and endpoints.
3. **Statistical criteria for smoothing selection:** conditional CV,
   GCV, the original residual-based AICc/BIC conventions, and the
   Gaussian restricted/contrast likelihood with fixed numeric mu.
4. **Spectral and structured computational methods:** retained SVD,
   Gram eigendecomposition, banded Cholesky, selected inverse,
   other exact and approximate algorithms; a per-penalty cost table.
5. **Complete-workload complexity and algorithm selection:** full
   M-candidate/R-series complexity bounds, conditioning, accuracy,
   admissibility, and decision rules in one development.
6. **Illustrative example and reproducible implementation:** the exact
   3rd-difference D/Q matrices and synthetic Gaussian example now
   belong together, followed by the Python interface.
7. **Discussion and conclusions:** statistical and computational
   implications, relation to neighboring methods, model limitations
   and future empirical validation.

**Appendix A: Gaussian derivations.** The *verbatim proof bodies* of
the contrast/REML theorem and the quadratic/logdet proposition were moved
from the core likelihood section; original labeled mathematical equations
are retained. The main text keeps statements and a reference to their proof.

**Appendix B: Historical and computational provenance.** The complete
algorithm-origin table and historical citations were moved from the
opening of the algorithm section, eliminating the 9-page historical jump.

The original eight files `reading_guide.tex`, `model.tex`,
`order_interpretation.tex`, `smoothness.tex`, `criteria.tex`,
`algorithms.tex`, `complexity.tex`, `stability.tex`,
`policy.tex` and their mathematical statements remain accessible
at their prior paths for independent agents. `main.tex` controls the
order. The new file is `sections/appendix_likelihood_proofs.tex`.
No experiment number is allocated because this is not an experiment.

## Scientific safeguards

- Original full SVD is of rectangular D, not of H.
- Demmler–Reinsch is an analogous spline penalty basis; Biessy's
  finite-difference Gram spectral/rank-reduced results are acknowledged.
- The smoother's fixed nonzero mu is due to Guerrero. Rank normalization
  is a simple, operational rescaling of the historical trace index.
- The Gaussian restricted likelihood and variance-ratio interpretation
  are not claimed to be novel methodology.
- SVD is not universally faster than banded Cholesky; complete
  conditional CV requires leverages and other diagnostics.
- No claims of temporal forecast validation, measured runtime speedups,
  jointly estimated mu or physical jerk ground truth.
- Funding, individual CRediT roles and competing interests still
  require author sign-off. AI disclosure remains explicit.

## Technical verification

Run the original mathematical verifier and tests, plus the new
narrative-structure regression test:

```bash
python paper/csda-unified-theory/verify_theory.py
python paper/csda-computational-costs/verify_theory.py
python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_*.py' -v
```

The dedicated `.github/workflows/csda-unified-theory.yml` on
`editorial/csda-narrative-architecture-20261124` must compile
the official Elsevier CAS manuscript with the original figure and
both sidewaystables, apply native PDF rotation, verify zero body
paragraph overflow > 0.5 pt, reject unresolved citations,
inspect embedded STIX fonts and publish the source/PDF/hash
artifact. Confirm all 64 equation labels and all referenced
proof/theorem/table targets. Visually inspect page 1, first theory,
cost tables, Gaussian appendix, provenance appendix, and declarations.
No large numerical experiments or benchmarks should be rerun.

The workflow may archive the verified PDF **on this feature branch**;
a review PR must remain open pending explicit user approval
for any merge. No journal submission was authorized.
