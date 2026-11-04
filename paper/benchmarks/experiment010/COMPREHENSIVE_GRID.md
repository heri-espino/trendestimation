# Experiment010 — complete-grid execution and reproducibility

## Current scientific scope (2026-11-03)

The manuscript focuses on (1) numerical accuracy and feasibility and
(2) genuine measured end-to-end criterion computation times for all ten
pre-existing complete-method pipelines. The user declined the additional
cost-prediction-model and fallback-regret proposals in older Experiment010
notes. Retain previous research; do not expand the paper.

Independent work branch: research/experiment010-comprehensive-grid,
based on the existing draft PR #100. Do not merge either branch without
authorization. No change to production trendestimation default.

## Interpretation of "all methods"

The full grid currently crosses **the ten existing implemented complete
criterion pipelines**, not every possible numerical method for the dual
PLS linear system. In particular, independent dual LDL, QR, dedicated
dual banded Cholesky, and newly developed fast Toeplitz techniques
are not silently counted as implemented or benchmarked. Such methods
must first provide complete, tested CV/GCV/AICc/BIC/MLE outputs,
not merely a fast fit, before being added as separate experimental
pipelines. This distinction avoids claiming an exhaustive algorithm
survey when only the implemented ten are being compared.

## Entire factorial

- n: 64, 128, 256, 512, 1024, 16384, 131072 (7 levels)
- d: 1 through 6 (6)
- reference mean: 0, observed-difference data mean, fixed 0.15 (3)
- observation scale: low and high (2)
- criterion: CV, GCV, BIC, AICc, MLE (5)
- grid denominators: 100, 1000, 10000, 100000 (4)
- pipelines: all ten named in Experiment010 README (10)
- workloads: one/grid S crossed with one/multiple series (4)
- coordinate: direct_s and mapped_lambda (2)
- two real repetitions, R=2 for the multiple-series workloads
- same S candidates across methods, including the exact S=1 endpoint
- Windows PCAG103A-08, existing Conda environment trendestimation,
  BLAS threads=1; no dependency installations

Total: **5040** parameter configurations, **50400** method-case attempts,
**403200** planned method/workload/coordinate cells. The implemented
one-S workload appears once for each denominator; it is therefore
repeated in these 403200 cells. The older proposal mentioned R>=3;
the actual run has R=2 and must not be misrepresented.

The complete PLAN (not measured timings) was committed to the
[immutable archive](https://github.com/heri-espino/trendestimation/tree/results/experiment010-41647428485-a1-comprehensive-plan).
Plan counts: **264240 eligible under conservative resource budgets;
106320 work-budget excluded; 26880 dense-memory excluded;
5760 naive-runtime excluded.** Total 403200. These statuses are
not numerical certificates, nor solver execution statuses.

## Bounded real runs

[GitHub Actions #41647428485](https://github.com/heri-espino/trendestimation/actions/runs/41647428485)
initially scheduled four disjoint shards (0,1,2,3 of 16),
each with a 40-method-case window starting at cursor 0.
Read the completed job status and raw result branches before
claiming that any of these batches finished.

The complete manifest is generated with --plan-only. Actual runs use
--preset comprehensive --manifest-scope shard. The hash of case_id
assigns a case and all its ten methods to the same deterministic
shard. The maximum runtime is 600 seconds per batch, 25 seconds per
method process, 40 method-case attempts; maximum work 80 million
conservative units and dense memory budget 2 GiB.

Every run contains exact source revision, environment, the selected
shard's full mask, complete attempt ledger, raw successful timings,
numerical score-parity rows and failure logs. Ineligibility across
every workload is recorded as resource_ineligible_all_workloads
without launching a solver and WITHOUT reporting zero as a
successful timing. Unfinished attempts are not_executed_budget.

**Resume from batch_summary.json -> next_attempt_offset** with the
same shard_count and shard_index, and a unique output. Do not reuse
a prior branch name or overwrite results.

### Continue on the unmerged research branch

**Reliable launch mechanism:** create or edit the file
paper/benchmarks/experiment010/REQUEST_BATCH.json with this content,
then commit and push it to research/experiment010-comprehensive-grid:

```json
{
  "enabled": true,
  "shard_index": 4,
  "shard_count": 16,
  "start_attempt": 0,
  "max_method_attempts": 40
}
```

Its push triggers the one-job workflow
.github/workflows/experiment010-comprehensive-request.yml.
On subsequent requests, change the shard or the exact
start_attempt using the last batch_summary.json. Every
changed request generates a unique run-ID archive.
A pull request or default-branch merge is NOT required to use
the request-file push trigger.

The convenience workflow_dispatch inputs in the original
comprehensive workflow may be inaccessible until the
workflow file is present on the repository default
branch. Do not rely on that UI for an unmerged PR.

### Run locally in PowerShell

From repository root, with existing Conda environment:

    $env:PYTHONPATH = "$PWD\src"
    conda run --no-capture-output -n trendestimation python paper\benchmarks\experiment010\run_batches.py --preset comprehensive --manifest-scope shard --shard-index 0 --shard-count 16 --start-attempt 40 --max-method-attempts 40 --max-seconds 600 --per-method-seconds 25 --repeats 2 --series-count 2 --max-work 80000000 --output paper\benchmarks\experiment010\runs\unique-batch

The shown cursor 40 is ILLUSTRATIVE; always read the real
next_attempt_offset from the corresponding archived batch.
Commit and push the generated data, logs and metadata.

## Meaning of statuses

- eligible in manifest: under the conservative *predicted* resource
  limit; not a successful benchmark.
- completed_with_csv: raw file exists; further check per-row status=ok,
  evaluations==M*R and numerical validity.
- score_parity_only_not_precision_certified: approximate agreement
  against a spectral score, not an independent forward-error certificate.
- unverified_no_spectral_reference: spectral reference unavailable.
- resource_ineligible_all_workloads: no solver run; elapsed_s=0
  is a placeholder and MUST NOT be ranked.
- method_timeout_no_credible_time: no finished criterion timing.
- execution_failed, process_error, score_disagreement: record exactly.

An accurate high-precision independent trend/criterion validation is
still necessary for high difference orders and large S. The full
design is complete, but a full experimental execution is NOT complete
until every method-case attempt is addressed and all feasible cells
have either successful measurements or explicit failures under the
stated fixed budget.


## Uncapped comparison branch and actual VM PowerShell runs

Follow [UNCAPPED_LOCAL.md](UNCAPPED_LOCAL.md) on the independent
research/experiment010-uncapped-checkpointed branch (draft PR #103).
The uncapped experiment is an **explicit opt-in replacement** for
arbitrary 25-second method timeouts and 600-second run budgets;
physical-memory eligibility and numerical failure recording remain.
The first historical full-grid four-shard result archives remain
unchanged as *capped preliminary evidence*. No uncapped numerical
results should be claimed before the user executes and uploads them
from PCAG103A-08. The PowerShell launcher creates a unique results
branch and pushes actual rows and error logs after each method-case
checkpoint batch. There is no background scheduled completion.
