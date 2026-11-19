# Critical prior-art correction: Guerrero (2007) already forecast PLS trends

**Verification date:** 2026-11-07. **Status:** Direct primary-source check of the original Guerrero (2007) PDF supplied to this research conversation, plus published 2020 application and library documentation. This is a literature correction, **not** a claim that a prior paper matches our particular \(d=3\), nonzero-reference NGSIM forecasting workflow.

## 1. The source that future agents must read first

Víctor M. Guerrero (2007), “Time series smoothing by penalized least squares,” *Statistics & Probability Letters* **77** (12):1225–1234, DOI [10.1016/j.spl.2007.03.006](https://doi.org/10.1016/j.spl.2007.03.006).

**Primary PDF inspected:** user-provided *Time Series Smoothinhg by Penalized Least Squares 2.pdf* (11 pages, including author personal-copy cover), specifically original printed **p. 1228, Remark (v)** and **p. 1233, Example 2**. These are printed journal page numbers, *not* the PDF viewer's page labels. The source PDF is not redistributed in the repository.

**Remark (v), p. 1228:**
- Explicitly addresses **extrapolating the estimated trend**.
- States that \(\mu\ne0\) leads to a degree-\(d\) limiting polynomial, while \(\mu=0\) yields degree \(d-1\).
- Defines an \(h\)-step forecast of the trend from its last \(d\) estimated historical values.
- Gives formulas for \(d=0,1,2\), **including a nonzero \(\mu\) term**, e.g.
  \[
  \widehat\tau_N(h)=\frac{h(h+1)}2\,\mu+(h+1)\widehat\tau_N-h\widehat\tau_{N-1},
  \qquad d=2,\quad h\ge1.
  \]
- Immediately afterward, equation (17) defines a data-derived \(\widehat\mu=(N-d)^{-1}\mathbf1^\top D_d Z\). Therefore **data-estimated nonzero reference means and extrapolation were both present in the original framework**.

**Example 2, original p. 1233:** Reports extrapolated Mexico GDP trends for 2006 Q1 and Q2 using both \(d=1\) and \(d=2\) with estimated difference means. The \(d=2\) example explicitly reports \(\widehat\mu=-9\times10^{-6}\) on log-GDP second differences, with forecasts **14.4030** and **14.4129** in log units. Thus the original paper did **not** stop at fitting: it provides actual future trend forecasts and checks withheld observations. Do not write “Guerrero only smoothed historical trends.”

**Another direct applied precedent:** Elba Ramos-Ibarra and Eliud Silva (2020), “Trend estimation and forecasting of atmospheric pollutants in the Mexico City Metropolitan Area through a non-parametric perspective,” *Atmósfera* 33(4):401–420, DOI [10.20937/ATM.52757](https://doi.org/10.20937/ATM.52757). This paper uses controlled smoothness with an HP/Kalman representation and forecasts pollution trends. Its published methodology specifically cites Guerrero's \(d=2\) forecast and assumes \(\mu=0\) for that displayed formula. It is **not** evidence of prior \(d=3,\mu\ne0\) vehicle-jerk forecasting.

## 2. Exact distinction from our existing implementation

| Dimension | Guerrero (2007) | Paper C \`run_case.py\` |
| --- | --- | --- |
| Estimator | Established finite-difference PLS with general \(d,\mu\) | Same mathematical family; third difference interpreted as vehicle jerk |
| Forecast formula worked out | \(d=0,1,2\); explicit nonzero-\(\mu\) formulas | \(d=1,2,3,4\) program paths; emphasis on \(d=3\) |
| Boundary conditions | Extrapolation using the final \(d\) **estimated trend points** | Fit a degree-\((d-1)\) polynomial to the last **25 fitted trend values** after subtracting \(\mu\binom{t}{d}\), then restore the particular solution |
| Scientific application | Mexico real GDP (plus historical smoothing examples) | NGSIM US-101 longitudinal positions, 10-Hz sampling and jerk interpretation |
| Parameter selection and evaluation | User-prescribed smoothing percentage; earlier special-case study | Shared normalized \(S\)-grid with CV/GCV/AICc/restricted BIC/profile ML and 0.5-, 1-, 2-second chronological holdouts |
| Claims permitted | Already introduces PLS trend forecasting, including \(\mu\ne0\) | May contribute a *particular physical application*, explicit reference-jerk ablation, software implementation and carefully validated held-out comparisons |

### A mathematically natural \(d=3\) extension (derived here, NOT quoted from Guerrero)

For a fitted trend whose **future** third differences are constrained to equal the scalar \(\mu\), let \(\widehat\tau_n\) be its final fitted value and \(h\ge1\). Applying the degree-3 forward-difference recurrence gives

\[
\boxed{
\widehat\tau_n(h)=
\widehat\tau_n+
h(\widehat\tau_n-\widehat\tau_{n-1})+
\binom{h+1}{2}(\widehat\tau_n-2\widehat\tau_{n-1}+\widehat\tau_{n-2})+
\binom{h+2}{3}\mu.
}
\]

This is a **straightforward mathematical extension** of the recurrence and limiting-polynomial idea in Guerrero (2007), *not* a new statistical estimator or evidence of historical priority. It would be a useful **three-point continuation baseline** against our current **25-point locally fitted continuation**, especially under noisy estimated jerk. These procedures will differ for a nonpolynomial fitted historical trend; do not replace archived forecasts silently.

**Unit note:** With sampling interval \(\Delta t\), the physical reference jerk is \(\mu/(\Delta t)^3\) in m/s³. The third-difference recurrence formula above uses one time **index** per step and a horizon \(h\) measured in samples.

## 3. Software novelty requires a feature-specific claim

There are existing software implementations of related mathematical components:

- Python [\`pybaselines.utils.whittaker_smooth\`](https://pybaselines.readthedocs.io/en/stable/generated/api/pybaselines.utils.whittaker_smooth.html) implements \((W+\lambda D^\top D)\widehat y=Wy\), with selectable difference order. This documents **Python Whittaker/PLS smoothing**, not necessarily Guerrero's nonzero \(\mu\), normalized-S inversion, forecast continuation and five-criterion interface together.
- R [\`TSsmoothing\`](https://leticiaram.r-universe.dev/TSsmoothing) (Ramírez-Ramírez, Islas-Camargo and Guerrero, 2019) implements controlled-smoothness PLS trend estimation.
- R [\`WH\`](https://cran.r-project.org/package=WH) (Biessy) explicitly implements WH extrapolation and parameter selection.

Our Python package may supply a **distinct, comprehensively validated combination** of fixed/data-derived \(\mu\), high-order \(d\), normalized S, spectral and structured solvers, criteria and worked NGSIM continuation—but uniqueness requires a reproducible **feature matrix** over other packages and versions. “I did not find an identical Python library” does **not** logically imply “no previous research forecast with PLS.”

Do not claim the library is the only Python penalized least-squares smoother or the first Python software in this broad class.

## 4. What remains a viable applied contribution

1. **Exact physical interpretation:** \(d=3\) third-difference PLS with \(\mu/(\Delta t)^3\) as the reference jerk.
2. **Software and numerical integration:** A reproducible Python implementation with smoothness-index control, honest conditional selection criteria, rigorous numerical QA, multiple orders and reference-mean policies.
3. **Forecasting methodology to test:** A last-25-fit-points local-polynomial continuation with a fitted \(d=3\) trend and separately specified \(\mu\), contrasted with the *classical last-three-points recurrence*, Biessy-style zero-weight extension and physical trajectory baselines.
4. **Causal attribution:** Separate the impact of nonzero \(\mu\) on smoothing from the effect of cubic extrapolation, using the exact crossed-cell decomposition in [EXTRAPOLATION_DECOMPOSITION.md](../EXTRAPOLATION_DECOMPOSITION.md).
5. **Statistical evidence:** More independent vehicles and known-jerk simulations, predeclared reference estimators and selection policies; do not infer general superiority from 15 overlapping origins.

**Defensible current wording:** “We investigate an implementation and application of third-difference, nonzero-reference penalized least-squares smoothing with local-polynomial extrapolation for vehicle trajectories. Although penalized trend extrapolation was already analyzed by Guerrero (2007) and others, the specific reference-jerk interpretation and its impact on vehicle-position forecasts remain to be tested against strong competing methods.”

**Priority status:** Exact first use of *this combination* remains **unverified**; even if a broad literature search finds no exact duplicate, originality should be argued through the specific validated contribution, not an unsupported exclusivity assertion.
