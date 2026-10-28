# Experiment003 — large-series smoothness-grid preparation and reuse

Status: **author-Windows execution only; full/large measurements pending**.
Automatic CI benchmarking has been removed at the owner's request.
Do not replace existing Experiment001/002 numerical archives with smoke output.

## Scientific questions

1. Does caching the \`n,d,S\` -> \`lambda\` grid save substantial time over
   repeated inversion once a prepared spectrum is available?
2. Does eigenvalues-only **banded** spectral preparation make it economical
   to expose S while solving trends with banded Cholesky, compared with
   requiring a full SVD?
3. How does the cost of one fit differ from a complete grid and from
   repeatedly fitting R independent series?
4. At which n/d/M/R configurations are spectral full-curve fits
   competitive with uncached or factor-cached banded Cholesky?
5. How does this differ from GCV criterion evaluation? (Never equate
   a full-trend timing with an O(n)-per-candidate spectral score.)

## Method and a critical control

Use a **matched grid** of M normalized smoothness targets in [0.15, 0.80].
Compute the SAME candidate penalties from banded-only eigenvalues and
full SVD, validate numerical parity, and feed identical penalties to
every fit/score path. Fixed mu in {0,.15}, and the same seeded observations
are used for every comparison.

The finite grid avoids floating-point near-singular tail behavior.
S=0 and S=1 are exact analytic boundaries and are already covered by
the library and previous experiments. This benchmark is about *cost and
reuse*, not full-domain numerical validity or improved forecast error.

The methods differ precisely in their accounting:

- **known-lambda banded Cholesky, cold:** no S mapping or eigenvalues;
  banded matrix factorized anew for every lambda and each series.
- **known-lambda cached Cholesky:** factors all lambda matrices once,
  then reuses across R series. Stores M factor matrices.
- **S-to-lambda cached Cholesky:** prepares *banded eigenvalues only*,
  constructs the target grid once, prepares factors, reuses them.
- **known-lambda full SVD:** pays for one full spectral decomposition,
  projects each data series once, reconstructs the M trends.
- **S-to-lambda full SVD:** adds mapping cost to the SVD path; returns
  same curves as known lambda.
- **GCV native-S:** SVD once, but invert the same M targets for every
  new series, computing matched GCV scores.
- **GCV cached-S:** SVD once, invert M targets once, reuse candidates.
- **GCV provided lambda:** same spectral scores but omits inversion
  from runtime accounting by design.

For independent series or statistical selectors sharing n,d,M,S:
S-grid mapping does not depend on y or fixed numeric mu. In contrast,
banded factors depend on each individual lambda; they can be cached for
a fixed grid, but one factor does not work for *all* penalties.

## Complexity / fair interpretation

Let n be series length, d fixed order, M grid size, k inverse iterations,
R number of independent series:

- Dense full-SVD preparation: O(n^3) arithmetic and O(n^2) memory.
- Banded Cholesky refactorization for new lambda: O(nd^2); solve O(nd).
- Eigenvalues-only symmetric banded Q: measured separately, not
  assigned an unjustified universal complexity (depends on algorithm).
- Cached inverse S-grid after obtaining positive spectrum: O(M k n).
- Exact spectral GCV (RSS+EDF after projecting each series): O(M n)
  per series, plus O(n^2) projection per series.
- Full spectral trends: O(M n^2) per series.
- Cached banded Cholesky factor-grid storage: O(M n d).

**The known-lambda Cholesky baseline does not pay for the inversion**.
Its separation is intentional. No experiment result proves that S is
intrinsically cheaper than lambda. End-to-end strategy selection is
conditional on workload, reuse, device, and whether input is specified in
S or lambda.

## Presets

| Preset | Main n | Purpose | Independently seeded data × technical blocks |
| --- | --- | --- | --- |
| smoke | 48 | tests correctness only | 1 × 1 |
| quick | 128, 256 | local pilot; M=1/11/21 | 2 × 3 |
| full | 256, 512, 1024 | matched M=21 R=4 scaling, M=1/81, R=1/12 and d=1/2/3 | 3 × 4 |
| large | 1024, 1536, 2048 | compare large n holding M=21,R=4; optional M=81 | 2 × 3 |

For each case, both fixed means mu=0 and mu=.15 use the same observations.
An independent seed—not each machine timing repetition—is the proper
unit for inferential comparisons. No significance claims are made from
this small experimental design. The larger runs can be expensive because
real full SVD is performed; begin with quick/full and record walltime.

These are **new** experiments, not rerenders of previous archived runs. **No GitHub Actions verification is required**: run the smoke tests and benchmarks directly in your local Conda environment.
Do not claim their timings exist before running them on the intended VM.

## Windows PowerShell: validation and real experiments

Work on branch \`experiment003/large-series-s-grid-caching\` and use:

\`\`\`powershell
git fetch origin
git worktree add -b experiment003/windows-local ..\trendestimation-exp003 origin/experiment003/large-series-s-grid-caching
Set-Location ..\trendestimation-exp003

conda activate trendestimation
python -m pip install -e ".[dev,plot]"
python -m pip install -r paper/requirements.txt

# Only verifies correctness; tiny 48-point study
python -m pytest -q tests/test_experiment003_large_s_grid.py

# Small local pilot; already generates plots and automatically publishes results:
python paper/benchmarks/experiment003_large_s_grid.py --preset quick --publish

# The larger author-workstation experimental campaigns:
python paper/benchmarks/experiment003_large_s_grid.py --preset full --publish
python paper/benchmarks/experiment003_large_s_grid.py --preset large --publish
\`\`\`

Both full and large are **independent runs** with separate timestamped,
Git-tracked directories at
\`paper/benchmarks/experiment003_large_s_grid/runs/\`.
The \`--publish\` flag commits and pushes all generated raw, summary,
seed-level and numerical-parity CSVs, machine/BLAS metadata, source
revision, an AwesomeFigures PDF/SVG/PNG gallery and text analysis. It
does not stage unrelated files and will not force-push. Partial failures
retain partial CSVs and a FAILURE.txt, which are also pushed if possible.

To regenerate figures later without rerunning the numerical experiment:

\`\`\`powershell
python paper/benchmarks/experiment003_analyze.py --run-dir paper/benchmarks/experiment003_large_s_grid/runs/<actual-run-folder>
git add .
git commit -m "experiment003: update AwesomeFigures report from archived measurements"
git push
\`\`\`

## Required next review after Windows runs

- Verify numerical parity at **all sampled** n,d,mu before interpreting speed.
- Measure variability across **independent data seeds** rather than inflating
  degrees of freedom with repeated timing trials.
- Inspect total end-to-end costs (setup+conversion+factors+evaluation);
  also report first/subsequent series and peak estimated cache size.
- Compare matched n,d,M,R scenarios only; do not claim a crossover when
  more than one workload dimension changes.
- Consider a future PreparedSmoothnessGrid public class only after these
  exploratory results and separate correctness/performance review.
- Do not merge new findings into the Springer article as numerical claims
  until their raw sources and host metadata are in the repo.

## Reproducibility handoff

Source:
- \`paper/benchmarks/experiment003_large_s_grid.py\`
- \`paper/benchmarks/experiment003_analyze.py\`
- \`tests/test_experiment003_large_s_grid.py\`

Immutable older results for context (never rewritten):
- \`paper/benchmarks/results/full_s_search_modes/\`
- \`paper/computational-statistics-submission/research/final_vm/\`
- \`notes/experiment002_full_s_factorial.md\`

Git repository is the only durable handoff channel for agent/VM runs.
