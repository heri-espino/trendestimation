# Repository integration audit — November 4, 2026

The author authorized merging the open PRs and cleaning up the repository.
All 15 PR heads below are preserved as ancestors of the integration branch.
Merges retain original commits, scripts, measured data and provenance.

## Preserved PRs

| PR | Branch | Original head |
|---|---|---|
| [#69](https://github.com/heri-espino/trendestimation/pull/69) | `docs/future-project-smoothness-trend-comparison` | `33af2013180d57bab90bc58b1b512b17b7f21cdf` |
| [#78](https://github.com/heri-espino/trendestimation/pull/78) | `fix/ci-sncs-typography-unused-import` | `009bab820ef4e154ff674b1e1f2d23ba61014b18` |
| [#79](https://github.com/heri-espino/trendestimation/pull/79) | `feature/smoothness-first-computation-paper` | `30f017be52b03fb19d81e8765351adbb2a5adc36` |
| [#80](https://github.com/heri-espino/trendestimation/pull/80) | `experiment003/large-series-s-grid-caching` | `bae98e76a079528b006a3404ed007606c241e2f4` |
| [#81](https://github.com/heri-espino/trendestimation/pull/81) | `feature/sncs-awesomefigures-auto-publication` | `75893f916c3bf54f243f87454ca6053bfd7c8645` |
| [#82](https://github.com/heri-espino/trendestimation/pull/82) | `analysis/experiment003-windows-results-20261028` | `36b35e8a8f9c24d76ea64d147b615cbf2eb1bf8f` |
| [#90](https://github.com/heri-espino/trendestimation/pull/90) | `experiment005/paired-accuracy-runtime` | `b39618f7fce7a4af8ae6c262142dcda5d73ad78a` |
| [#91](https://github.com/heri-espino/trendestimation/pull/91) | `experiment005/joint-accuracy-runtime` | `873e6a544b1a5569901ab251482665a74bdfdb8b` |
| [#100](https://github.com/heri-espino/trendestimation/pull/100) | `research/experiment010-multibackend-frontier-design` | `5eb5b30ae8a172dc1d56f2d46f1024c6ce9370ab` |
| [#101](https://github.com/heri-espino/trendestimation/pull/101) | `research/experiment010-comprehensive-grid` | `1f12c962ee84589048457074bf276db598d9c933` |
| [#103](https://github.com/heri-espino/trendestimation/pull/103) | `research/experiment010-uncapped-checkpointed` | `8a02f4a52d81994daef83c4d8d1ef168aa9c832e` |
| [#104](https://github.com/heri-espino/trendestimation/pull/104) | `research/experiment010-parallel-local` | `bf4195c12e3c4b07e039df85971b303ab1d83d37` |
| [#105](https://github.com/heri-espino/trendestimation/pull/105) | `research/experiment010-focused-three` | `09b9f7aa36443bb119d799632dc91bda85d32433` |
| [#109](https://github.com/heri-espino/trendestimation/pull/109) | `paper/csda-computational-theory` | `4353e61a63683f4d0f199852c4fe4069d70cd289` |
| [#110](https://github.com/heri-espino/trendestimation/pull/110) | `paper/springer-implementation-experiment011` | `31c310590d1799a0002f045a052f47a68052b2da` |

## Conflict decisions

- Preserve both current manuscript handoffs; label older Experiment010 instructions as historical.
- Preserve the four manuscript tracks and the approved 29-case Experiment011 design.
- Preserve current fit-only `experiment005/run.py`. PR #90 precision/runtime uses `experiment005/paired_run.py`; update its workflows, commands and imports. Archived datasets and original input hashes are untouched.
- Preserve the newer historical SNCS PDF instead of PR #79's older binary. Rebuild the historical PDF before redistributing it as matching the integrated source.
- Preserve theory-first Paper B `main.tex` and `main.pdf` from PR #109. PR #100's earlier empirical manuscript remains in Git at `5eb5b30ae8a172dc1d56f2d46f1024c6ce9370ab`; retain its evidence and other files without making that manuscript current.
- Preserve old AwesomeFigures outputs and numerical data. Restore incidental figure rewrites made by tests in this scratch checkout.
- This cleanup does not launch a benchmark campaign, Windows run, new parameter search or manuscript submission.
- Historical factorial and uncapped runners remain available for reproduction, but are not the active Experiment011 schedule.

## Branch cleanup policy

After merge, remove only fully integrated PR source branches. Keep all `results/*`,
backup branches and branches with unique unmerged commits. Recover deleted PR heads
from the immutable commits above or corresponding PR refs.

## Next action

Read [SESSION_HANDOFF.md](SESSION_HANDOFF.md). Create the Windows results worktree from
`origin/main`, then run the pending small 16-series/16-worker GCV pilot.
The d=4 and n=1024/2048/4096 cases remain prepared; Windows completion is not claimed.

## Validation

- Combined root suite: **1236 passed, 4 skipped, 26 subtests passed** (Python 3.12, one OpenBLAS thread).
- Experiment011: **22 unittest checks passed**.
- Paper B deterministic verification: **12 algebraic cases passed**.
- Ruff: `src tests benchmarks paper/benchmarks/experiment011` passed.
- All 15 original PR head commits verified as ancestors.
- No timing ranks or new Windows observations were generated.
- Historical manuscript PDFs were not rebuilt during integration; the Paper B theory PDF is retained from its validated source branch.
