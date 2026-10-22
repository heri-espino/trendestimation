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

View docs/_build/html/index.html. Notebooks are not executed by Sphinx
(nb_execution_mode = "off"). Open each .ipynb file in Jupyter and
run its cells locally for figures and numerical outputs.

## Release policy

This PR's workflow only validates the HTML build. It does not
publish GitHub Pages, Read the Docs or PyPI.
