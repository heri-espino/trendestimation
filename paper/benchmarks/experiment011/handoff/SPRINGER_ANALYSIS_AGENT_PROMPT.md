# Prompt: finish Springer empirical timing paper through GitHub Actions

You are responsible for completing the statistical analysis, figures, writing and compiled PDF for the canonical Springer Computational Statistics paper in `heri-espino/trendestimation`. Specialize in the empirical complete-criterion timing tensor. Work autonomously through a reviewable manuscript PR; do not stop at an outline.

## Access model: use Actions, not an interactive VM session

You do NOT have direct Windows desktop, terminal, SSH or filesystem access. You have repository access and should use GitHub Actions jobs on the self-hosted **PCAG103A-08**, Windows X64 runner to read the existing files, analyze data, generate figures and compile the paper. The author reports the runner active; verify actual job scheduling and filesystem access. Runner availability does not guarantee the service account can read the user's directories.

You are authorized to create scoped analysis/figure/build scripts and workflows, dispatch them using available GitHub tools or an authenticated CLI, inspect logs/artifacts, fix issues and rerun analysis/builds. You are NOT authorized to rerun the completed large numerical experiments, merge or submit the article. Do not ask the author to upload raw files merely because your own environment cannot see the VM: first probe access through the runner. If dispatch capability, runner scheduling or filesystem permission actually blocks you, report the specific evidence and minimum action needed.

## Read the repository first

Inspect current branches, PRs and workflows. Fetch `docs/experiment011-completion-handoff` (PR #124; inspect current merge state) and read its handoff folder, root/paper/experiment AGENTS.md, README.md, AI_HANDOFF.md, paper/SESSION_HANDOFF.md, PUBLICATION_MAP.md, SPRINGER_AGENT_BRIEF.md, SPRINGER_READINESS.md and BUILD_ON_PC08.md. Read actual Experiment006 source, Experiment011 cases/campaign/verify/analyze/tests, and `additional_seeds.py`/`resume_seeds.py` on `research/experiment011-additional97`. Do not assume all controllers are on main or obey obsolete pending-run instructions over this completed campaign.

Canonical target: `paper/main.tex` and `paper/sections/`, official `sn-jnl`. CSDA A (`paper/csda-spectral-smoothness/`) owns numerical precision; CSDA B (`paper/csda-computational-costs/`) owns complexity theory; NGSIM (`paper/ngsim-jerk-case-study/`) owns physical/forecast applications. `paper/computational-statistics-submission/` is a historical SNCS manuscript, not this target. Understand these projects without editing or claiming their contributions as new Springer findings.

## Existing local data: read through the self-hosted runner

Original checkout:
`C:\Users\175199\trendestimation-PC08_add97svd_20261105_025108`

Final cumulative report, relative to original checkout:
`paper\benchmarks\experiment011\campaigns\PC08_resume12_20261108_200034\report.json`

Author's console confirms 2813 recorded / 2813 planned, remaining 0. This is job completion, not numerical certification. GitHub's last inspected results report had only 2338 records; inspect current refs but do not substitute an older remote checkpoint.

Backup root:
`C:\Users\175199\experiment011-backups\experiment011_20261109_072910742`

The author supplied successful `VERIFIED COPY` output after the backup script compared copied files with source SHA-256 hashes. Its metadata contains `report.json`, `provenance.json`, `files_sha256.csv`. Independently verify through the runner before treating it as audited input. A same-disk copy is not independent disaster recovery.

A workflow's `$env:GITHUB_WORKSPACE` is a fresh source checkout, NOT the original experiment directory. Check out new analysis code there and pass the absolute original/backup paths as **read-only data inputs**. Do not checkout, clean, reset, git-switch or write generated outputs inside either data directory. Resolve report paths against their documented original root or explicit mirrored-backup root, not the workflow checkout. Do not require measured data-source SHA to equal the new analysis commit; verify content hashes and record both revisions separately.

The final report spans many original and continuation tags. Raw files are under `paper/benchmarks/experiment011/runs/<tag>_sNNN/<case>/blockNNN/`, including `measurements/raw_times.csv`, environment, case manifest and QA. Keep `runs_parallel/` separate. Inspect report records and source to resolve all canonical files; the final campaign folder alone is insufficient.

## Workflow engineering and publication

First run a small read-only preflight on PC08: require expected runner name, check all absolute paths and account access, read/hash report and provenance, validate 2813 unique expected jobs, inspect inventory and a referenced block, check Python/plotting/TeX availability. Publish compact diagnostic metadata. No benchmark.

Use existing labels `[self-hosted, Windows, X64]` and require `RUNNER_NAME=PCAG103A-08`; runner NAME is not automatically a label. Use custom `pc08` only if actually configured. Run independent jobs serially or with a coordinated concurrency lock; avoid interrupting other workloads. Use the existing Conda environment through:
`C:\Users\175199\AppData\Local\miniconda3\Scripts\conda.exe run --no-capture-output -n trendestimation ...`
Do not modify the shared environment unnecessarily.

Inspect `.github/workflows/compile-papers-pc08.yml` and `scripts/build_papers_pc08.py`. The existing manual build accepts `paper=springer`, compiles `paper/main.tex`, uploads PDF/log/hash artifacts and pushes a separate `artifacts/papers-pc08-<run-id>-a<attempt>` branch. It is not an Experiment011 ingestion/analysis workflow and does not automatically regenerate your new empirical figures. Adapt/reuse it after generating the actual analysis inputs. Do not use a historical figure builder that silently executes fresh simulations or repopulates outdated tables.

Select the intended manuscript source ref; record its SHA and analyze/build the intended revision. Inspect workflow registration/triggers: a brand-new workflow only on a feature branch may not yet be dispatchable. Use an existing suitable dispatch entrypoint or a narrowly scoped branch trigger if needed; do not silently merge into main merely to register a workflow. Follow repository Actions permission rules. Scope `contents: write` to publication jobs, use explicit output allowlists, and avoid token leakage or broad `git add .`.

Save derived outputs in a new run-specific workspace/output directory. Publish compact report/provenance/inventory, analysis tables, figure source/vector PDFs, analysis logs and the compiled manuscript PDF to a dedicated results/build branch with GitHub Actions artifacts as an additional copy. Artifacts expire, so they are not the only archive. Keep raw measurements local; no automatic raw archive upload, LFS migration, Git history rewrite or force push. Publish accessible PNG figure previews where useful. Provide exact PDF and figure links, source SHA, workflow run and output hashes. Never present an old tracked PDF as a successful new build.

## Scientific analysis

Validate expected keys, seeds, rotated method-order blocks, source/design hashes, raw-row counts, QA and candidate completeness. Follow the final cumulative report's canonical job selection. Preserve interrupted/orphan attempts but exclude them from independent replication. Build a reproducible accepted-record-to-file manifest; never recursively pool every historical run folder.

This is 29 selected cases x 97 additional seeds = 2813 jobs, not 2813 timing rows or a completed 252000-cell factorial. Represent a sparse long-form tensor over n,d,criterion,mu policy,amplitude,M,R,coordinate,workload,method,seed/repeat plus host, executable/environment hashes, concurrency and status. Missing or infeasible cells stay masked, not zero seconds.

Original phases include 24 concurrent small jobs, initially one worker for large jobs, then 12-worker continuations; one BLAS thread per job. Recover actual `phase_workers`/lineage. Do not assign the final report's top-level workers=12 to earlier records or pool contention strata as isolated-latency measurements. Timing sums are not campaign throughput without wall-time provenance.

Separate valid complete results from numerical, mapping, process, dependency, resource and partial-grid outcomes. A 95/100-candidate failure cannot win a full-grid timing comparison. Shared mapping failures are not automatically attributable to one solver. Float64 parity is not high-precision certification; SVD is not presumed universally successful. Keep analytic S=1, mu=data conditional plug-in CV, MLE normalization and charged hybrid diagnostics qualifications. No solver/tolerance changes.

Audit/extend analyze.py with tests for manifest selection, duplicate attempts, coverage, exclusions, pairing and concurrency. Report attempted/eligible/valid denominators, failure uncertainty, timing distributions and medians, setup/mapping/evaluation/cold/warm components, paired speedups and interval estimates. Pair matching case/data/repeat/source/environment/execution strata; bootstrap independent seed clusters with correlated method/workload rows together. Rotating block labels 0..2 are not the full independence structure. Check seed-stream dependencies. Discuss survivor bias and sensitivity. Compare naive only where valid measured pairings exist.

Explain CV vs scalar criteria, spectral setup amortization, banded/spectral comparisons, direct-S vs mapped-lambda at identical candidates, four workloads, and observed crossover slices. Do not invent missing surfaces, treat operation counts as measured seconds, claim universal optimality or introduce forecasting RMSE.

## Figures, writing and completion

Choose the figures yourself based on audited findings and explanatory value. Candidate ideas include coverage/failure maps, matched timing slices, paired ratio intervals, setup-vs-evaluation decompositions, coordinate/cache comparisons and criterion-specific crossover views. These are suggestions, not mandatory panels: omit unsupported/redundant plots. Every figure must identify relevant workload, validity, sample size and execution conditions. Follow repository AwesomeFigures and official Springer typography conventions; retain vector/source outputs and previews.

Write a coherent empirical article, revising title/abstract/introduction/methods/results/discussion/limitations/data availability to fit the evidence. Cite established PLS/WH and computational prior art accurately, without duplicating companion-paper novelty. Add claim-to-data links and reproducible analysis commands. Keep declarations/coauthor/submission gates explicit rather than invented.

Complete meaningful tests, regenerate tables/figures from canonical inputs, compile the actual updated Springer source through Actions, inspect the PDF visually (download/render if necessary), resolve material errors, then preserve the PDF, figures and provenance in GitHub. Update handoffs/readiness. Open a scoped PR without merging. Final response must give the PDF link, figure links, PR and Actions runs, key findings with uncertainty, verification and remaining limitations. A plan or successful compile of the old manuscript is not completion.
