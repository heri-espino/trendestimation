# Paper C — full-text jerk and NGSIM state-of-the-art audit

**Date:** 2026-11-19. **Scope:** Author-supplied eight complete PDFs plus independently verified publisher records for two 2026 papers. **Manuscript change:** Nine new BibTeX keys, carefully limited additions to the Introduction, Methods, noise-calibration section, real NGSIM section and Discussion. No experiments, historical results, figures, model implementations, source data or supplemental atlas changed.

## Mathematical framing: what is measured?

Paper C operates on longitudinal observed positions $y_i=\tau(t_i)+\varepsilon_i$ at $\Delta t=0.1$ s, with discrete third differences $D_3\tau/(\Delta t)^3$ used as a jerk proxy. For independent observation noise $\operatorname{Var}(\varepsilon_i)=\sigma_\varepsilon^2$, $\operatorname{Var}(D_3\varepsilon_i/(\Delta t)^3)=20\sigma_\varepsilon^2/(\Delta t)^6$, which follows directly from the stencil $(-1,3,-3,1)$. Correlated errors require the actual covariance $D_3\Sigma_\varepsilon D_3^\top$; replacing it with iid variance can distort the smoothing interpretation.

The objective $\min_\tau\{\|y-\tau\|^2+\lambda\|D_3\tau-\mu\mathbf 1\|^2\}$ is established PLS (Guerrero), not a new estimation principle. Setting $\mu=0$ penalizes squared discrete jerk around zero; $\mu\ne0$ instead penalizes deviations from **constant nonzero** reference jerk. Neither constrains speed, acceleration or jerk to specified physical ranges. At large $\lambda$ the reference dictates a polynomial limiting trajectory, not proof that real traffic exhibits constant jerk.

## Author-supplied full papers — methods, evidence and citation boundaries

### 1. Bisoffi et al., 2017 — FINALLATEX.pdf (14 PDF pages)

**Source:** *Longitudinal Jerk Estimation of Driver Intentions for Advanced Driver Assistance Systems*, IEEE/ASME Transactions on Mechatronics, 22(4):1531–1541, [DOI 10.1109/TMECH.2017.2716838](https://doi.org/10.1109/TMECH.2017.2716838). Uploaded HAL version.

- **PDF pp. 2–3 (abstract, introduction):** authors explicitly target **online driver-intentional jerk**, not a smoothed finite difference of camera positions. Signals available on the vehicle CAN bus, acceleration and pedal actuation inform their dynamics.
- **PDF pp. 4–5, Eqs. (2), (10)–(11):** acceleration sensor includes road grade/offset; model distinguishes driver-intended acceleration and physical vehicle acceleration. Their state vector contains velocity, intended acceleration, acceleration offset and intended jerk. The imposed $\dot{\bar j}_i=0$ is a **noisy process equation**, not an exact physical truth.
- **PDF pp. 6–7, Eqs. (12)–(18):** model-based Kalman observer and a high-gain-inspired scalar tuning parameter produce an explicit responsiveness-versus-measurement-noise tradeoff. Experiments use on-vehicle road-test signals.
- **Citation justified:** direct vehicle-specific prior work on estimating noisy jerk via a dynamical model. **Not justified:** claiming that they recovered NGSIM true jerk or that their state-space model is the PLS normal equation.
- **Manuscript placement:** new state-of-the-art Introduction and Methods discussion of distinct sensor channels; Discussion on alternative future comparisons.

### 2. Montanino & Punzo, 2013 — 2013-MontaninoPunzo-TRR.pdf (13 scanned PDF pages)

**Source:** *Making NGSIM Data Usable for Studies on Traffic Flow Theory: Multistep Method for Vehicle Trajectory Reconstruction*, Transportation Research Record 2390:99–111, [DOI 10.3141/2390-11](https://doi.org/10.3141/2390-11). Uploaded full scanned article; page figures visually inspected, no OCR substitutions.

- **PDF pp. 1–3:** identifies source-coordinate tracking outliers and residual medium/high-frequency errors as distinct mechanisms, with dramatic amplification in estimated speed/acceleration. Figure 2 visualizes unrealistic derivative spikes.
- **PDF p. 4, Methodology and Step 1:** **four-step** process: (1) remove outliers, (2) suppress high-/medium-frequency speed oscillations, (3) remove residual unphysical accelerations while preserving consistency, (4) remove newly introduced oscillations. The authors explicitly show the tradeoff between smoothing noise and erasing stop/acceleration behavior.
- **PDF pp. 5–10 (Figs. 3–8):** reconstructed speed/acceleration, spectrum and outlier corrections. Low-pass filtering alone either leaves anomalies or overly smooths the observed dynamics; constrained/local polynomial reconstruction addresses remaining physical inconsistencies.
- **PDF pp. 10–13:** demonstrates the multi-stage procedure on NGSIM I-80 and compares reconstructed speed/acceleration distributions and selected cases with raw records.
- **Citation justified:** NGSIM pipeline separates tracking outliers, physically unplausible derivatives, and random residual errors. **Not justified:** saying its final acceleration estimates are independent physical ground truth or that it established our specific nonzero-$\mu$ jerk penalty.
- **Manuscript placement:** Introduction and real-data quality warning; previously cited 2015 paper is a **different** article.

### 3. Zhang, Jin, Piccoli & Sartipi, 2024 — 1-s2.0-S1093968726001581-main.pdf (19 pages)

**Source:** *Deep Spatial-Temporal Embedding for Vehicle Trajectory Validation and Refinement*, Computer-Aided Civil and Infrastructure Engineering 39(11):1597–1615, [DOI 10.1111/mice.13160](https://doi.org/10.1111/mice.13160).

- **PDF pp. 1–3:** explicitly separates indirect automatic smoothing from direct manual video verification; describes NGSIM validation via video scanlines and spatial-temporal maps.
- **PDF pp. 3–7, Fig. 1 and Methods:** video-to-spatiotemporal-map instance segmentation using contrastive embeddings to find/refine vehicle tracks. This is an **upstream video and tracking refinement task**, rather than smoothing the already exported one-dimensional CSV using just $y_i$.
- **Later results and conclusion:** quality checks include car-following/lane changes, positional consistency and estimated jerk statistics, with manually processed image-derived reference trajectories. Such manual reference positions are better *observational validation*, but not accelerometer-verified physical jerk.
- **Published correction checked:** [Corrigendum, DOI 10.1111/mice.13303](https://doi.org/10.1111/mice.13303), corrects original Methodology Eqs. (2)–(4), including the normalized embedding similarity and loss expressions. The revised Paper C does **not** copy or rely on those equations; the bibliography explicitly flags the corrigendum.
- **Citation justified:** recent NGSIM data-quality validation and jerk anomaly diagnostics. **Not justified:** calling manually reprocessed camera trajectories independent physical jerk ground truth or treating DSTE as a position-only PLS alternative.

### 4. Fan, Jin & Yin, 2024 — ISTTT25-proceedings-050-min.pdf (27 pages)

**Source:** *Two-Step Quadratic Programming for Physically Meaningful Smoothing of Longitudinal Vehicle Trajectories*. Uploaded open ISTTT25 proceedings manuscript, corroborated with the final *Transportation Science* 58(6):1371–1388 [DOI 10.1287/trsc.2024.0524](https://doi.org/10.1287/trsc.2024.0524). The proceedings and typeset journal are related versions; quote only claims supported in the proceedings/publisher abstract.

- **PDF pp. 1–4:** clearly distinguishes their method from a standard **single weighted sum** of squared residual and roughness penalties. They incorporate prior position error and physically plausible speed and high-order derivative bounds.
- **PDF pp. 5–7, Eq. (4) and finite-difference definitions:** constructs the discrete higher-order derivative matrices $W^{(k)}$; its symplectic alignment convention should not be confused with the forward stencil used by Paper C.
- **PDF subsequent quadratic-program sections:** step 1 minimizes discrepancy subject to derivative bounds; step 2 minimizes roughness subject to derivative and positional-error envelopes, with additional equalities needed for uniqueness of the roughness objective. Existence/uniqueness results depend on these constraints.
- **Final experimental sections:** NGSIM and highD application, comparison with manually re-extracted camera trajectories and up-to-third-order choice.
- **Citation justified:** **closest direct predecessor**: third-order optimization-based camera-trajectory smoothing on NGSIM. **Not justified:** claiming that this approach estimates $\mu$ in our Guerrero-style PLS, or that our unconstrained PLS enforces kinematic feasibility.
- **Manuscript placement:** Introduction (state of art), Methods (precise estimator distinction), Discussion (relative scope and future physically constrained baseline).

### 5. Cameron & Miller, 2015 — eScholarship UC item 1jq5d0pq.pdf (54 pages)

**Source:** *A Practitioner's Guide to Cluster-Robust Inference*, *Journal of Human Resources* 50(2):317–372, [DOI 10.3368/jhr.50.2.317](https://doi.org/10.3368/jhr.50.2.317). Uploaded university manuscript.

- **PDF pp. 2–4, abstract and Introduction:** repeated observations in a cluster can share errors; ordinary standard errors can overstate precision.
- **PDF pp. 5–7, Eqs. (2)–(6):** cluster-correlated residual covariance changes the variance of estimators; validity of conventional cluster-robust asymptotics hinges on many independent clusters.
- **Section VI (few clusters):** warns that conventional corrections can remain unreliable with few groups.
- **Citation justified:** why 200 NGSIM episodes nested in five coarse recording blocks should not be treated as 200 iid population samples. **Not justified:** a new cluster-robust confidence interval for the paper's recorded-position RMSE with only five blocks, or treating Cameron–Miller's OLS formulas as directly the nonlinear RMSE confidence interval.
- **Manuscript placement:** real-case sample-definition paragraph and Discussion.

### 6. Wang, 1996 technical report / published 1998 — download.pdf (27 pages)

**Source:** uploaded University of Wisconsin **August 1996 technical report** *Smoothing Spline Models With Correlated Random Errors*. The published paper is Wang (1998), *Journal of the American Statistical Association* 93(441):341–348, [DOI 10.1080/01621459.1998.10474115](https://doi.org/10.1080/01621459.1998.10474115), independently verified with publisher and author index.

- **PDF pp. 2–3:** directly states usual CV/GCV/GML performance may fail for correlated errors and develops joint estimation of smoothing and covariance parameters.
- **PDF pp. 4–7:** introduces covariance-weighted spline objective, a generalized marginal likelihood and the mixed-effects/BLUP/REML connection.
- **Later simulation section:** compares joint methods across dependence settings; do not transpose published numerical results to Paper C.
- **Citation justified:** classical covariance-aware smoothing and importance of jointly specifying error dependence. **Not justified:** saying that Paper C implemented Wang's spline, jointly estimated NGSIM AR(1) covariance, or derived the current $S_{\mathrm{cov}}$ formula from that paper.
- **Manuscript placement:** covariance misspecification/calibration section and limitations Discussion.

### 7. Harville, 1977 — harville-ML-approaches-to-variance-components-1977-JASA.pdf (20 pages)

**Source:** *Maximum Likelihood Approaches to Variance Component Estimation and to Related Problems*, *Journal of the American Statistical Association* 72(358):320–338, [DOI 10.1080/01621459.1977.10480998](https://doi.org/10.1080/01621459.1977.10480998). Uploaded publisher pagination.

- **PDF pp. 2–4:** reviews maximum likelihood for mixed models; describes Patterson--Thompson restricted likelihood as accounting for degrees of freedom lost when fitting nuisance fixed effects.
- **PDF pp. 3–5:** models $y=Xa+Zb+e$ with covariance dependent on variance components; includes fixed/random effect estimation and general variance-components objectives.
- **Citation justified:** historical and general reasoning for **joint unknown-reference REML** versus fixed-mean profile likelihood in Paper C.
- **Not justified:** copying Harville's general ML into the exact $m=n-3$, one-nuisance-mean determinant correction; Paper C derives that separately under its own difference-space covariance.

### 8. Hansen, 1989 report / published 1990 — cam89-04.pdf (27 scanned pages)

**Source:** uploaded UCLA CAM Report 89-04 (February 1989) *Truncated SVD Solutions to Discrete Ill-Posed Problems with Ill-Determined Numerical Rank*. Published as Hansen (1990), *SIAM Journal on Scientific and Statistical Computing* 11(3):503–518, [DOI 10.1137/0911028](https://doi.org/10.1137/0911028).

- **PDF pp. 2–6:** mathematically compares truncated singular-value inverse solutions with Tikhonov damped spectral filtering, with Picard/spectral-decay conditions.
- **PDF pp. 6–15:** derives perturbation, conditioning and regularization error relationships between hard cutoff and soft attenuation. Both have bias/noise tradeoffs.
- **Citation justified:** historical spectral regularization and risk of noisy high-index modes. **Not justified:** equating the inverse-problem TSVD solution of $Ax=b$ with our exact right-singular-vector projector of the roughness matrix $D_3$ or a universal prediction that hard truncation performs worse in jerk RMSE.
- **Manuscript placement:** already-cited Hansen entry, now expanded explanation in Methods; avoids adding a duplicate new record.

## Additional current external state-of-the-art sources (not in uploaded eight PDFs)

- **van Breugel, Kutz & Brunton (2020)**, *Numerical Differentiation of Noisy Data: A Unifying Multi-Objective Optimization Framework*, *IEEE Access* 8:196865–196877, [DOI 10.1109/ACCESS.2020.3034077](https://doi.org/10.1109/ACCESS.2020.3034077). Open publisher-indexed full article via [PubMed Central](https://pmc.ncbi.nlm.nih.gov/articles/PMC7899139/). General numerical differentiation and tuning, **not** an implemented new Paper C experiment.
- **Ding, Zhang, Peng, Zeng, Ren & Li (2026)**, *Reconstruction Strategy of Vehicle Trajectory Data for Video Recognition Based on a Two-Step Method of Interpolation Filtering*, *Scientific Reports* 16:7428, published **February 5, 2026**, [DOI 10.1038/s41598-026-38947-0](https://doi.org/10.1038/s41598-026-38947-0). Full open HTML inspected; explicitly uses interpolation followed by filtering and reports jerk-exceedance diagnostics in a Zhengzhou urban-intersection video dataset. Not NGSIM data and not validated true jerk, despite citing NGSIM precedents; its independently recorded vehicle-instrument signals are a distinct measurement scenario.
- **Xie, Zheng, Liu, Wang, Duan, Tang & Ran (2026)**, *A Physics-Informed Neural Network for Vehicle Trajectory Reconstruction in Cut-In Scenarios with Sparse and Noisy Observations*, *Systems* 14(5):535, [DOI 10.3390/systems14050535](https://doi.org/10.3390/systems14050535). Publisher abstract and bibliographic metadata inspected; physics-informed model evaluated on sparse NGSIM cut-in reconstruction, not direct recovery of known physical jerk. This is a modern neighboring family and should receive only a concise contextual citation.

## Source-to-manuscript claim map

| Source | Proposed BibTeX key | Manuscript placement | Claim supported |
| --- | --- | --- | --- |
| Montanino & Punzo 2013, full upload | montanino2013 | Introduction, real-case, Discussion | NGSIM multi-step outlier correction versus residual smoothing |
| Zhang et al. 2024, full upload | zhang2024ngsim | Introduction, real-case, Discussion | Video/STMap validation, manually processed positional reference, jerk-based QA |
| Bisoffi et al. 2017, full upload | bisoffi2017jerk | Introduction, Methods, Discussion | Enhanced Kalman online driver-intended jerk with CAN/acceleration/pedals |
| Hansen 1990, full 1989 scanned report | hansen1990tsvd (existing) | Methods | Classical TSVD/Tikhonov spectral regularization, no exact estimator equivalence |
| Harville 1977, full upload | harville1977 | Methods, calibration | Restricted likelihood fixed-effects adjustment |
| Wang 1998, full 1996 report | wang1998correlated | Calibration, Discussion | Joint smoothing/correlation parameters under dependence |
| Cameron & Miller 2015, full upload | cameronmiller2015 | Real case, Discussion | Serial/cluster dependence and limits of five-block extrapolation |
| van Breugel et al. 2020, open full text | vanbreugel2020 | Introduction, Methods | Noisy numerical differentiation and explicit tuning tradeoffs |
| Ding et al. 2026, open full text | ding2026 | Introduction, Discussion | Current interpolation/denoising with jerk QA on *other* video data |
| Xie et al. 2026, verified abstract | xie2026 | Introduction, Discussion | Current sparse NGSIM reconstruction using physics-informed learning |

## Rival models, scientific synthesis and empirical limits

- **Thesis:** A targeted third-order difference regularizer is well-matched to discrete-jerk reconstruction when its spectral noise assumptions hold, and nonzero-$\mu$ supports sustained reference jerk.
- **Antithesis:** Hard physical bounds (Fan), explicit noise correlations (Wang), state-space driver intent (Bisoffi), video-tracking correction (Zhang), event-preserving nonsmooth filters (Zhu), and newer interpolative/PINN reconstructions target different failure modes; third-order PLS cannot replace these without data, assumptions or additional constraints.
- **Synthesis:** Retain established PLS and only claim original **controlled comparisons/conditional interpretation** in the frozen 1,296 synthetic known-jerk cases, 1,944 dependent calibration treatment cases from 72 independent parents, and 200 clustered NGSIM recorded-position forecasts. The adverse spline-plus-quadratic-Taylor 0.3480 m first-second result is preserved. Conditional $S$ is not absolute sensor precision and these 200 episodes do not provide true physical jerk.

A future fair comparator must use the same positions, training-only tuning and testing protocols; online filters, sensor-aided state-space models and upstream video reconstructions cannot be ranked directly against a position-only PLS model without harmonizing inputs and targets.

## Practical verification and authoring rules

These are *citations and literature-positioning changes*, not authorization for re-running Experiments004–008. No source PDF is committed to GitHub (copyright/license safeguards). Before merging: compile with existing Elsevier CAS class via the designated PC08 Windows runner, visually inspect all paper pages, check all citations/BibTeX keys, pass immutable AwesomeFigures input audit, refresh the guarded **16-file** SHA-256 ledger using committed Git bytes (note Windows working-tree line endings), and verify Python 3.10/3.12/documentation CI. Preserve the 12-page atlas, prior compiled PDF immutable build archives, numerical results, source plots and agent handoff. The author has **not** authorized journal submission.
