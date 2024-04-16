`Before` and `after` arguments
------------------------------
.. currentmodule:: time_split

The `before` and `after` :attr:`~types.Span` arguments determine how much data is included in the
**Data** (given by `before`)  and **Future data** (given by `after`) ranges of each fold.

.. list-table::
   :header-rows: 1

   * - Argument type
     - Interpretation
     - Example
   * - String ``'all'``
     - Include all data before/after the scheduled time. Similar to
       `sklearn.model_selection.TimeSeriesSplit(max_train_size=None) <https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html>`_
     - :ref:`sphx_glr_auto_examples_cron_schedule_keep_all_before.py`
   * - ``int > 0``
     - Include all data within `N` schedule periods from the scheduled time.
     - :ref:`sphx_glr_auto_examples_n_splits_dynamic_before_and_after.py`
   * - Anything else
     - Passed as-is to the :class:`pandas.Timedelta` class. Must be positive. See
       :ref:`pandas:timeseries.offset_aliases` for valid frequency strings.
     - :ref:`sphx_glr_auto_examples_timedelta_schedule_and_after.py`

.. seealso:: The :doc:`../auto_examples/index` page.
