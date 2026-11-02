# Experiment007 — Observed-difference mean solver study

This report is generated exclusively from the archived actual timing
and numerical validation files. This is a **fit-only** pilot with
**12 independent seed blocks**, with **3 cold timing repetitions per block**; not a complete statistical-criterion benchmark.

Primary mean: mu='data'=mean(np.diff(y,n=d)) computed independently
for each observed series. Fixed mu=0 is a control, not the default.

- Timed workloads: 13824
- Individual method/fit QA records: 72576
- Timing rows passing ALL required fit-accuracy checks: 11372 / 13824
- Independent Decimal-85 accuracy checks: 3072 / 72576

## Descriptive winners among complete numerically agreeing methods

| Workload | SVD | Cholesky | Sparse LU | FFT-PCG | No eligible method |
| --- | ---: | ---: | ---: | ---: | ---: |
| one_s_one_series | 2 | 17 | 17 | 0 | 0 |
| grid_one_series | 14 | 17 | 3 | 2 | 0 |
| one_s_three_series | 3 | 17 | 16 | 0 | 0 |
| grid_three_series | 15 | 15 | 4 | 2 | 0 |

These are **not** universal optimal dimension switches: they combine
only n=64/128/256, 12 seed blocks and limited S-grid sizes. The sampled
fixed mu=0 and data-derived mean policies must not be conflated.
Speed rankings exclude an entire method×workload×seed block if
even one candidate failed numerical agreement, rather than counting
incomplete grids as fast winners.

Most correctness checks use spectral SVD as a provisional comparator.
An 85-decimal-digit independent reference is available for selected
n<=128, high-d, high-S cases only. A forward-error threshold of 1e-6
is used for QA. Dataset generation knows the latent trend only to
report mu_true as a diagnostic; the solver receives mu='data', never
that oracle. No complete cell is independently certified at all S.

Do not replace the package default with a rule inferred from this
pilot; collect additional independent precision references, more
seeds and larger series, and time full criterion computations first.

## Provenance correction

This summary previously contained a hard-coded two-seed description from the initial pilot report generator. The recorded metadata.json and raw CSVs establish **12 seeds** and **3 cold timing repetitions** for this run. Only the explanatory wording in RESULTS.md was corrected; all numerical CSV measurements, metadata, and their content hashes remain unchanged. The report generator has been fixed for subsequent runs.
