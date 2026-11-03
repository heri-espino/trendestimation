# Experiment010: publication evidence and controlled follow-up

## Scope of this frozen evidence
This folder contains **48 real method-workload observations**, not predicted
or synthetic timings, copied directly from two immutable GitHub result branches.

The experiment is **one** numerical configuration:
- (n=64), (d=1), `mu=data` interpreted as
  `mean(D_d @ y)` for each observed series;
- high-amplitude synthetic input; residual `BIC`;
- candidate-grid denominator `M=100000`, exact same
  candidate values and `seed=20261102`;
- four workloads: single S and full S-grid each for one or two series;
- two parameter coordinate modes: direct `S` and once-mapped `lambda`;
- **two repeat seeds**, with complete per-repeat raw time components.

The raw CSV is `three_backend_bic_n64_d1.csv`.
Columns `source_sha`, `source_archive` and `parallel_workers`
explicitly preserve original platform and version provenance.
The frozen source archives are:

1. [Eight-worker naive + spectral + other methods](https://github.com/heri-espino/trendestimation/tree/results/experiment010-uncapped-PCAG103A-08-20261103T165925192Z-shard0-offset20);
2. [One-worker sparse CHOLMOD only](https://github.com/heri-espino/trendestimation/tree/results/experiment010-uncapped-PCAG103A-08-20261103T193236486Z-shard0-offset26).

The original run metadata and Conda package snapshots remain **on those
results branches**. Do not modify or replace them. All three methods produced
16 `status=ok` rows with nearly identical BIC scores at the stored
selected smoothness. This is float64 score parity, not high-precision
forward-error certification.

## Scientific limitation: concurrency is not matched

SVD and naive inverse were launched as parts of an **8-worker pool**
that ran nine numerical pipelines simultaneously; the later sparse
CHOLMOD backfill was run in isolation with **one worker**.
Therefore the `total_cold_s` medians cannot be used as an
unconfounded relative-performance ranking. They are descriptive
actual timings from a known Windows machine, useful to show
implementation readiness and traceability. Do not silently
remove this qualifier in the paper.

Also, `-Workers 8` on `-MethodAttempts 1` only schedules **one**
independent subprocess. It does not internally parallelize the
CHOLMOD factorization. The worker count is the maximum number of
independent method--case processes, not a solver BLAS thread count;
the launcher's per-process numerical BLAS thread count is one.

## A properly controlled matched serial comparison (optional)

For a fairer **one-worker isolated-latency comparison**, run all
three selected methods within **one batch**, using the same
machine, pinned environment, input `seed`, original ten-slot
cursor, and a quiet machine. This deliberately reruns the
*same* (n=64,d=1) configuration under matched conditions.
The old archives remain immutable.

From a **clean worktree containing the currently checked
Experiment010 parallel runner, e.g.**
`origin/research/experiment010-cholmod-v05-compat`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paper\benchmarks\experiment010\run_uncapped_local.ps1 -ShardIndex 0 -ShardCount 16 -StartAttempt 20 -MethodAttempts 10 -Workers 1 -Methods "naive_inverse,spectral_svd,sparse_cholesky_banded_trace"
```

The above rerun takes the previously archived 20--29 source
positions but creates a **new timestamped result branch**, so the
provenance remains separate and the original results are preserved.
It is a targeted **replication**, *not* a continuation cursor:
do not use its `next_attempt_offset=30` to infer other shard
progress, and do not overwrite an existing output.

For a throughput comparison using the available 32 logical CPU
processors, one can run an appropriately sized set of **multiple
independent method--case tasks** with `-Workers 8`; that measures
concurrent throughput, not isolated algorithm latency, and must
use the same case mix/worker pressure for each policy. A
single sparse-Cholesky task will not occupy eight workers.

## Reproducible audit

```powershell
python paper\benchmarks\experiment010\publication_evidence\check_table.py
```

This checker validates the complete 48-row design, all original
source SHAs and eight-vs-one worker provenance, exact repeat pairing,
matched selected smoothness and relative BIC parity against SVD,
then verifies medians transcribed into the manuscript's LaTeX table.
It does **not** execute any numerical experiments.

The paper inclusion is
`paper/sections/experiment010_three_backend.tex`. The large
Experiment010 factorial manifest should not be described as an
already completed experimental dataset. This one-case engineering
check supports reproducibility but not universal numerical,
statistical or hardware-performance claims.

The central theoretical computational point is independent of this
small experiment: (A_\lambda=I+\lambda D_d^\top D_d)
is SPD and (d)-banded, enabling (O(nd^2)) banded
Cholesky factorization and (O(nd)) storage. CHOLMOD with a
separately charged exact banded selected-inverse criterion is
a **hybrid**; it should not be labeled a pure Cholesky timing.

## Submission status

This is a manuscript preparation and software-evidence update.
Corresponding author contact, coauthor contribution statements,
funding disclosures and final submission approval still need
the authors' actual confirmation. Do not fabricate them.
