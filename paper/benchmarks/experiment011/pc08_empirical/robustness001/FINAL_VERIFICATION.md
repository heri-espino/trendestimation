# Springer robustness001: final PDF and figure verification

Verified 9 November 2026. **Latest PDF:** the 15-page Springer
Computational Statistics empirical manuscript including the four
user-requested Cholesky/SVD numerical reliability, full-grid timing,
and source-code memory-policy figures. The previous 11-page PDF
from Actions run 42638070663 predates these additions and remains
historical, not the latest manuscript.

## Reproducibility and exact artifacts

- Immutable original 2813-record Experiment011 report SHA-256:
  c5d4898c83c731ada23a10957f80adc43616200206dc76573f365d38ba37f723
- Frozen original long-form tensor SHA-256:
  a25f674981b1c20df678638287df289c4d888ae62417a3f58ed8a6b2a08fce13
- Canonical prior accepted tensor and matching bootstraps:
  results/experiment011-springer-derived-42636962129
- New reproducible four-figure supplementary set:
  results/experiment011-robustness001-pc08-42642807292
- Figure generator PC08 Actions run:
  https://github.com/heri-espino/trendestimation/actions/runs/42642807292
- **Fresh final PDF build:** https://github.com/heri-espino/trendestimation/actions/runs/42643291205
- Archived output branch:
  https://github.com/heri-espino/trendestimation/tree/artifacts/springer-empirical-pc08-42643291205
- New compiled PDF path:
  paper/builds/pc08/springer-empirical-42643291205/springer.pdf
- Source commit used for PDF:
  6ad96bda1841bdbe4f3f38bc723f0b4aa4664d37
- PDF binary SHA-256, independently checked against new build manifest:
  aad05992ae19f4d5db9c7c2ec1e1a4fcc67bb086c3465a645b472b70a4a859a8
- PDF bytes: 529793
- PDF pages: 15, official Springer sn-jnl template.

## Verification performed

1. Confirmed GitHub Actions job used the correct named Windows runner,
   pre-existing trendestimation Conda environment and original
   source-branch SHA (not a historical or main-branch PDF).
2. Existing source-only Experiment011 regression suite: 7/7 tests passed.
3. Renderer used the previously frozen tensor and bootstraps; assertions
   confirmed 2813 recorded jobs, 92,679 rows, 76,220 complete rows,
   9,096 KKT-rejection rows, 6,336 S inversion-error rows and exactly
   9 target failure families with 97 seed indices each.
4. Generated Figs. 5--8 as vector PDFs and PNGs along with source
   script, CSV classifications and claim-to-data ledger. Reviewed all
   four chart previews. The fixed Figure 6 correctly formats n labels
   as integers.
5. The existing builder ran a fresh forced latexmk compilation,
   produced a successful manifest and verified source commit, PDF bytes
   and SHA-256. Final TeX inspection reported no undefined citations,
   references, overfull horizontal boxes or fatal errors. A few
   nonfatal underfull-line warnings are retained.
6. Downloaded the successful Actions ZIP and selected the
   run-specific springer-empirical-42643291205/springer.pdf,
   deliberately rejecting the older 42638070663 PDF that also
   happened to be present in the archive.
7. Opened the new PDF with PyMuPDF, independently confirmed its SHA-256
   and 15-page length, extracted textual references to KKT, 9096,
   the 6984 nine-case subset, SVD, Cholesky and memory trade-offs.
8. Rendered all 15 new pages to separate PNGs and a full contact
   sheet and visually reviewed layout, all four new figures,
   the original four figures, source tables, references and
   declarations. No clipped/blank figure, missing table or
   materially broken page layout was detected.
9. New manuscript PR #126 is still a draft against the
   unmerged handoff PR #124 branch. No merge, new numerical
   experiment, raw-data upload, tolerance change or journal
   submission was performed.

## Scientific claims and limitations

- An SPD Cholesky factor may be computed successfully but
  the post-solve KKT backward-error check may fail. The
  observed 9096 timing/status rows are not 9096 independent
  events, and the spectral evaluator does not apply the
  exact same acceptance test.
- Nine case families have 100% single-candidate completion
  for both methods but 0% full-grid banded completion versus
  100% spectral grid completion, across the observed 97
  seed indices per case. This is a bounded claim.
- Large-n d=4 smoothness inversion errors affect SVD
  too; a universal SVD guarantee is rejected.
- One valid conditional CV case at n=256,d=3 reverses
  from banded/SVD = 0.698 [0.671,0.724] for one candidate
  to 4.846 [4.567,5.125] for M=100, within matched phase.
  All uncertainty is independent-seed-cluster, not rowwise.
- Five dense float64 matrices (SVD) or seven (naive inverse)
  are source-code memory admission policies, not observed
  peak RSS. The two-array banded curve is only an illustrative
  lower-order storage component. No memory failure was
  observed in the 970 work-budget skips.
- Coauthor approval, funding, correspondence, publication
  disclosures, and independent high-precision mathematical
  accuracy beyond existing tests remain outstanding.

## Reproduction

Source-branch checkout, run on PCAG103A-08 using the same Conda env:

    python paper/benchmarks/experiment011/pc08_empirical/robustness001/render.py

    python -m unittest discover -s paper/benchmarks/experiment011/pc08_empirical -p test_*.py -v

    python scripts/build_papers_pc08.py --paper springer --output-dir paper/builds/pc08/verification002 --require-runner

These commands process frozen inputs and compile the manuscript. They
must not run the original numerical Experiment011 campaign, alter the
original raw checkout or same-disk backup, or change solver tolerances.

Review/retarget the draft PR after its handoff base is handled.
Never merge or submit without explicit authorization.
