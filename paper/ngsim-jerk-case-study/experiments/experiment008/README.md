# Paper C Experiment008 — physical PLS versus truncated-SVD and conventional jerk smoothers

**Status: COMPLETED on self-hosted PCAG103A-08, 2026-11-09.** [Successful Actions run #42717662044](https://github.com/heri-espino/trendestimation/actions/runs/42717662044). Source research commit **c219e1f264aaa306bfaa2ea0dd644fb48596380b**.

This is an **application-level** comparison, not a numerical-solvers benchmark. It was requested after the author clarified that Paper C should present third-order penalized least-squares (PLS) smoothing, its interpretable index S, known-truth simulations and real trajectories, compared against established physical jerk-estimation methods.

## Critical SVD distinction

An SVD factorization of the PLS normal equations computes **the same PLS estimator**, so comparing a full SVD with Cholesky is purely a numerical-implementation/timing exercise and belongs in the separate computational-statistics paper.

We instead benchmark a **different spectral regularizer**, the truncated SVD of the third-difference operator D3.

Let D3=U diag(sigma_j) V_positive.T, with **ascending** singular values so low roughness modes come first. Let V0 span the quadratic nullspace and q satisfy D3 q=mu 1. Then:

`PLS: q+V0 V0.T(y-q)+sum_j [1/(1+lambda sigma_j²)] v_j v_j.T(y-q)`.

`TSVD: q+V0 V0.T(y-q)+sum_{j<=r} v_j v_j.T(y-q)`.

Two spectral truncation policies:

1. **TSVD-GCV:** choose r over 0,...,n-4 using training-only position GCV, never future or true jerk;
2. **TSVD-matched-EDF:** set r=round(sum_j [1/(1+lambda sigma_j²)]), with the lambda selected previously by PLS on the same historical observations. This isolates **soft versus hard shrinkage at matched effective complexity**; it is not independently selected by GCV.

PLS and both TSVD policies use the **same historical global cubic OLS reference mu** already estimated in Experiment006. PLS lambda and mu are **read only** from the archived Experiment006 `plugin_global_ols_continuous` selection rows; no previous likelihood search is rerun.

External historical trend comparators, fitted on identical historical observations: natural cubic smoothing spline selected with SciPy's GCV criterion, and Savitzky–Golay window 21/degree 3. For future position we apply both the exact previous last-three-point d3 recurrence and the same local25 quadratic extrapolation to every fitted trend. Note that splines with their own quadratic Taylor continuation remain an **additional prior end-to-end forecast benchmark**, not the same continuation rule.

## Exact source archives and data independence

Synthetic: original Experiment005 [full PC08 simulation archive](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp005-pc08-42547250403-a1) and its confirm/trajectories.jsonl.gz; archived Experiment006 confirm/selections_rows.csv for the same **1,296 independent synthetic trials**, known clean positions, historical known finite jerk and 20 clean withheld future positions.

Real: original [Experiment004](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp004-pc08-42538556206-a1) official FHWA NGSIM source selection plus Experiment006 real/selections_rows.csv; exactly **200 recorded episodes**, 80 historical positions and future 5/10/20 frames. No independently observed true physical jerk or absolute sensor noise precision exists in NGSIM.

The source positions are SHA-256 checked against their original immutable manifests. No source trajectories are regenerated, the old PLS parameter-selection campaign is **not rerun**, no future labels are used to choose any smoother.

## Successfully completed data and results

| Study | Cases | Fitted method rows | Horizon/rule forecast rows |
| --- | ---: | ---: | ---: |
| Synthetic known-truth | **1,296** | **6,480** | **38,880** |
| Real NGSIM recorded position | **200** | **1,000** | **6,000** |

**Historical synthetic known finite third-difference jerk RMSE** (m/s³) over the same 1,296 cases:

| Historical smoother | RMSE |
| --- | ---: |
| PLS, global cubic OLS mu and continuous Gaussian profile ML | **2.441257** |
| TSVD, matched PLS effective degrees of freedom | **2.941621** |
| Savitzky–Golay, degree 3/window 21 | **36.829147** |
| Natural cubic smoothing spline, GCV | **60.913063** |
| TSVD, position-GCV-selected rank | **250.718104** |

This is evidence of a good **physical third-derivative reconstruction** under the tested simulated DGPs, not evidence of universal PLS superiority. A position-GCV rank can leave large noisy third differences even when historical/future position itself is acceptable.

**One-second clean synthetic position forecast** (m), **identical** last-25 quadratic continuation:

PLS 0.435296; TSVD matched 0.450206; TSVD-GCV 0.488903; spline GCV 0.461424; SG 0.482451. The baseline outcomes are not those of a spline's independently chosen Taylor boundary rule.

**One-second future recorded-position RMSE** (m), **identical** last-three-point d3 continuation on 200 NGSIM episodes:

PLS 0.514386; TSVD matched 0.511776; TSVD-GCV 0.533672; spline GCV 0.494562; SG 0.818773. A **separate spline GCV + quadratic Taylor** benchmark from earlier Experiment004/006 obtained 0.348043 m, outperforming all five common-rule variants. The real data do **not** support claiming PLS decisively outperforms TSVD or spline forecasts.

Full 0.5/1/2-second method/rule rows, true-jerk outcomes and summaries are in the `synthetic/` and `real/` directories of the complete run, never replaced by rounded manuscript tables.

## Persistent VM and repository storage

**Complete, non-overwriting PC08 directory**:

```text
C:\Users\175199\Documents\TrendEstimation-PaperC\experiment008\run-42717662044-a1\
  synthetic\
    fitted_rows.csv
    forecast_rows.csv
    summary.csv
    RESULTS.md
    run_manifest.json
  real\
    fitted_rows.csv
    forecast_rows.csv
    summary.csv
    RESULTS.md
    run_manifest.json
  metadata\
    source_commit.txt
    source_directories.txt
    requirements-resolved.txt
    file_inventory.json
  logs\
    preflight.log
    synthetic.log
    real.log
```

**Permanent independent Git results archive:** [results/paper-c-exp008-pc08-42717662044-a1](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp008-pc08-42717662044-a1/paper/ngsim-jerk-case-study/experiments/experiment008/runs/pc08-42717662044-a1). The recursively inventoried 16 files (7,230,292 bytes, inventory excluded) include each file's VM-relative path, size and SHA-256. The original generated source trajectories and NGSIM raw provider pages remain in their original, separately referenced immutable Experiment005/004 source archives.

**Code:** [run.py](run.py), [tests](../../../../tests/test_paper_c_experiment008.py) and [.github/workflows/paper-c-experiment008-pc08.yml](../../../../.github/workflows/paper-c-experiment008-pc08.yml).

## New manuscript placement

Paper C's intended structure is (i) PLS physical model and S interpretation, (ii) two simulation results: Experiment007 relative-noise calibration plus Experiment005/006/008 known jerk benchmark, and (iii) real 200-episode NGSIM forecasting. The computational backend comparison (SVD vs Cholesky vs banded solves) is retained in the repository but **removed from the main paper**. The "SVD" in the current manuscript is a hard-filtering physical estimator. Author review remains required for submission, all coauthor attribution and any final paper merge.
