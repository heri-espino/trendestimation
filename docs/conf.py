"""Sphinx configuration for the trendestimation documentation."""

project = "trendestimation"
author = "Heriberto Espino-Montelongo"
release = "0.1.0a0"

extensions = [
    "sphinx.ext.autodoc",
    "myst_nb",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
autodoc_typehints = "description"
autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Render real Jupyter notebooks without running code in CI or site builds.
nb_execution_mode = "off"
html_theme = "furo"
html_title = "trendestimation — scientific trend smoothing"
html_short_title = "trendestimation"
html_show_sphinx = False
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_favicon = "_static/favicon.svg"

html_theme_options = {
    "source_repository": "https://github.com/heri-espino/trendestimation/",
    "source_branch": "main",
    "source_directory": "docs/",
    "light_css_variables": {
        "color-brand-primary": "#2159c7",
        "color-brand-content": "#2159c7",
        "color-admonition-background": "#f2f7ff",
    },
    "dark_css_variables": {
        "color-brand-primary": "#91b6ff",
        "color-brand-content": "#91b6ff",
    },
}
