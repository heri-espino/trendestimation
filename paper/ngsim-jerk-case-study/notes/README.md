# Paper C — literature review and annotated reading notes

**Status:** Research notes for the NGSIM/jerk case study, not a submitted paper or a claim of historical priority. Updated 2026-11-05.

**New extrapolation research handoff (2026-11-05):** Read [the nonzero-reference forecast research question](EXTRAPOLATION_RESEARCH_HANDOFF.md), [the exact fit-versus-extrapolation decomposition](EXTRAPOLATION_DECOMPOSITION.md), [alternative training-only reference means](MU_POLICY_CATALOG.md), and [the predeclared ablation plan](EXTRAPOLATION_ABLATION_PLAN.md). The broad claim “first PLS extrapolation” is not defensible: see [Biessy's 2025/2026 WH extrapolation method](papers/biessy_2026_extrapolation.md). **These are notes and hypotheses, not measured new results.**

Start with [the evidence-based review](LITERATURE_REVIEW.md), then the individual annotations below. The [earlier targeted novelty audit](../NOVELTY_AUDIT.md) is preserved for provenance; the notes here add the user's primary PDF manuscripts and Tang et al.'s LaTeX source. The [mathematical annotations](MATHEMATICAL_NOTES.md) and [manuscript checklist](MANUSCRIPT_PLAN.md) describe what to do with the literature rather than altering the existing results.

## Paper-by-paper notes

| Source | Role in Paper C | Notes |
| --- | --- | --- |
| Guerrero (2007, 2008); Cortés-Toto et al. (2017) | Prior mathematical/statistical model and criteria | [Guerrero / Cortés-Toto](papers/guerrero_cortes_2007_2017.md) |
| Marczak & Buisson (2012) | NGSIM I-spline filtering and jerk diagnostics | [Marczak & Buisson](papers/marczak_buisson_2012.md) |
| Cao et al. (2021) | Position/velocity V-spline, adaptive acceleration regularization and CV | [Cao et al.](papers/cao_2021.md) |
| Tang, Yoon & Barfoot (2019) | Continuous-time GP motion prior with white noise on jerk | [Tang et al.](papers/tang_2019.md) |
| Fan, Jin & Yin (2024) | Closest NGSIM/third-derivative constrained-QP predecessor | [Fan et al.](papers/fan_2024.md) |
| Zhu et al. (2024) | Two-stage quadratic/absolute trend filtering and physical constraints | [Zhu et al.](papers/zhu_2024.md) |
| Biessy (2025 online; 2026 volume) | Explicit Whittaker–Henderson extrapolation with zero-weight future samples and uncertainty | [Biessy (extrapolation)](papers/biessy_2026_extrapolation.md) |

## Reading rules

- **Source:** Report a finding only if supported by the supplied article, the extracted statistical literature, or a named publisher record. Identify whether the supplied item is a journal PDF, TRB draft, arXiv source archive, or an abstract.
- **Interpretation:** A comparison to our PLS estimator is a research annotation, not a quotation from the cited study.
- **Unknown:** When only a published abstract or proceedings version is available, do not describe uninspected main-article details as verified.
- **Citation:** Use the DOI/arXiv URL in each note. The supplied commercial PDFs and source tarball are **not committed**; the references and notes suffice for scholarly provenance.
- **Jerk:** Third differences of measured positions are estimates, not independently measured actual jerk. The reference mean is not necessarily physical truth.

## Current Paper C source of truth

- Model and data pipeline: [methods](../sections/methods.tex), [case-study README](../README.md), [run_case.py](../run_case.py).
- Existing **five-vehicle** pilot numbers: [generated forecast table](../generated/forecast_table.tex) and [empirical summary](../generated/empirical_summary.tex). They are descriptive and not rerun here.
- Intended publication scope: [publication map](../../PUBLICATION_MAP.md). Other manuscripts own numerical precision, cost theory and algorithm timing.
- Future study protocol: [manuscript plan](MANUSCRIPT_PLAN.md). Planned experiments are not measured results.

**Do not** treat a lowest jerk-amplitude curve as proven better jerk estimation: ground-truth jerk is unavailable for the recorded NGSIM trajectories.
