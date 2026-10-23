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
marketing tagline. The main document element, `#furo-main-content`, now
fades into view on navigation, while the sidebar stays visually stationary.
Sidebar groups still animate when explicitly expanded or collapsed.
Notebook input boxes have no enclosing gray borders; standard non-notebook
code blocks retain their usual styling. The landing page keeps a compact Python example and
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


## Sidebar navigation, page transitions, and API sections

Furo uses separate colors for ordinary content links, visited links, and
**top-level sidebar links**. These are all mapped to the single restrained
navy-derived `--te-link` token in
`docs/_static/css/custom.css`; the other controls still derive from
`--te-brand`. Regular sidebar labels are neutral; selected navigation
and content links use muted navy. The code syntax palette remains
independent of the brand colors.

`docs/_static/js/sidebar.js` uses Furo's existing checkbox state and a
short height/opacity animation to expand and collapse subtrees. It does
not intercept navigation, modify URLs, or disrupt browser history.
A short CSS entrance transition applies after each regular page load.
Both effects respect `prefers-reduced-motion`; pages remain functional
without JavaScript.


The disclosure labels also support Tab, Enter and Space, expose
``aria-expanded`` state, and show a visible keyboard focus outline.
This enhancement works even when the Web Animations API is unavailable;
the existing ``sidebar.js`` remains the only animation controller.

The `docs/api.rst` landing page links to independent
`docs/api/{core,selection,variances,forecasting,simulation,visualization}.rst`
pages, each containing **Sphinx autodoc directives**. Public signatures
and behavior stay sourced from Python docstrings. Update
`docs/api.rst` and one of the section files when the public API changes.
Complexity formulas in mathematical/benchmark pages use MathJax
`:math:\`\\mathcal{O}(n)\`` rather than raw `O(n)` text.

## AwesomeFigures SVG notebook plots

Every executable notebook configures the GitHub-only
[AwesomeFigures](https://github.com/awesomefigures/awesomefigures) package
as a Matplotlib style (``elegante``, Okabe–Ito categorical palette, DejaVu
Sans, no LaTeX, no deliberate artist rasterization). The site uses **the
same DejaVu Sans 2.37 family**: Furo's body and heading font stacks are
explicitly set, and the browser loads version-pinned Fontsource DejaVu
Sans faces from jsDelivr when no matching local font is installed.
External SVG images cannot inherit that website CSS, so their Matplotlib
labels are saved as vector glyph paths (``svg.fonttype="path"``). The
figures retain scalable vector rendering and exact DejaVu letter shapes
even on machines lacking the font. These outlined labels are **not**
selectable/searchable SVG text; canvas descriptions and captions remain
real HTML text. A browser without CDN access falls back to the local
DejaVu font, if installed, or Arial, so complete web-page matching cannot
be guaranteed offline.
After loading AwesomeFigures,
all 13 notebooks call ``apply_documentation_figure_style()`` from
``trendestimation._docs_style`` to enlarge typography consistently:
16 pt body, 19 pt axes titles, 17 pt labels, 14 pt ticks, 15 pt legends
and 21 pt figure titles. The forecasting plot utilities now respect these
values rather than forcing 8-9 pt labels. The statistical algorithms,
data, selection criteria, and numerical outputs are unchanged.

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
raster pixel data inside an SVG. Figure text from Matplotlib is outlined
(``svg.fonttype='path'``), not editable/searchable text. Generated figures
are not committed or deployed automatically.

### Rebuilding figures after typography changes

SVG plots are generated from notebook execution, not re-styled afterward
like HTML text. An older deployed SVG remains unchanged until the
corresponding notebook has been executed again and Sphinx HTML rebuilt.
The PR preview automatically executes the three introductory notebooks,
but the ten longer notebooks and Pages deployment remain manual-only:

```bash
python -m pip install -e '.[docs,plot]'
python -m pip install -r docs/requirements-figures.txt
python scripts/run_notebooks.py --fast --in-place --fail-fast
TRENDESTIMATION_DOCS_EXECUTION=off python -m sphinx -W -b html docs build/site
```

The plotting font is reproducible because DejaVu Sans is bundled with
Matplotlib. The Sphinx site requests the same font and fetches a pinned
Fontsource webfont over HTTPS when it is not locally installed. Without
webfont access, the website uses its configured fallback while SVG
glyph outlines retain the intended font. No font binaries are checked into
the repository. Rebuild the notebooks and redeploy the site manually to
replace previously cached SVG figures; CSS alone cannot change those files.

## Naive versus cached spectral benchmark

The [computation guide](benchmarks.rst) explains the one-time full SVD,
its asymptotic costs, reuse for EDF/smoothness, RSS-based criteria,
and exact LOOCV via cached leverages. It distinguishes a deliberately
naive dense implementation from the separate banded-solver benchmark.
Run `python docs/examples/naive_vs_spectral.py` from the repository
root for a seeded apples-to-apples CV/GCV comparison; scores are
checked for numerical agreement before times are printed. Setup and
repeated candidate scoring are reported separately. The benchmark is
manual-only and is not executed as part of CI or Sphinx builds.


## Mathematics in notebook Markdown

MyST-NB does not interpret `$...$` as math unless the MyST
`dollarmath` extension is explicitly enabled. `docs/conf.py` configures
`myst_enable_extensions = ["dollarmath", "amsmath"]` alongside
`sphinx.ext.mathjax`. Write notebook **Markdown cells** using standard
LaTeX (no Unicode pseudo-equations, no screenshots):

- Inline: `$\lambda=\sigma_\varepsilon^2/\sigma_\eta^2$`
- Display: a separate `$$` line, a LaTeX formula, then another `$$` line
- Aligned environments: standard `\begin{align}...\end{align}`

Example Markdown cell:

~~~markdown
The penalty is $\lambda=\sigma_\varepsilon^2/\sigma_\eta^2$.

$$
\widehat{\sigma}_\varepsilon^2 =
\frac{1}{n-d}\sum_{j=1}^{n-d}\frac{z_j^2}{c_j}.
$$
~~~

MyST parses the math into Sphinx equation nodes; MathJax then typesets
the HTML in the browser. This is **separate from Matplotlib / SVG
figure typography**: `svg.fonttype="path"` affects only labels inside
generated figures, not mathematical Markdown in Jupyter notebooks.

A strict Sphinx build can succeed even when math delimiters are shown
literally. The Sphinx preview workflow therefore also runs
`python scripts/check_rendered_notebook_math.py build/site` to assert
that actual equation nodes occur in the built HTML. It does not execute
the computational notebook cells. Refresh or republish Sphinx after
merging to make these changes visible on the public site.
