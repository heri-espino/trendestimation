# Experiment011: 97 additional seed trials

The author requested another 97 seeds after the 29-case, three-block Windows campaign. Keep that evidence and its failures intact. This follow-up uses the same 29 cases, methods, tolerances, grids and resource guards: 2813 case/seed jobs, up to 24 concurrent processes and one BLAS thread each. This is concurrent-load evidence, not isolated latency or the separate full factorial.

The original seed bases are 20261103 + 10000*block. The engine adds 100000*repeat + 23*series_index + 29*n + 7*d. Simply extending the old block spacing would reuse random streams across repeats. The new 97 bases are 1000000000 + 1000000*i for i=0..96, with labels s003 through s099. Regression checks establish no repeat/series stream collisions within any matched case against the original bases. Smoke cases originally have one seed; do not describe their final total as 100 independent seeds.

`campaign.py run --seed` explicitly overrides the base data seed and records it in the existing case manifest. Without this option the original behavior is unchanged. `additional_seeds.py` rotates method order through existing block positions and uses a separate tag for each base seed. No solver or archived case file changes.

Run from a clean repository root with PYTHONPATH=src:

    python paper/benchmarks/experiment011/additional_seeds.py --run-tag PC08_add97_UNIQUE --workers 24

Add `--dry-run` to validate the 2813-job schedule without timing. Outputs are under `runs/<tag>_sNNN/` and `campaigns/<tag>/`. The controller refuses an existing campaign folder; interrupted campaigns are not automatically resumed. It atomically checkpoints every completed job and reports per-method row statuses, missing QA, QA issues and incomplete candidate counts. Exit 2 indicates recorded numerical/infrastructure problems; preserve outputs regardless. Budget/memory skips remain separate. A zero exit is not high-precision certification.

Archive all output on a dedicated results branch after completion, including nonzero exits. Do not run another timing campaign simultaneously. Actual worker occupancy varies; 24 is a concurrency limit, not affinity or a guaranteed CPU count. No new Windows observations are claimed by preparation.

Validation: 25 Experiment011 stdlib checks pass, including seed-stream separation, explicit-seed provenance and negative-seed rejection. Full schedule dry-run reports 2813 jobs. No attempt to fix numerical failures by changing tolerances. Independent high-precision checks remain necessary before asserting numerical superiority; zero observed failures never proves universal SVD success.

## Author-approved large SVD extension

The author additionally requested SVD at n=2048 and 4096, allowing actual numerical/process failures to be recorded. Use `additional_seeds.py --large-svd --workers 24`. All cases at n<1024 finish in the first concurrent phase. Only after that executor has fully drained, every n>=1024 case runs with exactly one active case process and one BLAS thread. The n2048/4096 effective cases compare spectral_svd and banded_cholesky; n1024 retains its existing method list. There are still 2813 case/seed jobs, now with additional method measurements in 388 large case/seed jobs.

The opt-in effective large case uses an explicit expanded work budget and bypasses the inherited SVD runtime exclusion at n>2048. The existing 2-GiB dense-memory preflight remains in force. For n4096 its five-matrix SVD estimate is about 640 MiB, so it is eligible; this estimate is not a hard OS cap or a guarantee of available RAM. No tolerance, solver algorithm, original cases.json, archived timing or prior failure is changed. The effective methods, cap and opt-in flag are recorded in each manifest; phase worker counts are recorded per job. Numerical failures, missing QA and nonzero child exit codes remain explicit. No success or OOM diagnosis is inferred merely from elapsed time.

Validation: 27 unittest checks pass, including full n4096 SVD preflight admission, retention of cases.json, and rejection of the override for unintended sizes. The 2813-job opt-in schedule passes dry-run. New Windows SVD measurements remain pending. n16384/131072 are outside this 29-case follow-up.

## Interrupted Windows run and continuation

The author uploaded `results/experiment011-PC08_add97svd_20261105_025108` after VM shutdown. Its report preserves 2272 of 2813 jobs; 541 remain. Reported numerical failures are completed observations and must not be rerun merely to obtain success. The first 2231 jobs belong to the small-case phase; 41 large jobs were recorded before interruption. Original source is a8a9c4704eccfad8461a3c0e5f8502f18c2a6199.

`resume_seeds.py --previous-report PATH --run-tag NEW_TAG --publish` validates the original seed/case/block keys, rejects duplicates or changed numerical sources, and schedules only missing jobs with one BLAS thread and one case process. CRLF versus LF variants of the same design file are accepted explicitly, retaining the original recorded checksum. The source-content check rejects substantive numerical changes. No old output path is overwritten, including the interrupted job's partial attempt. The new report contains cumulative completed records plus the original report's SHA-256. Subsequent interruptions can therefore resume from the latest cumulative report using another new tag.

Publication is synchronous after each case finishes: stage only the new continuation campaign and its new run-tag paths, commit and push to the current results branch. A push error stops before launching another job. The new controller must be committed on the results branch before launch. Do not modify the old raw data or confuse recorded numerical failures with process errors. The optional --dry-run validates without running solvers.

Verified on the uploaded checkpoint: exactly 2272 preserved / 541 remaining. All 28 Experiment011 checks pass, including duplicate rejection and retention of failed numerical outcomes. Windows execution of the continuation is pending.

## Author-approved 12-worker continuation

The author requested faster completion after the serial large-n phase. `resume_seeds.py --workers 12` now runs up to twelve independent case processes, one BLAS thread each; default remains one and accepted range is 1..12. This supersedes the previous one-worker preference only when explicitly selected. Existing numerical memory guards remain; nominal dense reservation is workers*2GiB (24 GiB at twelve), not a hard OS memory cap. Concurrent-load times must stay labeled separately from earlier one-worker measurements.

Only the parent writes the cumulative report and commits. Each publication stages that report, the finished job's closed log and its unique case/block directory. It never stages a sibling worker's active log or partial raw CSV. Preserved outcomes are skipped regardless of numerical success, and fresh attempt tags prevent overwriting interrupted paths. Stop the earlier controller and ensure its case subprocess has exited before starting the new continuation. Choose the latest cumulative report, not necessarily the original 2272-job report.

Verification: 29 Experiment011 tests pass, including exclusion of active sibling files from publication. A dry run against the archived 2272-job checkpoint confirms 541 remaining jobs with workers=12. Actual twelve-worker Windows continuation is pending; no speedup factor is promised.
