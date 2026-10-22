trendestimation
===============

**A reproducible Python toolkit for penalized least-squares trend smoothing.**

Estimate trends using finite-difference penalties of arbitrary admissible
order, Guerrero's nonzero difference mean, and established smoothing selection
criteria. The **same executable Jupyter notebooks** drive the tutorials and
the documentation site.

.. grid:: 2
   :gutter: 2

   .. grid-item-card:: Quickstart
      :link: quickstart
      :link-type: doc

      Installation and your first penalized trend.

   .. grid-item-card:: Illustrated notebook gallery
      :link: gallery
      :link-type: doc

      Eight executable mathematical and computational walkthroughs.

   .. grid-item-card:: Mathematics
      :link: mathematics
      :link-type: doc

      Difference matrices, spectral diagonalization, and smoothness.

   .. grid-item-card:: Computing performance
      :link: benchmarks
      :link-type: doc

      Banded-versus-spectral timing and cost assumptions.

.. note::

   This pre-release implements **published in-sample methods** only.
   Experimental future-horizon TSCV, dynamic branch tracking, and
   forecast-optimal smoothing are intentionally excluded.

.. toctree::
   :maxdepth: 2
   :caption: Learn

   quickstart
   gallery
   mathematics
   benchmarks
   references

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
