Jupyter notebook tutorials
==========================

The notebooks are the **executable examples** for this library. They use
fixed random seeds and synthetic data, so they can be reproduced without
external data downloads.

Start with the first notebook to fit a penalized trend, then explore
classical smoothing-parameter selection and the role of differencing order.

.. note::

   The HTML documentation displays notebook source without executing it
   during the Sphinx build. This keeps builds deterministic and lightweight.
   Download the .ipynb files from the repository and run them locally
   to generate figures and numerical outputs.

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
