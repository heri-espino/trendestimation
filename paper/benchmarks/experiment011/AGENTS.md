# Experiment011 — controlled Springer complete-criterion runtime study

**Do not edit or launch before reading:** root `README.md`, `AGENTS.md`, `AI_HANDOFF.md`, `paper/PUBLICATION_MAP.md`, `paper/SPRINGER_READINESS.md`, `paper/benchmarks/experiment006/{README.md,run.py,selected_inverse.py}`, `paper/benchmarks/experiment008/README.md`, `paper/benchmarks/experiment009/README.md`, `paper/benchmarks/experiment010/publication_evidence/README.md`, then `cases.json`, `campaign.py`, `verify.py`, the tests and all relevant open PRs.

## Objective

Measure complete in-sample selection costs at identical prescribed smoothness candidates, not fit-only wall time. Explain the interaction of
\(n,d,M,R,\mathcal C,\mu\), setup/amortization, candidate inversion, and cache reuse. The focused question is whether measured **CV** preference boundaries differ from **GCV**, and where a reusable spectral backend beats a banded complete criterion pipeline.

Re-use the already tracked Experiment006 run_slice; no fork of its solver is permitted without independent parity tests. A separate scoped PR should resolve any numerical defect. Record status and make no universal fastest-method claims.

## Source files and immutable evidence

- `cases.json`: predeclared 21 cases (2 smoke, 13 pilot, 6 confirm); stage and resource gates are binding. It is a **plan**, never measured data.
- `campaign.py`: prints/list plans or runs **one case, one independent block**. Defaults to no numerical run. Phase `confirm` requires explicit `--allow-confirm`.
- `verify.py`: independently audits all complete-status/skip rows and matched \(S\)/score parity; MLE scores may have a lambda-independent additive difference. It does not certify high-precision forward error.
- `tests/test_campaign.py`: fast stdlib regression tests.
- `reference/experiment010_matched_n64_d1_bic.csv`: 48 copied historical **single-worker** rows from original `results/experiment010-uncapped-PCAG103A-08-20261103T222938857Z-shard0-offset20` (source SHA `f16f2bab6cfa37c6423c7f2d4554208efa9f683a`). It is **not** Experiment011 output and is not independent replication.
- `runs/<tag>/<case>/block000/`: output paths generated at runtime, NEVER overwritten or deleted. Commit/push raw files on a new results branch.

## Strict owner/agent contracts

**Agent 1 (engineering)** owns `campaign.py`, `verify.py`, `cases.json`, tests and smoke CI. Confirm that the existing run_slice actual statistical criteria and record schema are unchanged. Tests and smoke must pass before using the university workstation.

**Agent 2 (Windows measurement)** owns `runs/<machine-run-id>/` only. Use the clean source branch, the same Conda environment, one worker and one BLAS thread. Run blocks 0,1,2 on an idle computer with independent seeded series and rotated method order, push each finished block. A single `--block` is not three parallel workers. Do not install dependencies or render figures while timing.

**Agent 3 (analysis)** owns a separate statistical analysis module and a Springer figures PR. Reject invalid/undefined/failed/unsupported cells as timing winners; report their frequency. Pool only matching host/revision/criterion/mean, never across Experiment010's mixed-worker archive. Paired bootstrap over independent measurement blocks, not rows mistakenly assumed independent.

**Agent 4 (publication QA)** checks all analysis, numerical validity, provenance, and author/submission gates; updates `paper/SPRINGER_READINESS.md`. Never merge without authorization.

## Numerical boundaries

- Full SVD score/fit work differs by criterion. For CV, the leverage vector requires \(O(n(n-d))\) per candidate; scalar GCV/AICc/BIC/ML scores can amortize more efficiently.
- Banded Cholesky with selected inverse is the complete criterion backend; sparse CHOLMOD with an additional banded trace is a **hybrid**, and its double diagnostics must be charged.
- The inherited Experiment006 runner's `total_cold_s` is *an attributed timing*, not a fresh OS-process restart on every repeat; preserve this qualification. It includes common S-grid mapper setup for n<=512 even when evaluating Cholesky.
- Fixed \(\mu=0\) criteria are exact conditional in-sample formulas; `mu=data` explicitly opts into conditional plug-in, **not exact refitted LOOCV**.
- MLE may have an additive lambda-independent constant difference across normalizations. Compare matching minima; do not require equality of absolute raw MLE values.
- The positive S grid includes exact S=1; BIC may have a divergent interpolation boundary as S→0. A finite lower grid endpoint is a constraint, not an optimality proof.
- Dense resource gates are authoritative: `infeasible_dense_memory`, `infeasible_naive_runtime`, `budget_exceeded`, and any numerical/dependency failure are recorded outcomes.
- Preserve all archived cases, failing stdout/stderr, environment and script hashes. At least one independent high-precision check is required before declaring a high-d backend numerically superior.

## Experiment record template

For each new output group, document: question, predeclared case ID and block, hardware/software/Conda/BLAS, seed, exact command, raw status counts, numerical QA, medians and paired uncertainty when appropriate, findings, limitations, what to do next, original Git SHA and result-branch SHA.

No results should live only in chat, an Actions artifact or temporary VM. No secrets or licensed source PDFs in Git. Do not replace historical raw result files, edit other agents' branches or merge PRs without user authorization.
