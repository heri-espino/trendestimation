"""Sphinx site with executable MyST notebooks and Furo theme."""
from __future__ import annotations

import os

project = "trendestimation"
author = "Heriberto Espino Montelongo"
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
html_title = "trendestimation | Scientific Python trend smoothing"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#1e4265",
        "color-brand-content": "#135b83",
    },
    "dark_css_variables": {
        "color-brand-primary": "#78bfeb",
        "color-brand-content": "#78bfeb",
    },
}
exclude_patterns = ["_build", ".DS_Store", "README.md"]
autodoc_typehints = "description"
nb_execution_mode = os.environ.get("TRENDESTIMATION_DOCS_EXECUTION", "auto")
nb_execution_timeout = 600
nb_execution_allow_errors = False
nb_execution_raise_on_error = True
nb_merge_streams = True
