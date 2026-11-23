**AICc scorer-domain correction (2026-11-20):** The original small-phase 100-seed immutable result branch has 6,000 `numerical_failed` status rows, all AICc. The numerical scorer legitimately returns `+inf` for inadmissible AICc candidate penalties; the old Experiment013 runner aborted after such a result. The corrected source records finite versus undefined candidates, continues the search, distinguishes `criterion_undefined` and actual numerical errors, and adds `Run-Grid.ps1 -Criteria aicc` to measure only the source-versioned AICc addendum. Never mutate or relabel the historical branch. Audit the new AICc run before integrating result sets, and report implementation-source differences explicitly.

# Experiment013 — independent agent handoff

## Mission and source of truth

The canonical Springer Computational Statistics manuscript is paper/main.tex.
The frozen historical Experiment011 campaign (97 additional seed realizations,
2813 case/seed jobs and archived Windows observations) is never overwritten.
Experiment012 is the earlier focused 100-seed CV/GCV amortization implementation.
Experiment013 provides the new complete 7 n x 3 d x 3 methods x 5 criteria x
4 M design with an extra first-candidate checkpoint. The scientific reason is
to include d=2 and make method/criterion/sample-size coverage explicit.

Before edits read root AGENTS.md, paper/AGENTS.md, paper/SPRINGER_READINESS.md,
paper/SESSION_HANDOFF.md, Experiment006 run.py/selected_inverse.py,
Experiment011 completed campaign handoff and Experiment012 README/run.py,
then this directory's README, run.py, analyze.py, Run-Grid.ps1 and tests.

## Execution constraints

- The numerical source is the existing Experiment006 Evaluator; do not replace
  the naive inverse with solve, or a selected-inverse banded criterion with
  fit-only Cholesky.
- One worker and one BLAS thread; fixed mu=0, low amplitude and R=1.
  All methods receive the identical independent seed and nested direct-lambda
  candidate sequence. Every criterion is complete and uses its own valid score.
- Runtime/initialization distinction: one method setup, first candidate score,
  then cumulative cold cost through M=10,100,1000,10000; a method's
  invalid/infeasible cells are recorded as status, never zero seconds.
- Large-n naive and SVD cases are subject to explicit resource gates.
  The coverage manifest is complete even when numerical data are sparse.
  No runtime prediction masquerades as a stopwatch measurement.
- The PowerShell launcher on Windows 11 must be started from a clean,
  synchronized main worktree, and must push unique results branches via
  a separate Git worktree after measurement; original raw outputs persist.
  An interrupted run may resume only at identical source, settings and
  environment. Do not modify others' branches.
- Make numerical QA and source-hash validation precede all speedup inference.
  Keep statuses, missingness, seed clusters, paired agreement and hardware
  provenance. Bootstrap independent seeds, not millions of repeated rows.
- Do not relabel Experiment011's reported 97-seed intervals as 100-seed ones
  or pool differently defined S and lambda candidate schedules.
- After real results: render AwesomeFigures, update abstract/results/figures,
  compile the official Springer PDF, inspect all pages, publish immutable
  figures and PDF, and update readiness/handoff. No journal submission without
  author approval.

No empirical new measurements have been executed by source-only PR creation.
