# Experiment011 — measured complete-criterion runtime frontiers

**Experiment011 completion update (2026-11-09):** The author reports **2813/2813 case-seed jobs recorded, remaining 0**, on the Windows VM. Read the [completed-campaign handoff](handoff/COMPLETION_HANDOFF.md) and [Springer analysis prompt](handoff/SPRINGER_ANALYSIS_AGENT_PROMPT.md) before following older pending-run instructions. Final raw data acquisition, verified backup and numerical/timing analysis remain pending; GitHub still has only the inspected 2338-job checkpoint. Preserve local raw files and use the documented no-automatic-publication backup procedure. These observations include 24/1/12-worker phases and must not be pooled as isolated-latency measurements.

**Session continuation (2026-11-04): read [SESSION_HANDOFF.md](../../SESSION_HANDOFF.md) first.** It records the four-paper split, approved 29-case scope, current PRs, Windows missing-file diagnosis, exact results-worktree commands, and pending measurements. The next author action is the small 16-series/16-worker GCV pilot; the Windows campaign is not yet measured.

## Current author decision — focused Experiment011 (November 4, 2026)

Keep the original 21-case Experiment011 protocol and add only targeted
CV/GCV comparisons at **d=4** for **n=256, 1024, 2048, 4096**:
two pilot cases at n=256 and six confirm-stage cases at larger n,
**29 cases in total**. The n1024 confirm cells explicitly permit
a 750-million-work-unit cap so SVD can be compared with banded Cholesky
on the full M=100, R=3 grid; n2048/4096 use the feasible banded
backend only. All larger cases require the existing opt-in
`--allow-confirm`. No older run, criterion, or historical result
is overwritten.

An **optional throughput-only** `campaign.py parallel-series`
mode runs independent small series (n<=256, M<=1000) in spawned
processes, up to 32 workers, each with one BLAS thread. It writes
`runs_parallel/` with per-series checkpoints and real wall times.
It deliberately **does not replace** the serial shared-cache
single/multiple-series latency benchmark. The author's 32 logical
processors are a capacity ceiling, not proof that 32 workers
will run faster than 8 or 16. The old 252,000-cell factorial is
retained only as an archival index, **not** a new study mandate.


**Status:** the 29-case staged design is implemented; small hosted serial
and process-pool smoke checks have passed. The real Windows 29-case
measurement campaign has **not** been executed.

## Practical PowerShell commands for the approved additions

Run from the repository root on the university Windows computer with
the existing `trendestimation` Conda environment:

```powershell
# See every existing and newly added case; no benchmarks are started.
python paper/benchmarks/experiment011/campaign.py list
python paper/benchmarks/experiment011/campaign.py plan

# One actual small d=4 CV pilot.
python paper/benchmarks/experiment011/campaign.py run --case pilot_cv_n256_d4_m100 --run-tag PCAG103A08_002 --block 0

# Inspect larger confirmation cases without executing numerical work.
python paper/benchmarks/experiment011/campaign.py run --case confirm_cv_n1024_d4_m100 --run-tag PCAG103A08_002 --block 0 --allow-confirm --dry-run
python paper/benchmarks/experiment011/campaign.py run --case confirm_cv_n4096_d4_m100 --run-tag PCAG103A08_002 --block 0 --allow-confirm --dry-run
```

For `n=1024,d=4,M=100`, the confirm-stage work cap is
750 million nominal units, explicitly permitting SVD and banded
Cholesky under the resource preflight. For `n=2048` and
`n=4096`, only banded Cholesky is predeclared.
Their timings are useful for scaling, but are **not**
an independent SVD/Cholesky numerical-parity comparison.
Those larger runs remain optional and should be reviewed after
the smaller pilot.

### Optional: process one independent series per worker

```powershell
# Example: 16 independent short series on up to 16 processes.
python paper/benchmarks/experiment011/campaign.py parallel-series --case smoke_gcv_n64_d1_m100 --run-tag PCAG103A08_parallel001 --block 0 --series-count 16 --series-workers 16

# Explore 32 workers only if the machine remains idle and resources permit.
python paper/benchmarks/experiment011/campaign.py parallel-series --case pilot_cv_n128_d3_m100 --run-tag PCAG103A08_parallel032 --block 0 --series-count 32 --series-workers 32
```

This is genuinely per-independent-series multiprocessing using
`spawn` (Windows compatible), at most 32 processes, each with
one BLAS thread. It is **not** a change to the serial four-workload
timing experiment. Every process privately constructs the
factorization and smoothness mapping, so the wall time reflects
parallel throughput **without sharing** spectral/Cholesky caches
across series. Thus these timings must not be pooled with the
serial common-factor-cache results. The separate
`runs_parallel/<run-tag>/<case>/blockNNN/` archive records
individual per-series rows, completion status, method/repeat
wall time, throughput, and numerical parity. Only
`n<=256` and `M<=1000` are allowed. Start with
8 or 16 workers when possible: 32 logical processors do
not guarantee that 32 concurrent processes are optimal.

Persist the new `runs_parallel/` output and `runs/` output
on the dedicated results branch via `git add .`,
`git commit` and `git push`. Do not overwrite prior
run tags or force-push other agents' results.




### Focused 29-case Experiment011 is the active study; the full factorial is historical context

The previously requested comprehensive-factorial indexing specification is
preserved from Experiment008 as historical background. It is **not** the
currently authorized run schedule. The existing full factorial has axes
now exposed through `full_plan.py` in this experiment. Its axes are:

- n={64,128,256,512,1024,16384,131072};
- d={1,2,3,4,5,6};
- mean policy={fixed 0, observed-difference plug-in data, fixed 0.15};
- amplitude={low,high};
- criterion={CV,GCV,BIC,AICc,Gaussian MLE};
- 10 complete-criterion algorithm/hybrid names (including naive inverse);
- two coordinate implementations={direct_s,mapped_lambda};
- four workloads={one S/one series, full S-grid/one series,
  one S/R series, full S-grid/R series};
- candidate grids M={100,1000,10000,100000}, including exact S=1
  for full grids; a one-S workload at S=0.5 is NOT duplicated four times.

That archived factorial therefore contains
7*6*3*2*5*10*2*(2+2*4) = **252,000 unique planned
method-workload-coordinate cells**. Those are the index of a long-form
timing tensor, not 252,000 observed seconds. The full design records
resource ineligibility, numerical failures, undefined criteria, and
missing observations explicitly. Dense n=131072 inverses are physically
infeasible for the 2-GiB benchmark budget and must not be run.
A successful measured cell also has an independent `block` and
`repeat` index. No RMSE is part of this experiment.

From the repository root:

```powershell
python paper/benchmarks/experiment011/full_plan.py
```

This command only produces
`plans/full_factorial_plan.csv.gz` and
`plans/full_factorial_plan.csv.metadata.json`; it does not
execute solver benchmarks. The script delegates to the original
Experiment008 manifest implementation, checking its source SHA
and all expected factor levels. The historical factorial plan uses three series and
six planned repeats per cell (three independent blocks and
two repeats each), with explicit 2-GiB dense-memory and work
budget safeguards. A method/case with a resource skip remains a
tensor cell with no fictitious timing.

**Critical comparison:** In the current Experiment006 runner,
`direct_s` and `mapped_lambda` both evaluate the *same*
candidate S values. The first inverts S on demand, while the
second precomputes S→lambda once per candidate grid.
This is a timing comparison of coordinate-translation
strategies, **not** a test of two different continuous
optimization algorithms or of a separately sampled log-lambda grid.
Any true continuous-optimizer comparison must be designed,
implemented and validated as a separate method factor.

**Prior evidence:** Experiment008 already planned the same 252,000
cells and archived partial real measurements; Experiment009
analyzed theoretical/empirical crossover from those data;
Experiment010 archived the matched n64/d1/BIC pilot.
Reconcile these existing rows by n,d,mu,amplitude,criterion,
M,R,coordinate,source SHA, machine and concurrency before
spending time on a repeated study. Do not import a time
measurement from a different source revision into a supposedly
paired block.



## Question and scientific design

Can a reusable SVD be faster than banded Cholesky with selected inversion for repeated full S-grids, and how does the crossover change when the criterion is ordinary conditional **CV** rather than scalar **GCV** (or AICc/ML)? Which techniques remain admissible as n, d, candidate count M and independent series count R grow?

The primary outputs are actual complete-criterion latency (seconds or milliseconds depending on magnitude), cost components (setup, grid inversion, scoring), numerical validity and resource skips. No forecast RMSE is estimated here. This experiment does not claim a new smoothing penalty.

We reuse `paper/benchmarks/experiment006/run.py` **as is**: it already implements and times complete criteria with naive inversion, spectral SVD, banded Cholesky plus exact selected inverse and explicitly named hybrids. The new Experiment011 controller adds a small predeclared design, work/memory caps, one-case runs, rotating method order across blocks, immutable metadata and independent paired QA. It does not merge or duplicate the unmerged Experiment010 orchestration PR stack.

### Focused stages (currently 29 cases)

| Stage | Cases | Purpose | Execution |
|---|---:|---|---|
| Smoke | 2 | Wiring/numerical QA, n64 d1/d3, M100 | GitHub Actions or Windows, single block and repeat |
| Pilot | 15 | GCV-vs-CV crossover probes, n64/128; AICc and ML controls at n256, conditional mu=data controls and optional CHOLMOD | Windows VM, three blocks × two repeats per block |
| Confirm | 12 | Selected scaling up to M10000; d=4 CV/GCV at n1024/2048/4096; **only after pilot** | Requires explicit `--allow-confirm` and new resource review |

The parameter grid is the same `S={j/M: j=1,...,M}` for every backend including exact S=1. In the inherited runner, the single-candidate workload uses S=.5. All four configurations are evaluated for every case: one S / one series, full S-grid / one series, one S / three series, full S-grid / three series (two series in smoke). Both direct-S and once-mapped-lambda policies are evaluated. No grid outcome has been measured merely by writing `cases.json`.

**Important:** `mu='data'` means the mean of the observed d-th differences for the *training* series. For CV/GCV/AICc/BIC the resulting score is conditional plug-in, not exact leave-one-out mean refitting. Optional CHOLMOD is recorded by its real import status; SciPy SuperLU is not a fallback under its name.

## Windows PowerShell (the university VM)

Use the complete exit-checked worktree procedure in [SESSION_HANDOFF.md](../../SESSION_HANDOFF.md#exact-next-windows-run-fresh-results-worktree) for the pending parallel pilot. The older serial example below remains useful for serial runs; its worktree/branch names must be new. Use the existing Conda environment and repository `src` on PYTHONPATH, without package installation. Run when the workstation is idle:

```powershell
git fetch origin
git worktree add --detach ..\trendestimation-springer origin/paper/springer-implementation-experiment011
Set-Location ..\trendestimation-springer
git switch -c results/experiment011-PCAG103A08-001
conda activate trendestimation
$env:PYTHONPATH = (Join-Path (Get-Location).Path "src") + [IO.Path]::PathSeparator + $env:PYTHONPATH
python -m unittest discover -s paper/benchmarks/experiment011/tests -v
python paper/benchmarks/experiment011/campaign.py list
python paper/benchmarks/experiment011/campaign.py plan
python paper/benchmarks/experiment011/campaign.py run --case smoke_gcv_n64_d1_m100 --run-tag PCAG103A08_001 --block 0
```

The source runs one complete-criterion case with one BLAS thread. It writes a unique `runs/PCAG103A08_001/<case>/block000/` folder with raw CSV, summary, environment, experiment011 case manifest and numerical QA JSON. For a typical pilot, **manually run blocks 0, 1 and 2 separately**, and check the preceding output before launching the next:

```powershell
python paper/benchmarks/experiment011/campaign.py run --case pilot_gcv_n128_d3_m100 --run-tag PCAG103A08_001 --block 0
python paper/benchmarks/experiment011/campaign.py run --case pilot_gcv_n128_d3_m100 --run-tag PCAG103A08_001 --block 1
python paper/benchmarks/experiment011/campaign.py run --case pilot_gcv_n128_d3_m100 --run-tag PCAG103A08_001 --block 2
```

Repeat for the paired CV case `pilot_cv_n128_d3_m100`, and then the M1000 cases if the pilot is stable. To inspect a planned large case without running:

```powershell
python paper/benchmarks/experiment011/campaign.py run --case confirm_cv_n256_d3_m1000 --run-tag PCAG103A08_001 --block 0 --allow-confirm --dry-run
```

The explicit confirmation flag is required for the real larger run. Do **not** execute the full old Experiment010 50,400-method-slot factorial merely because 32 logical processors exist.

After **each** completed block, preserve the outputs in the results branch:

```powershell
git add .
git commit -m "experiment011: archive matched Windows block and numerical QA"
git push -u origin results/experiment011-PCAG103A08-001
```

Then create a PR against the Springer experiment preparation branch. Do not merge without authorization. Existing result branches must not be overwritten or force-pushed.

### CI smoke

The dedicated `.github/workflows/springer-experiment011-smoke.yml` runs the deterministic case plan, stdlib unit tests, and **one tiny n64/m100/GCV case** on a GitHub runner. This smoke is *software QA*, **not a measured Windows result**. It uploads raw pilot outputs as an artifact and commits them to this dedicated Springer branch (without rewriting main), making them available to other agents; the Windows results are still required to draw hardware conclusions.

### Existing matched reference

The file `reference/experiment010_matched_n64_d1_bic.csv` contains 48 real n64/d1/BIC rows copied verbatim from `results/experiment010-uncapped-PCAG103A-08-20261103T222938857Z-shard0-offset20`. It was measured with **one worker and one BLAS thread**, two repeats, and is **not** a new Experiment011 run. A different 48-row pilot in main's `publication_evidence/` was collected under *mixed worker counts*, so do not pool the two sets.


## Assemble the measured timing tensor and naive-baseline speedups

After the Windows blocks are committed, derive **one long-form table
of actual measured seconds** and matched paired speedups:

```powershell
python paper/benchmarks/experiment011/analyze.py --runs paper/benchmarks/experiment011/runs --run-tag PCAG103A08_001 --output paper/benchmarks/experiment011/analysis/PCAG103A08_001
```

The outputs are `measured_timing_tensor.csv`,
`paired_naive_speedups.csv`, `block_aggregated_times.csv`
and `analysis_summary.json`. The first preserves every actual
successful/failed/undefined or budget-limited row with its full
experiment keys. The second produces **naive_seconds / method_seconds**
only on the same case, block, repeat, coordinate, workload, source
revision and environment when both outcomes are valid and their
selected S/criterion scores agree to the reported float64 tolerance.
At large n the naive method is often ineligible; it has
**no invented baseline speedup**.

The aggregate uses **independent block means**, not 4 workload
rows or 2 coordinate rows as independent replicates. It requires
at least 3 complete independent seed blocks before outputting
a deterministic block-bootstrap 95% interval. If two run tags
repeat the same deterministic seed, they are not counted as
independent blocks. A one-block smoke produces a mean
but **no confidence interval**. Cells remain separated by
host, software/BLAS fingerprint, runner source hash, criterion,
data magnitude, n, d, mu, M, R and coordinate policy; it does
not silently pool Linux and Windows timings.

The adjacent `theory_big_o_work_not_seconds` column contains
theoretical complexity families, **not calibrated predictions**.
Numerical crossover fits/plots must be based on valid measured
cells across multiple n,d,M and compared with theoretical
slopes only after the data exist. There is **no RMSE output**.
The source files, analysis outputs and run-specific README
must all be committed and pushed. The default source path
selection uses only the requested `--run-tag`, preventing
accidental aggregation of previous smoke tags.


## Outputs and mathematical validity

- `cases.json`: 29 declared cases. Current plans use `plans/experiment011_plan_<design-checksum>.json`; the preserved `plans/experiment011_plan.json` belongs to the original 21-case version. All are **eligibility plans**, not real timings.
- `measurements/raw_times.csv`: all actual rows, including failed/ineligible states; `summary.csv` and `paired_speedups.csv` are derived, *conditional* summaries from the inherited runner.
- `measurements/environment.json`: host, source commit, numerical package versions, BLAS pools, seed and conditional-data-mu status.
- `experiment011_case.json`: controller source SHA, rotated method order, block seed, stages, and status.
- `experiment011_qa.json`: independent status and matched selected-S/float64 score audit; MLE may include a lambda-independent score offset. `float64_parity_only_not_precision_certified` is **not an 85-digit forward-error check**.
- Inherited `total_cold_s` uses its established setup attribution, not independent process-spawn cold starts. The common spectral S-to-lambda mapper for n<=512 must be charged and explicitly disclosed for all methods. Avoid calling its warm times a truly separately spawned hot process.
- Statistical uncertainty must be based on **independent blocks**, not within-workload timing subrecords. Three blocks with two repeats are a preliminary dispersion study, not a population-level generalization.
- At high n or high M many dense or computationally expensive methods will produce explicit `infeasible_*` or `budget_exceeded` outcomes; those are scientifically relevant, not missing-data errors to impute away.

## What follows

1. Pass source/CI smoke with archived QA.
2. On one quiet VM, execute selected paired CV and GCV pilots under common n,d,M,R,mu.
3. Review all numerical validity and status counts. Any high-d or large-S claimed accuracy needs independent stronger reference validation.
4. Decide confirm cases based on results and resource limits. Run blocks separately, archiving after each.
5. Generate source-linked Springer tables, bootstrapped **block-level** uncertainty and AwesomeFigures plots only from valid matched data; explicitly name conditioning, memory, mapping and hybrid diagnostics.
6. Update `paper/SPRINGER_READINESS.md`, prepare a paper-only PR for `paper/main.tex`, compile the Springer PDF and obtain coauthor approval.

For edit rules, consult `AGENTS.md` in this folder and `paper/SPRINGER_AGENT_BRIEF.md`. No empirical best-method claim is certified by the preparation step.
