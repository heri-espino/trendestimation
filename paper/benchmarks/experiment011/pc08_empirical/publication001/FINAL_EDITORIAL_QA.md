# Final Springer journal-language PDF verification

Status: **scientifically and typographically compiled; pending author submission declarations.**
Date: November 9, 2026.

## Build and fidelity

- Official Springer Nature \`sn-jnl\` template; canonical source
  \`paper/main.tex\` and three academic sections.
- Successful Windows PCAG103A-08 build:
  https://github.com/heri-espino/trendestimation/actions/runs/42654369909
- Frozen manuscript/figure source SHA:
  \`0579c831df81b821f1920358092c9b522511fbe1\`
- Immutable compiled artifact branch:
  \`artifacts/springer-empirical-pc08-42654369909\`
- Exact PDF path:
  \`paper/builds/pc08/springer-empirical-42654369909/springer.pdf\`
- PDF SHA-256 independently checked against the actual
  downloaded binary and build manifest:
  \`462a4cfb82e4bb290d85e38034f1485ce0983460645d3f8729d2008cbae48745\`
- Size: 514,672 bytes. Pages: 16.
- No LaTeX fatal errors, missing references or citations,
  overfull boxes; two nonfatal underfull lines.
- Seven existing ingestion/analysis unit tests passed.
- All sixteen pages rendered to images and reviewed;
  all eight scientific figures and their captions are present,
  and the new numerical table is readable.
- Public-facing PDF text has no \`Experiment011\`, \`pilot\`,
  \`smoke\`, \`GitHub Actions\`, \`PC08\` or raw-machine-directory
  strings; only reproducibility information suited to an
  academic data/code availability statement remains.
- The revised spectral grid figure was separately inspected
  and its legend moved away from the plotted confidence
  intervals before the final build.
- The revised memory policy figure was regenerated without
  the source benchmark identifier.
- DOI/reference metadata from the canonical bibliography
  were retained; no fabricated experimental result,
  untested method or new statistical estimator was added.

## Scientific conclusion and boundaries

**Primary claim:** in the eight representative matched and valid
complete-criterion CV/GCV 100-candidate grids, SVD is faster
than the measured banded implementation; spectral decomposition
should be the recommended default for repeated searches **when
dense workspace allocation is feasible**. A single-candidate
ratio can favor banded Cholesky, and the plotted larger
fourth-order configurations exhibit inversion failures for
both implementations. Numerical completion is not directly
equivalent to high-precision accuracy, as the two implementations
use different acceptance checks. The memory figure is an
admission-policy model, not measured peak RAM.

## Submission sign-off

The older draft listed Daniela Cortés-Toto as a coauthor
without independently established contribution or consent.
The revised author-review title page lists only the verified
project author. **The author must explicitly approve the final
authorship and contributions;** verified collaborators can and
should be restored before submission with their consent.
Likewise, corresponding email, funding statements, competing
interests and permissions for raw numerical data must be
confirmed before journal submission.

The current draft PR #126 is intentionally unmerged, stacked
on open PR #124. Nothing has been submitted to a publisher,
and no long-running numerical campaign has been restarted.
