# NGSIM real-vehicle jerk and trend forecasting case study

## Next study: controlled known-jerk simulation (Experiment005)

The author authorized a separate
[known-jerk simulation](experiments/experiment005/README.md)
after the successful, strictly observational Experiment004.
The [frozen design](experiments/experiment005/config.json)
tests six analytic jerk regimes, GCV/profile ML with five
`mu` references, two forecast continuations and
spline/SG baselines under three noise structures and
three error levels. There are 96 pilot and 1,296
disjoint-seed confirmation trajectories on the designated
PCAG103A-08 runner, with full clean/noisy series and
run outputs saved on the VM and immutable Git branch.
The synthetic-only oracle reference is a diagnostic
upper bound, not a valid FHWA forecasting procedure.
Compare *true discrete jerk error* and clean-future-position
forecast error. **The next manuscript claims must be
based on actual successful runs, not this planned grid.**
Existing real NGSIM data and conclusions remain separate.


## Completed expanded real NGSIM Experiment004 (2026-11-08)

**Result and exact VM file record:** [Experiment004 run ledger](experiments/experiment004/RUN_LEDGER.md).
The [PCAG103A-08 workflow #42538556206](https://github.com/heri-espino/trendestimation/actions/runs/42538556206)
successfully downloaded 400,000 real FHWA source position rows in
20 auditable API pages, selected **200 contiguous episodes** (100 per
site), and computed **6,600 valid forecast errors and 800 PLS
GCV/profile-ML selections**. All **38 generated VM files** (about
34.2 MB) are recorded in SHA-256 inventory under the persistent
VM folder `Documents\TrendEstimation-PaperC\experiment004\run-42538556206-a1`;
the result branch contains complete scored rows and metadata while
the raw page bytes remain on the VM. The NGSIM paper compiled too.

The real-data study shows **GCV cubic smoothing splines, with
quadratic Taylor continuation, have lower pooled RMSE at 0.5,
1 and 2 seconds** than the tested PLS last3/local25 policies on
this expanded convenience sample. The profiled Gaussian ML selector
is available and shows modest changes versus GCV; a nonzero mu is
not uniformly favorable. These outcomes challenge the pilot's
apparent general PLS advantage, and validate the need to report
negative or horizon-dependent findings. Only **five coarse recording
session proxies** appear across the 200 episodes; nominal bootstrap
inference assuming independent episodes is exploratory, not a
population-level significance result. True physical jerk is not
independently observed. The original manuscript's earlier pilot
results remain intact, not silently replaced.


## New decision: expanded **real-only** GCV versus ML study

[Experiment004](experiments/experiment004/README.md) implements
an expanded, auditable FHWA US-101/I-80 download and selection of
recorded trajectories, then compares the established d=3 PLS
smoother using **GCV or the library's Gaussian profiled marginal
likelihood (`mle`)**, for zero/training-mean mu and last3/local25
continuations. Baselines are GCV natural cubic splines,
Savitzky--Golay and local quadratic extrapolation. The author
explicitly prioritized **real positions over simulations**. Results
use paired episode-level, site-stratified bootstrap intervals
against recorded future position, not independently known physical
jerk.

**External raw/complete results** are kept on PCAG103A-08 outside
the checkout: see experiment004 for the complete permanent VM
directory tree, hashes, file inventory, Git results branch and
PowerShell reproduction commands. The workflow must succeed before
new sample sizes, method rankings or numerical claims are reported.
Existing pilot and manuscripts are untouched by the source-code-only
experiment004 implementation.


## New recurrence and spline benchmark evidence (2026-11-08)

The first three **sequential, source-controlled Paper C experiments** now
compare the (d=3) PLS three-point continuation, the original 25-point
continuation, smoothing splines, Savitzky--Golay and local polynomial
forecasts on identical chronological recorded-position holdouts:

- [Experiment001: Guerrero-inspired d=3 recurrence](experiments/experiment001/README.md):
  900 matched forecast records; preserves original Paper C data and results.
- [Experiment002: conventional spline/SG/polynomial comparators](experiments/experiment002/README.md):
  315 raw rows, 21 summaries; [PC08 success #42521326853](https://github.com/heri-espino/trendestimation/actions/runs/42521326853).
- [Experiment003: GCV-selected natural cubic spline](experiments/experiment003/README.md):
  180 rows, 12 summaries; [PC08 success #42521725044](https://github.com/heri-espino/trendestimation/actions/runs/42521725044).
  Primary comparison table: [RESULTS.md](experiments/experiment003/results/RESULTS.md).
- [Recompiled experimental manuscript](https://github.com/heri-espino/trendestimation/actions/runs/42522124213)
  using PCAG103A-08; the PDF and build manifest are preserved in the
  separate branch `results/paper-c-pdf-pc08-42522124213-a1`.
- [Research PR #121](https://github.com/heri-espino/trendestimation/pull/121)
  contains all code, reports, raw results and revised TeX. Remains subject to
  author/coauthor review before a merge or submission.

**New scientific finding:** GCV-selected PLS with (d=3,mu=0) and the
three-point recurrence performs best at 0.5,s (RMSE 0.074519,m), is
nearly tied with a GCV-selected cubic smoothing spline at 1,s
(0.295769 vs 0.295081,m), and is outperformed by the spline at 2,s
(1.299841 vs 0.808529,m). The effect of nonzero (mu) depends strongly
on the chosen extrapolator. These are **descriptive errors against future
camera positions, not measured true jerk**.

**Crucial sampling qualification:** The five saved track segments belong
to **only two distinct vehicle IDs**, and the 15 forecasting origins are
correlated. They do not support independent vehicle-level inference.
A new known-jerk simulation and substantially more independent vehicles
are needed before a publishable claim of physical jerk accuracy or
general forecasting superiority. No global first-use assertion is verified.
The source code represents a new documented use of this repository's own
Python library; it does not establish the first use of (d=3) PLS itself.


## Extrapolation and reference-jerk research handoff (2026-11-05)

**Start here for new Paper C agents:** [EXTRAPOLATION_RESEARCH_HANDOFF.md](notes/EXTRAPOLATION_RESEARCH_HANDOFF.md) documents the precise d=3, nonzero-$\mu$ forecasting hypothesis, what the existing `continuation()` actually implements, and why a first-use claim is unverified. [EXTRAPOLATION_DECOMPOSITION.md](notes/EXTRAPOLATION_DECOMPOSITION.md) derives the exact **fit-vs-continuation** attribution at fixed smoothness; [MU_POLICY_CATALOG.md](notes/MU_POLICY_CATALOG.md) registers proposed alternative training-only $\mu$ estimators; [EXTRAPOLATION_ABLATION_PLAN.md](notes/EXTRAPOLATION_ABLATION_PLAN.md) defines a future sequential experiment, explicitly **not yet run**. Biessy (2025/2026) already develops Whittaker–Henderson extrapolation: [source note](notes/papers/biessy_2026_extrapolation.md).

The current NGSIM experiment has **only two** $\mu$ policies (`zero` and `sample`), 5 recorded vehicles, and no true jerk measurements. No new policies, empirical experiments, forecast results, or manuscript
figures were created. One **deterministic algebra regression test** in
`tests/test_reference_jerk_extrapolation.py` checks the existing
continuation and the proposed two-effect decomposition.

## Literature review and annotated notes (2026-11-05)

The source-grounded, **Markdown-first** [literature review index](notes/README.md)
links six annotated prior-work groups, a [method comparison](notes/LITERATURE_REVIEW.md),
[mathematical deductions](notes/MATHEMATICAL_NOTES.md), the
[original-PDF/source inventory](notes/SOURCE_INVENTORY.md), and a
[manuscript/experiment plan](notes/MANUSCRIPT_PLAN.md).
The earlier [targeted novelty audit](NOVELTY_AUDIT.md) is also preserved.

**Main warning:** Guerrero-style nonzero-mean PLS is established mathematics.
Fan et al. (2024) already study NGSIM, jerk-related third-order constraints
and physically bounded quadratic programming. The current five-vehicle
pilot estimates **held-out position**, not observed true jerk; no
first-in-literature, physical superiority or independent vehicle-level
inference is established. The training reference `mean(D3*y)` depends
algebraically on endpoint second differences. These notes do **not**
change the archived data, manuscript, figures, or existing pilot outcomes.


Separate third manuscript in paper/ngsim-jerk-case-study.

## Public real measurements

FHWA / US Department of Transportation NGSIM US-101, DOI
10.21949/1504477. Official source:
https://data.transportation.gov/d/8ect-6jqj

The official dataset labels the license CC BY-SA 3.0. Its 10-Hz
camera-derived raw longitudinal positions are preserved, with exact
feet-to-meters conversion, original times, identifiers and a SHA256
record. See data/provenance.json and fetch_ngsim.py for the original
query, deterministic track selection and audit rules. Five real tracks
are recorded, never simulated, ranked or fabricated.

## Design

80 points per training window; 3 chronological origins per track;
3 future horizons (0.5, 1, 2 seconds). Orders d=1,2,3,4 and
five selectors (CV, GCV, AICc, restricted BIC and marginal Gaussian
ML) on a common full S-grid in [0,1]. Mean of differences is
fixed zero or a training-only observed-difference plug-in.
Plug-in CV is conditional, not exact leave-one-out refitting.

The PLS estimator does NOT natively forecast. The application
explicitly appends a local degree-(d-1) polynomial extension of
the last 25 fitted observations, with the particular solution
mu * binomial(t,d) added for nonzero third differences.
That is a heuristic, not a state-space or predictive distribution.

The third difference of a position series approximates jerk times
the cube of the sampling interval. No independently measured jerk
ground truth exists for these traces.

Three physical prediction baselines are evaluated on the same
future observed positions: constant velocity, constant acceleration,
and Savitzky-Golay smoothing plus velocity extension.
Seven fit-only numerical backends at d=3, S=0.90 provide separate
runtime and numerical-discrepancy diagnostics.

## Reproduce on Windows PowerShell

From the repository root:

    conda activate trendestimation
    python -m pip install -e .
    python -m pip install -r paper/requirements.txt
    python paper/ngsim-jerk-case-study/run_case.py
    Copy-Item paper/els-cas-templates/cas-dc.cls,paper/els-cas-templates/cas-common.sty,paper/els-cas-templates/cas-model2-names.bst -Destination paper/ngsim-jerk-case-study
    python paper/ngsim-jerk-case-study/render_paper.py
    Push-Location paper/ngsim-jerk-case-study
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
    Pop-Location
    Start-Process "./paper/ngsim-jerk-case-study/main.pdf"

To redownload a possible newer source revision, run fetch_ngsim.py
before the study and audit the new hash; do not silently overwrite
the frozen dataset used for this paper.

The GitHub Actions analysis and paper workflows preserve all raw
data subsets, selection rows, forecast holdouts, plots, editable PGF
sources and the compiled two-column Elsevier CAS manuscript.
Results are illustrative, not a physical safety prediction.
