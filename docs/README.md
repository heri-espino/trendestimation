# Building the documentation

This is the source for the Sphinx site, using Furo, sphinx-design,
sphinx-copybutton, and MyST-NB. Jupyter notebooks are the canonical
worked examples; the site embeds the **same files**.

At the repository root:

```bash
python -m pip install -e '.[docs,plot]'
python -m pytest tests/test_notebook_gallery.py -q
python scripts/run_notebooks.py --list
python scripts/run_notebooks.py --fast --in-place --fail-fast
TRENDESTIMATION_DOCS_EXECUTION=off python -m sphinx -b html -W docs build/site
```

Open `build/site/index.html`. The command `--in-place` is intentionally
explicit: without it, executed notebooks and timing logs stay under `build/`
and are not part of tracked sources.

The GitHub Pages workflow runs only through `workflow_dispatch`, not
on each push, because notebook execution/plots can be costly. Review
the PR, configure Pages in GitHub Settings, then dispatch the workflow.

For user-machine cost reporting, use the `--watts` and
`--mxn-per-kwh` options only when measured or documented assumptions
are available.
