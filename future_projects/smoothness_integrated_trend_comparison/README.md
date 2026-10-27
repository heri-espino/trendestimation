# Future project: smoothness-integrated trend comparison

**Status:** Research proposal / mathematical working note. **Not implemented in the released `trendestimation` API, experimentally validated, or submitted as a paper.** This directory is intentionally separate from `paper/` (active manuscripts) and `notes/experiment00*` (completed or ongoing experiments).

## Artifacts

- [Two-column LaTeX research note](trend_comparison_two_column.tex) — derivations, finite-difference reference drift, smoothness-indexed trend families, Hilbert-space distances, level–shape decomposition, spectral formulations, and rolling-window comparisons.
- [AGENTS.md](AGENTS.md) — scope boundaries, reproducibility requirements, and proposed next steps for independent agents.

The note uses **NewTX text/math**, dark navy `#000D3C`, and a full-width abstract above a two-column body. Its standalone figures are generated directly in LaTeX via `pgfplots`.

## Mathematical proposal

For equally spaced, aligned series `y1, y2` of length `N`, a difference order `1 <= d < N`, and a *difference-drift* target `mu`, estimate the penalized trend as

```math
\hat{\tau}_{\lambda,\mu}(y)=
\arg\min_{u\in\mathbb R^N}
\{\|y-u\|_2^2+\lambda\|D_du-\mu\mathbf1_{N-d}\|_2^2\}.
```

Use the established normalized, trace-based smoothness coordinate `S in [0,1]` from [the smoothness-parameterization note](../../notes/smoothness_parameterization.md). Treat the `S=1` case as the *exact infinite-penalty limit*.

The candidate global comparison is

```math
\mathcal D(y_1,y_2)^2 =
\frac1N\int_0^1\|\tau_{y_2}(S)-\tau_{y_1}(S)\|_2^2\,dS.
```

For each `S`, separate the **signed mean level difference** `mu_Delta(S)` from the centered difference; this is distinct from the penalization parameter `mu`. For `d >= 1` and the ordinary first-through-`d` difference penalties, the fitted sample mean is preserved even with nonzero difference drift. The global distance splits into nonnegative squared mean-level and centered-shape contributions.

For a rolling window of length `w`, examine

```math
\mathcal D_w(t)^2 =
\frac1w\sum_{k=t-w+1}^t\int_0^1
[\tau_2(S,k)-\tau_1(S,k)]^2\,dS.
```

Retain the **signed difference surface** `Delta(S,t)`, not only its absolute value or RMS, to identify the direction of divergence.

### Proposed change-point extension (not yet in the LaTeX note)

Study regime changes in the signed difference itself, not merely a growing nonnegative distance. For the toy pair

- `y1 = (1,1,1,1,1,1,1,1,1)`
- `y2 = (1,1,1,1,1,3,5,7,9)`

the raw difference is `(0,0,0,0,0,2,4,6,8)`: in this noiseless example a slope change occurs after observation 5. A candidate model is segmented regression

```math
\Delta(S,t)=a(S)+b(S)t+c(S)(t-\kappa)_++\varepsilon(S,t)
```

with a shared change point `kappa` chosen by minimizing integrated residual loss over `S`. Compare this with first-difference CUSUM, ordinary segmented regression, and multiple-change-point methods, without claiming detection ability before validation. Evaluate retrospective and strictly causal online variants separately; full-sample smoothing leaks future information into historical fitted trends.

## Compile the current note

From this directory, with a LaTeX distribution containing `newtxtext`, `newtxmath`, `microtype`, `pgfplots`, `dblfloatfix`, `fancyhdr`, `titlesec`, `mathtools`, `bm`, `booktabs`, and related packages:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error \
  -outdir=build trend_comparison_two_column.tex
```

Result: `build/trend_comparison_two_column.pdf`. The root `.gitignore` excludes `build/`; commit reproducibility-relevant figures, logs, code, and results in deliberately tracked research subdirectories when experiments begin, rather than relying on temporary VMs or chat history.

## Proposed experimental progression

1. **experiment001 — synthetic verification:** implement the global, level/shape, rolling, and scale–time distances; check identities, exact `S=0/1` limits, quadrature refinement, and matched/unequal `mu`.
2. **experiment002 — controlled change points:** synthesize intercept shifts, slope shifts, transients, phase shifts, and heteroscedastic/correlated noise; report false-alarm rates, detection delays, onset uncertainty, and null cases.
3. **experiment003 — agroenvironmental case study:** only after the baseline study, compare aligned NDVI/NDMI or hydrological series with verified external context and no leakage.

Each future experiment should preserve its code, configuration, environment, raw and processed results, figures, analysis, failures, reproduction commands, and next-step handoff on its own reviewed branch.

## Important boundaries

- This is an **exploratory proposal**, not a feature currently shipped by the library.
- Integrating squared Euclidean differences through a common linear smoother induces a positive-definite spectral weighting; investigate which empirical advantages remain over Euclidean and single-scale baselines before claiming novelty.
- If smoothing calibration or reference drifts differ between series, do not silently apply the same common-linear-operator simplification.
- Level–shape decomposition removes **constant offsets**, not automatically trends in slope, multiplicative scaling, or timing differences.
- The current note's figures are **illustrative synthetic data**, not field observations or a validated regime-change result.
