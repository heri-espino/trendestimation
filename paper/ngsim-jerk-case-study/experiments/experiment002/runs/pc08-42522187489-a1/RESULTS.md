# Experiment002 — conventional trajectory forecasts on frozen NGSIM pilot

**Status:** completed descriptive matched benchmark; NOT independent vehicle-level validation.
Five track segments originate from **two vehicle IDs**; the 15 origins overlap.
No true jerk ground truth. All reported errors are observed future-position errors.

## Training-only, predeclared methods

- Cubic smoothing spline with estimated training-only noise scale; quadratic or cubic Taylor continuation.
- Cubic smoothing spline followed by the same local-25 quadratic continuation as PLS.
- Savitzky–Golay (window 21, degree 3) endpoint derivatives, quadratic or cubic Taylor continuation.
- Ordinary local polynomial degree 2 or 3 on the last 25 raw positions.

The spline smoothing target is s = n*clip(1.4826*MAD(D3 y)/sqrt(20),0.01,0.75)^2.
This is a **fixed heuristic**, not tuning against future positions or a claimed observation noise variance.

## RMSE by horizon (meters)

| Method | 0.5 s | 1.0 s | 2.0 s |
| --- | ---: | ---: | ---: |
| PLS_GCV_guerrero_last3_sample | 0.076879 | 0.311304 | 1.400591 |
| PLS_GCV_guerrero_last3_zero | 0.074519 | 0.295769 | 1.299841 |
| PLS_GCV_local25_sample | 0.244122 | 0.475185 | 1.120968 |
| PLS_GCV_local25_zero | 0.294535 | 0.583065 | 1.392788 |
| raw_local_cubic25 | 0.423392 | 0.932856 | 2.660816 |
| raw_local_quad25 | 0.294545 | 0.583075 | 1.392789 |
| savgol_21_taylor2 | 0.284041 | 0.570384 | 1.307166 |
| savgol_21_taylor3 | 0.284394 | 0.576780 | 1.394193 |
| spline_cubic_local25 | 0.293741 | 0.581674 | 1.390157 |
| spline_cubic_taylor2 | 0.271408 | 0.789528 | 2.719651 |
| spline_cubic_taylor3 | 0.375908 | 1.558552 | 8.594327 |

## Limits and next steps

This is a small, previously examined retrospective sample, with two unique vehicles and correlated windows.
No independent statistical superiority or physically measured jerk is established.
Compare on held-out vehicle IDs and known-jerk simulations, and explore robustness
to spline smoothness and the size of the forecasting window before submitting Paper C.

