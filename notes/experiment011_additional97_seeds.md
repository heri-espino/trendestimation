# Experiment011: 97 additional seed trials

The author requested another 97 seeds after the 29-case, three-block Windows campaign. Keep that evidence and its failures intact. This follow-up uses the same 29 cases, methods, tolerances, grids and resource guards: 2813 case/seed jobs, up to 24 concurrent processes and one BLAS thread each. This is concurrent-load evidence, not isolated latency or the separate full factorial.

The original seed bases are 20261103 + 10000*block. The engine adds 100000*repeat + 23*series_index + 29*n + 7*d. Simply extending the old block spacing would reuse random streams across repeats. The new 97 bases are 1000000000 + 1000000*i for i=0..96, with labels s003 through s099. Regression checks establish no repeat/series stream collisions within any matched case against the original bases. Smoke cases originally have one seed; do not describe their final total as 100 independent seeds.

`campaign.py run --seed` explicitly overrides the base data seed and records it in the existing case manifest. Without this option the original behavior is unchanged. `additional_seeds.py` rotates method order through existing block positions and uses a separate tag for each base seed. No solver or archived case file changes.

Run from a clean repository root with PYTHONPATH=src:

    python paper/benchmarks/experiment011/additional_seeds.py --run-tag PC08_add97_UNIQUE --workers 24

Add `--dry-run` to validate the 2813-job schedule without timing. Outputs are under `runs/<tag>_sNNN/` and `campaigns/<tag>/`. The controller refuses an existing campaign folder; interrupted campaigns are not automatically resumed. It atomically checkpoints every completed job and reports per-method row statuses, missing QA, QA issues and incomplete candidate counts. Exit 2 indicates recorded numerical/infrastructure problems; preserve outputs regardless. Budget/memory skips remain separate. A zero exit is not high-precision certification.

Archive all output on a dedicated results branch after completion, including nonzero exits. Do not run another timing campaign simultaneously. Actual worker occupancy varies; 24 is a concurrency limit, not affinity or a guaranteed CPU count. No new Windows observations are claimed by preparation.

Validation: 25 Experiment011 stdlib checks pass, including seed-stream separation, explicit-seed provenance and negative-seed rejection. Full schedule dry-run reports 2813 jobs. No attempt to fix numerical failures by changing tolerances. Independent high-precision checks remain necessary before asserting numerical superiority; zero observed failures never proves universal SVD success.
