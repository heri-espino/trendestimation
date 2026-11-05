# Source inventory, provenance, and verification level

Date: 2026-11-05. This is a Markdown source ledger for Paper C. The PDFs were supplied in the conversation for reading and are **not** redistributed or committed.

| Record | Basis actually inspected | Exact source and location | Confidence / caveat |
| --- | --- | --- | --- |
| Fan, Jin & Yin (2024) | Full abstract supplied by the author; public journal metadata/abstract; accessible ISTTT25 proceedings text | [Transportation Science 58(6):1371–1388](https://doi.org/10.1287/trsc.2024.0524), [ISTTT25 proceedings PDF](https://limos.engin.umich.edu/isttt25/wp-content/uploads/sites/3/sites/4/2024/06/ISTTT25-proceedings-050-min.pdf) | High for the two-step design, physical bounds, existence/uniqueness claim and NGSIM/highD validation reported by the authors. Do not infer numerical implementation details unverified against final journal full text. |
| Marczak & Buisson (2012) | User-provided 21-page TRB annual meeting manuscript; checked methods, Tables 1–3, figures and conclusion; publisher record | Supplied *MarczakBuisson2012-TRR-Issue2315-pp3546.pdf*; [published Transportation Research Record 2315:35–46](https://doi.org/10.3141/2315-04) | High for the supplied preprint. The preprint is not the publisher typeset version; cite final DOI and identify preprint page numbers explicitly. |
| Cao et al. (2021) | User-provided published 16-page Sensors article, equations (1)–(3), (10)–(15), (18), CV (20)–(22), simulations and tractor application | Supplied *sensors-21-03215-v2.pdf*; [Sensors 21(9),3215](https://doi.org/10.3390/s21093215) | High; position **and** velocity are inputs; acceleration is penalized, not jerk. |
| Zhu et al. (2024) | User-provided published 13-page Elsevier article, equations (1)–(11), Algorithm 1, CitySim assessment, discussion and conclusion | Supplied *1-s2.0-S0001457524000770-main.pdf*; [Accident Analysis & Prevention 200:107532](https://doi.org/10.1016/j.aap.2024.107532) | High; first uses ℓ2 filtering and consistency, second ℓ1 filtering, constrained acceleration/jerk; CitySim is its main experimental dataset. |
| Tang, Yoon & Barfoot (2019) | User-provided arXiv v2 source tarball extracted locally for reading; manuscript abstract, WNOJ construction and experimental conclusions | Supplied *arXiv-1809.06518v2.tar.gz*; [arXiv:1809.06518](https://arxiv.org/abs/1809.06518) | High for the archived LaTeX source, but journal bibliographic metadata/DOI are not independently certified in these notes; distinguish this paper from the later 2020 **A Data-Driven Motion Prior** article. |
| Guerrero (2007; 2008), Cortés-Toto et al. (2017) | Existing repository literature/extracted markdown and Paper C bibliography | [extracted literature corpus](https://github.com/heri-espino/Trend-Estimation/tree/main/literature/extracted); respective DOI links in [annotations](papers/guerrero_cortes_2007_2017.md) | Medium for formula transcriptions pending publisher-PDF confirmation; high for existence of the nonzero-mean model and studied smoothing criteria. |
| Punzo, Borzacchiello & Ciuffo (2011) | Indirect citations and bibliographies in uploaded Marczak and Zhu papers, not a direct full-text review in this pass | [Transportation Research Part C 19(6):1243–1262](https://doi.org/10.1016/j.trc.2010.12.007) | **Secondary-only.** Do not attribute detailed experimental numbers or claims until primary text checked. |

## Checkable locations inside uploaded papers

- **Marczak–Buisson TRB manuscript:** p.2 abstract; pp.4–6 earlier filters; p.7 Table 2 jerk/acceleration indicators; pp.8–10 I-spline construction; p.12 comparison setup; p.18 Table 3 jerk metrics; p.19 limitations and tuning fairness.
- **Cao Sensors:** pp.1–2 scope; pp.3–5 position/velocity objective and matrix form; pp.6–7 cross-validation; pp.7–9 synthetic results; pp.9–11 tractor GPS case; p.11 discussion.
- **Zhu AAP:** p.1 abstract; pp.3–5 optimization model and constraints, Algorithm 1; pp.6–7 CitySim quality controls; pp.8–10 four-step orders, physical checks; p.11 prediction test; p.12 conclusion.
- **Tang arXiv:** *main.tex* abstract/introduction; section *White-Noise-On-Jerk Motion Prior*; experiment evaluation; conclusion.
- **Fan:** online journal abstract and public proceedings PDF text; published online **22 August 2024** according to publisher. The author-supplied abstract and journal publisher agree on essential method.

## What has not been verified

1. Exhaustive international prior-art search (including theses, regional journals and unpublished preprints).
2. Full final publisher-version mathematics and supplementary material of Fan et al.
3. Reproduction of Fan/Cao/Zhu/Marczak/Tang algorithms in our code.
4. Any source-ground-truth NGSIM jerk signal.
5. Updated experimental performance on an independently chosen larger traffic dataset.

**No new physical data, benchmarks, plots, or simulations were produced by this reading-only task.**
