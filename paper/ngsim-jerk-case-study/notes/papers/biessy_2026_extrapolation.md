# Biessy (2025 online / 2026 volume) — Whittaker–Henderson extrapolation

**Bibliography:** Guillaume Biessy. “Whittaker–Henderson smoothing revisited: A modern statistical framework for practical use.” *ASTIN Bulletin* 56(1):1–31 (January 2026), [DOI 10.1017/asb.2025.10061](https://doi.org/10.1017/asb.2025.10061), first published online **3 September 2025**. [Publisher full text](https://www.cambridge.org/core/journals/astin-bulletin-journal-of-the-iaa/article/whittakerhenderson-smoothing-revisited-a-modern-statistical-framework-for-practical-use/237E3C12164917F768932FDBC2079100).

**Primary-source status:** Read the open-access publisher HTML abstract, introduction, Section 7 on extrapolation, and the discussion; original article's supplemental numerical experiments have **not** been independently reproduced.

## Core message for Paper C

This article is **direct contrary evidence** to the broad statement that “our work is the first extrapolation using penalized least-squares/Whittaker–Henderson smoothing.” The paper explicitly develops **Whittaker–Henderson extrapolation** and uncertainty quantification. Its model and applications are in actuarial smoothing and experience-table estimation rather than NGSIM vehicle motion with a nonzero third-difference mean.

### Extrapolation mechanism, compared fairly

**Biessy Section 7:**
- Extend the equally spaced time/domain grid with future positions treated as **zero-weight observations**.
- Solve an **extended penalized smoothing problem**. For two-dimensional arrays, add constraints so the historical fitted values remain consistent with the original fit rather than moving when new penalty terms are introduced.
- Derive predictive credibility intervals including structural and future innovation uncertainty in a statistical/Bayesian interpretation.
- Explicitly discusses earlier P-spline mortality extrapolation (Currie et al. 2004; Delwarde et al. 2007) and a two-dimensional consistency correction (Carballo et al. 2021).

**Our current Paper C:**
- Fit the length-\(n=80\) observed training window using *Guerrero-style* PLS with third-difference reference mean \(\mu\).
- Form a polynomial particular solution \(p_\mu(t)=\mu\binom t3\), then fit a **local quadratic** to the final 25 historical *smoothed* residualized points and extend it to the next \(h\) observed timestamps.
- Add back the future cubic particular solution; evaluate against independently held-out **camera-derived vehicle positions**.
- This is **not** the same as extending the WH optimization to future zero-weight samples. The present method does **not** produce credible intervals or arise from a unique model-defined predictive distribution.

## Scientific implications

1. A broad novelty claim about WH/PLS extrapolation is untenable.
2. A narrower result may still be meaningful: the **reference-jerk policy** under \(d=3\), and the separation of its impact on historical fits versus a specified local continuation in short-horizon vehicle forecasting.
3. **Recommended future baseline:** implement a standard zero-weight **extended WH forecast** under matched \(d,\mu,S\) and identical observed windows. Benchmark that against the current local-polynomial continuation. Include Biessy-like constraints only where the modeled domain requires them; do not imply that a two-dimensional consistency issue necessarily arises in our one-dimensional NGSIM trace.
4. Extrapolation uncertainty from a model-based procedure should not be equated to empirical RMSE or converted into intervals without calibration.
5. Because Biessy notes that penalty **order** governs how the smoothing extrapolates, our \(d=3\) study should explicitly separate penalty order, reference mean, and extrapolation rule.

## Suggested related-work wording

> Whittaker–Henderson smoothing has previously been extended beyond the observed domain, including with zero-weight future positions and uncertainty quantification (Biessy, 2026). Our study instead examines a separate local-polynomial continuation of a third-difference PLS trend centered on zero or a training-derived reference jerk, in order to isolate how that reference influences short-horizon vehicle-position extrapolation.

This wording states a **difference**, not historical priority for a specific unsearched combination. A future agent should compare the complete extrapolation procedures before asserting any novel theorem or universal performance benefit.

**Not completed:** No WH-baseline implementation, Monte Carlo, independent-vehicle replication, or new NGSIM benchmark has been run as part of this annotation.
