## Updated and compiled manuscript — November 10, 2026

- Author requested **update, compile, and push** the existing Paper C research draft. Only the separate `paper/paper-c-scientific-editorial-review` branch / [draft PR #133](https://github.com/heri-espino/trendestimation/pull/133) was modified; PR #131, unrelated manuscripts, immutable Experiments004–008, and numerical selections were not altered.
- Source edits in `sections/discussion.tex`: reconcile nominal (rather than full-estimator exact) effective-complexity matching and explicitly identify Experiments005–008 and their archived source; remove an unbreakable DOI from the final-page reproduction paragraph, referencing the existing dataset bibliography instead, after visually observing its intrusion into the adjacent column.
- **Latest completed Windows PCAG103A-08 build:** [Actions #42769072781](https://github.com/heri-espino/trendestimation/actions/runs/42769072781), source SHA `b06568453a97f7054b4ae0379dc6672cceec8744`, **success**. Result: 12-page, 749,643-byte Elsevier CAS draft `paper/ngsim-jerk-case-study/main.pdf`, SHA-256 `7b9d8f6b2550f3a43da14a0bd795de16dcf1c705cc83eac43191e80eda03c576`. Both old-six-figure and scientific-methods integrity audits passed; the final page was re-rendered and visually checked, confirming the DOI no longer overlaps the opposite column.
- All rendered PDF pages, final audited PDF, original frozen-data paired-bootstrap audit, vector figures, build logs, Conda snapshot and exact inventory are stored in immutable [results/paper-c-methods-pdf-pc08-42769072781-a1](https://github.com/heri-espino/trendestimation/tree/results/paper-c-methods-pdf-pc08-42769072781-a1/paper/ngsim-jerk-case-study/visuals/runs/methods-pc08-42769072781-a1). The immediately preceding [#42768833952](https://github.com/heri-espino/trendestimation/actions/runs/42768833952) build is also preserved independently.
- Original scientific comparisons remain unchanged: known synthetic jerk PLS 2.4413 versus nominally-EDF-matched TSVD 2.9416 m/s³; synthetic paired-stratum RMSE difference 0.5004 with 95% bootstrap interval [0.3227, 0.7134] m/s³; calibration correlation 0.965 for correct-covariance joint REML; adverse NGSIM spline-plus-Taylor 0.3480 m cumulative first-second window RMSE.
- This is a **compiled research draft, not a journal submission**. Coauthor approvals, authorship, declarations and journal-specific checks remain required. No merge authorized.

---

## Latest verified scientific correction — PCAG103A-08 run 42767882100 (2026-11-10)

**Author request:** Resolve the previously identified conditional TSVD-GCV and estimated-reference EDF qualifications, trace the near-interpolation failure, separate forecasting comparisons, and verify on the available self-hosted Windows runner. Completed as a manuscript/mathematical-audit revision; **no original experiment was rerun or retuned**.

- **Successful official 12-page Elsevier CAS PDF:** [PC08 run #42767882100](https://github.com/heri-espino/trendestimation/actions/runs/42767882100), 748,811 bytes, SHA-256 `5b6c5305c928e42f4a8b0665f5b2eb0a3a31f9238f86cf427cc3b6defb9ace3f`. The PDF is published at `paper/ngsim-jerk-case-study/main.pdf` on `paper/paper-c-scientific-editorial-review`. Full source/hash/environment/logs/page renders are preserved in [results/paper-c-methods-pdf-pc08-42767882100-a1](https://github.com/heri-espino/trendestimation/tree/results/paper-c-methods-pdf-pc08-42767882100-a1/paper/ngsim-jerk-case-study/visuals/runs/methods-pc08-42767882100-a1). Both manuscript PDF audits passed and all 12 pages were rendered; visually inspected methods/formula, physical tables/figures and new bootstrap paragraph.
- **Frozen-result diagnostic:** `visuals/audit_frozen_svd_comparison.py` reads ONLY Experiment008 original `synthetic/fitted_rows.csv`, source SHA-256 `4e2443cbd3d005bfeab4c513ab22f04d6ff5c79231bade55e94dd437cffc74ae`. It reproduces the 1,296 matched cases and 54 balanced design cells (24 cases/cell), all original published RMSEs, and the 145 high ranks (75/76) accounting for 0.78946505685 of TSVD-GCV total squared jerk error. Its own immutable JSON is `metadata/frozen_svd_pairwise_audit.json` in the above results branch.
- **New reproducible paired uncertainty:** Conditional on the 54 prespecified equal-weight simulation cells, a 5,000-resample stratified bootstrap with fixed seed 30133 gives **RMSE(TSVD nominal EDF) − RMSE(PLS)=0.50036438 m/s³**, 95% interval **[0.32268065, 0.71336849] m/s³**. The ratio is 1.20496177, 95% interval [1.14452374, 1.26584314]. This is *descriptive conditional synthetic-design Monte Carlo uncertainty*, not real-driver or universally representative inference.
- **Reproducible mathematical checks:** `tests/test_paper_c_plug_in_edf.py` proves by explicit matrix identities and fitted-trajectory comparisons (at fixed tuning) the plug-in reference mean changes PLS/TSVD hat-matrix traces. `tests/test_paper_c_frozen_svd_audit.py` checks deterministic paired bootstrapping, missing source pairs and corrupted MSE rejection. Five targeted Windows tests passed, and repository Python 3.10/3.12 plus documentation CI passed on the earlier reviewed source commit [#42767674823](https://github.com/heri-espino/trendestimation/actions/runs/42767674823).
- **Method definitions accurately qualified:** The archived `tsvd_gcv_cubic_ols` has conditional, plug-in **position-GCV**, not exact full-estimator GCV. The archived rank-matched TSVD is *nominally* matched in fixed-reference EDF, not exact EDF after estimating `mu` from the same training sample or selecting tuning. These are correctly described in `sections/methods.tex`, `sections/synthetic_case.tex`, `sections/real_case.tex`, and the abstract. A future fully estimated-mean GCV reanalysis would be a **new**, separately approved study; do not silently change/overwrite Experiment008.
- **Forecast comparison target:** The stored horizon-`H` metric is cumulative-window RMSE over frames 1..H; the five-method common continuation comparison still uses method-dependent reference `mu`, and the spline quadratic Taylor comparator changes both smoother/continuation. The manuscript distinguishes these claims. It retains the unfavorable real NGSIM spline result and does **not** infer observed physical jerk.
- **Workflow reliability repaired:** `.github/workflows/paper-c-methods-compile-pc08.yml` now clears interrupted rebase metadata only in its own verified self-hosted Git checkout, skips stale-source PDF publication instead of rebasing binary scientific figures, and archives an append-only unique results-only Git branch. Previously failed, superseded builds remain preserved in their own run roots.

**Status:** Scientifically audited, 12-page compiled research draft in **draft PR #133** stacked on unmerged PR #131. Coauthor authorship/affiliation/declarations/journal-fit review and explicit submission permission remain external gates. No merge, journal submission, large scientific rerun or numerical result replacement was performed.

---

# Paper C: scientific and editorial review of PR #131

**Status:** research-only editorial continuation on `paper/paper-c-scientific-editorial-review`, branched from PR #131 head `d1f7cfdef83b81f6384516cd9816c3c8ad496769` on 2026-11-09. Parent PR #131 remains open and unmerged. PR #132 is a parallel, unmerged narrative alternative. This branch does not overwrite either.

## Scope and provenance

The author specifically wants a physical/statistical paper, not a computation-time paper. The canonical source is `paper/ngsim-jerk-case-study/main.tex`. The immutable Experiment005/006/008 synthetic source contains 1,296 common trajectories, **not three distinct sets of replications**; Experiment007 has 1,944 dependent factorial conditions within 72 independently sampled parents; the NGSIM record has 200 selected episodes from five coarse recording blocks, with no independently observed clean jerk. No experiments were rerun for this review.

Sources examined: root `README.md`, `AGENTS.md`, `AI_HANDOFF.md`, paper-level routing and session files, primary method-first handoff, all six manuscript sections, `references.bib`, Experiment008 `README.md` and `run.py`, both PR #131/#132 metadata, PR #132 statistical structure handoff, the on-branch figure PNGs, and frozen Experiment008 synthetic/real `summary.csv` and synthetic `fitted_rows.csv`. The literature narrative follows the previously source-annotated `notes/LITERATURE_REVIEW.md` and `notes/SOURCE_INVENTORY.md`; claims of historical first use remain excluded.

## Additional source-level and page-by-page review (2026-11-09)

- **Forecast metric definition (correction):** Experiment008 `compare()` computes `mean((prediction[:H]-truth[:H])**2)` for each episode, then its aggregate is `sqrt(mean(case_mse))`. Experiment006 `forecast_metric()` uses the same first-`H` frame averaging. Therefore the published 0.5/1/2-second figures and tables are **cumulative-window RMSE**, not errors only at exactly 0.5/1/2 seconds. Equations, captions, narrative, and the two regenerated Experiment008 figure axes now use this precise definition; none of the archived scores was changed.
- **First revised PDF inspection:** Windows manuscript-only Actions run [#42745055261](https://github.com/heri-espino/trendestimation/actions/runs/42745055261) passed and generated a 12-page PDF, SHA-256 `2c4e6e28c0d16af3bd7396309006a607930e226fe8ed5e0464adc714345569e2`, with all 12 pages rasterized and individually inspected through the results archive `results/paper-c-methods-pdf-pc08-42745055261-a1`. The inspection found a stranded equation number (TSVD hard-filter Eq. 8), the class's misleading stock footer 'Preprint submitted to Elsevier', and underexplained horizon scoring. The subsequent source revisions use `needspace`, override only the footer (not the official CAS class), and clarify window RMSE. A **later** build must be checked for the revised page layout and final PDF identity before claiming completion.
- Figure content is clear, reference sources resolve, and the original adverse real spline result is visible. No scientific experiment was rerun.

### Final compiled draft (PCAG103A-08)

- **Successful manuscript-only run:** [Actions #42746042540](https://github.com/heri-espino/trendestimation/actions/runs/42746042540), on the independent review branch, no scientific experiment or original data reconstruction.
- **12-page PDF:** `paper/ngsim-jerk-case-study/main.pdf` in `paper/paper-c-scientific-editorial-review`, **747,073 bytes**, SHA-256 **`97233d49dbd922108ecca7ac72b650640e285b7bb08ec7fb93d19e44996b5ac2`**. All figure checksum and manuscript content checks passed.
- **Immutable full provenance and PDF page images:** branch `results/paper-c-methods-pdf-pc08-42746042540-a1` under `paper/ngsim-jerk-case-study/visuals/runs/methods-pc08-42746042540-a1/`, including `pages/page-01.png` through `page-12.png`, `pages/contact-sheet.png`, build/requirements/source manifests and logs. ORCID now appears on first page, the CAS footer correctly says **Research draft — not submitted**, and the TSVD equation number is no longer orphaned.
- Both the original pre-fix 12-page PDF and the intervening revised PDF are independently archived rather than overwritten. This is a **compiled research draft**, not publication or coauthor approval.

## Scientific audit findings

1. **Finite physical jerk:** the reported historical outcome is `D3(true position)/(0.1 s)^3` versus the same operator on the fitted historical position, not a noisy observed continuous jerk or independent ground truth on NGSIM.
2. **Physical reference units:** `mu` is a *discrete third difference in meters*, and `mu/(0.1 s)^3` is the corresponding reference jerk proxy in m/s^3.
3. **S is relative:** for independent isotropic observation error and third-difference innovations, the population spectral fraction equals `S(lambda)`. It is not the probability an observation is wrong or the sensor's absolute noise variance. Experiment007 is calibrated over only 72 independent parents, with an adverse correlated-noise counterexample.
4. **Different SVD estimator:** Experiment008 uses hard truncation of ascending singular modes of `D3`, rather than an alternative factorization used to solve the identical PLS problem.
5. **Conditional TSVD GCV:** `RoughnessSVD.gcv_rank(y,mu)` centers at the *already fitted* cubic-OLS `mu=a^T y`, then minimizes `n*||residual||^2/(m-r)^2` for ranks `0..m-1`. This is conditional plug-in GCV. In the complete smoother, the mean is estimated from the very same position data, so the exact full-smoother GCV denominator differs. No new rank search was performed; historical results retain their genuine selection rule.
6. **Conditional complexity matching:** with `q_mu=mu q1`, `D3 q1=1`, and cubic-OLS linear mean `a^T y`, for fixed lambda and cutoff rank r, the full plug-in smoother maps are `H+(I-H)q1 a^T` and `P_r+(I-P_r)q1 a^T`. Their traces are `tr(H)+a^T(I-H)q1` and `3+r+a^T(I-P_r)q1`. Experiment008 matches only the *fixed-mu* trace `tr(H)` to `3+r`, so the reported comparison is a **nominal EDF-matched ablation**, not proof that the full selected procedures have identical statistical complexity. The selection of lambda and r from y adds further nonlinearity not included in these fixed-tuning traces.
7. **Decomposition of adverse TSVD error from immutable rows:** in the 1,296 synthetic `fitted_rows.csv` cases with method `tsvd_gcv_cubic_ols`, 120 selected rank 76 and 25 selected rank 75 (145/1,296 = 11.19%). These 145 accounted for 78.9465% of the sum of recorded per-case `historical_jerk_mse_m2_s6`, while the complete TSVD-GCV pooled jerk RMSE was 250.7181036098 m/s^3. This is a deterministic aggregation of the original frozen rows, **not** a fresh simulation.
8. **Continuation comparison:** the same algorithm is applied in Experiment008 to all fitted trends; PLS and TSVD use cubic-OLS training-derived `mu`, while spline and Savitzky-Golay use zero. Spline's 0.348043m at one second is a separate end-to-end quadratic Taylor continuation comparison, not a common-boundary-rule fit ablation.
9. **Archival result reconciliation:** the frozen Experiment008 summary rows directly confirm PLS/TSVD matched synthetic jerk RMSE 2.4412570862/2.9416214671 m/s^3, synthetic local25 one-second RMSE 0.4352956734/0.4502057723m, and real 3-point one-second RMSE 0.5143855166/0.5117758414m. The unfavorable spline result is retained.

## Editorial actions

- Organize the sections as physics/introduction, methods, Simulation Study I (known-jerk), Simulation Study II (S calibration), real NGSIM, discussion.
- Broaden historical framing using Whittaker, Guerrero, Biessy, Marczak/Buisson, Cao, Fan/Jin/Yin, and Tang/Yoon/Barfoot without claiming new general PLS theory.
- Qualify the conditional plug-in TSVD-GCV rule and the nominal EDF comparison in the methods; explain concentrated near-interpolation jerk error using frozen results.
- Explicitly label method-dependent `mu` in a common continuation algorithm.
- Preserve all earlier figures, source datasets, initial pilot context, and negative spline results.

## Outstanding verification before submission

- Run the isolated PCAG103A-08 manuscript-only compilation and hash/integrity audits. Do **not** rerun Experiments004--008, and publish only on this review branch and a new results-only archive.
- Inspect all final PDF pages for overfull boxes, repeated/crowded figures, table legibility, and citation/reference integrity. Automated PDF-text audits alone are not sufficient.
- Have the proposed authors verify authorship/affiliation, citations and venue requirements. An Elsevier CAS class file does not establish an accepted journal.
- If desired later, predeclare a **new** study to compare full plug-in TSVD-GCV versus its conditional version or other physically constrained trajectory methods. The present article must not relabel old scores as such a new method.
- No merge, pull request integration or journal submission without explicit approval.

## Scientific primary sources

Guerrero (2007), DOI 10.1016/j.spl.2007.03.006; Cortes-Toto et al. (2017), DOI 10.1080/03610918.2015.1005236; Biessy (2025 online/2026 volume), DOI 10.1017/asb.2025.10061. Additional bibliography is in `references.bib`; literature verification levels are in `notes/SOURCE_INVENTORY.md`.

## Review continuity

Begin from PR #131 and this note, then inspect source commits and dedicated PC08 build history. PR #132's known-first chronological organization is useful, but its removal of the TSVD physical benchmark is contrary to the author's decision. Do not merge competing branches wholesale. Maintain `AGENTS.md`, `AI_HANDOFF.md`, `paper/SESSION_HANDOFF.md`, and `paper/PUBLICATION_MAP.md` when the new build is verified.
