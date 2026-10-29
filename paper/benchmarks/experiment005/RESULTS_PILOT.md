# Experiment005 — first paired pilot findings (not yet a publication result)

## What was done

Joint numerical accuracy, latent-trend RMSE and timing were generated
from one immutable set of observations per condition on the same
single-thread GitHub-hosted Linux CPU. These are NOT reconstructed
by joining separate Experiment004 and Windows timing datasets.

Source run: paper/benchmarks/experiment005/runs/quick-hosted-40967124055/
Input commit: 7e5bf07f7f3f40a0f4f5e867dbf7656ebbbdd929.
Workflow: GitHub Actions run 40967124055 (paired-quick job).
Time and machine provenance: environment details in summary.json.
Reference: independent 85-digit banded dual at finite lambda;
independent 85-digit constrained polynomial QR at S=1;
exact y at S=0. All independent reference computation EXCLUDED
from recorded solver timing.

Design: n={32,64}, d={1,3,5,6}, shapes={smooth,kink},
noise={iid,AR(1)}, 2 independent seeds per design,
mu={0, mean(D_d y)}, 110 smoothness points from S=0 to S=1,
five criteria, three end-to-end backends, two matched S policies.
Five timing repetitions for each frozen fit.
There are 4,608 individual fit measurements and 3,840
selection-pipeline measurements.

## What we observed

**Independent high-precision frozen-S fits** (relative L2 tolerance 1e-5):
4,262/4,608 passed, 282 were numerically inaccurate and 64 failed.
All 512 shift-free SVD frozen-S records passed. The 512 dual-SVD
and scaled augmented QR records also passed. Primal banded Cholesky
is increasingly vulnerable at high d and S; its largest recorded
relative error at d=6 was about 681, so it cannot be recommended
solely because it has low fit-only wall time.

**Complete user-facing S selection:** 2,550/3,840 pipelines
satisfied the full-grid score parity and high-precision selected-fit
validation threshold. All 1,280 SVD selection records passed.
Banded Cholesky passed 222/320 cases at d=1 but 0/960
at d=3,5,6, under the stringent full-grid numerical-validity rule.
The Gram-eigen backend passed all 640 cases at d=1,3, but
228/320 at d=5 and 180/320 at d=6.

**Matched coordinate caching** (SVD only, scores evaluated at
identical penalty candidates): median native-S versus cached-S
selection-only time ratios across valid matched pairs were
6.98 (d=1), 7.14 (d=3), 7.07 (d=5), and 7.04 (d=6).
When amortization is impossible and all recorded preparatory
phases are charged to one search, the *phase-summed* cold
native/cached ratios are only about 1.02, not seven.
Cold totals are NOT directly timed continuous whole-program spans.
Thus the contribution is an interpretable S interface with
repeatedly reusable pretransformation, NOT a universal 7x
one-off end-to-end algorithm.

**Latent-trend recovery:** All methods were evaluated on
matched data against known truth; criterion RMSE differences
reflect a mixture of selection and simulation effects and
cannot be generalized from two seeds. Restricted BIC at
S>=0.10 often selects the lower boundary, consistent with
the previously documented limitation of its unrestricted form.
These are IN-SAMPLE historical-trend RMSE values, not forecast RMSE.

## Scientific limits

- TWO independent seeds per condition are insufficient for reliable
  bootstrap inference or universal superiority claims.
- Small n={32,64}; not a scaling or asymptotic validation.
- CI timing host is not PCAG103A-08; do not mix its raw times
  with Windows results from the earlier manuscripts.
- High-S numerical reference uses frozen float64 lambda and mu,
  independently solved with mpmath; errors do not measure the
  finite precision of the S->lambda inversion itself.
- Classical CV conditions on the empirical plug-in mu;
  this is not leave-one-out re-estimation of mu.
- Score agreement against library SVD is double-precision
  cross-backend parity, not a separate MP score certificate.
- Fit-only speed and complete criterion-grid speed differ.
- The preliminary experimental figures show valid and invalid
  methods, but the final journal version must use a matched,
  prespecified accuracy threshold and independent seed-level CIs.
- Caching ratios must be separated into cold, warm and
  amortized repeated-series workloads.

## Next actions before a combined CSDA manuscript

1. Run the full 10-seed preset on the user's Windows runner after
   inspecting platform/driver details and available runtime.
2. Verify selected-difference-mean policies and full-grid score
   precision at problematic d=5,6 nodes independently, ideally with
   high-precision score truth at a sentinel subset.
3. Test at longer series lengths and distinguish setup cost
   from actual repeated-series end-to-end wall time.
4. Compute paired confidence intervals, failure rates, and
   eligible-only Pareto fronts on saved raw data, not across hosts.
5. Develop a single accuracy-versus-time CSDA paper using only
   scientifically admissible and reproducible claims.
