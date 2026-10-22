# Contributing to trendestimation

Contributions are welcome, especially correctness checks, conditioning
experiments, reproducible benchmarks, and improvements to the documentation.
Discuss a substantial API change in an issue before implementation.

## Development setup

From the repository root:

```bash
python -m pip install -e '.[dev,docs,plot]'
python -m pytest -q
python -m ruff check src tests benchmarks
```

Before a release candidate, maintainers should also run:

```bash
python -m sphinx -b html docs docs/_build/html
python -m build
python -m twine check dist/*
python benchmarks/compare_banded.py
```

The numerical benchmark is manual. Its output depends on hardware,
BLAS/LAPACK implementation, sample length, difference order, and number
of smoothing-parameter evaluations.

## Research quality

- Add independent reference tests whenever numerical behavior changes.
- Distinguish in-sample smoothing from out-of-sample forecasting.
- Classical CV/GCV/AICc/BIC here assume fixed numeric `mu` and do not
  include re-estimation of the observed-difference plug-in mean.
- Report seeds, tolerances, data-generating processes, boundary conventions,
  numeric precision, and exact software versions for experiments.
- Attribute published Whittaker–Henderson, Guerrero, and Cortés-Toto methods
  to their authors; do not represent them as novel discoveries.
- Do not commit copyrighted journal PDFs, private financial data, secrets,
  access keys, or material you cannot license.
- Heavy experiments, report/PDF builds, benchmarks and publication remain
  manual. Lightweight lint/tests may run on every pull request.

## Pull requests

Work on a topic branch, update tests and documentation when necessary,
and describe the scientific impact of your changes. Update CHANGELOG.md
for user-visible behavior. Do not push directly to main.

By contributing original material you agree that it may be distributed
under this repository's MIT License.
