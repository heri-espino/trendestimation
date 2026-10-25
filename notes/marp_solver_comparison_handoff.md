# Marp handoff — PLS solver backend comparison

**Scope:** slide-ready notes ONLY. Do **not** edit the active Marp branch or
its slides while another agent is working on them. Integrate on that branch
after coordinated review of the independent backend PR.

## Equations worth displaying

The *same* fitted trend is solved by all three numerical backends:

\[
\hat\tau_\lambda=p_\mu+(I+\lambda D_d^\top D_d)^{-1}(y-p_\mu).
\]

With \(D_d=U\Sigma V^\top\),

\[
D_d^\top D_d=V\Sigma^\top\Sigma V^\top,\qquad
\hat\tau=p_\mu+V \operatorname{diag}((1+\lambda\delta_j)^{-1})V^\top(y-p_\mu).
\]

The spectrum of \(D_d^\top D_d\) consists of squared singular values and
\(d\) exact zeros (for \(d\ge1\)). Forming \(D_d^\top D_d\) can square the
positive-subspace condition number. Cholesky factors \(I+\lambda Q\) in a
banded representation rather than computing eigenvectors.

## Proposed Marp sections (do not paste results until measured)

1. **Why three methods?** Same PLS objective, different numerical
   factorization; existing SVD core is the reference implementation.
2. **SVD vs eig(Q)**: mathematically equivalent, different floating-point
   accuracy and rank-deficiency sensitivity.
3. **Banded Cholesky**: assembly avoids dense Q, one new factorization
   per finite positive lambda, exploits bandwidth d.
4. **Fair experiment**: show *setup*, *one full fit*, *M repeated fits*,
   *M batched fits with cached projection*, *setup plus M fits*, and
   *maximum discrepancy vs SVD*, for several n, d, M and mu.
5. **Do not confuse operations**: CV leverage/EDF/GCV/MLE after SVD
   are not the same task as a single full-trend Cholesky solve.
6. **Default policy**: keep existing SVD as the safe compatibility
   baseline until benchmark outputs are reviewed; workload-specific
   auto selection requires further reproducible evidence.

## Benchmark commands

```bash
python benchmarks/compare_solver_backends.py --preset quick --repeats 5 --threads 1 --output build/solver-backends.json
python benchmarks/compare_solver_backends.py --preset full --repeats 7 --threads 1 --output build/solver-backends-full.json
```

Include the machine/BLAS/Python/NumPy/SciPy metadata and seed beside the
plots. These are host-specific measurements, **not a universal ranking**.
Do not fabricate charts, speed ratios or results.

## Sources

- Cortés-Toto, Guerrero, and Reyes (2017), existing PLS selection reference.
- Weinert (2007), *Efficient computation for Whittaker–Henderson smoothing*.
- Project's current `paper/sections/timing_experiments.tex` and
  `docs/benchmarks.rst` for the earlier fair banded comparison.
- The new `docs/solver_backends.rst` for exact current API behavior.

**Branch safety:** This handoff stays in `notes/` of the independent PR.
The presentation's ongoing branch remains untouched.
