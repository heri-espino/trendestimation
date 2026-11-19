# Paper C — noisy jerk estimation and NGSIM literature (2026-11-19)

This is a **targeted source-to-claim review**, supplementing [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md), [METHODS_CITATION_AUDIT.md](METHODS_CITATION_AUDIT.md), and [DEPENDENCE_AND_INFERENCE_REFERENCE_SELECTION.md](DEPENDENCE_AND_INFERENCE_REFERENCE_SELECTION.md). Base main commit: 536ab8a7063f4932cbb12c925ed2dd1514768138. The compiled manuscript already contains 42 references. This review **does not modify** LaTeX, BibTeX, figures, PDFs, experiments, workflow configurations or publication checksums.

## 1. Mathematical problem and why noise matters

Let \(y_i=x(t_i)+\varepsilon_i\), \(t_i=i\Delta t\), where \(x\) is latent position, \(j=x'''\) is physical instantaneous jerk, and \(D_3\) has stencil \((-1,3,-3,1)\). Paper C measures **discrete jerk proxy** \(D_3x/(\Delta t)^3\), not independently observed physical jerk. Under iid position error of variance \(\sigma_\varepsilon^2\),

\[
\operatorname{Var}((D_3\varepsilon)_i/(\Delta t)^3)
=20\sigma_\varepsilon^2/(\Delta t)^6.
\]

At 10 Hz and **hypothetical** position-noise standard deviation of 0.05 m, this gives 223.6 m/s³ raw-discrete-jerk noise SD. This is a mathematical conditional example, **not an empirical NGSIM noise estimate**.

Our estimator minimizes \(\|y-\tau\|_2^2+\lambda\|D_3\tau-\mu\mathbf1\|_2^2\). With \(\mu\ne0\), we penalize variation *around nonzero reference jerk*, NOT absolute minimum jerk. At large \(\lambda\), position trends toward a cubic satisfying constant discrete third difference, rather than to the quadratic trend for \(\mu=0\).

## 2. Closest predecessor papers already present in Paper C

| Reference / verified source | Method and relevant evidence | Manuscript action / scientific boundary |
| --- | --- | --- |
| **Fan, Jin & Yin (2024)**, [Two-Step Quadratic Programming for Physically Meaningful Smoothing of Longitudinal Vehicle Trajectories](https://doi.org/10.1287/trsc.2024.0524), Transportation Science 58(6):1371–1388 | **Closest prior art:** two constrained quadratic programs, physical upper/lower derivative limits, prior image-position error bounds, third-order derivative constraints, NGSIM and highD assessment against manually re-extracted data. The publisher record explicitly distinguishes it from standard weighted discrepancy-plus-roughness smoothing. | **Existing** BibTeX key: fan2024. Expand related work, not duplicate bibliography. No claim of first jerk/third-derivative smoothing. Our single soft, nonzero-centered unconstrained PLS is mathematically and physically different; it does NOT guarantee feasible speed/jerk. |
| **Punzo, Borzacchiello & Ciuffo (2011)**, [NGSIM trajectory accuracy](https://doi.org/10.1016/j.trc.2010.12.007) | Explicit **jerk analysis, consistency analysis, and spectral analysis** for NGSIM data, accounting for differentiated measurement errors. | **Existing:** punzo2011. Give it an explicit jerk-validity role instead of citing only generic dataset limitations. No observed true physical jerk. |
| **Marczak & Buisson (2012)**, [New Filtering Method for Trajectory Measurement Errors and Its Comparison with Existing Methods](https://doi.org/10.3141/2315-04), Transportation Research Record 2315:35–46 | NGSIM I-80 I-splines, comparable classical filters, jerk-magnitude and sign-reversal QA. Existing [paper note](papers/marczak_buisson_2012.md) identifies smoothing failures that can erase stops and unfairly tuned competing methods. | **Existing:** marczak2012. Important warning: smoother jerk is not verified physical jerk. |
| **Thiemann, Treiber & Kesting (2008)**, [Estimating Acceleration and Lane-Changing Dynamics from NGSIM](https://doi.org/10.3141/2088-10) | Smooths position, speed and acceleration with boundary handling; derives noise-amplification concern. | **Existing:** thiemann2008. Acceleration target, not independently observed jerk. |
| **Cao et al. (2021)**, [V-Spline: Adaptive Smoothing Spline for Trajectory Reconstruction](https://doi.org/10.3390/s21093215) | Adaptive Hermite splines use **independently measured position AND velocity**, penalize acceleration; application includes tractor trajectories. | **Existing:** cao2021. Input requirements differ; not the same position-only NGSIM benchmark. |
| **Tang, Yoon & Barfoot (2019)**, [White-Noise-on-Jerk Motion Prior for Continuous-Time Trajectory Estimation on SE(3)](https://doi.org/10.1109/LRA.2019.2891492) | Stochastic continuous-time robotic pose prior with *zero-mean white noise on jerk*; favors constant acceleration on average. | **Existing:** tang2019. A zero-mean jerk *innovation* is not the same as deterministic constant **nonzero** reference jerk. |

## 3. New direct-jerk, noisy differentiation, and NGSIM citation candidates

| Priority | Candidate / verified publisher DOI | Observation type and method | Appropriate claim | Critical distinction |
| --- | --- | --- | --- | --- |
| **High** | **Nakazawa, Ishihara & Inooka (2003)**, [Real-Time Algorithms for Estimating Jerk Signals from Noisy Acceleration Data](https://doi.org/10.3233/JAE-2003-282), International Journal of Applied Electromagnetics and Mechanics 18:149–163 | **Measured acceleration**, jerk as latent random walk; Kalman and robust state estimation with colored measurement noise | There is prior work explicitly estimating jerk under measurement noise using state-space approaches. | Not NGSIM, not camera position-only inputs, not our exact PLS. |
| **High** | **Bisoffi, Biral, Da Lio & Zaccarian (2017)**, [Longitudinal Jerk Estimation of Driver Intentions for Advanced Driver Assistance Systems](https://doi.org/10.1109/TMECH.2017.2716838), IEEE/ASME Transactions on Mechatronics 22(4):1531–1541 | Vehicle dynamics + CAN-bus/driver signals, enhanced Kalman estimation, noise–responsiveness tradeoff | Direct vehicle-specific jerk estimation exists in the control literature. | Intended driver action and online filtering differ from observational offline jerk proxy. |
| **High** | **van Breugel, Kutz & Brunton (2020)**, [Numerical Differentiation of Noisy Data: A Unifying Multi-Objective Optimization Framework](https://doi.org/10.1109/ACCESS.2020.3034077), IEEE Access 8:196865–196877 | Multiobjective parameter choice across noisy differentiation families, including total variation regularized jerk; open-source [PyNumDiff](https://github.com/florisvb/PyNumDiff). | Method selection/parameter choice and direct derivative recovery are different objectives from position fitting; principled possible new benchmark. | Published study does NOT establish that its methods beat Paper C on known-jerk data. Any TVRJ comparator would need a new, audited experiment. |
| **High** | **Zhang, Jin, Piccoli & Sartipi (2024)**, [Deep Spatial-Temporal Embedding for Vehicle Trajectory Validation and Refinement](https://doi.org/10.1111/mice.13160), Computer-Aided Civil and Infrastructure Engineering 39:1597–1615 | NGSIM video/spatiotemporal-map reconstruction, manually processed trajectory comparisons, jerk magnitude/sign reversal QA. | Modern trajectory-data QA also treats jerk anomalies as evidence of recording/tracking problems. | Manually corrected **position** is not independently sensed physical jerk. Publisher lists corrigendum; verify before final publication. |
| **Medium** | **Shi & Liu (2019)**, [NGSIM Vehicle Trajectory Reconstruction](https://doi.org/10.11936/bjutxb2017120020), Journal of Beijing University of Technology 45(6):601–609 | Wavelets/outlier detection, polynomial interpolation and Kalman noise filtering; I-80 speed/acceleration/jerk review. | Direct NGSIM noisy-trajectory reconstruction and estimated jerk QA. | Journal abstract inspected, not all equations; no verified independent jerk ground truth. |
| **Medium** | **Montanino & Punzo (2013)**, [Making NGSIM Data Usable for Studies on Traffic Flow Theory](https://doi.org/10.3141/2390-11), Transportation Research Record 2390 | Multiple outlier-correction and noise-filtering stages aiming to preserve driving dynamics. | Additional NGSIM measurement-error preprocessing precedent. | NOT the same article as already cited Montanino & Punzo (2015), BibTeX key montanino2015. |
| **Background** | **Flash & Hogan (1985)**, [The Coordination of Arm Movements](https://doi.org/10.1523/JNEUROSCI.05-07-01688.1985), Journal of Neuroscience 5(7):1688–1703 | Minimizes integral of squared jerk in **human arm movements**. | Historical physical motivation for smooth motion/minimum jerk. | Not proof all vehicle drivers minimize jerk, and not our nonzero-centered penalty. |
| **Cross-domain** | **Barratt, Kochenderfer & Boyd (2019)**, [Learning Probabilistic Trajectory Models of Aircraft in Terminal Airspace from Position Data](https://doi.org/10.1109/TITS.2018.2877572), IEEE T-ITS 20(9):3536–3545 | Model trajectory from aircraft radar positions, with acceleration/jerk quadratic smoothing formulation in the author's paper. | Optional adjacent-domain precedent for trajectory regularization. | Not automotive NGSIM data; do not prioritize over direct vehicle papers. |

## 4. Estimator comparability and mathematical connections

| Method | Data | Objective or modeling assumption | Genuine scientific competitor? |
| --- | --- | --- | --- |
| Paper C (currently tested) | Position only | Squared position residual + \(\lambda\|D_3\tau-\mu\mathbf1\|_2^2\) | Existing baseline; already compared to hard TSVD, natural cubic spline, Savitzky–Golay on frozen cases. |
| Fan-style constrained QP | Position, derivative bounds, position-error prior | Two-stage constrained quadratic programs; hard feasible speed/acceleration/jerk limits | Yes, only with correctly reproduced constraints and fair matching of data/validation. Not yet tested here. |
| Position-only jerk-driven Kalman/GP smoother | Position; assumed system + covariance parameters | Latent \(x,v,a,j\) dynamics; offline smoother and causal filter are separate procedures | Yes, if properly adapted to position-only observation. Nakazawa/Bisoffi original inputs differ. Not yet tested. |
| TV-regularized derivatives/jerk | Position; penalty selection policy | Nonsmooth regularization preserving abrupt derivative changes | Yes, if a **third derivative** is explicitly reconstructed and tuning is fair. Not yet tested. |
| V-spline | Position **plus independently measured velocity** | Adaptive acceleration-smooth spline | Not comparable without controlling extra data. |
| Zhang DSTE | Original video/scanline/spatiotemporal-map inputs | Upstream camera detections/tracking and quality refinement | Important *data-processing* prior, not plug-and-play single-series derivative baseline. |
| Full SVD of PLS normal equations | Exactly PLS inputs | Same solution to same quadratic | Not a different estimator; solver comparison only. Hard spectral truncation is distinct. |

**Possible generalized covariance-aware PLS, conceptual only:** When measurement errors and genuine third-difference innovations have covariance matrices \(\Sigma_\varepsilon\) and \(\Sigma_u\), respectively, an estimator could minimize

\[
(y-\tau)^\top\Sigma_\varepsilon^{-1}(y-\tau)
+(D_3\tau-\mu\mathbf1)^\top\Sigma_u^{-1}
(D_3\tau-\mu\mathbf1).
\]

This is the natural Gaussian generalized-PLS criterion **conditional on known positive-definite covariance matrices**; it does not imply the original Paper C experiment fitted these matrices or recovered true NGSIM error statistics. This connects Gaussian Bayesian smoothers, generalized least squares and state-space filtering.

## 5. Concrete editorial placements

1. **Introduction:** Expand existing generic Fan/Marczak/Punzo references to distinguish the **physically constrained third-order NGSIM trajectory reconstruction** literature from our unconstrained \(\mu\)-centered PLS. Mention the direct jerk estimator family (Nakazawa, Bisoffi) with clear differences in signals and causal versus historical inference.
2. **Methods, immediately after \(\|D_3\tau-\mu\mathbf1\|_2^2\):** State \(\mu=0\) means conventional minimum-jerk-centered roughness; nonzero \(\mu\) means shrinkage toward sustained nonzero discrete jerk. For mathematical background reference Flash & Hogan carefully as *arm* movement only, not proof for all cars.
3. **Other smoothers/numerical differentiation:** Reference van Breugel et al. (2020) alongside Ahnert--Abel and Chartrand. Cite PyNumDiff as a possible fair *future* framework, not a baseline used in Experiments004–008.
4. **Real NGSIM data section:** Add Shi--Liu and Zhang et al. as data-quality/reconstruction prior art, explain manually refined positions are a possible stronger observable reference, **not independent physical jerk**. Montanino--Punzo (2013) adds earlier multi-stage reconstruction precedent.
5. **Discussion/limitations:** Most close work has either hard feasibility constraints, different observed signals, or upstream camera corrections. Paper C's current evidence is *conditional* Gaussian \(S\)-calibration + known **synthetic** jerk reconstruction + descriptive 200-episode **recorded-position** forecasting, with an adverse spline-Taylor 0.3480 m first-second result.
6. **No shortcut:** Adding new references to canonical sections requires a source-matched Windows PDF, visual inspection, frozen-asset audit and refresh of the 16-file checksum inventory. Do not edit TeX/BibTeX without that build.

## 6. BibTeX candidates for the NEXT manuscript release

These seven entries are **proposed** and deliberately **not added** to references.bib yet. Bibliographic fields below were checked against accessible publisher, university or PubMed metadata; no paywalled full-text claim of algorithm details is made.

~~~bibtex
@article{nakazawa2003jerk,
  author={Nakazawa, Shin-ichi and Ishihara, Tadashi and Inooka, Hikaru},
  title={Real-time Algorithms for Estimating Jerk Signals from Noisy Acceleration Data},
  journal={International Journal of Applied Electromagnetics and Mechanics},
  year={2003}, volume={18}, pages={149--163}, doi={10.3233/JAE-2003-282}
}
@article{bisoffi2017jerk,
  author={Bisoffi, Andrea and Biral, Francesco and Da Lio, Mauro and Zaccarian, Luca},
  title={Longitudinal Jerk Estimation of Driver Intentions for Advanced Driver Assistance Systems},
  journal={IEEE/ASME Transactions on Mechatronics},
  year={2017}, volume={22}, number={4}, pages={1531--1541},
  doi={10.1109/TMECH.2017.2716838}
}
@article{vanbreugel2020,
  author={van Breugel, Floris and Kutz, J. Nathan and Brunton, Bingni W.},
  title={Numerical Differentiation of Noisy Data: A Unifying Multi-Objective Optimization Framework},
  journal={IEEE Access}, year={2020}, volume={8}, pages={196865--196877},
  doi={10.1109/ACCESS.2020.3034077}
}
@article{shi2019ngsim,
  author={Shi, Jianjun and Liu, Chenqiang},
  title={{NGSIM} Vehicle Trajectory Reconstruction},
  journal={Journal of Beijing University of Technology},
  year={2019}, volume={45}, number={6}, pages={601--609},
  doi={10.11936/bjutxb2017120020}
}
@article{zhang2024ngsim,
  author={Zhang, Tianya Terry and Jin, Peter J. and Piccoli, Benedetto and Sartipi, Mina},
  title={Deep Spatial-Temporal Embedding for Vehicle Trajectory Validation and Refinement},
  journal={Computer-Aided Civil and Infrastructure Engineering},
  year={2024}, volume={39}, pages={1597--1615},
  doi={10.1111/mice.13160}
}
@article{montanino2013,
  author={Montanino, Marcello and Punzo, Vincenzo},
  title={Making {NGSIM} Data Usable for Studies on Traffic Flow Theory: Multistep Method for Vehicle Trajectory Reconstruction},
  journal={Transportation Research Record},
  year={2013}, volume={2390}, doi={10.3141/2390-11}
}
@article{flashhogan1985,
  author={Flash, Tamar and Hogan, Neville},
  title={The Coordination of Arm Movements: An Experimentally Confirmed Mathematical Model},
  journal={The Journal of Neuroscience},
  year={1985}, volume={5}, number={7}, pages={1688--1703},
  doi={10.1523/JNEUROSCI.05-07-01688.1985}
}
~~~

**Publication verification boundary:** Zhang et al. (2024) has a journal-linked corrigendum, which should be reviewed before final journal publication. Source access here ranges from open publisher HTML to publisher abstracts and author records; this is a targeted verified literature scan, not a systematic full-text literature review. The proposed new methods are NOT additional completed experiments.

## 7. Scientific continuation and journal guardrails

Any separately authorized follow-up computational study should use the original archived cases (no rerunning Experiment004–008), predeclare baseline hyperparameters and train/test splits, preserve negative results, and use new sequential experiment numbering and a distinct immutable results archive. A review of original NGSIM camera frames versus manually corrected tracks might improve **position** validation, but neither is a sensor ground truth for physical jerk.

For citation insertion: use new scoped branch from live main; preserve original input hashes; trigger only the existing **manual** manuscript PC08 workflow; inspect all PDF pages and bibliography, update the source-matched PDF and canonical SHA-256 ledger using committed Git bytes; run Paper C tests and main CI; merge only after validation. No journal submission without separate author authorization.
