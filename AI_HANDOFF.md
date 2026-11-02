# AI_HANDOFF — latest

## Experiment005: sparse/iterative PLS, current branch

Branch: feature/experiment005-structured-solvers; PR #94.

Existing SVD/eigh/banded-Cholesky preserved; added banded_lu, sparse_lu
(SuperLU), optional sparse_cholesky (real CHOLMOD), and matrix-free PCG
with fft/dst/jacobi/none preconditioners. The new methods are fit-only.
Matrix A and RHS are built without a high-degree polynomial subtraction.

Review src/trendestimation/_structured_solvers.py, the integration in
src/trendestimation/solvers.py, tests/test_experiment005_structured_solvers.py
and paper/benchmarks/experiment005/run.py. Numerical correctness/parity,
normal-equation residuals, finite lambda, zero & infinity limits,
fixed/plug-in mu, convergence failures and factor-cache reuse are tested.

Do NOT claim fastest sparse Cholesky without separately installing and
timing optional SuiteSparse CHOLMOD. FFT/DST are approximate surrogate
preconditioners; convergence depends on conditioning and boundaries.

The next research step is to run the larger experiment005 preset on the
author's Windows workstation and publish the evidence to the repository,
then compare fit-only performance and full criterion selection separately.

Previous experimental timing data and the two CSDA manuscripts remain
unchanged. Maintain their provenance and do not alter recorded values.


## CSDA computational four-workload manuscript branch — 2026-11-02

Branch: paper/csda-four-workload-20261102; independent of the still-draft
Experiment006 code PR #95 and its self-hosted runner job. Do not merge
this paper PR without the user authorizing it. Existing baseline paper,
its six AwesomeFigures vector figure families, archived 80,640-row
Windows timing results, and prior numerical companion are preserved.

The existing paper/csda-computational-costs/main.tex now includes:
- sections/structured_criteria.tex: exact banded selected inverse,
  conditional CV/GCV/BIC/AICc/ML computations, nonzero-mu RHS,
  nine honest end-to-end complete criterion pipelines.
- sections/experiment006_design.tex: four M×R workload configurations,
  n to 131072, d=1,...,6, fixed mu zero/nonzero, high/low magnitude,
  100/1000/10000/100000 S grids including exact S=1,
  matched direct-S/onetime-pretranslated-lambda policies.
- sections/experiment006_status.tex: historical measured evidence
  explicitly separated from the unrun large factorial and
  hypothesis testing protocol.
- BibTeX adds Erisman/Tinney (1975), selected inverse prior art.

The main.tex abstract reports only confirmed historical d=2/d=3
n=48 grid-reuse times; no new full-factorial results are claimed.
New paper CI: .github/workflows/csda-four-workloads-paper.yml.
GitHub-hosted LaTeX build copies original CAS class and references
pre-existing TeX-native AwesomeFigures assets without rerunning figures.
Outputs: main.pdf, publication hashes, archived GitHub Actions ZIP.

To extend results, retrieve real raw CSV and numerical status from
the Experiment006 results-only branch after a successful runner run.
Keep machine-specific timings and conditional performance conclusions
explicit. Confirm author order, coauthor consent, and citation metadata
before submission. The full factorial is NOT completed.
