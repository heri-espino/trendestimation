# Experiment003 — GCV-selected smoothing spline on frozen NGSIM

**Status:** completed historical pilot only; 5 segments from 2 vehicle IDs.
The SciPy cubic smoothing spline penalty is selected by GCV exclusively
from the first 80 training positions. No future observation tunes it.
All errors refer to recorded future positions, not measured physical jerk.

## Mean position RMSE in meters over 15 overlapping origins

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
| spline_gcv_local25 | 0.294515 | 0.583008 | 1.392618 |
| spline_gcv_native | 0.329222 | 1.738036 | 11.683102 |
| spline_gcv_taylor2 | 0.123310 | 0.295081 | 0.808529 |
| spline_gcv_taylor3 | 0.329222 | 1.738036 | 11.683102 |

## Scientific limitations

Four spline continuations share the same GCV-estimated historical spline.
Natural spline boundary conditions can force nearly linear extrapolation
or unstable higher-order polynomial extrapolation depending on data.
This sample has only two distinct vehicle identifiers and overlapping origins.
Any strong result needs many independent vehicles and simulated known-jerk truth.
Neither a first-in-literature claim nor proof of physical jerk accuracy is supported.

