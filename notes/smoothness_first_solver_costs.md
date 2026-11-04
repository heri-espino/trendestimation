# Smoothness-first computing: source-of-truth handoff

## Question

Can a user specify only normalized smoothness S in [0,1] while
\`trendestimation\` continues to compute the published PLS estimator efficiently?
What is the full cost of converting S to the internal lambda parameter, and
when is spectral preprocessing preferable to banded Cholesky?

This is a **paper synthesis / API extension, not experiment003**.
No new statistical selection or timing measurement was made.

## Mathematical answer

For n>d, positive eigenvalues delta_j of D_d.T D_d and r=n-d:

S(lambda) = r^{-1} sum_j lambda*delta_j/(1+lambda*delta_j).

It is strictly increasing for lambda>0; S(0)=0, S(infinity)=1.
The n,d-specific inverse maps S to lambda; it depends on neither observed y
nor fixed mu. The user-facing new \`fit_smoothness\` simply calls the
existing validated inversion and fitting routines. Existing lambda-based
APIs remain supported. Underlying estimators and criteria are unchanged.

## Complexity and caveats

- Dense SVD/eigh setup O(n^3), memory O(n^2); each full reconstructed
  trend O(n^2) after preparation; spectral EDF/GCV/AICc/BIC and
  conditional-likelihood scores O(n) per candidate after projection.
- Banded Cholesky refactors for each distinct lambda in O(n d^2)
  with O(n d) storage; a known-lambda trend fit can be substantially
  cheaper than full SVD preprocessing.
- Classical CV leverages cost O(n^2) with a dense spectral basis;
  a Cholesky **trace/leverage** benchmark is not comparable to a
  factorization-plus-one-trend benchmark.
- Inverting one smoothness target costs O(k n) after preparing
  the spectrum, k being root iterations; mapping M targets once
  costs O(M k n). Mapping is **not** free, especially when there
  is only one score or when the spectrum must be constructed.
- If P criteria share M equal S targets, naive independent inversions
  cost PM inversions while cached mapping costs only M. Do not
  confuse this advantage with a claim that S is inherently faster than
  lambda, and never compare a uniform-S and a log-lambda grid as
  if they contained the same candidate penalties.
- Extreme endpoints must be treated analytically. S near 1 can
  challenge float64 conditioning, particularly at high d.
- Weinert (2007, DOI:10.1016/j.csda.2006.11.038) already studied
  efficient structured Whittaker-Henderson smoothing; the novelty
  here is the integrated software, normalization and measured
  workload-by-workload comparison, not invention of banded
  matrix algorithms or PLS.

## Evidence actually archived (do not rerun)

- \`paper/computational-statistics-submission/research/final_vm/solver/analysis/paired_comparisons.csv\`
  records independent-seed paired SVD/eigh/banded-Cholesky measurements,
  including confidence intervals and Holm-adjusted comparisons.
- For n=32,d=2,mu=0: total-time SVD/BChol = **1.554** with M=1
  but **0.419** with M=64. These favour different methods and
  are host/workload specific. n=96,d=2,mu=0,M=16 gives **2.093**.
- \`paper/benchmarks/windows_full_s_analysis/selected_s.csv\` and
  \`paired_grid_costs.csv\` document matched native-S and pretranslated
  S-to-lambda strategies. A saved n=48,d=2,mu=0 five-criterion
  comparison totals **11.234ms** naive native S versus
  **3.980ms** once-mapped S-to-lambda, with mapping charged once;
  descriptive 2.823x advantage at those precise conditions.
- Solver inversion benchmarks in
  \`paper/computational-statistics-submission/research/final_vm/inversion/\`
  compare Brent, Newton, secant and bisection in float64.
- \`notes/experiment001_solver_selection_figures.md\`,
  \`notes/experiment002_full_s_factorial.md\`,
  \`notes/criterion_coordinate_factorial.md\` contain experimental
  design and historical distinctions and must be read before
  drawing additional conclusions.

## Feature changes

- \`src/trendestimation/core.py\` adds
  \`TrendSmoother.fit_smoothness(y, *, smoothness, mu, method, tol, maxiter)\`
  and top-level \`fit_smoothness(y, *, smoothness, order, mu, ...)\`.
- \`src/trendestimation/__init__.py\` exports the additive API.
- \`tests/test_fit_smoothness_api.py\` checks exact parity with the
  prior estimator for several n/d/mu choices and endpoints.
- \`paper/computational-statistics-submission/sncs_computational_tradeoffs.tex\`
  derives algorithmic complexity, mapping overhead and observed
  solver crossover. Included in \`sncs_main.tex\`.
- The branch-specific \`sncs-smoothness-first.yml\` action compiles
  the paper from **saved figures**, verifies tests and commits the
  expanded PDF on the feature branch. No numerical benchmark
  or search runs in this workflow.

## Next steps / open questions

- Review the LaTeX PDF for clipped lines, table widths, citations
  and precise limits; retain old figures and source experiments.
- Discuss whether the library should later expose a more
  comprehensive \`select_smoothness\` workflow that caches the
  selected lambda internally without a second inversion.
- Measure only if a **new**, explicitly documented
  experiment is approved; name it sequentially, and archive
  all raw results, logs, analysis, figures and source revision.
- Never merge this or another branch without user authorization.

## Windows PowerShell (source branch after PR review)

\`\`\`powershell
git fetch origin
git switch feature/smoothness-first-computation-paper
git pull --ff-only origin feature/smoothness-first-computation-paper
python -m pip install -e ".[dev,plot]"
python -m pytest -q tests/test_fit_smoothness_api.py
powershell -ExecutionPolicy Bypass -File .\paper\computational-statistics-submission\build_sncs.ps1

git add .
git commit -m "paper: archive smoothness-first complexity manuscript"
git push
\`\`\`
