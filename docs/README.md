# Documentation development

The documentation is a Sphinx + Furo + MyST-NB site.

- The API reference is generated from Python docstrings via Sphinx autodoc
  (with Napoleon for NumPy-style docstrings). Update the source docstrings
  when an API signature or parameter meaning changes.
- Tutorials are real Jupyter notebooks under docs/examples. Keep examples
  deterministic and small; avoid remote downloads and large computations.
- The home page is a simple visual entry point; implementation details
  should live in docstrings and worked notebooks.
- The design system lives in docs/_static/css/custom.css and supports
  responsive layouts, dark mode, keyboard navigation and reduced motion.

## Build locally

Run from the repository root:

    python -m pip install -e ".[docs]"
    python -m sphinx -n -W --keep-going -b html docs docs/_build/html

View docs/_build/html/index.html. The three small deterministic notebooks
are executed during Sphinx builds (nb_execution_mode = "auto"); their
figures and numerical outputs are embedded in the generated HTML.
Open the .ipynb files in Jupyter to modify and rerun the examples.

## Release policy

This PR's workflow only validates the HTML build. It does not
publish GitHub Pages, Read the Docs or PyPI.


## Updating the API from docstrings

The source of truth for public API documentation is the Python docstring
next to its class, method, or function in `src/trendestimation/`. The
Sphinx reference page `docs/api.rst` uses `autoclass` and `autofunction`
directives; `sphinx.ext.autodoc` imports the package and reads those
docstrings whenever Sphinx builds the site.

**For an existing documented API item:**

1. Edit its NumPy-style source docstring, not a duplicate description in
   `docs/api.rst`. Include an accurate short summary, `Parameters`,
   `Returns` (or `Yields`), and, when appropriate, `Raises`, `Notes`,
   and a minimal `Examples` section.
2. Keep the written behavior synchronized with the function signature
   and implementation. In particular, distinguish in-sample smoothing
   and classical selection from forecasting or out-of-sample validation.
3. Run `python -m sphinx -n -W --keep-going -b html docs docs/_build/html`.
   Rebuilding automatically incorporates changes to **already referenced**
   classes, functions, and methods.
4. Examine `docs/_build/html/api.html` and inspect the rendered arguments,
   mathematics, and cross-references.

**For a new public function/class/method:** update `docs/api.rst` as well.
It currently lists public symbols and selected methods **explicitly**, so
new Python objects do not all appear in the website automatically. Link
new API items from the appropriate tutorial or notebook when helpful.

## Updating the Jupyter examples

The canonical executable tutorials are the three notebooks in
`docs/examples/`. Use seeded synthetic series and keep figures and
explanations matched to the current Python API. MyST-NB uses
`nb_execution_mode = "auto"` during a Sphinx build, so it executes
notebooks when needed and embeds generated outputs in the HTML.
Examples written **only inside a Python docstring** are rendered as
code/text; the standard HTML build does not independently run them as
doctests. Use the notebook tutorials or separate tests for executable
verification.

## Build vs deployment

- A change to an existing documented docstring updates the **generated
  API page on the next Sphinx build**, not instantly on GitHub.
- Pull requests modifying `src/**`, `docs/**`, or `pyproject.toml`
  trigger the Sphinx-check workflow. Passing CI means HTML was built;
  it does **not** mean a live documentation website was updated.
- The PR workflow uploads a downloadable HTML **preview artifact**.
- No public-site deployment is configured in this PR. To update a hosted
  website automatically after merging to `main`, a separate
  GitHub Pages or Read the Docs deployment must be approved and set up.
- Updating homepage copy, notebook instructions, styling, and navigation
  still requires editing their corresponding `docs/` source files.

## Review checklist

When changing an API, verify: (1) the source docstring describes actual
behavior, (2) `docs/api.rst` includes any new public symbol,
(3) associated notebooks still execute, (4) strict Sphinx build passes,
and (5) the preview looks correct on mobile and desktop. Do not infer
that a successful build has deployed the website.
