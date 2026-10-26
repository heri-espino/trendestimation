Complete smoothness domain: all solvers and criteria
=====================================================

This experiment searches the **entire normalized smoothness domain**,
including both exact limits and the finite values closest to one.
The preceding finite grid experiments deliberately omitted extreme
conditioning. Here that conditioning is itself part of the study.

The common 17-point grid
------------------------

.. math::

   S \in \{0,0.1,0.2,\ldots,0.9,1\}
   \cup\{0.95,0.99,0.999,0.9999,0.999999,0.999999999999\}.

Each interior smoothness target is inverted **once** to obtain the
same penalty for every backend. The exact limits are not approximated
by a huge/small float.

- **S=0, lambda=0:** trend equals observations; conventional
  interpolation-only CV and GCV scores are undefined.
- **S=1, lambda=infinity:** for d>=1 the limiting trend is a
  polynomial of degree d-1 after applying the fixed difference-mean
  adjustment. For d=0 it is the constant vector mu.
  Exact endpoint scores come from analytical limits, not an
  infinite Cholesky factorization.
- **Gaussian MLE at d=0:** not implemented for this stochastic model;
  recorded as *not applicable*. Other four criteria are tested for d=0.

Seven numerical solvers, five statistical criteria
--------------------------------------------------

The seven backends are dense fresh, dense cached, general banded,
dense Cholesky, banded Cholesky, symmetric eigendecomposition (eigh),
and SVD.

The five statistical selection rules are CV, GCV, AICc, BIC and
conditional Gaussian profiled marginal MLE.

All valid combinations test both fixed mu=0 and mu=0.15, and
all difference orders **d=0,1,2,3,4,5**. Each backend scores the
same observations and identical candidate penalties. The separate
coordinate-timing experiment tests repeated S inversion versus
reusing an already mapped lambda grid; these are distinct questions.

A numerical instability or factorization failure at the largest
finite lambda is **not** evidence of a smaller statistical optimum.
Only methods whose entire finite interior grid agrees numerically
can be ranked as valid whole-grid timing winners. Mathematically
undefined criterion values are recorded separately.

Full-grid computation time
--------------------------

For each criterion the following charts show total time, including
backend preparation and finite interior scoring. An absent solver
point means it did **not** complete the entire grid accurately.

.. image:: ../paper/figures/full_s_time_cv.svg
   :alt: Seven numerical solver timings for classical CV across difference orders 0 to 5
   :width: 100%

.. image:: ../paper/figures/full_s_time_gcv.svg
   :alt: Seven numerical solver timings for GCV across difference orders 0 to 5
   :width: 100%

.. image:: ../paper/figures/full_s_time_aicc.svg
   :alt: Seven numerical solver timings for corrected AIC across difference orders 0 to 5
   :width: 100%

.. image:: ../paper/figures/full_s_time_bic.svg
   :alt: Seven numerical solver timings for BIC across difference orders 0 to 5
   :width: 100%

.. image:: ../paper/figures/full_s_time_mle.svg
   :alt: Seven numerical solver timings for profiled Gaussian MLE across difference orders 1 to 5
   :width: 100%

Stability across the near-one tail
----------------------------------

Each cell counts verified finite interior candidates, out of fifteen.
An unstable score may be due to an ill-conditioned finite penalty
matrix, cancellation or the particular criterion's singularity.

.. image:: ../paper/figures/full_s_validity_gcv.svg
   :alt: Heatmap of finite-S candidate agreement for GCV by difference order and seven numerical backends
   :width: 100%

.. image:: ../paper/figures/full_s_validity_mle.svg
   :alt: Heatmap of finite-S candidate agreement for marginal Gaussian MLE by difference order and seven numerical backends
   :width: 100%

Selection results for both reference means
------------------------------------------

These are the criterion-optimal candidate smoothness levels on the
common grid, computed through the validated SVD implementation.
**Criterion scores should not be compared across criterion types.**

.. image:: ../paper/figures/full_s_selected_mu0.svg
   :alt: S selected by CV GCV AICc BIC and MLE over d=0 to 5 for mu=0
   :width: 100%

.. image:: ../paper/figures/full_s_selected_mu015.svg
   :alt: S selected by CV GCV AICc BIC and MLE over d=0 to 5 for mu=0.15
   :width: 100%

The high-smoothness penalty tail
--------------------------------

.. image:: ../paper/figures/full_s_lambda_tail.svg
   :alt: Mapped logarithmic lambda for the same near-one S targets across all six difference orders
   :width: 100%

The chart excludes lambda=0 and lambda=infinity only because neither
can be represented on a finite logarithmic axis. **Both were scored.**

Experiment provenance and reproduction
--------------------------------------

The full measurement matrix and original failure states are archived:

- ``paper/benchmarks/full_s_reference/candidate_scores_and_times.csv``
- ``paper/benchmarks/full_s_reference/full_grid_summary.csv``
- ``paper/benchmarks/full_s_reference/s_lambda_grid.csv``
- ``paper/benchmarks/full_s_reference/environment.json``

A reference run uses n=24, one independent seeded synthetic series
and two timing repetitions on a GitHub-hosted Linux machine.
These measurements do **not** use the author's Windows full experiment
or establish a universally fastest implementation.

Repeat on Windows PowerShell (new output directory):

.. code-block:: powershell

   conda activate trendestimation
   python paper/benchmarks/full_s_backend_criteria.py --preset full --repeats 5
   python paper/figures/render_full_s_factorial.py

The full preset additionally studies n=48 and a second seed.
The experiment is classical **in-sample** selection, not forecast
cross-validation or out-of-sample prediction.

See :doc:`mle_coordinate_figures` for public-selection
search-space timing with native S versus reusable lambda, and
:doc:`grid_reuse_selection` for the separate GCV repeated-series study.



Single evaluation versus complete and repeated searches
--------------------------------------------------------

The extension to Experiment002 measures three distinct workloads on
the **same complete 17-point normalized-S grid**: one evaluation at
S=0.5, a whole grid search on one series, and the same grid visited
on multiple independently sampled series. Each workload includes
seven numerical backends, all five supported criteria, both fixed
means, and difference orders d=0..5 (conditional MLE remains N/A at d=0).

.. image:: ../paper/figures/full_s_single_grid_repeated.svg
   :alt: Seven backend runtimes for one GCV score, one full smoothness grid and three repeated complete grid searches
   :width: 100%

Cold versus shared preprocessing is explicitly recorded for repeated
series. Shared preparation is potentially beneficial for spectral
factorizations and for any d-specific backend state; it does **not**
mean a Cholesky factor at one lambda works at a different penalty.

.. image:: ../paper/figures/full_s_search_reuse_speedup.svg
   :alt: Ratios of cold to reused backend preparation over three repeated full-grid GCV searches
   :width: 100%

Three ways to search a finite full-domain grid
----------------------------------------------

The grid budget is 17, with exact S=0 and S=1 boundaries in all
three policies:

- **Native S grid:** invert S to lambda each time a search scores
  its candidates, including repeated searches.
- **Convert S to lambda once:** precompute and reuse the mapped
  17 penalties. The standalone timing includes one initial
  mapping, while the backend-only timing excludes it.
- **Direct lambda grid:** sample 17 log-spaced penalty candidates
  with the same two exact endpoints and identical finite
  *outer* endpoints. Its intermediate candidates differ from
  the S-based grids.

The first two paths are statistically identical at the same
candidate points; the third policy can choose a different
discrete minimum because its interior points differ.

.. image:: ../paper/figures/full_s_grid_coordinate_times.svg
   :alt: Measured five-criterion runtime for native S, once-translated S to lambda, and direct lambda grids
   :width: 100%

Continuous optimization is a separate problem
---------------------------------------------

We also measure bounded scalar optimization on the two equivalent
continuous coordinates, minimizing the criterion in S or in
log-lambda, with exact endpoints tested analytically.

.. image:: ../paper/figures/full_s_continuous_coordinate_times.svg
   :alt: Measured runtime of local bounded scalar search on S versus log lambda for the five criteria
   :width: 100%

A bounded scalar search generally evaluates **different candidates**
from a 17-point grid, uses a variable number of function calls,
and can converge to a local, not global, minimum. It therefore
cannot be treated as identical to the grid search.

.. image:: ../paper/figures/full_s_coordinate_selected_s.svg
   :alt: Smoothness selected by five criteria under equal grids, independent log lambda grid and local continuous optimizers
   :width: 100%

For all plots, unavailable Gaussian MLE at d=0 is recorded as
not applicable and numerically unstable near-one solutions do
not qualify as valid whole-grid winners. The raw data preserves
the full error/status record and the benchmark code performs
reference-score verification outside its measured timing blocks.

Source and timing conventions
-----------------------------

- `paper/benchmarks/full_s_search_reference/search_mode_timings.csv`:
  method, criterion, difference order, mean, workload R,
  policy, cold/shared preparation, runtime, selected smoothness,
  success flags and function-evaluation counts
- `paper/benchmarks/full_s_search_reference/search_grid_preparation.csv`:
  independently measured S-to-lambda inversion cost
- `paper/benchmarks/full_s_search_reference/environment.json`:
  reproducible host/BLAS/seed/runtime metadata

The single and premapped full-grid standalone times explicitly count
the required S-to-lambda inversion once. That cost must be **shared
once**, not 35 times, when using a common penalty grid for all
five criteria and seven solvers. If lambda candidates are already
known and supplied directly, their construction is not charged
to backend evaluation time. The two local continuous optimizers
are not certified global solvers.

Run the full benchmark separately on your Windows VM:

.. code-block:: powershell

   conda activate trendestimation
   python paper/benchmarks/full_s_search_modes.py --preset full --repeats 7

The Windows CSVs default to
`paper/benchmarks/results/full_s_search_modes/`.
Do not mix them with the archived Linux-hosted reference data.
