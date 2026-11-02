# Experiment006 — Complete-criterion computation time and reliability

**Status:** research implementation, draft PR #95; full factorial NOT measured. No statistical RMSE is evaluated.

## Scientific goal

Compare four work configurations: (one S, one series), (grid of S, one series), (one S, R series), (grid of S, R series). All use the same finite-difference PLS model at d=1,...,6 with fixed mu=0 or 0.15. Conditional plug-in mu=data is additionally available for MLE, not classical CV/GCV/AICc/BIC.

Complete requested levels: n={64,128,256,512,1024,16384,131072}; d={1,...,6}; amplitude={low 1e-3,high 1e6}; criterion={cv,gcv,bic,aicc,mle}; S grid={j/M, j=1,...,M} for M={100,1000,10000,100000}, exactly including S=1; direct_s versus mapped_lambda coordinate policies. Repeat on matched seeded series blocks. The single-S workload uses S=0.5 and is not artificially repeated once per grid size in the factorial manifest.

## Exact mathematics and computational methods

The normal equation is A_tau=rhs, where A=I+lambda D_d.T D_d and rhs=y+lambda mu D_d.T 1. The fixed-mu conditional EDF is trace(A^-1) and normalized smoothness is S=(n-EDF)/(n-d). S=1 means lambda=+infinity, evaluated through the constrained polynomial limit, NOT a huge finite penalty.

The exact banded selected inverse uses a Takahashi backward recurrence on Cholesky factors to calculate diagonal leverage and trace using O(n d^2) arithmetic and O(n d) storage. It is independently validated against a full dense matrix inverse and existing spectral CV/GCV/AICc/BIC and marginal-MLE scores. The MLE banded score omits only the lambda-independent logdet(D D.T) offset, irrelevant when selecting lambda within fixed n,d.

The currently implemented complete-criterion pathways include true naive dense inversion, full SVD, banded Cholesky with exact selected inverse, and six **explicit hybrid pipelines**: banded LU+banded trace, sparse LU+banded trace, optional CHOLMOD+banded trace, and FFT/DST/Jacobi PCG+banded trace. Each hybrid actually fits with the named solver and computes exact conditional trace/leverage and criterion diagnostics with an independently timed banded factorization. It is NOT being represented as an intrinsic fast all-in-one sparse or iterative criterion algorithm. The Experiment005 *pure fit-only* methods remain marked fit_only_not_complete_criterion when requested without a diagnostic complement. Improving each hybrid to avoid its duplicate factorization is future research.

## Complexity

- Naive explicit inverse: O(n^3) per penalty; O(n^2) memory. A single n=131072 float64 dense matrix requires 128 GiB; the dense baseline must be skipped above an explicit resource ceiling.
- Full dense spectral SVD: O(n^3) preparation; O(n^2) storage; after one data projection, O(n) per GCV/AICc/BIC/MLE score, O(n^2) per ordinary CV.
- Banded Cholesky + exact selected inverse: O(n d^2) per penalty for factor/trace and O(n d) memory; a subsequent solve costs O(n d).
- Mapping M targets via numerical S inversion with k root iterations each requires O(M k n d^2) using the banded trace oracle. This can dominate M=100000 at n=131072 and cannot be treated as free.
- Retaining M banded factors requires O(M n d) memory, potentially hundreds of GiB; reuse must have an explicit cache budget.
- The existing PCG/FFT/DST fit-only methods have iteration-dependent costs and do NOT automatically provide exact EDF, ordinary CV diagonal leverage or marginal likelihood.

## Four workloads and coordinate comparison

Direct_s evaluates the exact same S candidate values but performs inverse mapping during each criterion evaluation. Mapped_lambda precomputes the lambda candidates for a grid once per timed search and reuses them across independent series. The two policies must produce identical chosen S under a fixed, numerically valid method; the improvement is time/cache reuse, not statistical accuracy. An independently chosen uniform log-lambda grid is a DIFFERENT model-selection candidate set and needs a separately labelled comparison.

Timing is decomposed into initial method preparation, per-series projection/preparation, S-to-lambda mapping, criterion evaluations, and total work with and without accounting for initial setup. Only valid complete repetitions appear in winning timing summaries; all numerical failures, undefined scores, time/memory ineligibility and unavailable methods must be recorded.

## Statistical and numerical exclusions

Classical CV and the other fixed-mu scores are not exact refit estimators when mu is estimated from all data; only conditional plug-in MLE supports mu=data in the current API. Published RSS-BIC is unbounded below as S approaches zero from above, so the reported grid lower bound is a constraint, not a mathematical solution. High-order nonzero mu may imply huge polynomial values even for low-amplitude observations. Floating point failures and KKT residuals must be audited; small KKT residual does not imply certified forward accuracy.

## Run on Windows PowerShell, keeping other agents' work untouched

    git fetch origin
    git worktree add -b experiment006/windows-local ..\trendestimation-exp006 origin/research/experiment006-full-computational-factorial
    Set-Location ..\trendestimation-exp006
    conda activate trendestimation
    python -m pip install -e ".[dev]"
    python -m pytest -q tests/test_experiment006_selected_inverse.py tests/test_experiment006_bench.py

Generate the full plan WITHOUT running the impossible entire factorial at once:

    python paper\benchmarks\experiment006\plan.py --repeats 7 --series-count 8 --output paper\benchmarks\experiment006\runs\windows001\factorial_manifest.csv

Run actual small smoke:

    python paper\benchmarks\experiment006\run.py --preset smoke --output paper\benchmarks\experiment006\runs\windows001\smoke

Run one larger paired experiment slice:

    python paper\benchmarks\experiment006\run.py --preset slice --n 256 --d 3 --mu 0.15 --amplitude high --criterion gcv --grid-denominator 1000 --methods banded_cholesky,spectral_svd,naive_inverse --repeats 7 --series-count 8 --output paper\benchmarks\experiment006\runs\windows001\n256_d3_gcv_high

Outputs: raw_times.csv, summary.csv, paired_speedups.csv and environment.json, with actual timing observations, status, machine/BLAS versions, seed, source checksum and Git revision. Commit and push all measured outputs from the dedicated worktree; never overwrite previous runs or leave authoritative results only in chat. Do not add credentials or licensed source PDFs.

## Unfinished publication gates

1. Optimize each sparse/iterative hybrid to compute criterion-specific diagnostics without an unnecessary additional banded factorization; never count fit-only solves as complete CV/GCV/AICc/BIC/MLE.
2. Optimize selected inverse with compiled execution and validate against a high-precision reference for d=5,6, nonzero mu and near S=1.
3. Make S-to-lambda grid generation efficient for M up to 100000 without silently sacrificing smoothness precision.
4. Instrument true cold independent trial setup, warmups, randomized paired method ordering and bootstrap intervals across independent timing blocks; report n/d/criterion-specific failure rates.
5. Evaluate fair caching across methods, criteria and series within a memory budget.
6. Confirm literature novelty: Guerrero (2007,2008) already introduced the percentage-of-smoothness parameter; Weinert (2007) already established fast Whittaker-Henderson GCV algorithms. Do not claim first use of S.

References: Guerrero (2007), DOI 10.1016/j.spl.2007.03.006; Guerrero (2008), DOI 10.1111/j.1751-5823.2008.00047.x; Cortes-Toto et al. (2017), DOI 10.1080/03610918.2015.1005236; Weinert (2007), DOI 10.1016/j.csda.2006.11.038.

## After the Windows runs

Save the local results in the independent experiment006/windows-local branch:

    git add paper/benchmarks/experiment006/runs/windows001
    git commit -m "experiment006: archive paired computational timing data"
    git push -u origin experiment006/windows-local

The full dataset is represented as a **long-form tensor** with explicitly
named factor axes, not a giant dense n-dimensional NumPy array. A row with
infeasible or incomplete status is a scientifically important observation.
The timing summary reports mean, median, standard
deviation, a seeded 95% bootstrap interval for the mean (when >=2
independent repeats complete), and paired speedup against explicit
inversion where the latter is feasible. These are conditional on the
selected host, threading settings, and run protocol; bootstrap of timing
repetitions alone does not prove universal speed superiority.

The six hybrid pipelines should be requested with the unambiguous names
banded_lu_banded_trace, sparse_lu_banded_trace,
sparse_cholesky_banded_trace, pcg_fft_banded_trace,
pcg_dst_banded_trace and pcg_jacobi_banded_trace.
If scikit-sparse is absent, the CHOLMOD hybrid records an explicit setup
failure; it never falls back to sparse LU. All numerical failures are
retained and prevent a successful time ranking. The research protocol
must not conflate fit-only speed with an end-to-end criterion cost.

To aggregate real runs and calculate empirical log-log exponents after
there are at least three n values with matched factor levels:

    python paper\benchmarks\experiment006\analyze.py --runs paper\benchmarks\experiment006\runs\windows001 --output paper\benchmarks\experiment006\analysis\windows001

Those empirical slopes reflect the *composite implementation* and are
not proofs of the asymptotic theoretical exponents.


## PCAG103A-08 self-hosted execution without administrator access

The university Windows 11 PC must **never** run `actions/setup-python`,
`pip install`, `conda create`, or any system-level installation as part of
the benchmark workflow. It already contains the relevant environment:

    C:\Users\175199\AppData\Local\miniconda3\envs\trendestimation

IMPORTANT: `trend-estimation` (with hyphen) is a second, different
environment and must not be selected. We use `trendestimation`.

The GitHub Actions workflow `.github/workflows/experiment006-selfhosted-pilot.yml`
calls `C:\Users\175199\AppData\Local\miniconda3\Scripts\conda.exe`
with `run --no-capture-output -n trendestimation python`, so it uses
the existing Conda environment without modifications or admin rights.
The checkout source is selected via `PYTHONPATH=$GITHUB_WORKSPACE/src`,
rather than relying on an installed package version. Tests are run
before timing. A missing dependency is reported explicitly, NOT installed.

Earlier Actions run #41430529868 failed in `actions/setup-python` and
never executed mathematical tests. The corrected workflow commit
`05edb60` removes that step. Do not interpret that failure as a solver
failure or as measured benchmark evidence.

## High-d nonzero-mean numerical audit and conservative guard (2026-11-02)

The independent 85-digit **Decimal** dual banded reference requires only
Python's standard library, avoiding installations on the university's
non-administrator Windows runner. It compares the *same frozen float64*
y, lambda and mu for all backends and also checks agreement with a
55-digit reference. The audited data have been **committed and pushed** to
`results/experiment006-highd-41439239921`. The successful action is
https://github.com/heri-espino/trendestimation/actions/runs/41439239921 .

The diagnostic covers n=128, d={5,6}, mu=0.15, two independent seeds,
and S={0.75,0.85,0.90,0.91,0.95,0.99,1.0}; 28 cases/backend.
The threshold for this *forward-error audit only* is 1e-6 relative to
the independent 85-digit trend. Counts are not runtime-performance wins:

| Fit backend | Accurate/28 | Inaccurate/28 | Solver rejected/28 | Largest observed relative forward error |
| --- | ---: | ---: | ---: | ---: |
| Shift-free full SVD | 28 | 0 | 0 | 6.18e-9 |
| Primal banded Cholesky | 16 | 12 | 0 | 21.24 |
| Sparse SuperLU | 22 | 6 | 0 | 6.86e-2 |
| FFT PCG, strict check | 14 | 0 | 14 | 7.64e-12 among accepted fits |

**Conclusion:** a small normal-equation residual does not guarantee an
accurate fitted trend at extreme high-order/high-smoothness penalties.
The 24 numerical-failure rows in pilot #41437886131 cannot be fixed by
simply relaxing a tolerance. In particular, accepting the inaccurate
primal Cholesky at S=0.99 would be scientifically wrong.

The new explicitly named `guarded_svd_cholesky` *benchmark policy* uses
shift-free full SVD when d>=5 and banded Cholesky for d<=4. The former
is empirically accurate for the tested n=128 high-d, nonzero-mu cases.
Its O(n³) setup and O(n²) memory are **fully charged** and an explicit
dense feasibility gate prevents using this policy at n=131072.
This is a conservative validated-small/medium-n fallback,
**not** a universally efficient high-order solver and **not** a proof of
accuracy for arbitrary n,d,mu,S. Retain all legacy method failures and
actual backend names; never ascribe spectral time to banded Cholesky.

The next numerical research priority is a high-precision or
condition-aware, structure-exploiting high-d path at large n; this
remains open. Do not claim that the full factorial is complete.
