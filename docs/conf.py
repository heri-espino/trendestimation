"""Sphinx configuration for the independent release package."""
project = "trendestimation"
author = "Heriberto Espino Montelongo"
release = "0.1.0a0"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]
html_theme = "furo"
exclude_patterns = ["_build"]
autodoc_typehints = "description"
