# Paper C — predeclared reference-mean × continuation ablation

**Execution ledger correction, 2026-11-08:** This is an **older planning
protocol** whose original proposed experiment001 designation is now
superseded. Actual Paper C
[experiment001](../experiments/experiment001/README.md) tested
the last-three-point recurrence against the local25 extrapolator,
[experiment002](../experiments/experiment002/README.md) benchmarked
conventional splines/SG/local-polynomials on PCAG103A-08, and
[experiment003](../experiments/experiment003/README.md) tested a
training-only GCV spline on PCAG103A-08. The proposed **known-jerk
simulation and full 2x2 mu ablation remain UNEXECUTED**, now assigned
to **experiment004 or later**. Preserve this protocol as pre-existing
research intent, not previously observed results. Five trajectory
segments constitute only **two distinct vehicle IDs**.


**Status:** **PLANNED, NOT EXECUTED**. Updated 2026-11-05. This is the specification for a **future Paper C \`experiment001\`**, not the independent Springer/algorithm Experiment011 and not the previously archived five-vehicle paper result.

## Research problem

The archived \`run_case.py\` computes a quadratic PLS trend using reference \(\mu\), then **also uses the same \(\mu\)** when adding back a cubic particular solution during extrapolation. The present comparison therefore cannot tell whether lower future-position error is due to
1. a better historical smoothed trend;
2. the nonzero cubic continuation term;
3. changing the smoothness selected by CV/GCV/AICc/BIC/ML when \(\mu\) changes; or
4. chance variation among five vehicles and overlapping origins.

The analytic fixed-\(S\) decomposition is in [EXTRAPOLATION_DECOMPOSITION.md](EXTRAPOLATION_DECOMPOSITION.md). The candidate reference policies are [here](MU_POLICY_CATALOG.md).

## Hypotheses and falsification

- **H1 (sustained jerk):** For data-generating motion with fixed nonzero jerk near the forecast origin, a suitably estimated reference improves short-horizon **future-position RMSE** relative to zero-reference quadratic continuation. Reject as a general claim if improvements vanish under independent seeds or change sign under modest boundary noise.
- **H2 (attribution):** The benefit is partly or entirely explained by the **continuation reference term** rather than historical PLS smoothing. Determine the two exact contributions via a fixed-\(S\) counterfactual 2×2 design.
- **H3 (reference stability):** A predeclared cubic regression reference is more stable than \(\operatorname{mean}(D_3y)\) in the presence of endpoint outliers. Test this rather than assuming robustness.
- **H4 (nonstationary jerk):** A global nonzero reference may worsen forecasts across abrupt braking and piecewise jerk changes; report failure cases, not merely pooled averages.

No novelty or performance claim follows from stating these hypotheses.

## Phase 0 — deterministic implementation checks (test source now added)

The non-experimental regression source `../tests/test_reference_jerk_extrapolation.py` checks the existing continuation's identities and the telescoping mean. Run from the repository root with

```powershell
python -m unittest discover -s paper/ngsim-jerk-case-study/tests -v
```

This is **algebraic QA only**: it does not run synthetic parameter searches, NGSIM forecasts, or a published Monte Carlo evaluation.

Use a new test module, not a rewrite of current published output, to validate

\[
\widehat\tau_\mu=Hy+\mu(I-H)q,\qquad
F_{\mu,\nu}=LHy+\mu L(I-H)q+\nu(q_f-Lq).
\]

Check exact matching with the current \`continuation\` for \(\nu=\mu\), the 2×2 zero-interaction identity for fixed \(S\), and \(S=0/1\) endpoints. Verify the raw-mean telescoping formula for \(n=80\) and sensitivity to the first/last three positions. Mark separate valid/invalid floating-point conditions.

## Phase 1 — known-truth simulation

**Predefine and serialize** the scenario matrix before producing results:

| Factor | Small pilot design | Rationale |
| --- | --- | --- |
| Observation count | \(n=80\) plus one longer window, e.g. 160 | Reuse original paper's horizon geometry; test sensitivity to history length |
| Sampling rate | \(\Delta t=0.1\) s | NGSIM matching; units m, m/s², m/s³ |
| True jerk regimes | zero, constant \(+\!j_0\), constant \(-\!j_0\), smooth sinusoid, abrupt sign reversal, sudden braking | Correct and misspecified jerk-reference scenarios |
| Observation errors | independent Gaussian positions, serially correlated positions, one endpoint-contamination scenario | Isolate data noise and boundary sensitivity |
| \(\mu\) policies | zero, raw sample mean, global cubic OLS, tail cubic OLS, robust tail cubic; plus true oracle in synthetic only | Registered in [MU_POLICY_CATALOG](MU_POLICY_CATALOG.md) |
| Smoothness | The **same** fixed \(S\) grid for direct effect analysis; separately a training-only selector study | Distinguish mechanism from parameter optimization |
| Continuation | 2×2 crossed fit/reference, then each same-reference full pipeline | Exact mechanism attribution |
| Horizons | 0.5, 1 and 2 s | Match the current paper |
| Replication | Prespecified seed list with independent realizations | Reproducible uncertainty and failure analysis |

Avoid pretending this is already an authorized final large computation. Use an intentionally bounded pilot, freeze configurations, collect runtime and numerical validity statuses. Select larger replication counts only after pilot correctness and resource estimates are documented.

### Primary and secondary outcomes

**Primary:** per-series future-position mean squared error at each horizon, pooled only across independent synthetic replications or independent real vehicle IDs. A percent improvement should be paired with a confidence interval appropriate to the unit of independence.

**Secondary:** known-truth *historical* position RMSE, true jerk RMSE (m/s³), estimated-\(\mu\) bias/variance, acceleration/jerk physical bound exceedances, event detection/retention, failure rates, computation time. Do not compute “jerk RMSE” against raw third differences of noisy observed NGSIM positions.

### For physical fairness

Compare not just the overall forecast \(F_{\mu,\mu}\), but all four

\[
F_{0,0},\quad F_{\mu,0},\quad F_{0,\mu},\quad F_{\mu,\mu}
\]

at **exactly matched \(\lambda\)/\(S\)**, same fitted polynomial window, same observations and same future timestamps. Then examine a separate **training-only selected \(S\)** design, where selection-policy effects are recorded explicitly. Do not present counterfactual crossings as a new externally validated forecast method.

## Phase 2 — independent real-vehicle holdouts (future \`experiment002\`, not yet run)

- Predeclare a disjoint set of vehicles or a new dataset (highD/CitySim only if license and independent velocity availability are audited).
- Train/freeze model, smoothing and \(\mu\) rules on allowed vehicles; ensure no future position enters them.
- Add established competitors: position-only smoothing spline; Savitzky–Golay; Kalman/GP constant-acceleration or jerk prior; Fan et al.'s constrained QP if reproducible from official materials; \(\ell_2/\ell_1\) comparator as data allow.
- Distinguish models with *independent measured velocity* from position-only models. Avoid unfair input budgets.
- Report per-vehicle paired results, heterogeneous maneuver regimes, vehicle-block/bootstrap confidence intervals and sensitivity analyses.
- Do not claim improved true physical jerk in real traffic without an independent measurement standard.

## Phase 3 — advanced reference family (future \`experiment003\`, conditional)

Only after Phase 1/2 evidence: investigate locally time-varying \(\mu_i\), Bayesian jerk prior, or hard physical constraints. These are **different statistical problems** and would need new estimators, theory, selection criteria and tests; do not silently fold them into the existing Guerrero fixed-\(\mu\) API.

## Reproducibility and parallel agents

1. Read root and paper \`AGENTS.md\`, [NGSIM README](../README.md), actual [source](../run_case.py) and this plan. Do not alter other papers' experiments.
2. Create a distinct \`feature/\` or \`research/\` branch/PR from latest \`origin/main\`; isolate \`paper/ngsim-jerk-case-study/experiments/experiment001/\` **when implementing**. Preserve original \`results/\`, \`data/\`, figures and TeX.
3. Include \`config.json\`, seeds, DGP formulas, requirements, code SHA, source data hashes, any units conversions, a test command, \`README.md\` with why/how/results/next, and one row per trial (including invalid runs).
4. For large results, use Git LFS or documented external immutable storage, never GitHub secrets.
5. Review correctness and the small pilot before authorizing expansion; store every actual numeric outcome in the repo and open a PR (do not merge without explicit author approval).
6. Amend the review and manuscript **only after** audited empirical results exist and coauthors agree. No claims of future acceptance or verified first use.

## Acceptance criteria for a genuinely stronger Paper C

The research can support an applied methodological contribution if:
- a nonzero-reference policy gives a **replicable** gain on a predeclared endpoint-relevant outcome across independent vehicles/scenarios;
- the gain's source is quantified (historical fit vs extrapolation vs selection);
- estimated reference jerk has a documented noise/endpoint sensitivity;
- true jerk recovery is evaluated only where truth is available;
- the improvement is compared to serious existing trajectory smoothers and physical constraints;
- statistical uncertainty and harmful/failure regimes are disclosed.

Otherwise the paper remains a valuable limited application/negative result without an unsupported novelty claim.
