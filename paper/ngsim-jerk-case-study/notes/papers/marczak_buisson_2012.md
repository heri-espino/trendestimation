# Marczak & Buisson (2012) — NGSIM I-spline filtering and jerk diagnostics

**Citation:** Florian Marczak and Christine Buisson, *New Filtering Method for Trajectory Measurement Errors and Its Comparison with Existing Methods*, *Transportation Research Record* 2315:35–46 (2012), [DOI 10.3141/2315-04](https://doi.org/10.3141/2315-04).

**Inspected primary source:** User-supplied 21-page TRB 2012 annual meeting draft (not the final publisher layout). The page numbers below refer to that draft.

## Problem and method

The authors seek to reduce errors in vehicle position, speed and acceleration used in car-following calibration and validation. They analyze **NGSIM I-80**, specifically the 5:00–5:15 p.m. 2005 segment, and compare several filters. Their proposed smoother represents positions with **I-splines**—piecewise polynomial functions using nonnegative/monotone spline bases—with knots selected by two strategies:

- **Threshold strategy:** Fit local linear segments and add a knot when position deviations exceed a threshold.
- **Action-point strategy:** Form a position-error envelope and find a parsimonious set of points; use those points as spline knots.

The fit and tuning trade off mismatch to observed positions and variability of estimated acceleration. Their calibration exercise sampled **500 trajectories** from the I-80 data (draft pp.9–10). Comparison methods include symmetric exponential moving averages, a Butterworth filter, local weighted regression and a Kalman filter (p.12).

## Jerk as an evaluation variable

Their **Table 2 (p.7)** defines physically motivated quality indicators:
- fraction of acceleration outside a reference range (used there: ±3 m/s²);
- acceleration standard deviation across a track;
- fraction of estimated |jerk| above **15 m/s³**;
- fraction of one-second windows with more than one estimated jerk sign reversal.

These are **diagnostics under the authors' assumptions**, not universal physical laws; low values do not establish agreement with latent true jerk.

**Table 3 (p.18)** in the supplied draft reports, respectively, the percentage of one-second windows with multiple jerk sign reversals and percentage of jerk samples over the threshold:

| Input/filter | Multiple reversals (%) | High-jerk fraction (%) |
| --- | ---: | ---: |
| Original NGSIM | 98.6 | 35.7 |
| I-splines | 0.3 | 0.6 |
| I-splines + action points | 0.7 | 1.0 |
| Symmetric exponential moving average | 59.7 | 0.8 |
| Butterworth | 47.3 | 5.3 |
| Locally weighted regression | 13.9 | 1.3 |
| Kalman filter | 17.0 | 1.5 |

**Interpretation:** These results describe the authors' I-80 sample, thresholds and tuning, not a validated distribution of true jerk.

## Important negative findings and fairness warning

- Figures 3–4 (draft pp.13–14) show that the I-spline filter can **erase a recorded vehicle stop** while repairing apparent missing-observation artifacts.
- Figure 7 (p.17) shows **some vehicles experience increased acceleration variability** after I-spline processing.
- In their conclusion (p.19) the authors explicitly note the filtering comparison is **not entirely fair**: their new spline methods were calibrated on that dataset, while alternatives largely retained parameters from previous studies.

## How this informs Paper C

1. Our study cannot claim first use of jerk to assess NGSIM smoothing.
2. Report derivative diagnostics beyond position RMSE: physical threshold exceedances, sign reversals and event-preservation; keep thresholds labeled as chosen sensitivity settings.
3. Check that a low-jerk smoother is not merely erasing stops and maneuvers; inspect representative vehicles/segments.
4. Use **matched tuning data and budgets** across competing filters—an explicit limitation of this predecessor.
5. I-80 and our US-101 recordings are different datasets and should not be compared numerically as if they were paired.

**Manuscript sentence supported:** “Marczak and Buisson (2012) compared I-spline and classical NGSIM trajectory filters using distributions of speed, acceleration and jerk, and noted that strong smoothing may obscure genuine maneuvers.”

**Source boundary:** this reading is based on the uploaded TRB draft; cite the final journal version's DOI in the manuscript.
