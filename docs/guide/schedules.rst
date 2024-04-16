Schedules
=========
.. currentmodule:: time_split

There are two types of :attr:`~types.Schedule`; bounded and unbounded. Any collection will be
interpreted as a bounded schedule. Unbounded schedules are either `cron` expressions, or a pandas
:ref:`offset alias <pandas:timeseries.offset_aliases>`.

* Bound schedules. These are always viable.

  >>> import pandas
  >>> schedule = ["2022-01-03", "2022-01-07", "2022-01-10", "2022-01-14"]
  >>> another_schedule = pandas.date_range("2022-01-01", "2022-10-10")

* Unbounded schedules. These must be made bounded by an `available` data argument.

  >>> cron_schedule = "0 0 * * MON,FRI"  # Monday and friday at midnight
  >>> offset_alias_schedule = "5d"  # Every 5 days

Bounded schedules are sometimes referred to as explicit schedules.

.. seealso:: The :doc:`../auto_examples/index` page.
