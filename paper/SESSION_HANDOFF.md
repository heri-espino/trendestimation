**Paper C scientific-editorial continuation (2026-11-09):** Review branch `paper/paper-c-scientific-editorial-review` is derived from the unchanged open PR #131, not PR #132. Read [scientific editorial audit](ngsim-jerk-case-study/notes/SCIENCE_EDITORIAL_REVIEW.md) for method-dependent reference-jerk comparability, conditional plug-in TSVD-GCV/EDF caveats, the exact archival near-interpolation error decomposition, and improved known-jerk-before-calibration reading order. **No Experiment004--008 rerun, no merge and no submission.** Publication PDF/build status must be checked against this branch's latest Actions run; the earlier PR #131 11-page PDF remains a valid historical build, not evidence that these new edits have compiled.

# Start here — publication split and the next Experiment011 Windows run
## Newest paper request: third-order PLS physical methodology, simulations + real data (Nov 9, 2026)

[Full editorial and results handoff](ngsim-jerk-case-study/notes/METHOD_FIRST_EDITORIAL_HANDOFF.md). User declined a computational (backend/timing) focus for Paper C; it now explains Guerrero PLS, normalized smoothness index S, Gaussian noise interpretation, and actual physical jerk/vehicle reconstruction, with independent synthetic and recorded real cases. A NEW Experiment008 [run #42717662044](https://github.com/heri-espino/trendestimation/actions/runs/42717662044) compared soft PLS spectral regularization with hard TSVD truncation of D3, spline GCV and SG, matching the archived Experiment005 1296 known-jerk synthetic trials and Experiment004 200 real NGSIM episodes. Historic PLS profile-ML lambda/mu are reused unchanged from Experiment006. Known jerk RMSE PLS 2.441 vs EDF-matched TSVD 2.942 m/s³; real 1s three-point PLS .514 vs TSVD .512 m; separately spline quadratic Taylor .348 m. Experiment007 1944 controlled noise-factorial cases/72 independent parent draws remain intact and their S calibration figures included. Successful official Elsevier CAS PDF [run #42719535746](https://github.com/heri-espino/trendestimation/actions/runs/42719535746) passes both audits (11 pages). Compiled PDF on [open PR #131](https://github.com/heri-espino/trendestimation/pull/131); full VM path C:\Users\175199\Documents\TrendEstimation-PaperC\manuscript-methods\run-42719535746-a1; immutable full archive results/paper-c-methods-pdf-pc08-42719535746-a1. Original five figure files, criterion heatmaps and backend comparisons are preserved in Git but solver comparisons excluded from main paper. No merge, other projects remain isolated.

## Newest Paper C Experiment007 — smoothness/noise calibration COMPLETE (2026-11-09)

[Full verified run ledger](ngsim-jerk-case-study/experiments/experiment007/RUN_LEDGER.md). The author requested targeted validation of relative spectral observation-noise attribution by the normalized S index with **separate controlled changes in true jerk variability**. [Successful PC08 #42660204414](https://github.com/heri-espino/trendestimation/actions/runs/42660204414) and cloud #42660028292 executed complete 162-case pilot and 1,944-case confirm, four selectors and 7,776 valid selections. All factorial outcomes are **paired**: 72 independent generated parents underlie 1,944 conditions, so bootstrap uses parents. Under iid Gaussian assumptions joint REML calibration Spearman .9654, MAE .01148; increasing noise raises selected S ~+.1498, increasing actual jerk SD reduces S ~−.1387; same-ratio scaling leaves S fixed despite 16x observation variance. Serially correlated error caused MAE ~.0712 (iid jerk) and .1111 (AR1 jerk), a serious limitation. Windows complete root C:\Users\175199\Documents\TrendEstimation-PaperC\experiment007\run-42660204414-a1; 39 exact file paths and SHA hashes, all clean/noisy generated arrays, experimental configs, risk/parameter rows and five plots in unique Git results branch results/paper-c-exp007-pc08-42660204414-a1. New manuscript position: S is a **model-dependent relative spectral noise fraction**, not physical sensor precision or universally clean data. Existing Experiment004 real-data spline superiority and Experiment006 joint REML negative result both remain intact. No paper PDF or unrelated research altered. Read latest ledger before any further work.

## Most recent Paper C verified Experiment006 (Nov 9, 2026)

The author authorized joint optimization of the reference mean mu and penalty lambda, plus a forecast-directed training-only shrinkage comparison. [Completed experiment006 run ledger](ngsim-jerk-case-study/experiments/experiment006/RUN_LEDGER.md), [PC08 success #42639588117](https://github.com/heri-espino/trendestimation/actions/runs/42639588117), [PR #127](https://github.com/heri-espino/trendestimation/pull/127). Reused (not recreated) Experiment005 simulated 96 pilot/1296 confirmation trajectories and Experiment004 real 200 NGSIM episodes. New persistent VM root: C:\Users\175199\Documents\TrendEstimation-PaperC\experiment006\run-42639588117-a1; all 47 files, 18.5MB and SHA-256 paths mirrored to isolated Git results branch. The unknown-mean REML corrects the nuisance mean by GLS and removes one additional likelihood dimension; it is *not* the previous conditional sample plug-in. Under synthetic known truth global OLS mean with fixed-mu profile ML achieves jerk RMSE 2.441 m/s³, compared with 3.295 for joint REML; zero fixed mu is 2.587. Joint REML 1-second synthetic local25 clean-position RMSE 0.498m vs 0.405m for fixed-zero ML. In real camera positions, joint REML selected lambda=0 in 161/200 episodes; its 1-second local25 RMSE was 0.578m versus spline 0.348m. **Early grid analysis incorrectly included zero; corrected strictly predeclared 15-point grid results are used here.** Scientific result is negative/mixed, not a new globally superior estimator. No manuscript revision or merge performed. Older status notes below are dated history.


## Newest Paper C results: Experiment005 simulation complete (2026-11-08)

[Run ledger](ngsim-jerk-case-study/experiments/experiment005/RUN_LEDGER.md), [successful hosted run #42547883064](https://github.com/heri-espino/trendestimation/actions/runs/42547883064), [complete Git archive](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp005-cloud-42547883064-a1). Confirm: 1,296 independent analytic known-jerk trials plus 96-trial pilot; 12,960 PLS selections, 89,424 complete forecast rows, 15,552 historical jerk error rows, 62,208 fixed-S reference ablation rows and no invalid outcomes. All first-party generated true/noisy trajectories, full data, plots, configuration, environment and file hashes are committed. PLS with profile ML and global cubic OLS mean historical jerk RMSE **2.918 m/s³**, zero mean **3.021**, GCV spline **60.913** under the simulated conditions; nonzero reference helps sustained jerk but may worsen reversals, and sample mean is endpoint-sensitive. **Do not claim this proves real camera jerk accuracy:** real FHWA Experiment004 preferred the spline in future recorded-position forecasts. PCAG103A-08 run #42547250403 remains queued as a *separate* Windows computation, not VM-confirmed. Import cloud data using the checksum-verifying PowerShell sync script, which must label the copy as an import. No simulation manuscript rewrite or merge has occurred. Older notes below are dated and superseded by this verification.


## Latest Paper C update: known-jerk Experiment005 (2026-11-08)

The author has just authorized **simulations** following
completed observational Experiment004. Read
[experiment005 README](ngsim-jerk-case-study/experiments/experiment005/README.md)
and its fixed [config.json](ngsim-jerk-case-study/experiments/experiment005/config.json).
A dedicated PCAG103A-08 workflow runs a small pilot of
96 independently seeded analytic jerk trajectories and,
only on success, a 1,296-trial confirmation with separate
seeds. It compares d=3 PLS GCV vs Gaussian profile ML,
zero/sample/global-OLS/tail-OLS/synthetic-oracle `mu`,
both existing continuation rules and GCV spline/SG
baselines. Outputs directly measure **known historical
discrete jerk** and clean-position forecasts, unlike
earlier NGSIM only recorded-position error.
A fixed-S crossed reference-mean ablation separates
smoother and extrapolation effects. All datasets,
noisy/clean trajectories, losses, figures, failure
rows and reproducibility metadata reside in a unique
non-overwriting PC08 persistent directory, and are
pushed in full to an independent Git results branch.
**Do not infer numerical success from workflow creation.**
This branch is separate from the active PR #122 based
on earlier Paper C PR #121. No manuscript has yet been
rewritten with these *not-yet-validated* simulation results.


## Completed expanded real-only Paper C experiment004 (2026-11-08)

[Completed run ledger](ngsim-jerk-case-study/experiments/experiment004/RUN_LEDGER.md);
[PCAG103A-08 workflow #42538556206](https://github.com/heri-espino/trendestimation/actions/runs/42538556206);
[stacked code PR #122](https://github.com/heri-espino/trendestimation/pull/122)
against still-open Paper C PR #121.
FHWA real data: **200 episodes** (100 each US-101/I-80),
400,000 downloaded source observations, 6,600 completed forecasts,
800 PLS GCV/profiled marginal ML selections and a successful
paper compilation. 38 VM-generated files/8 data/result/log/build
directories are listed with SHA-256 values in the full
`file_inventory.json` on the VM and Git results branch.
All raw original API pages and results reside at
`%USERPROFILE%\Documents\TrendEstimation-PaperC\experiment004\run-42538556206-a1`.
The Git results-only branch is
`results/paper-c-exp004-pc08-42538556206-a1`, including all
compact numeric records and provenance metadata.

**Scientific finding:** The tuned GCV cubic spline with quadratic
continuation has pooled RMSE of **0.135, 0.348, 0.879 m** at
0.5/1/2 seconds, compared to **0.143, 0.512, 1.869 m** for
PLS d=3, mu=0, profiled Gaussian ML, last3 recurrence.
Thus the expanded evaluation does **not** confirm a general
PLS forecast advantage. The study has just five coarse recording
session proxies; episode-level bootstrap inference is exploratory
and true physical jerk is unobserved. Do not claim universal
PLS or nonzero-mu superiority based on the five-track pilot.
No simulations were requested or conducted. The earlier
“workflow running” statements below are dated history.
The source manuscript has **not been rewritten** with the new
expanded results; this is the next editorial task.


## Paper C real NGSIM expansion — new user decision (2026-11-08)

The author chose **not to run synthetic known-jerk experiments** for
the present manuscript. Instead, expand the official US-101 and I-80
raw-position dataset, compare PLS with `criterion="gcv"` versus the
repo's `criterion="mle"` (profiled Gaussian marginal likelihood),
and include GCV smoothing splines and Savitzky--Golay. The new
[experiment004 README](ngsim-jerk-case-study/experiments/experiment004/README.md)
describes input pagination, session-aware episode IDs, fixed training
window/origin/horizons, bootstrap, file tree and VM-only raw storage.
Source/data/results must be recorded separately in
`%USERPROFILE%\Documents\TrendEstimation-PaperC\experiment004\run-<id>-a<attempt>`.
The self-hosted workflow runs on PCAG103A-08 from a new branch stacked
on Paper C PR #121 and produces an immutable results-only Git branch
for complete scored rows, file hashes and references. **Never infer
success before reading the actual run; do not claim true physical jerk
accuracy, or unique real drivers from reused numeric Vehicle_IDs.**
Retain prior simulation ideas as optional future work, not an
authorized immediate experiment.


## Paper C empirical follow-up and publication draft (2026-11-08)

**Active research PR:** [#121](https://github.com/heri-espino/trendestimation/pull/121).
The new Paper C subdirectory `ngsim-jerk-case-study/experiments/`
contains **three sequential experiments**, with permanent output records:
[experiment001](ngsim-jerk-case-study/experiments/experiment001/README.md)
(Guerrero-inspired third-order recurrence; 900 rows),
[experiment002](ngsim-jerk-case-study/experiments/experiment002/README.md)
(spline/SG/local-polynomial rules; 315 rows), and
[experiment003](ngsim-jerk-case-study/experiments/experiment003/README.md)
(training-only GCV spline; 180 rows). The latter two completed on the
self-hosted PCAG103A-08 runner
([run 42521326853](https://github.com/heri-espino/trendestimation/actions/runs/42521326853),
[run 42521725044](https://github.com/heri-espino/trendestimation/actions/runs/42521725044)).
An updated NGSIM manuscript including the matching table compiled
successfully on PC08
([run 42522124213](https://github.com/heri-espino/trendestimation/actions/runs/42522124213));
its PDF/logs are preserved on a separate results-only branch.

**Findings:** PLS with (d=3,mu=0) and the last-3 recurrence:
RMSE 0.0745, 0.2958 and 1.2998,m at 0.5/1/2,s. A GCV spline with
quadratic Taylor continuation gives 0.1233, 0.2951 and 0.8085,m:
PLS is favorable at 0.5,s, tied at 1,s, worse at 2,s. Nonzero-(mu)
benefit reverses by continuation. The five track segments represent
**only two distinct original vehicle IDs**, 15 overlapping origins,
and no independent jerk truth. These are historical exploratory results,
not proof of first use, physical jerk fidelity, or population efficacy.
Old statements below saying no Paper C experiment has run are dated
historical notes and superseded by this section.

Future research: independent vehicle-ID validation, known-jerk
synthetic experiment (next free identifier `experiment004`), then
fit-versus-continuation (mu) ablation, without mixing them into
the independent Springer Experiment011 timing workstream.
Do not merge open PRs without explicit user authorization.


## Paper C new research question (2026-11-05)

See [extrapolation research handoff](ngsim-jerk-case-study/notes/EXTRAPOLATION_RESEARCH_HANDOFF.md),
[fit-versus-continuation proof](ngsim-jerk-case-study/notes/EXTRAPOLATION_DECOMPOSITION.md),
[mu policy catalogue](ngsim-jerk-case-study/notes/MU_POLICY_CATALOG.md),
and [planned factorial ablation](ngsim-jerk-case-study/notes/EXTRAPOLATION_ABLATION_PLAN.md).
The distinctive **hypothesis** is a training-derived nonzero
jerk reference at d=3 with separate local polynomial continuation,
not first-in-history PLS forecasting: Biessy (2025 online/2026
volume) already develops WH extrapolation. At fixed S the mu
difference has an exact decomposition into fitted-trend and
continuation contributions. Only existing `zero` and `sample`
mu policies are currently implemented. **No future Paper C
experiment has been run**. Preserve its original pilot and do not
confuse this independent workstream with the Windows Experiment011
algorithm timing study below.


## Paper C annotated literature review (2026-11-05)

The user requested **Markdown annotations and a merged repository record**,
not an image. Read [Paper C literature index](ngsim-jerk-case-study/notes/README.md),
[comparison](ngsim-jerk-case-study/notes/LITERATURE_REVIEW.md), and
[math observations](ngsim-jerk-case-study/notes/MATHEMATICAL_NOTES.md)
before future NGSIM study edits. Source notes distinguish uploaded
Marczak/Cao/Zhu PDFs, the Tang arXiv source, Fan's published abstract
and the existing Guerrero/Cortés-Toto extracted literature.
No evidence has been added to the five-vehicle pilot and no broader
originality claim has been established. This does not change Experiment011
or any other paper's research scope.


## Manuscript compilation workflow (2026-11-04)

Editorial [PR #112](https://github.com/heri-espino/trendestimation/pull/112) was merged into `main` at `9b64b244`. An independent PC08 manuscript-only workflow is documented in [BUILD_ON_PC08.md](BUILD_ON_PC08.md). It compiles five active and two historical LaTeX entrypoints on the named university Windows runner using the existing `trendestimation` Conda Python and preinstalled TeX. Run it manually; it does **not** run Experiment011 or update measured results. Each execution archives PDFs, LaTeX logs and SHA-256 provenance to an isolated results branch rather than `main`. A first successful PC08 run is still required before claiming that all sources compile.

Updated: 2026-11-04 (America/Mexico_City). This is the compact session-continuation
record requested by the author before a context reset. Read this, root
`AGENTS.md`, `AI_HANDOFF.md`, `PUBLICATION_MAP.md`, `SPRINGER_READINESS.md`, and
`benchmarks/experiment011/{AGENTS.md,README.md,cases.json}` before acting.
The case file specifies the executable design; earlier 21-case and full-factorial
notes are historical. Do not expand the experiment or change its algorithms
as part of resuming this session.

## Parallel manuscript editorial review — November 4, 2026

A separate **draft** [PR #112](https://github.com/heri-espino/trendestimation/pull/112) proposes prose improvements and two mathematical clarifications across the manuscript portfolio. Read [EDITORIAL_LITERATURE_AUDIT.md](EDITORIAL_LITERATURE_AUDIT.md) for the source-to-claim ledger, tested CV leverage correction, and remaining primary-source checks. This editorial work has **not** run Experiment011, replaced numerical results, recompiled every paper or authorized submission. The four-paper split and pending 29-case Windows protocol are unchanged. Do not merge this editorial PR without review and author approval.

## Integration update — November 4, 2026

The author explicitly authorized merging and repository cleanup. The integration
PR consolidates the previously open research PRs while preserving their history.
After integration, use `origin/main` for the next results worktree. The four-paper
split, 29-case design and pending Windows pilot are unchanged. See
[REPOSITORY_CLEANUP.md](REPOSITORY_CLEANUP.md) for the audit and conflict decisions.
The pre-integration PR/branch statements below are historical provenance.

## Immediate state and next action

- Repository: `https://github.com/heri-espino/trendestimation`.
- Active preparation: **open, unmerged PR #110**, branch
  `paper/springer-implementation-experiment011`. Inspected source head:
  `d3782571983724e66fb081cd1f371761301b2f17`. This handoff is a later
  documentation update on that branch; fetch its current tip before continuing.
- At inspection, PR #110 targets `main` at
  `54e00c2d11e29e8fff2ee5deadb5ca17aa39e851`.
- **User is blocked before the first Windows parallel-series run.** They ran
  `campaign.py` from `C:\Users\175199\trendestimation`, and Python reported
  `[Errno 2] No such file or directory`. Their `git pull` fetched the preparation
  branch but left their current checkout without that file. The transcript does
  not establish which branch was checked out. Fetching an open PR branch does
  not put its files into the current working tree.
- Resolution: create a separate results worktree from the preparation branch,
  use the existing Conda environment and that worktree's `src`, then execute the
  exact small pilot below. Preserve the user's original checkout and results.
- **No successful Windows Experiment011 run was provided in this session.**
  The failure occurred before Python could load the benchmark. Do not describe
  the planned 16/32-worker runs, d=4 pilots, or larger confirmations as measured.
- The author approved the focused Experiment011 study and asked for d=4,
  n=1024/2048/4096, plus optional parallel independent small-series computation
  on their 32-logical-processor machine. They explicitly liked the rest of the
  existing design. The 252,000-cell historical factorial is not the active task.
- This update preserves decisions and reproduction instructions; it does not
  launch the Windows campaign, alter `cases.json`, change solvers, or merge PRs.

## Scientific ownership of the manuscripts

| Track | Canonical source | Contribution and boundary | Current continuation |
|---|---|---|---|
| CSDA A | `paper/csda-spectral-smoothness/` | Spectral formulation, smoothness normalization, numerical reliability, shift-free reconstruction, high-precision evidence | Preserve; do not absorb into the timing paper |
| CSDA B | `paper/csda-computational-costs/` | Amortized operation/storage bounds, complete-criterion costs, selected inverse, conditional algorithm crossover; a bounded timing/jerk illustration provides context | Open PR #109, `paper/csda-computational-theory`; inspected head `4353e61a63683f4d0f199852c4fe4069d70cd289` |
| Springer Computational Statistics | `paper/main.tex`, `paper/sections/` | Implementation, actual measured milliseconds/seconds, caching, full-criterion numerical validity, reproducible latency and separate throughput experiments | Experiment011 on PR #110; results-driven manuscript rewrite follows validated Windows data |
| NGSIM application | `paper/ngsim-jerk-case-study/` | Real vehicle-position trajectories, d=3 jerk proxy, training-derived mean, estimated trend and separately constructed forecast with chronological holdouts | Preserve data/provenance and application claims separately |

`paper/computational-statistics-submission/` is a preserved historical **SN
Computer Science** draft. It is distinct from the canonical Springer
**Computational Statistics** source `paper/main.tex`. Preserve the Springer
`sn-jnl` and Elsevier CSDA templates in their respective manuscripts.

The latest CSDA B revisions are on PR #109, not necessarily in `main` or this
branch: redesigned core/hybrid tables, explicit conditional method-choice
discussion, theoretical regime and amortization figures, a matched timing
illustration and a contextual NGSIM figure. Inspect that branch before editing
it. Reused evidence must be attributed; theory, precision, runtime, and physical
forecasting are separate scientific questions, not interchangeable novelty.

## Approved Experiment011 design

`paper/benchmarks/experiment011/cases.json` has **29 cases: 2 smoke, 15 pilot,
12 confirm**. Preserve the original 21 and the eight approved additions:

| Additional cases | d | M | Complete-criterion methods |
|---|---:|---:|---|
| `pilot_{gcv,cv}_n256_d4_m100` | 4 | 100 | spectral SVD and banded Cholesky |
| `confirm_{gcv,cv}_n1024_d4_m100` | 4 | 100 | spectral SVD and banded Cholesky; explicit 750,000,000-unit work cap |
| `confirm_{gcv,cv}_n2048_d4_m100` | 4 | 100 | banded Cholesky only |
| `confirm_{gcv,cv}_n4096_d4_m100` | 4 | 100 | banded Cholesky only |

Braces in the table denote two case names, not literal CLI syntax. Confirm
cases require `--allow-confirm` and should follow review of smaller pilots.
Banded-only large-n times establish scaling observations, not SVD superiority
or independent cross-method numerical parity. They do not prove dense methods
impossible on all hardware; they reflect this predeclared resource design.

The targeted cases cover d=1,2,3,4, n=64 through 4096 selectively, M=100/1000/
10000 selectively, zero and separately labeled conditional data-derived means,
CV/GCV/AICc/MLE, low-amplitude smoke and mostly high-amplitude pilots. They are
not a Cartesian product; BIC, d=5/6, fixed mu=0.15, M=100000, and very large n
remain in historical studies/indexes rather than this selected case list.

The serial `campaign.py run` evaluates four workloads for one case/block:
one S/one series, full S-grid/one series, one S/multiple series, and full
S-grid/multiple series. One S is 0.5; a full grid is `{j/M: j=1,...,M}`,
including exact S=1. Both `direct_s` and `mapped_lambda` use the same candidates:
on-demand S-to-lambda mapping versus pretranslation/reuse, not two continuous
optimization algorithms. Pilots/confirmations plan blocks 0,1,2 with two
repeats per block, independent seeded inputs and rotated method order; smoke
has one block/repeat. The primary outcome is **computing time, not RMSE**.

Serial outputs go to `runs/<tag>/<case>/blockNNN/`. Existing Experiment006
`run_slice` supplies the complete-criterion computation; Experiment011 admits
n=2048/4096 only inside its temporary input-admission context. Do not edit the
historical Experiment006/008 factor levels or pull in the open Experiment010
runner stack merely to execute this campaign.

## Exact next Windows run: fresh results worktree

Run this in **PowerShell** from the existing university checkout. The chosen
worktree and result branch are new names; if either already exists, inspect and
resume it or choose a new sequence. Do not delete, reset, or force-push it.
Native-command exit checks prevent accidentally continuing in the old checkout.
No package installation is needed: the existing non-admin Conda environment is
`trendestimation` (not `trend-estimation`).

```powershell
Set-Location "C:\Users\175199\trendestimation"
git fetch origin
if ($LASTEXITCODE -ne 0) { throw "Git fetch failed." }

git worktree add -b results/experiment011-PCAG103A08-parallel001 "C:\Users\175199\trendestimation-springer-exp011-parallel001" origin/main
if ($LASTEXITCODE -ne 0) { throw "Worktree creation failed; inspect existing paths/branches before continuing." }
Set-Location "C:\Users\175199\trendestimation-springer-exp011-parallel001"

conda activate trendestimation
if ($LASTEXITCODE -ne 0) { throw "Conda activation failed." }
$env:PYTHONPATH = (Join-Path (Get-Location).Path "src") + [IO.Path]::PathSeparator + $env:PYTHONPATH
if (-not (Test-Path "paper/benchmarks/experiment011/campaign.py")) { throw "Wrong checkout: Experiment011 is missing." }

python -m unittest discover -s paper/benchmarks/experiment011/tests -v
if ($LASTEXITCODE -ne 0) { throw "Experiment011 checks failed; preserve the output and review before timing." }

python paper/benchmarks/experiment011/campaign.py parallel-series --case pilot_gcv_n64_d1_m100 --run-tag PCAG103A08_parallel001 --block 0 --series-count 16 --series-workers 16
$experimentExitCode = $LASTEXITCODE

# Archive available rows/checkpoints even if the numerical run failed.
git add .
if ($LASTEXITCODE -ne 0) { throw "Result staging failed; keep the worktree." }
git commit -m "experiment011: archive Windows 16-series 16-worker GCV pilot and QA"
if ($LASTEXITCODE -ne 0) { throw "Result commit failed; inspect and preserve the run before pushing." }
git push -u origin results/experiment011-PCAG103A08-parallel001
if ($LASTEXITCODE -ne 0) { throw "Result push failed; keep the worktree and retry archival." }
if ($experimentExitCode -ne 0) { throw "Benchmark failed; review the preserved manifest/checkpoints before another run." }
```

This runs **one small GCV case**, n=64,d=1,mu=0,high amplitude, with naive
inverse, spectral SVD, and banded Cholesky. Six method/repeat groups run in
sequence; within each group up to 16 processes handle 16 independent series.
Each worker uses one BLAS thread and evaluates both one-S and M=100 grid
workloads under both mapping policies. Expected complete coverage is
`3 methods * 2 repeats * 16 series * 2 workloads * 2 policies = 384 rows`;
this is an expectation, not a successful-result count. Read `parallel_qa.json`
and all statuses before calling it valid.

Output: `paper/benchmarks/experiment011/runs_parallel/PCAG103A08_parallel001/
pilot_gcv_n64_d1_m100/block000/`, including `parallel_manifest.json`,
`parallel_raw_times.csv`, `parallel_method_wall.csv`, `parallel_qa.json`, and
per-series worker checkpoints. Existing run paths refuse overwriting. Interrupted
outputs need a fresh tag for a new run; no automatic resume is promised.

Parallel mode is limited to n<=256,M<=1000,2<=R<=32,workers<=min(R,32).
Each process privately constructs mapper/factors; it does not share the serial
R-series cache. `group_elapsed_wall_s` covers a whole method/repeat group,
including both workloads/policies and process scheduling. Per-row setup is
attributed repeatedly; summing those rows is not group wall time. Keep this
throughput data separate from serial `runs/` and `analyze.py`. To compare 8,16,
32 workers later, hold total series count fixed (for example R=32), use new
tags and identical blocks, and vary only worker count; do not infer scaling by
changing both R and workers simultaneously.

## Evidence already available and limits

- Hosted process-pool QA: Actions `41796045403`, archive
  `runs_parallel/parallel_gha_41796045403/smoke_gcv_n64_d1_m100/block000/`.
  Manifest: source `88e7c60b67823a0ab96d71515765277fa3dfa05f`, Linux,
  3 independent series, 2 workers, 1 repeat. QA: **36/36 ok**, 24 paired
  comparisons, zero issues. This is not the Windows 16-worker pilot.
- Hosted serial smoke: Actions `41767817861`, 24/24 ok, 16 paired comparisons.
  Historical plan counts such as 187 eligible/5 budget-exceeded describe the
  original 21-case plan only; regenerate the checksum-versioned current plan
  rather than presenting those counts as the 29-case plan.
- At inspected preparation head `d378257...`, PR-triggered Actions
  `41796403299` (CI) and `41796403260` (lightweight benchmark smoke) completed
  successfully. Recheck the current commit rather than carrying this status
  forward to later changes.
- Experiment010 matched one-worker BIC reference: 48 real rows, one n64/d1
  setting, two repeats; frozen reference CSV in Experiment011. Its original
  branch is linked in `PUBLICATION_MAP.md`. Main's different 48-row table mixes
  eight-worker SVD/naive and one-worker CHOLMOD and cannot establish a matched
  ranking. Preserve both datasets with their provenance.
- Float64 selected-S/score agreement is parity, not independent forward-accuracy
  certification. High-d/high-S validity still requires appropriate independent
  numerical review. Invalid, partial, skipped or undefined cells cannot win.
- mu=data is the observed difference mean and the CV formula is conditional
  plug-in, not fully refitted leave-one-out CV. MLE absolute scores may have a
  lambda-independent normalization offset. CHOLMOD+banded diagnostics is a
  hybrid and must include both costs. Attributed serial cold time is not a
  fresh OS-process start for every repeat.

## Continuation checklist and ownership

1. Fetch/inspect current PR heads and any newly pushed Windows result branches.
   Read this handoff first; never infer Windows completion from a hosted smoke.
2. Help the author execute the worktree command above. Verify raw coverage,
   method/repeat wall times, numerical QA, environment and source hashes; record
   the actual result branch/commit in `SPRINGER_READINESS.md`.
3. Continue the approved small serial CV/GCV cases, including the d=4 n256
   pilot, on an idle machine with one BLAS thread. Archive each independent
   block before continuing. Then inspect opted-in confirm cases; no blanket
   factorial launch. Parallel throughput is optional, separate evidence.
4. Engineering owns controller/QA changes; Windows measurement owns new result
   directories; analysis owns derived tables/figures; independent QA reviews
   admissibility and claims. `SPRINGER_AGENT_BRIEF.md` has the full scopes.
   These are handoff roles, not a claim that persistent agents are running.
5. Aggregate only comparable serial data with existing `analyze.py`; naive
   speedups require an actually measured valid naive pairing (not available in
   every selected case). Uncertainty uses independent blocks, not grid points.
6. Rewrite/compile the Springer manuscript after data validation. Keep CSDA B's
   novelty and NGSIM forecasting claims separate; retain figures/source/data in
   Git and update handoffs. Journal declarations/coauthor approval remain open.
7. Commit/push completed work. Preserve all old results and concurrent branches.
   The author authorized repository integration on November 4, 2026. Future
   unrelated merges still require authorization.

## Verification of this documentation update

- `PYTHONPATH=src python -m unittest discover -s paper/benchmarks/experiment011/tests -v`:
  **22 tests passed** on the inspected source, including design, size admission,
  numerical-status auditing, naive pairing, block independence, and parallel
  coverage/resource rules.
- The exact pending 16-series/16-worker CLI invocation above was accepted with
  `--dry-run`; metadata confirmed the three methods, two repeats, one BLAS
  thread per worker, separate parallel archive, and `status=not_measured`.
- `git diff --check` passed. Experiment cases, numerical source, and previous
  raw measurement archives are unchanged by this handoff update.
- PowerShell itself and the Windows benchmark were not executed in this Linux
  session. These checks validate the CLI contract, not new runtime evidence.

Suggested next-session instruction: "Read `paper/SESSION_HANDOFF.md` on
`paper/springer-implementation-experiment011`, inspect new result branches,
and continue the approved Experiment011 Windows pilot. Preserve the four-paper
split and the 29-case scope."
