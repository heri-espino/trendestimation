"""Sphinx site with executable MyST notebooks and Furo theme."""
from __future__ import annotations

import os

project = "trendestimation"
author = "Heriberto Espino-Montelongo"
copyright = "2026, Heriberto Espino-Montelongo"
release = "0.1.0a0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx_design",
    "sphinx_copybutton",
    "myst_nb",
]
html_theme = "furo"
html_title = "trendestimation — scientific trend smoothing"
html_short_title = "trendestimation"
html_show_sphinx = False
html_static_path = ["_static"]
html_css_files = ["custom.css", "css/custom.css"]
html_favicon = "_static/favicon.svg"
html_theme_options = {
    "source_repository": "https://github.com/heri-espino/trendestimation/",
    "source_branch": "main",
    "source_directory": "docs/",
    "light_css_variables": {
        "color-brand-primary": "#1e4265",
        "color-brand-content": "#135b83",
    },
    "dark_css_variables": {
        "color-brand-primary": "#78bfeb",
        "color-brand-content": "#78bfeb",
    },
}
exclude_patterns = ["_build", ".DS_Store", "Thumbs.db", "README.md"]
autodoc_typehints = "description"
autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = True
nitpick_ignore_regex = [
    ("py:class", r"^(?:array_like|numpy\.ndarray|matplotlib\.axes\.Axes|optional|default=.*|\{.*|\".*)$"),
]
nb_execution_mode = os.environ.get("TRENDESTIMATION_DOCS_EXECUTION", "auto")
nb_execution_timeout = 600
nb_execution_allow_errors = False
nb_execution_raise_on_error = True
nb_merge_streams = True
