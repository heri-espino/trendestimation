# scikit-sparse / CHOLMOD 0.5 compatibility on Windows

The user's university Windows 11 Conda environment successfully installed
scikit-sparse and imported sksparse.cholmod. The legacy verification
expression cholesky(A)(b) failed with "TypeError: 'tuple' object is not
callable" because scikit-sparse 0.5 changed this API.

The corrected API is to call cho_factor(csc_array(A)).solve(b).
This integration fix uses SciPy CSC arrays only for the new API and
retains the legacy scikit-sparse 0.4 Factor.solve_A path for compatibility.
It does not replace CHOLMOD with SuperLU, change the PLS objective,
or reclassify unverified numerical results.

Actual user-provided Windows verification (on the research source branch)
was:

    110 passed in 3.15s

for tests/test_experiment005_structured_solvers.py and
tests/test_experiment010_parallel.py, followed by a real CHOLMOD-vs-banded
Cholesky fit for n=64,d=2,lambda=2,mu=0.15,seed=42:

    Maximum absolute error: 1.2948756650255078e-13
    PASS: True

The source patch in this separate main-targeted PR is copied verbatim
from the already CI-tested CHOLMOD-specific changes in research PR #106
(which merged into the focused Experiment010 research branch).
Added tests mock modern and legacy APIs in normal CI; the optional
installed-CHOLMOD test on the user's Windows VM also passed.
These are pointwise software parity checks, not a general 85-decimal
numerical-accuracy certificate.

This fix does not merge the separate Experiment010 research-plan stack
or alter the main Computational Statistics manuscript.
