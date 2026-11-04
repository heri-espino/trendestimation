# Experiment011 — measured complete-criterion runtime frontiers

**Status: prepared experimental protocol, not a completed numerical study.**


### Full factorial is the target; the 21 cases are only the pilot

The user's complete factorial specification is NOT the 21-case
`cases.json` subset. It is the originally audited Experiment008 grid,
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

The factorial therefore contains
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
and all expected factor levels. The plan uses three series and
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

### Explicit stages

| Stage | Cases | Purpose | Execution |
|---|---:|---|---|
| Smoke | 2 | Wiring/numerical QA, n64 d1/d3, M100 | GitHub Actions or Windows, single block and repeat |
| Pilot | 13 | GCV-vs-CV crossover probes, n64/128; AICc and ML controls at n256, conditional mu=data controls and optional CHOLMOD | Windows VM, three blocks × two repeats per block |
| Confirm | 6 | Selected n/d/M scaling up to M10000 and n512; **only after pilot** | Requires explicit `--allow-confirm` and new resource review |

The parameter grid is the same `S={j/M: j=1,...,M}` for every backend including exact S=1. In the inherited runner, the single-candidate workload uses S=.5. All four configurations are evaluated for every case: one S / one series, full S-grid / one series, one S / three series, full S-grid / three series (two series in smoke). Both direct-S and once-mapped-lambda policies are evaluated. No grid outcome has been measured merely by writing `cases.json`.

**Important:** `mu='data'` means the mean of the observed d-th differences for the *training* series. For CV/GCV/AICc/BIC the resulting score is conditional plug-in, not exact leave-one-out mean refitting. Optional CHOLMOD is recorded by its real import status; SciPy SuperLU is not a fallback under its name.

## Windows PowerShell (the university VM)

Do this after CI passes and when the workstation is idle. From the current repository checkout:

```powershell
git fetch origin
git worktree add --detach ..\trendestimation-springer origin/paper/springer-implementation-experiment011
Set-Location ..\trendestimation-springer
git switch -c results/experiment011-PCAG103A08-001
conda activate trendestimation
python -m pip install -e .
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

## Outputs and mathematical validity

- `cases.json`: immutable plan with 21 declared cases. `plans/experiment011_plan.json` is an **eligibility plan**, not real timings.
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
