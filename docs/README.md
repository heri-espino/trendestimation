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

## Design and API maintenance

The site uses a single **Pantone 2955 C-inspired navy** (approximate
web/sRGB value `#003A70`) throughout Furo, the notebook gallery,
Pygments code highlighting, visited links, active navigation and the
landing page. To choose a new brand color, edit **one variable** near
the top of `docs/_static/css/custom.css`:

```css
:root {
  --te-brand: #003A70; /* choose your single accent here */
}
```

All light/dark UI accent shades are derived from this token with
`color-mix()`. Neutral background, body text and nonsemantic gray
elements remain neutral for readability. The favicon SVG is a fixed
matching illustration; if you change the brand color, update the
icon's fill to match.

Sphinx loads this **single CSS file** in `docs/conf.py`.
The previous redundant `docs/_static/custom.css` is removed to prevent
conflicting definitions. Code-cell input borders, Pygments token colors,
sidebar links, visited links, buttons and subtle monochromatic gradients
share the same family. Syntax remains readable in Furo light/dark modes;
no green or purple is used as a decorative brand accent.

The home page retains accessible keyboard focus, reduced-motion support,
and responsive layouts. Colors used as semantic warnings/errors are not
redefined as brand accents.

Public API reference pages are generated from NumPy-style source docstrings
through Sphinx autodoc and Napoleon. Edit docstrings in
`src/trendestimation/` when signatures or behavior change; update
`docs/api.rst` when adding a public API object. Source docstring examples
are shown as text/code by Sphinx and are not automatically doctested.

There are two complementary tutorial collections:
- `docs/examples/`: three small introductory notebooks.
- `docs/notebooks/`: eight detailed research and benchmark notebooks.

To preview the complete site with a warning-strict build, set
`TRENDESTIMATION_DOCS_EXECUTION=off` and build Sphinx. The
`docs-preview.yml` workflow uploads HTML for inspection but does not deploy
it. The separate manual Pages workflow executes the longer notebooks
when explicitly requested.
