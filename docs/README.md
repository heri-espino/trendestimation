# Building the documentation

This is the source for the Sphinx site, using Furo, sphinx-design,
sphinx-copybutton, and MyST-NB. Jupyter notebooks are the canonical
worked examples; the site embeds the **same files**.

At the repository root:

```bash
python -m pip install -e '.[docs,plot]'
python -m pip install -r docs/requirements-figures.txt
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
web/sRGB value `#003A70`) for Furo and notebook **decorations**,
visited links, active navigation and the landing page. To choose a new brand color, edit **one variable** near
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
The previous redundant `docs/_static/custom.css` was removed to prevent
conflicting definitions. The one editable brand color controls only
**interface decorations**: links, sidebar navigation, button surfaces,
notebook input left borders, charts and restrained decorative gradients.

**Python syntax highlighting is intentionally independent of the brand.**
Furo/Pygments applies the conventional multicolor syntax in notebook and
regular code cells, so strings, numbers, comments, operators and keywords
remain distinct. The homepage's dark inline example uses a separate
readable multicolor palette. Do not add `.highlight span[class]` or
similar rules that tint every code token navy.

The design uses sharp **90-degree corners** via `--te-radius: 0px`
and restrained editorial typography. Hover and opening transitions are
slower, while `docs/_static/js/reveal.js` adds one-time section reveals
during scrolling through progressive enhancement. Without JavaScript,
all content stays visible; users who request reduced motion see content
without scroll reveals or forced smooth scrolling.

The browser page title is exactly **trendestimation**, not a longer
marketing tagline. The landing page keeps a compact Python example and
omits duplicate tutorial prose below its navigation cards.

The home page retains keyboard focus, accessible reduced-motion support,
and responsive layouts. Semantic warnings/errors are not recolored as
brand accents.

Public API reference pages are generated from NumPy-style source docstrings
through Sphinx autodoc and Napoleon. Edit docstrings in
`src/trendestimation/` when signatures or behavior change; update
`docs/api.rst` when adding a public API object. Source docstring examples
are shown as text/code by Sphinx and are not automatically doctested.

There are two complementary tutorial collections:
- `docs/examples/`: three small introductory notebooks.
- `docs/notebooks/`: ten detailed research, benchmark, and forecast notebooks.

To preview the complete site with a warning-strict build, set
`TRENDESTIMATION_DOCS_EXECUTION=off` and build Sphinx. The
`docs-preview.yml` workflow uploads HTML for inspection but does not deploy
it. The separate manual Pages workflow executes the longer notebooks
when explicitly requested.


## Gaussian MLE variance-component examples

The public `estimate_variance_components` API provides Gaussian
observation-noise and latent difference variances (plus standard deviations).
These are not forecast-error variances, raw residual MSE, or prediction
intervals. The introductory selection notebook and the longer criteria,
nonzero-mean, spectral, applied, MLE and forecast-pipeline notebooks
show the estimator under its stated assumptions.

Notebook execution remains manual. To run the dedicated MLE chapter use:

```bash
python scripts/run_notebooks.py --fast --only 09-gaussian-mle-and-guerrero-smoothness --fail-fast
```

The forecast chapter only estimates variance components from historical
observations, without incorporating the held-out future values.

## AwesomeFigures SVG notebook plots

Every executable notebook configures the GitHub-only
[AwesomeFigures](https://github.com/awesomefigures/awesomefigures) package
as a Matplotlib style (``elegante``, Okabe–Ito categorical palette, DejaVu
Sans, no LaTeX, no deliberate artist rasterization). This affects how
figures look, **not** the trend estimation algorithms or statistical scores.

Its full Git commit is pinned in ``docs/requirements-figures.txt``. Install
it separately from ``.[docs,plot]``: keeping the VCS URL out of published
``pyproject.toml`` metadata avoids a PyPI direct-reference dependency and
keeps core numerical installations free of plotting requirements.

The first code cell in each notebook calls
``set_matplotlib_formats("svg")`` from ``matplotlib_inline.backend_inline``.
When executed inside Jupyter, the produced ``image/svg+xml`` output is
stored in the notebook and embedded as SVG in Sphinx, without storing PNG
screenshots. The automatic PR preview executes only the **three short introduction**
notebooks, saving SVG outputs in its ephemeral checkout for HTML preview;
its 10 longer computational research notebooks remain unexecuted.
The manual GitHub Pages workflow executes the 10 extended notebooks in
place and Sphinx ``auto`` execution fills in the three introductory ones.
Full gallery execution and deployment remain manual.

To render the complete site with new SVG plots, run from the repository root:

```bash
python -m pip install -e '.[docs,plot]'
python -m pip install -r docs/requirements-figures.txt
python scripts/run_notebooks.py --fast --in-place --fail-fast
TRENDESTIMATION_DOCS_EXECUTION=off python -m sphinx -W -b html docs build/site
```

Chapter 10 additionally exports standalone vector files when
``SAVE_SVG=True`` (default: False); the figure filenames end in ``.svg``.
The SVG container is scalable, but ``imshow``/image artists can embed
raster pixel data inside an SVG. Matplotlib text remains editable where
supported (``svg.fonttype='none'``). Generated figures are not committed
or deployed automatically.
