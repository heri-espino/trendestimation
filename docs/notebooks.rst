Jupyter notebook tutorials
==========================

The notebooks are the **executable examples** for this library. They use
fixed random seeds and synthetic data, so they can be reproduced without
external data downloads.

These three short introduction tutorials complement the nine longer notebooks
in the :doc:`gallery`.

Start with the first notebook to fit a penalized trend, then explore
classical smoothing-parameter selection and the role of differencing order.
For a complete workflow—historical observations, fixed smoothness of 0.8,
trend extrapolation, six visualization functions and genuine future holdout
errors—open :doc:`notebooks/09-forecast-pipeline` in the :doc:`gallery`.
The forecast methods are transparent extrapolation baselines, not methods
shown to be forecast-optimal.

.. note::

   When documentation execution is enabled, the site build runs these
   small, deterministic notebooks and embeds
   their figures and outputs. Download the .ipynb files from the repository
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
The select_lambda function uses classical in-sample criteria for fixed numeric
reference means; it does not perform rolling or horizon-specific validation.
