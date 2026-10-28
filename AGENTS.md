# Repository handoff for independent agents

## Read before working

1. Read README.md and notes/README.md, especially
   notes/smoothness_parameterization.md,
   notes/experiment001_solver_selection_figures.md,
   notes/experiment002_full_s_factorial.md and
   notes/criterion_coordinate_factorial.md.
2. Read the public Python API in src/trendestimation/core.py,
   criteria.py and solvers.py, plus the relevant tests.
3. Read paper/computational-statistics-submission/SNCS_README.md
   and the included sncs_*.tex sections before editing the journal paper.
4. For smoothness-first cost work, read
   notes/smoothness_first_solver_costs.md.

## Branch and experiment discipline

- The repository is the source of truth; never rely on transient VM files.
- Work in a separate branch and open a PR. Do not force-push,
  overwrite another agent's changes or merge without authorization.
- Preserve raw experiment inputs, configurations, code, numerical
  measurements, logs, figures, analyses and manuscript PDFs.
- Name genuinely new experiments sequentially
  experiment003, experiment004, etc.; include motivation, method,
  reproduction instructions, findings and next actions.
- Source-only synthesis or rendering from archived numbers is
  not a new experiment. Never rerun costly benchmarks just to restyle figures.
- Keep secrets, licenses and unnecessary caches out of commits.
  Use LFS or documented external storage for files too large for GitHub.

## Mathematical/scientific invariants

- Guerrero's original index is n-normalized with upper limit (n-d)/n.
  The package's *order-normalized* S is (n-tr(H))/(n-d), in [0,1].
- The monotone map S<->lambda depends on n and d, not the data y
  or a fixed mu. For nonzero fixed mu, the fit is affine in y.
- Searching matched grids in S and lambda must yield matched
  penalties/scores; independent log-lambda grids are not comparable
  as identical finite optimization problems.
- Cholesky trend-only speed does not establish Cholesky CV/EDF speed.
  Distinguish spectral, general banded and actual banded Cholesky.
  Report complexity separately from machine-specific measurements.
- The new fit_smoothness convenience *hides* lambda; it does not
  remove the internal penalty, change the estimator, or eliminate
  the cost of scalar inversion.
- MLE is conditional/profiled under its stated assumptions;
  mu="data" is not joint maximum likelihood.

## Commands (Windows PowerShell, repository root)

\`\`\`powershell
python -m pip install -e ".[dev,plot]"
python -m pytest -q tests/test_fit_smoothness_api.py
powershell -ExecutionPolicy Bypass -File .\paper\computational-statistics-submission\build_sncs.ps1

git add .
git commit -m "research: document verified results"
git push
\`\`\`
