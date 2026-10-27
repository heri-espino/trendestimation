.. This table is generated solely from uploaded Windows CSV evidence.

Measured full Windows study
---------------------------

The source contains **80,640 real Windows search records**, with
two experimental seeds, seven timing repetitions and one BLAS thread.
For :math:\`n=48, d=2, \mu=0, R=1\`, spectral SVD, the following
millisecond values are medians of the two recorded seeds:

.. list-table:: Seventeen-point grid timings
   :header-rows: 1
   :widths: 25 25 25 25

   * - Criterion
     - Native S
     - Premapped S to lambda
     - Independent log-lambda
   * - CV
     - 2.004 ms
     - 1.879 ms
     - 0.545 ms
   * - GCV
     - 1.851 ms
     - 1.800 ms
     - 0.426 ms
   * - AICC
     - 1.887 ms
     - 1.810 ms
     - 0.458 ms
   * - BIC
     - 2.016 ms
     - 1.810 ms
     - 0.449 ms
   * - MLE
     - 3.477 ms
     - 2.035 ms
     - 0.515 ms

Native S and pretranslated S-to-lambda use the **same candidate
penalties**; independent log-lambda uses different interior points.
The source audit verified **4484** numerically valid matched-coordinate seed pairs.
Unstable numerical backends are excluded from full-grid winner
comparisons, not credited for completing only part of a search.
The exact S=1 / lambda=infinity endpoint is analytical.
The Gaussian MLE model is not applicable for d=0.
