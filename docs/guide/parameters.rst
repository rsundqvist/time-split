Parameter overview
------------------
.. currentmodule:: time_split

Overview of parameters used by :func:`time_split.split` and :func:`plot`. Integrations such as
:func:`~integration.pandas.split_pandas` may add or remove parameters, but the base function remains the same unless
otherwise stated.

.. list-table::
   :widths: 5 10 10 75
   :header-rows: 1

   * - Name
     - Default
     - Type
     - Description

   * - ``schedule``
     - N/A
     - Valid :attr:`~types.Schedule` types:

       * :attr:`~types.DatetimeIterable`
       * pandas :ref:`offset alias <pandas:timeseries.offset_aliases>`
       * `cron <https://pypi.org/project/croniter/>`_ expression
     - Generates training dates (:attr:`.DatetimeSplitBounds.mid`). **Examples:**

       * ``'7d'`` | *every 7 days, aligned to the end of the available data.*
       * ``'0 0 * * MON,FRI'`` | *every Monday and Friday at midnight.*
       * ``['2019-05-04', '2019-05-11']`` | *Hand-picked dates.*

   * - | ``before``
       | ``after``
     - | = `'7d'`
       | = `1`
     - Valid :attr:`~types.Span` types:

       * pandas :ref:`offset alias <pandas:timeseries.offset_aliases>`
       * Literal `'all'`
       * ``int >= 1``
     - Range before/after schedule timestamps.

       The **default** ``after=1`` :ref:`stretches <sphx_glr_auto_examples_list_schedule_no_data.py>` the
       :attr:`Future data <.DatetimeSplit.future_data>` until the next `schedule` timestamp, simulating models staying
       in production until a new model takes its place. That is, ``fold[i].end = fold[i + 1].mid`` for ``after=1``.

   * - ``step``
     - = `1`
     - ``int >= 1``
     - Keep every `step:th` fold in the `schedule`. **Default (1)** =keep all.

   * - ``n_splits``
     - = `0`
     - ``int >= 0``
     - Maximum number of folds. **Default (0)** =keep all.

   * - ``available``
     - = ``None``
     - :attr:`~types.DatetimeIterable`
     - Limits ``(min, max)``, or an iterable of datetime-like types that support the built-in :py:func:`min` and
       :py:func:`max` functions. Binds `schedule` to a range.

   * - ``flex``
     - = `'auto'`
     - :attr:`~types.Flex`
     - Expand `available` data to its likely `"true"` limits. **Example**: ``flex='d<3h'`` expands the
       ``(min, max)``-tuple derived from `available` to the nearest day, at most 3 hours from the original limit.

       See :func:`.expand_limits` for examples or to experiment with flex behavior.

Later folds are always [#]_ preferred. For more information about the `schedule`, `before/after` and `flex`-arguments,
see the :ref:`User guide`. See the :doc:`../auto_examples/index` page for plots using the various parameter options.

.. rubric:: Footnotes

.. [#] This is :attr:`configurable <time_split.settings.misc.snap_to_end>` when `schedule` and `after` are both
       :attr:`timedelta <time_split.types.TimedeltaTypes>` types.
