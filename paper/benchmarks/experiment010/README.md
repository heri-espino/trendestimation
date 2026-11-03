# Experiment010 — The feasible computational frontier for smoothness-indexed PLS

**Status:** research protocol only; no Experiment010 timings, calibrations, production auto-selector, or paper-level experimental conclusions are claimed. Builds on merged PR #98 (Experiment008) and PR #99 (Experiment009). All prior source and raw observations remain preserved. Follow `AGENTS.md` and `AI_HANDOFF.md`.

## Research question

For a known computational workload, which **complete, numerically reliable and actually available** solver is theoretically expected to finish fastest, and how often do **held-out, paired, empirical observations** confirm that choice? If the first-ranked candidate is infeasible, unavailable, or numerically invalid, which fallback should be chosen? The output should be an **empirically audited conditional frontier**, not a global SVD-versus-Cholesky cutoff or a universal hardware-independent winner.

We optimize computational time, not trend RMSE. Numerical correctness, complete criterion coverage, installation/convergence and resource feasibility are hard gates.

## Model, symbols and statistical contract

For `y in R^n`, difference order `1 <= d < n`, `D_d in R^((n-d) x n)`, penalty `lambda>=0`, and difference reference mean `mu`, solve

```text
tau_hat = argmin_tau ||y-tau||_2^2 + lambda ||D_d tau-mu*1||_2^2.
Q = D_d.T @ D_d,
A(lambda) = I + lambda*Q,
b(lambda,mu,y) = y + lambda*mu*(D_d.T @ 1),
A(lambda)*tau_hat = b.
```

Compare three **separate** reference-mean policies, crossing them with every eligible method and criterion:
1. `mu=0`: fixed zero difference mean.
2. `mu="data"`: `mu_hat=mean(D_d @ y)` separately for each observed series; this is **not** simultaneous optimization of mu and tau, nor necessarily the latent trend's exact difference mean.
3. `mu=c`: a fixed **nonzero** real constant. Use `c=0.15` as one directly reproducible control from earlier experiments, then add signed/scale-aware values as separately labeled sensitivity tests. Record `c` numerically and never silently identify this policy with `mu="data"`.

For **fixed numeric** mu, the smoothing matrix is `H_lambda=A(lambda)^(-1)`. Define normalized Guerrero smoothness:

```text
S_{n,d}(lambda) = (n - trace(H_lambda))/(n-d)
                = (1/(n-d)) sum_{j=1}^{n-d}
                    lambda*delta_j/(1+lambda*delta_j),
```

where positive `delta_j` are eigenvalues of `Q`. The S-to-lambda map depends on `(n,d)`, **not** on y or the chosen fixed/plug-in difference mean. Therefore one correctly computed S-grid translation may be shared across independent series, mean policies, statistical criteria and solvers with the same `n,d`. However, the *fitting RHS and criterion semantics* depend on mu. For `mu="data"`, existing CV/GCV/AICc/BIC comparisons are **conditional plug-in**, not exact leave-one-out re-estimation of the mean. The conditional MLE similarly does not jointly estimate mu. A truly refitted mean requires a separately derived/tested smoother and criteria; do not claim it has already been implemented.

## Smoothness FIRST: exactly matched candidate sets

Use the S-grid `S_i=i/M` for `i=1,...,M` with `M in {100,1000,10000,100000}`, plus a single-S workload `S=0.5`. Include **exact** `S=1 <-> lambda=+infinity` as a constrained polynomial limit, never approximate it with a huge finite lambda. The same candidate grid MUST reach every compared solver and coordinate strategy:

- `direct_s`: perform `S->lambda` conversion when an evaluation is requested.
- `mapped_lambda`: translate the ENTIRE S-grid once, cache the corresponding lambda values, then evaluate the **identical** points via each backend; charge prep, cache memory and translation to the right shared workload.

No independent logarithmic-lambda grid may be represented as the same statistical comparison. When comparing direct-S versus premapped-lambda for one end-to-end search, include all conversion overhead. For a shared grid across `R` independent series or five criteria, count mapping once, not R times. Measure actual overhead instead of assuming that a theoretical mapping bound is negligible. At large n and high d, avoid an implicit dense SVD merely to produce mapped lambda: include and compare accurate structure-exploiting S inversion.

## Backend enumeration (the actual existing experiment006/008 full-criterion set)

| Name | Type | Cost/limitation to include |
|---|---|---|
| `naive_inverse` | Explicit dense inverse baseline | Full inverse each candidate; dense RAM and cubic work; skip infeasible n |
| `spectral_svd` | Full shift-free spectral SVD | Dense cubic setup and quadratic memory; cached projections; criterion-specific per-candidate cost |
| `banded_cholesky` | Banded SPD Cholesky with selected inverse | Factorization + exact selected-inverse leverage/trace/logdet; forward-error sensitivity at high d/S |
| `guarded_svd_cholesky` | Existing composite fallback policy | Count actual selected primitive; **not** a novel independent solver |
| `banded_lu_banded_trace` | General banded LU plus Cholesky diagnostics | Double-factorization diagnostic work charged explicitly |
| `sparse_lu_banded_trace` | Sparse SuperLU plus banded diagnostics | Sparse setup, fill-in and separate exact diagnostics |
| `sparse_cholesky_banded_trace` | Optional genuine SuiteSparse CHOLMOD plus banded diagnostics | Must record dependency availability; never relabel SuperLU as CHOLMOD |
| `pcg_fft_banded_trace` | FFT-preconditioned PCG plus banded diagnostics | Observed iteration count, strict convergence and separate exact diagnostic work |
| `pcg_dst_banded_trace` | DST-preconditioned PCG plus banded diagnostics | Same; DST approximation alone does not certify the true boundary problem |
| `pcg_jacobi_banded_trace` | Jacobi-preconditioned PCG plus banded diagnostics | Same; depends on conditioning and stopping rule |

These are benchmark **pipelines**, not ten algebraically independent methods. Compare any additional `eigh`, direct banded LU or structured algorithm as a separate method only when its complete CV/GCV/BIC/AICc/MLE diagnostics are actually implemented and validated. Do NOT compare a fit-only elapsed time against a complete criterion-selection time.

## Factorial axes and staged experimental coverage

Define the workload
`w=(n,d,M,R,C,mu_policy,c,amplitude,P,hardware,threads,memory_budget,accuracy_tolerance,cache_policy)`.

- `n in {64,128,256,512,1024,16384,131072}`, `d in {1,...,6}`.
- `M in {1,100,1000,10000,100000}`, `R=1` or at least `3` independent series; four crossed `M/R` workload types.
- `C in {cv,gcv,bic,aicc,mle}`.
- `mu=0, "data", c` crossed with low/high observation amplitude and multiple generated seed blocks.
- Same S candidates for both `P=direct_s` and `P=mapped_lambda`; separate cold/new-series and warm/shared-cache regimes.
- Record package/BLAS versions, OS/CPU, single-thread **and** explicitly documented multi-thread experiments separately; do not use aggregate thread counts as evidence of realized parallel speedups.

The **full manifest** records planned/eligible/budget-skipped/memory-infeasible/unavailable/not-run/failed/successful status. Measurement is **adaptive and staged**, emphasizing known or predicted near-tie regions and all solvers with valid complete outputs. Explicitly do not attempt infeasible n=131072 dense matrices, nor promise all 100000-point grids will run on the university VM. Existing Experiment007 fit-only, Experiment008 complete-criterion, and Experiment009 frozen calibration must not be pooled as comparable timing observations.

## Theoretical and calibrated computational cost

For each algorithm `b`, criterion `C`, coordinate policy `P`, caching regime and hardware `h`, derive from the actual implementation a nonnegative cost decomposition:

```text
T_b(w,h) ~= T_setup_b(n,d,h)
         + T_map_{b,P}(n,d,M,R,h)
         + T_factor_and_diagnostics_b(n,d,M,R,C,h)
         + T_series_preparation_b(n,d,R,h)
         + T_scoring_b(n,d,M,R,C,h)
         + T_cache/memory_effect_b(w,h).
```

Known leading *operation-count* prototypes (not measured seconds):
- Naive dense inverse: about `O(M*n^3 + M*R*n^2)` if an inverse/diagnostics is genuinely shared across R; `O(M*R*n^3)` when recomputed; quadratic storage.
- Spectral SVD: `O(n^3 + R*n^2 + M*R*n^q_C)` with `q_C=1` for cached global scalar scores and up to 2 for ordinary CV leverage; dense quadratic storage.
- Proper banded Cholesky + selected inverse: `O(M*n*d^2 + M*R*n*d)` with shared candidate factors; `O(M*R*n*d^2)` if independent factors are rebuilt.
- Hybrids: **add** the method's factor/PCG cost AND an exact banded diagnostic cost; do not pretend sparse/iterative traces are free.
- PCG: explicit observed iterations `K(w)` multiply matrix-vector/preconditioner costs; there is no reliable deterministic general bound in terms of `n,d` alone that predicts actual runtime.
- S->lambda translation: separate iterative root-solving cost, potentially dominating the search for large M; allow efficient eigenvalue/trace or structure-based implementations but charge their setup and memory.

A pure Big-O winner cannot be identified at finite n without constants, numerical feasibility and implementation details. Fit calibration coefficients on **only training blocks**, with nonnegative cost coefficients / alternative justified parametric models and confidence intervals; assess predictions on held-out n, M, d, mu policies and new machine sessions. Use a real crossover holdout with at least two classes of observed winner; Experiment009's 61/61 and 8/8 one-class holdouts do **not** establish crossover prediction. Compare absolute timing prediction errors, paired winner accuracy and uncertainty in the decision surface. Report uncertainty for near-ties, not an invented universal threshold.

## Theoretical-minimum policy with empirical verification and fallback

Let `B` be the enumerated complete pipelines and `F(w)` the *independently justified feasible* subset. A method is admissible only when it supports criterion C and mean policy, is installed, satisfies peak-RAM limits, is expected to finish under the configured budget, and has suitable numerical certification for `(n,d,S,mu,amplitude)`. Never classify a numerical failure as a fast success.

```text
predict_and_rank(w):
    grid = canonical_S_grid(M)                  # user-facing S
    mapped = translate_once_if_requested(grid) # same candidates
    eligible = [b for b in B if complete_and_available(b,w)
                              and memory_budget_ok(b,w)
                              and certified_for_regime(b,w)]
    ranked = sorted(eligible, key=lambda b: calibrated_theoretical_T(b,w))
    if not ranked: return NO_CERTIFIED_METHOD
    for b in ranked:
        try:
            result = run_full_criterion(b, grid, mapped, w)
            independently_validate(result,b,w)
            archive_full_timing_and_diagnostics()
            return result, b, attempted_backends
        except (ConvergenceError, NumericalError, ResourceError) as exc:
            archive_failure(b, exc, w)
    return NO_CERTIFIED_METHOD
```

The **predicted** feasible minimum `b_hat=argmin_{b in F(w)} T_hat_b(w)` is a **hypothesis**. The **empirical oracle** `b_star=argmin_{b in verified_observed(w)} T_observed_b(w)` is computed only on held-out matched runs where every candidate is actually observed and numerically valid. Evaluate `regret=(T_observed_{b_hat}/T_observed_{b_star})-1`, median and distribution of speedups, top-k coverage, misranking frequency, fallback count/extra cost, and abstention rate. Do not treat `not run` or `unavailable` as observed slow methods; do not claim oracle completeness if methods were excluded from observation.

There is a statistical distinction between pre-execution availability (packages/RAM), accuracy established for a regime from independent tests, and post-run verification. Report all three; a runtime fallback should never silently relax its error tolerance.

## Measurement, outputs, tests and paper integration

1. **Repository-first:** new runnable source, tests, pinned environments, explicit input-provenance links to Experiments007–009, compressed long-form manifest, raw timings, failures, calibrations and plots under `paper/benchmarks/experiment010/`. Preserve immutable result branches; never overwrite prior measurements.
2. **University VM:** PCAG103A-08, Windows 11, non-admin. Use existing `C:\Users\175199\AppData\Local\miniconda3\envs\trendestimation` with `conda run --no-capture-output -n trendestimation python ...`; no setup-python/pip install/conda create in its Actions jobs. Respect agents' active work/branches.
3. **Numerical tests:** matched-grid score/selected-S parity, exact S=1 limit, fixed `c` and data-derived mu RHS, selected-inverse trace/leverage, independent high-precision high-d forward errors, PCG convergence and optional CHOLMOD availability, all five criterion semantics, fallback diagnostics. The BIC interpolation-boundary degeneracy remains an explicit limitation.
4. **Benchmark design:** independent seeds and paired timing blocks, randomized backend order, repetition and warm-up protocol, precision/status gates, memory limits and preregistered stop/time budgets. Report machine-specific mean/median/dispersion and confidence intervals without treating repeated grid points or timing repetitions as independent series.
5. **Publication:** extend the existing Elsevier two-column `paper/csda-computational-costs/` *only after* verifiable results. Organize: established smoothness S and Guerrero prior art; three mean policies; complete pipeline algorithms; theoretical cost-and-memory surfaces; implementation-aware calibrated model; empirical all-method comparison; feasible dispatch and fallback; error/regret/uncertainty; reproducibility/limitations. Prior art Weinert (2007) and Biessy (2026) must be acknowledged; do not claim invention of S or first structured fast GCV.

## Minimal staged next steps for an independent agent

- **Stage A — audit:** Inspect `README.md`, `AGENTS.md`, `AI_HANDOFF.md`, Experiment006–009 code/results, selected-inverse implementation, and both CSDA manuscript directories. Reconcile the latest main and concurrent PRs; no new source policy yet.
- **Stage B — exact baseline:** instrument all eligible method–criterion pathways on a small fixed `(n,d,M,R,mu)`, with identical S/lambda points and strictly validated scores, plus a timing breakdown. Ensure all ten methods are actually enumerated/executed or explicitly marked unavailable; Experiment008's bounded runner does not run all ten.
- **Stage C — theoretical model:** implement separate operation-count features and memory envelopes for each complete pipeline; fit machine-specific constants from **actual** recorded runs, not predicted data. Build `n,d,M,R,C,mu,hardware` frontier surfaces and uncertainty.
- **Stage D — targeted Windows runs:** prioritize empirical crossovers and high-order cases; include `mu=0`, `mu="data"`, `mu=c` and both coordinate policies. Independent numerical audits gate winners.
- **Stage E — fallback and heldout:** evaluate the ranked selector versus observed best feasible method, including second-choice paths and missing-dependency/memory scenarios.
- **Stage F — CSDA integration:** only publish figures and quantitative claims with archived raw CSV provenance, valid-pair denominators, reproducible source SHA and hardware details.

### Paper thesis and counter-thesis

**Thesis:** structural linear algebra and caching produce a computable, criterion-specific *theoretical* runtime ranking. **Counter-thesis:** numerical conditioning, unknown solver constants/iterations, memory, optional packages and benchmark noise can reverse that ranking. **Synthesis:** an empirical-calibrated **admissible computational frontier**, with verified fallback and reported regret, is a useful research object and potential library policy; it is not yet established by Experiments008/009 alone.

**Current conclusion:** Not yet implemented or proven. The objective of Experiment010 is to test it.
