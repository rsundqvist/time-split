`Before` and `after` arguments
------------------------------
.. currentmodule:: time_split

The `before` and `after` :attr:`~types.Span` arguments determine how much data is included in the
**Data** (given by `before`)  and **Future data** (given by `after`) ranges of each fold.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Argument type
     - Interpretation
   * - String ``'all'``
     - Include all data before/after the scheduled time. Equivalent to ``max_train_size=None`` when using
       `TimeSeriesSplit`_.
   * - ``int > 0``
     - Include all data within `N` schedule periods from the scheduled time.
   * - Anything else
     - Passed as-is to the :class:`pandas.Timedelta` class. Must be positive. See
       :ref:`pandas:timeseries.offset_aliases` for valid frequency strings.

.. _TimeSeriesSplit: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
