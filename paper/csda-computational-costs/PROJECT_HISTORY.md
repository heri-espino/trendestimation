# Computational research history for the completed paper

This index is a **reproducibility record**, not a new experiment or a new set of timing observations. It complements OBSERVED_RESULTS_SNAPSHOT.md and the paper's SOURCE_AUDIT.md. First read AGENTS.md, AI_HANDOFF.md and the existing benchmark READMEs before doing any additional work.

| Source/stage | What was done | What was established | What was NOT established |
|---|---|---|---|
| Original Windows full-S studies | n=24 and 48 historical analyses; fixed reference means 0/0.15, seven backends and criterion-search policies, 80,640 timing records; TeX-native AwesomeFigures | Matched S and translated-lambda candidate equivalence and approximately 2.668-fold (d=3) / 2.823-fold (d=2) amortized five-criterion mapping reuse in specified workflows | Any d=6 or sample-derived-mean result in that historical corpus; cross-machine universal speedups |
| Experiment005 | Banded LU, sparse SuperLU, optional CHOLMOD, and FFT/DST/Jacobi PCG integrated as **fit-only** methods; convergence and cache contracts | Multiple explicit PLS fit backends beyond SVD/Cholesky exist; sparse LU is not CHOLMOD | Complete criterion runtime of these fit-only methods |
| Experiment006 | Exact banded selected-inverse criterion diagnostics and six complete-criterion hybrid pipelines; independent 85-digit high-order numerical audit | At n=128,d=5/6,mu=0.15, reference forward-error passes: spectral 28/28, banded Cholesky 16/28, sparse LU 22/28, FFT-PCG 14/28 accepted and 14 nonconverged | Universal high-d backend reliability or timings at every sample size |
| Experiment007 | Sample-derived mean mu=data with explicit fixed-zero controls, several fit-only backends, six difference orders, series-reuse workloads | Winner could vary with n, d, amplitude, and requested output | Universal threshold d<=4 Cholesky / d>=5 SVD; full-criterion generalization |
| Experiment008 | Grid of one versus many S values and one versus many series, CV/GCV/BIC/AICc/MLE, two smoothness-coordinate policies, resource gating | 252,000 original planned combinations, 111,600 resource-eligible by the original manifest; 4,246 valid hosted timing records in four batches; 17 Windows pilot plus 48 broad timing slices archived; no fabricated times for infeasible methods. PR #98 merged | That planned or eligible cells were all actually measured; n>=16384 dense inversion feasibility |
| Experiment009 | Separate fitted-curve versus complete-criterion SVD/banded-Cholesky cost models and machine-specific calibration | Candidate count, series count, criterion and reuse alter the theoretical crossover; pilot one-class holdouts did not validate a genuine boundary. PR #99 merged | A universal n,d cutoff or validated ten-method dispatch policy |
| Experiment010 | All ten named complete-criterion policies; mu=0 versus mu=data versus fixed mu=0.15; bounded resumable Windows smoke/pilot and n256/n512 frontier; MLE normalization correction | 450 corrected-source method–case attempts; 5,570 status=ok timing records; 5,480 criterion-score-only matches, 18 mismatches, 72 no-reference records, 1,102 partial/failed; one S versus 100 S measured winner reversal at n=256,d=1 under all three mean policies | Completed 50,400-case factorial, complete high-precision criterion certification, held-out all-backend regret, or automatic best-feasible selector |

## Source and archive locations

- Manuscript: paper/csda-computational-costs/main.tex, sections/experiment010_observed.tex, and built main.pdf.
- Historical figures and data audit: paper/csda-computational-costs/SOURCE_AUDIT.md.
- Benchmark sources: paper/benchmarks/experiment005 through experiment010.
- Independent high-order reference: results/experiment006-highd-41439239921.
- Corrected Experiment010 first Windows run: results/experiment010-41587467639-a1-smoke and results/experiment010-41587467639-a1-pilot.
- Corrected Experiment010 continuing pilot: results/experiment010-41587723422-a1-pilot-offset60, offset120, offset180, offset240.
- n256/n512 targeted comparisons: results/experiment010-41642508020-a1-frontier-offset0 and offset60.
- Pre-correction MLE discrepancy: results/experiment010-41586066141-a1-pilot, held separate from all corrected-source estimates.
- Original cost-model theory: paper/benchmarks/experiment009 and notes/experiment009_crossover_findings.md.
- Exact per-run counts, statuses and links: OBSERVED_RESULTS_SNAPSHOT.md.
- Manuscript source branch: paper/observed-computational-study, based on draft Experiment010 PR #100; manuscript review PR #102.

## Interpretation

Every *timing* claim must specify cold/warm status, S-grid, sample length, difference order, criterion, mean policy, series count, source SHA, machine, and numerical-validity gates. Inner-loop stopwatch rows are not independent trial replicates. No unavailable method receives a synthetic value. A criterion-score parity pass does not establish an 85-digit accurate fitted trend. Keep the exact S=1 endpoint and conditional plug-in mu semantic distinctions.

The paper is intentionally finished **as an evidence-limited research report**, not as an affirmative claim of an optimal dispatcher or complete planned factorial. The next research campaign should be separately versioned, with independent numerical certification and cross-regime held-out frontier selection. Do not overwrite or backfill the current record, and do not merge paper PRs without explicit authorization.
