User guide
==========
High-level overview of relevant concepts. Click a topic on the left for details, or continue reading for a high-level
overview. For a summary of all :func:`time_split.split`-parameters, see the `overview <parameters.rst>`_ page.

.. seealso:: The :doc:`../auto_examples/index` page.

Types
-----
.. currentmodule:: time_split

A single fold is a 3-tuple of `bounds` ``(start, mid, end)`` (type :attr:`~types.DatetimeSplitBounds`). A list thereof
are called `'splits'` (type :attr:`~types.DatetimeSplits`).

Conventions
-----------
- The **'mid'** timestamp is assumed to be the (simulated) training date, and
- **Data** is restricted to ``start <= data.timestamp < mid``, and
- **Future data** is restricted to ``mid <= future_data.timestamp < end``.

Guarantees
-----------
* Splits are strictly increasing: For all indices ``i``,  ``splits[i].mid < splits[i+1].mid`` holds.
* Timestamps within a fold are strictly increasing: ``start[i] < mid[i] < end[i]``.
* If `available` data is given **and** ``expand_limits=False`` [#expand_limits]_, no part of any fold will lie outside the available range.
* Later folds are always preferred (see the `skip` and `n_folds`-arguments).

Limitations
-----------
* **Data** and **Future data** from different folds may overlap, depending on the split parameters.
* Date restrictions apply to ``min(available), max(available)``. Sparse data may create empty folds.
* :attr:`~types.Schedule` and :attr:`~types.Span` arguments (before/after) must be strictly positive.

.. toctree::
   :glob:
   :hidden:

   *

.. rubric:: Footnotes

.. [#expand_limits] By default, bounds derived from `available` data is flexible. See :ref:`Data limits expansion` for details.
