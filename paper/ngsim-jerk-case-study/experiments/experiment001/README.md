# Paper C — experiment001: three-point d=3 recurrence versus local-25 continuation

**Status:** Completed retrospective pilot on the original NGSIM source, using 150 archived d=3 PLS parameter choices. This is not the full simulation/ablation.

## Method and reproducibility

For a historical fitted trend z and mean third difference mu, the classical three-point forecast extension uses:

\[
\widehat z_N(h)=z_N+h(z_N-z_{N-1})+\binom{h+1}{2}(z_N-2z_{N-1}+z_{N-2})+\binom{h+2}{3}\mu.
\]

This formula is the algebraic d=3 extension of Guerrero (2007)'s reported d=1 and d=2 forecast recurrences. Guerrero did not explicitly present this third-order formula.

The competing local-25 method fits a quadratic to the final 25 fitted trend values after subtracting a known cubic particular solution. The archived **same PLS fitted trend and selected smoothness** feed both methods. This is an experiment about forecast extrapolators, not about whether PLS itself has been invented.

- NGSIM US-101 positions at 10 Hz; five track segments, **two unique vehicle IDs**, 3 chronological forecast origins per segment.
- 80-point training window; 0.5, 1 and 2-second future position horizons.
- Zero reference or the archived training-derived mean third difference, with CV/GCV/AICc/BIC/ML.
- Exactly 900 paired forecast rows and 60 summary rows saved under this experiment.
- Maximum absolute error reconstructing the original local25 mean-squared error: **4.37e-12** in an independent numerical calculation.

## Results: GCV-selected future position RMSE (m)

| Horizon | local25, zero mu | local25, sample mu | recurrence, zero mu | recurrence, sample mu |
| --- | ---: | ---: | ---: | ---: |
| 0.5 seconds | 0.294535 | 0.244122 | **0.074519** | 0.076879 |
| 1 second | 0.583065 | 0.475185 | **0.295769** | 0.311304 |
| 2 seconds | 1.392788 | **1.120968** | 1.299841 | 1.400591 |

At 1 second the recurrence is better for both reference policies, but **zero mu slightly outperforms sample-derived mu with the recurrence**. This reverses the direction seen under the local25 forecast rule. At 2 seconds, the local25 sample-mean forecast is better. There is **no universal winner**.

## Reproduce from repository root

    python paper/ngsim-jerk-case-study/experiments/experiment001/run.py --verify
    python -m pytest tests/test_paper_c_experiment001.py -q

Verification recomputes the saved 900 rows without overwriting the original paper data or outcomes. To regenerate just the experiment-specific output, run without the --verify flag.

## Handoff / next steps

The results are **descriptive** (only two distinct vehicle IDs, overlapping forecast windows, no independently observed true jerk). They do not demonstrate the first use of third-order penalized smoothing or calibrated future-position prediction.

Next run the focused [smoothing-spline and physically motivated benchmark](../experiment002/README.md), then predeclared independent-vehicle replication and known-truth jerk simulation. Do not tune alternative extrapolators on this retrospective evaluation set and then claim independent superiority.
