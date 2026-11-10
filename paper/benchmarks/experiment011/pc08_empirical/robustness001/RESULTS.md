# Experiment011 robustness001: completed postprocessing results

Date: 9 November 2026. All results are derived from the immutable
complete-criterion tensor, not new numerical experiment executions.

- **PC08 figure/action generation:** https://github.com/heri-espino/trendestimation/actions/runs/42642807292
- **Archived output branch:** https://github.com/heri-espino/trendestimation/tree/results/experiment011-robustness001-pc08-42642807292
- **Input timing tensor:** analysis run 42636962129
- **Original final report SHA-256:** c5d4898c83c731ada23a10957f80adc43616200206dc76573f365d38ba37f723
- **Input frozen compressed tensor SHA-256:** a25f674981b1c20df678638287df289c4d888ae62417a3f58ed8a6b2a08fce13

## Observed error mechanisms

| Method | Failure reason from raw comment | Method-level timing rows |
|---|---|---:|
| Banded Cholesky | PLS KKT backward-error rejection | 9,096 |
| Banded Cholesky | Inaccurate smoothness inversion | 2,112 |
| Spectral SVD | Inaccurate smoothness inversion | 4,224 |
| Naive dense inverse | Work-budget exclusion | 776 |
| Spectral SVD | Work-budget exclusion | 194 |

No detected large-series failure should be interpreted as a proven
non-positive-definite input to Cholesky: the banded source performs
the factorization and solve first, then checks a relative KKT
residual (threshold 1e-7), and raises \`ArithmeticError\` on
excess residual. Across the 9096 recorded failure rows, the
reported residual values range from 1.001266e-7 to 1.058734e-6
(median 1.407857e-7). These are repeated timing rows, not
independent numerical realizations. The spectral scorer does not
use precisely the same banded KKT gate; numerical correctness
needs independent certification.

Nine exact 97-seed case families show full completion for both
backends on the single-candidate workloads, and complete-grid
failure for all banded rows but complete-grid success for all
spectral rows:

| Case | n | d | M |
|---|---:|---:|---:|
| pilot_cv_n128_d3_m1000 | 128 | 3 | 1000 |
| pilot_gcv_n128_d3_m1000 | 128 | 3 | 1000 |
| pilot_cv_n256_d4_m100 | 256 | 4 | 100 |
| pilot_gcv_n256_d4_m100 | 256 | 4 | 100 |
| confirm_cv_n256_d3_m1000 | 256 | 3 | 1000 |
| confirm_gcv_n256_d3_m1000 | 256 | 3 | 1000 |
| confirm_gcv_n64_d3_m10000 | 64 | 3 | 10000 |
| pilot_mle_n256_d3_m100 | 256 | 3 | 100 |
| confirm_mle_n512_d3_m100 | 512 | 3 | 100 |

Each of these contributes 776 repeated full-grid timing rows per
method (97 seeds, 2 repeats, 2 coordinates, 2 series workloads);
the 6984 banded rejected rows in these nine cases and the
additional 2112 large-n fourth-order banded KKT rejected rows
sum to the observed 9096. Thus there are only 97 independent
seed clusters per case, not thousands of independent repeats.

**High-order caveat:** CV/GCV at n=1024,2048,4096 and d=4
also had 6336 total rows indicating inaccurate S inversion,
distributed across both methods. SVD is not universally robust;
invalid grids never win measured speed rankings.

## Valid paired performance

In the 24-worker phase, one BLAS thread per job, direct-S
coordinate, a single series and identical valid case-seed
pairing, the banded/SVD complete cold-time geometric ratio
for one candidate versus 100 candidates was:

| Case | One candidate | 100-candidate grid |
|---|---:|---:|
| GCV n=64,d=1, fixed mean | 1.001 [0.982,1.018] | 2.328 [2.282,2.374] |
| CV n=128,d=3, fixed mean | 1.069 [1.052,1.087] | 5.401 [5.244,5.555] |
| CV n=256,d=3, plug-in mean | 0.698 [0.671,0.724] | 4.846 [4.567,5.125] |

Confidence intervals come from the frozen independent-seed
bootstrap, not a new pseudoreplication of repeated timing rows.
Ratio above 1 favors SVD; below 1 favors banded.

## Memory is an admission model, not observed RSS

Experiment011 specifies a 2 GiB dense memory cap. Versioned
Experiment006 source computes a conservative allowance of
5×8n² bytes for SVD and 7×8n² bytes for a naive inverse,
with two banded arrays contributing about 2×8n(d+1) bytes.
At n=4096 the SVD allowance is 640 MiB; at unmeasured
n=8192 it is 2.5 GiB, above the cap. No peak RSS measurements
or out-of-memory events are inferred. All 970 explicit
\`budget_exceeded\` timing rows are due to configured
work ceilings, not demonstrable memory exhaustion.

## Reproduce, verify, then continue

Figure source: \`render.py\`, independent seed-bootstrap
reference: \`../derived/42636962129/paired_backend_seed_bootstrap.csv\`.
The run logs report all dataset checks passed; four vector
PDFs, four PNG previews, five analysis CSVs and JSON ledgers
were committed on the permanent results branch and scoped
manuscript PR. Re-run the renderer against the *frozen tensor*
to regenerate graphics, without changing the original source
or numerical tolerances.

Next: incorporate into \`paper/main.tex\` and the new
\`paper/sections/experiment011_robustness.tex\`, compile via
\`scripts/build_papers_pc08.py --paper springer\`, inspect
all pages, then update the draft PR #126. Never merge or
submit without author authorization.

## Fresh manuscript build requirement

This revision includes four additional vector figures and new numerical failure/memory sections. The PDF must be freshly rebuilt on PCAG103A-08 and inspected; the previously compiled Springer PDF predates robustness001 and must not be presented as the updated manuscript.
