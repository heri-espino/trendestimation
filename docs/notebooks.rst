Jupyter notebook tutorials
==========================

The notebooks are the **executable examples** for this library. They use
fixed random seeds and synthetic data, so they can be reproduced without
external data downloads.

These three short introduction tutorials complement the ten longer notebooks
in the :doc:`gallery`.

Start with the first notebook to fit a penalized trend, then explore
classical smoothing-parameter selection and the role of differencing order.
For an end-to-end pipeline that includes fixed 0.8 smoothness, historical
observations, extrapolation, six visualization methods and a separate
chronological holdout, visit :doc:`notebooks/10-forecast-pipeline` in the
:doc:`gallery`. The forecast is an illustrative conditional baseline.

.. note::

   When documentation execution is enabled, the site build runs these
   small, deterministic notebooks and embeds
   their SVG figures and outputs. The plotting style comes from pinned
   GitHub AwesomeFigures in ``docs/requirements-figures.txt``.
   Download the .ipynb files from the repository
   to explore the examples interactively in Jupyter.

.. toctree::
   :maxdepth: 1

   examples/01_first_trend
   examples/02_select_smoothness
   examples/03_difference_orders

Documentation conventions
-------------------------

The :doc:`api` pages are generated directly from Python **docstrings**
in the source package. Method signatures, parameters, and return types
should be edited in the Python source rather than duplicated
in hand-maintained reference pages.

Notebook examples illustrate existing software, not new forecast models.
The four classical in-sample criteria (CV, GCV, AICc, BIC) require a fixed
numeric reference mean. Gaussian marginal MLE is a separate selector that
also permits an observed-difference plug-in mean (``mu="data"``), without
jointly estimating that mean.

The short :doc:`examples/02_select_smoothness` tutorial and extended
:doc:`notebooks/09-gaussian-mle-and-guerrero-smoothness` chapter show
how to estimate *both* Gaussian variance components: observation noise
and latent differences of order d. The forecast-pipeline notebook uses
historical observations only; these are not forecast-error variances,
prediction intervals, or evidence of future forecast performance.
The selectors do not implement rolling or horizon-specific CV.
