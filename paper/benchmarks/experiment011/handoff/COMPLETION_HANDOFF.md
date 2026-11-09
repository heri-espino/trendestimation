# Experiment011 completed Windows campaign: acquisition and analysis handoff

Updated 2026-11-09. **Access correction:** The next agent has no interactive VM access but is expected to use GitHub Actions on the self-hosted PCAG103A-08 to read local data, analyze, render figures and compile. The author has now supplied successful VERIFIED COPY output for `C:\Users\175199\experiment011-backups\experiment011_20261109_072910742`; runner-level independent verification is still required. Read the updated Actions-specific prompt first.  This update supersedes earlier “Windows pending” instructions for this campaign only. Canonical Springer manuscript: `paper/main.tex`.

## Evidence and current boundary

The author supplied console output showing **2813 recorded / 2813 planned, remaining 0** from the local report below. This establishes reported scheduling completion, not numerical validity, a successful full grid in every row, or completion of the historical 252000-cell factorial. We have not read the final local report or raw files in this session. No timing winners, numerical pass rates, uncertainty estimates or backup success are claimed yet.

Fresh inspection of GitHub results branch `results/experiment011-PC08_add97svd_20261105_025108` at `9c7dded8` still finds the cumulative `PC08_resume12_20261105_163243` report with **2338** records and `in_progress`. Do not analyze that as the completed campaign. Publication was disabled by author request; local raw data must be acquired before the paper can be completed.

## Exact locations

| Artifact | Location |
|---|---|
| Windows checkout | `C:\Users\175199\trendestimation-PC08_add97svd_20261105_025108` |
| Author-reported completed report, relative to checkout | `paper/benchmarks/experiment011/campaigns/PC08_resume12_20261108_200034/report.json` |
| All campaign reports and logs | `paper/benchmarks/experiment011/campaigns/` |
| Raw complete-criterion outputs | `paper/benchmarks/experiment011/runs/<tag>_sNNN/<case>/blockNNN/` |
| Separate small-series parallel throughput | `paper/benchmarks/experiment011/runs_parallel/` (if present; do not combine with criterion latency) |
| Measurement files within each block | `measurements/{raw_times.csv,summary.csv,paired_speedups.csv,environment.json}` |
| Case and QA files within each block | `experiment011_case.json`, `experiment011_qa.json` |
| Controller implementation | `research/experiment011-additional97`, `additional_seeds.py` and `resume_seeds.py` under Experiment011 |
| Original numerical source | `a8a9c4704eccfad8461a3c0e5f8502f18c2a6199` (check per-case content hashes too) |
| Machine-readable location copy | `VM_LOCATIONS.json` next to this document |
| Backup and transfer procedure | `BACKUP_AND_TRANSFER.md` next to this document |
| Next-agent instructions | `SPRINGER_ANALYSIS_AGENT_PROMPT.md` next to this document |

Original tag `PC08_add97svd_20261105_025108`; subsequent tags include `PC08_resume97_20261105_151552`, `PC08_resume12_20261105_163243` and later November 8 recovery attempts. **The final report is cumulative; its records point to multiple earlier run folders. Copying only the final campaign directory is insufficient.** Preserve all Experiment011 folders, including interrupted attempts and logs. Discover authoritative paths from report records and manifests; do not assume the final tag owns every result. See `VM_LOCATIONS.json` for portable machine-readable metadata; it intentionally has no invented file hash.

## Design and interpretation

- 97 additional seed trials x 29 selected cases = 2813 case/seed jobs, not 2813 raw timing rows. Non-smoke cases rotate existing method-order block positions; smoke originally had only one base seed. Do not claim 100 seeds for every case.
- Additional seed bases: 1000000000 + 1000000*i, i=0..96; seed-index labels s003..s099. Validate against the actual controller and records before pooling.
- Original phase used up to 24 concurrent jobs for n<1024; large jobs initially used one; continuation used up to 12, with one BLAS thread per job. Use record `phase_workers` and report lineage, not just the final report's top-level `workers=12`.
- Large-SVD opt-in adds SVD at n2048/4096 alongside banded Cholesky, with inherited memory checks and explicit work-budget changes. Do not silently impose the earlier banded-only plan on these effective cases. No n131072/d6 full factorial was run by this campaign.
- Controller interruption and publication errors can leave raw completed or partial attempts outside cumulative records. Canonical selection must follow final recorded job identities. Preserve orphan files, mark them as excluded attempts, and do not count them as independent replication.
- Failures and skipped/budget outcomes count as recorded jobs. Retain separate process, mapping, residual/numerical, coverage, dependency and resource statuses. A failed grid with 95/100 candidates is not a valid fast completed grid.
- No evidence supports “SVD always succeeds.” Float64 selected-score agreement is parity, not a high-precision certificate. Mapping failures may affect multiple backends through shared infrastructure.

## Required analysis

1. Verify final report hash, unique `(seed_index, case)` identities, design hash, source consistency and seed/block agreement using the recovery controller's validation logic. Reconcile 2813 with all referenced raw/QA/environment files. Record missing/duplicate/corrupt files separately.
2. Build an explicit accepted-record-to-block-path manifest. Never recursively pool all `runs/`: that includes historical and interrupted attempts. Expand only canonical records from the completed campaign.
3. Audit `analyze.py` before reuse. Its current measured columns do not include controller concurrency and it recursively loads block folders; neither behavior handles this continuation lineage automatically. Add an analysis-only ingestion layer and tests for duplicate attempts and concurrency strata. Preserve current raw data and numerical runner.
4. Form a **sparse empirical timing tensor** in long form, indexed by n,d,criterion,mu policy,amplitude,M,R,coordinate,workload,method and seed/repeat, with host, environment/executable hashes and concurrency strata. Preserve statuses/masks; never fill unobserved cells with zero seconds. Record setup/mapping/evaluation/cold/warm costs and exact candidate coverage. S=1 is an analytic endpoint.
5. Summarize failures with denominators and distinguish attempted/admissible/valid-paired observations. Rank only complete, numerically admissible matched pipelines. Keep high-order uncertain comparisons descriptive until independent numerical checks pass.
6. Pair methods within the same case, seed, repeat, coordinate, host, source and concurrency stratum. Report medians, geometric paired speedups and uncertainty; resample independent seeds/blocks, keeping repeated workloads/methods together. Method-order block labels cycling 0..2 are not the only three independent trials in the 97-seed campaign. Inspect actual seed-stream dependencies before claiming independence.
7. Report sensitivity to exclusions and concurrency. One-worker and concurrent-load timings cannot establish one pooled isolated-latency ranking. Worker occupancy varies; a limit of 12 does not guarantee 12 active processes or CPU affinity. Timings alone do not establish total campaign throughput; require controller wall timestamps for throughput claims.
8. Address CV vs scalar GCV/AICc/MLE costs, setup amortization, four workloads, direct-S vs mapped-lambda over identical candidate S values and supported crossover slices. No RMSE/forecasting claims or unmeasured universal crossover surfaces. MLE conventions may differ by a lambda-independent constant; mu=data CV is conditional plug-in, not refitted LOOCV.
9. Save analysis code, raw-file checksums, input-selection manifest, long-form CSV, status tables, confidence intervals, vector figures, figure sources and claim-to-table ledger on a dedicated branch. Use documented external storage for large raw archives; keep compact report/manifest/derived tables in Git after size inspection.
10. Update Springer manuscript and readiness ledger only from audited evidence. Keep historical draft, CSDA theory/numerical and NGSIM ownership boundaries intact. Compile official sn-jnl source and inspect PDF. Commit/push scoped deliverables; no merge or journal submission without authorization.

## Pending actions and safety

Backup and raw-data transfer require access to the Windows VM. This chat environment cannot copy that disk. Run the documented backup block on the VM, then provide `report.json` and metadata first (or give a VM-capable agent the prompt). A same-disk copy protects against accidental edits, not loss of the VM/disk. Arrange a separate-disk or external copy before deleting the original checkout. No Git LFS files were reported by the user's local `git lfs` listing; the original `commit_refs` failure never proved an LFS quota diagnosis. Do not migrate LFS, prune objects, rewrite history or delete repository artifacts on that assumption.
