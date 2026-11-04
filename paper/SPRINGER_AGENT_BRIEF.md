# Springer Computational Statistics — agent coordination brief

**Session continuation (2026-11-04): read [SESSION_HANDOFF.md](SESSION_HANDOFF.md) first.** It records the four-paper split, approved 29-case scope, current PRs, Windows missing-file diagnosis, exact results-worktree commands, and pending measurements. The next author action is the small 16-series/16-worker GCV pilot; the Windows campaign is not yet measured.

**Primary object:** `paper/main.tex`, Springer Nature `sn-jnl` (`Computational Statistics`), as distinct from `paper/computational-statistics-submission/` (historical SN Computer Science draft) and the two Elsevier `cas-dc` CSDA manuscripts.

**First read, in this order:** `README.md`, `AGENTS.md`, `AI_HANDOFF.md`, `paper/PUBLICATION_MAP.md`, `paper/SPRINGER_READINESS.md`, `paper/main.tex`, `paper/sections/experiment010_three_backend.tex`, `paper/benchmarks/experiment010/publication_evidence/README.md`, `paper/benchmarks/experiment006/README.md`, `paper/benchmarks/experiment006/{run.py,selected_inverse.py}`, `paper/benchmarks/experiment011/{README.md,campaign.py}`, the relevant tests, and the open experimental PR stacks. Consult the CSDA B and NGSIM sources only for cross-reference and attribution.

## Four independent agents, with exclusive responsibilities

### Agent 1 — Experiment011 infrastructure / mathematical QA
**Own:** `paper/benchmarks/experiment011/{campaign.py,verify.py,tests/,AGENTS.md}` and its plan.
**Goal:** deterministic workload manifest, reproducible same-machine comparisons, explicit finite-memory guards, optional CHOLMOD reporting, reuse of existing Experiment006 complete-criterion runner, strict status ledger, QA for paired selected \(S\) (and normalized scores when comparable).
**Do not:** edit Springer manuscript prose, alter `src/trendestimation`, change Experiment010's open research branches or claim high-precision truth from float64 score agreement.
**Deliverable:** CI-tested reproducible scripts and a PR with CLI evidence, tests and limitations.

### Agent 2 — Windows runtime and archival
**Own:** new `paper/benchmarks/experiment011/runs/<machine-run-id>/...` serial outputs and separate `runs_parallel/<machine-run-id>/...` throughput outputs *only* on a dedicated `results/experiment011-* ` branch. Never write in another agent's experiment files.
**Machine:** university Windows 11 `PCAG103A-08`, Conda `trendestimation`, up to 32 logical CPU processors. Favor one worker and one BLAS thread for single-method latency. On the 32-logical-processor host, optionally study independent small-series multiprocessing with 2/8/16/32 process workers using `campaign.py parallel-series`; archive these throughput records separately, never mix them into serial timing summaries. Rotate method ordering across independently seeded blocks to control temporal drift; document CPU contention and caches.
**Procedure:** run Experiment011 smoke first, then carefully bounded pilot cases; archive *every* raw row, including ineligible and failed statuses, metadata and QA; commit and push promptly. If CHOLMOD is unavailable, report it and run the core methods rather than substituting SuperLU under its name.
**Do not:** redo Experiment010's 100,000-candidate BIC pilot or start a 50,400-cell full factorial without a separate rationale and approval.
**Deliverable:** a permanent results branch and a reviewable machine-specific pilot results PR (not merged).

### Agent 3 — Springer implementation manuscript and figures
**Own:** `paper/main.tex`, `paper/sections/` and any NEW `paper/figures/` outputs. Work on a separate manuscript branch or PR after Agent 2's QA passes.
**Goal:** a software-engineering experimental article: complete CV versus scalar GCV/AICc/ML distinctions; mapped versus direct S; cache regimes; end-to-end cold/warm timing, feasible backend ranks by workload; critical prior art. Use AwesomeFigures with the actual Springer `sn-jnl` LaTeX styles; keep vector PDF/PGF plus audit metadata.
**Do not:** replicate CSDA B's theorem/proof as a second claimed novel contribution, make a universal SVD-wins assertion, transfer NGSIM forecast accuracy into implementation timing, or fabricate unmeasured speedups. The existing main Springer PDF has mixed-worker Experiment010 evidence; replace its illustrative *ranking* only after controlled source validation.
**Deliverable:** PR with source, measured tables, figures, compiled PDF and explicit source-hash audit.

### Agent 4 — Independent methods/QA and editorial release
**Own:** independent audit scripts and `paper/SPRINGER_READINESS.md` status evidence; no unreviewed changes to other agents' owned files.
**Goal:** validate raw-row provenance, pair design, selected-criterion agreement, timing interpretation, statistical dispersion, figures and numerical claims, endpoint behavior, author metadata, journal rules, originality overlap and build artifact.
**Do not:** classify float64 parity as an 85-digit precision certificate, silently discard invalid runs, or merge.
**Deliverable:** checklist with exact files, run SHAs, evidence for every claim and explicit unresolved conditions.

## Coordination protocol

- Start from a freshly fetched ref and read `AGENTS.md`. Do not assume `main` contains open PR #109 or nested Experiment010 research code.
- Claim your own file scope/branch. If a shared interface must change, document the proposed contract first; do not overwrite concurrent work.
- Experiments must be numbered sequentially; this campaign is `experiment011`. Inside it, name cases by their design (e.g. `pilot_cv_n128_d3_m100`) and runs by machine plus sequence, not an unexplained date.
- Every experiment's README or run manifest must say what was done, why, how to reproduce, findings (or `not_measured`), numerical validity, and what follows.
- Use a PR against a safe base and preserve source files. **Never merge without explicit user approval.**
- Every completed source or result artifact should be committed and pushed: no evidence exists solely in a VM, Actions artifact or chat.
- After a pilot, update `paper/SPRINGER_READINESS.md` with the result branch SHA and one of `planned`, `measured`, `validated`, `insufficient`. Do not modify immutable raw source archives.

## Dependency map

Agent 1 setup/QA → Agent 2 pilots on the actual VM → Agent 4 independent validation → Agent 3 manuscript/figures → Agent 4 release check. Theory/CSDA Paper B may continue independently in PR #109; NGSIM and CSDA A work should not block Experiment011.
