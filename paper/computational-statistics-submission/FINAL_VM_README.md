# Final author-VM research run: solver inference and smoothness inversion

**Run once on the Windows 11 VM.** This protocol adds exactly two
previously missing research components to the standalone Springer
Computational Statistics manuscript. All generated artifacts are
saved **inside this GitHub repository**, not in ignored `build/`,
`paper/benchmarks/results/`, a temporary VM directory or chat logs.

## Windows 11 PowerShell, from the repository root

```powershell
git fetch origin
git switch --track origin/research/final-vm-inversion-solver-inference-paper

conda activate trendestimation
python -m pip install -e ".[dev,plot]"
python -m pytest -q tests/test_final_vm_study.py

# ONE measured run; automatically compiles the Springer manuscript:
python paper/computational-statistics-submission/run_final_vm_study.py --seeds 20 --repeats 5 --root-repeats 35 --threads 1

# Save ALL the measured evidence, source and paper in GitHub:
git add .
git commit -m "research: archive paired solver uncertainty and S inversion benchmark with final Springer PDF"
git push
```

The one-run script **resumes completed stages automatically** if a
network outage or TeX failure interrupts it. Rerunning it unchanged
does **not** retime already-complete steps; `--rerun` explicitly
overwrites measurements only when a new experimental run is intended.

### Requirements

The above assumes that Python is already in the active
`trendestimation` Conda environment, that `latexmk` and a
working MiKTeX/TeX distribution are available on `PATH`, and
that repository `main` was up to date when the feature branch was
created. If TeX is not available, run with `--skip-pdf` to preserve
all numerical evidence, then compile `main.tex` separately when
TeX becomes available.

The script **does not rerun** the previous exhaustive 80,640-case
Windows smoothness-coordinate study; it reuses its committed
reference CSVs and vector figures.

## 1. Paired full-trend solver uncertainty

Uses the existing `benchmarks/formal_solver_study.py`
and `benchmarks/analyze_formal_solver_study.py`.
The three actual numerical backends are:

- full SVD of the difference operator
- symmetric eigendecomposition of the penalty matrix
- actual *banded Cholesky* (not the older general banded solver).

The default full **quick workload design** has 21 matched
workloads, 20 distinct synthetic data seeds per workload
and five randomized timing blocks per seed. The primary
metric is **setup + all M fitted curves**, not one scalar
criterion evaluation or ML forecast. Every method is
validated numerically on the same data and penalties
before its timed trials. Test statistics operate on
**one median time per seed per workload**; repetitions
and penalty candidates are not treated as independent.

The three solver-pair comparisons for each workload
produce seed-bootstrap 95% *pointwise* confidence
intervals and Holm-adjusted familywise p-values from
paired two-sided sign-flip tests. The sign-flip test
assumes exchangeability/symmetry of paired log-ratios;
its significance is descriptive of these measured
workloads and the same host/session, not evidence
for hardware-independent speed superiority.

Raw files:

- `research/final_vm/solver/raw_measurements.csv`
- `research/final_vm/solver/numerical_accuracy.csv`
- `research/final_vm/solver/study_metadata.json`
- `research/final_vm/solver/analysis/timing_summary.csv`
- `research/final_vm/solver/analysis/paired_comparisons.csv`
- `research/final_vm/solver/analysis/analysis_manifest.json`
- `research/final_vm/solver/analysis/results.md`
- `research/final_vm/solver/analysis/paper_solver_timings.tex`
- `research/final_vm/solver/analysis/paper_solver_speedups.tex`
- numerical figures in `research/final_vm/solver/analysis/`.

## 2. Float64 inversion of normalized smoothness

The second experiment runs `benchmarks/inversion_study.py`
with precomputed SVDs and compares:

- Brent `brentq`
- bracket-safeguarded Newton `newton`
- bracket-safeguarded secant `secant`
- bisection `bisect`.

Default sizes `n=30,60,120`, orders `d=0,1,2,3`,
11 targets from `1e-14` to `1-1e-14`,
and 35 **randomized paired timing blocks per target**.
The **analytic d=0** cases are recorded but excluded
from root-solver ranking. One initialized
`TrendSmoother(n,d)` is reused for all method calls.
Each root is checked in the numerically stable smaller
smoothness tail to avoid near-one cancellation; success,
convergence failure, elapsed microseconds, iteration count,
function and derivative evaluations, and actual achieved
relative tail accuracy are stored.

This study reports empirical timing distributions and
numerical failures. It **does not** treat 35 technical
repetitions on one CPU as 35 independent experimental
replicates or attach unjustified significance tests.

Raw files:

- `research/final_vm/inversion/raw_inversions.csv`
- `research/final_vm/inversion/summary.csv`
- `research/final_vm/inversion/environment.json`.

## 3. Final paper and immutable evidence

The script writes:

- `final_solver_inference_table.tex`
- `final_inversion_table.tex`
- `final_computation_environment.tex`
- `figures/final_solver_inference.pdf`, `.svg`, `.png`
- `figures/final_inversion_speed.pdf`, `.svg`, `.png`
- the five previous Windows computational figures, copied into
  the submission for fully standalone LaTeX compilation
- `research/final_vm/run_commands.log`
- `research/final_vm/run_manifest.json`, with hashes and settings
- the regenerated `main.pdf`.

The paper integrates these in `computational_synthesis.tex`,
alongside the existing empirical CO2/FEDFUNDS 4x6 dashboards,
MLE, zero/data-derived mu comparisons, CV/GCV/AICc/BIC and the
previous scalar/fit benchmarks. The section includes no invented
pre-run results. Numerical rankings must cite the machine,
problem size, root accuracy and complete criterion workload.

### Very important

The VM's Git branch is the exchange channel between the
researcher and agents. After `git push`, the measured CSVs,
figures, LaTeX tables, statistical analysis, run log, and
compiled PDF all persist for review in the open PR. The agent
must review the measured outcome before merging into main;
different machines or sessions must not be pooled without
an explicit multi-host analysis.
