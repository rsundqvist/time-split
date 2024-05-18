Data limits expansion
=====================
.. currentmodule:: time_split

Data limits expansion allows bounds inferred from and `available` data argument to stretch
**outward** slightly, toward the likely "real" limits of the data.


.. code-block:: python

   from pandas import Timestamp
   from time_split.support import expand_limits

   limits = Timestamp("2019-05-11"), Timestamp("2019-05-11 22:05:30")

   expanded = expand_limits(limits, "d")
   assert expanded == (
       Timestamp('2019-05-11 00:00:00'),
       Timestamp('2019-05-12 00:00:00'),
   )


See :func:`.support.expand_limits` for more examples and manual experimentation.

.. list-table:: :attr:`~types.ExpandLimits` specification options.
   :header-rows: 1
   :widths: 20 80

   * - Type
     - Description
   * - ``False``
     - Disable expand_limits; use real limits instead.
   * - ``True`` or ``'auto'``
     - Auto-expand_limits using :attr:`settings.auto_expand_limits <settings.auto_expand_limits>`-settings.

       Snap limits to the nearest :attr:`~.settings.auto_expand_limits.hour` or :attr:`~.settings.auto_expand_limits.day`, depending on
       the amount of `available` data. Use :meth:`settings.auto_expand_limits.set_level <.settings.auto_expand_limits.set_level>` to
       modify auto-expand_limits behavior.

   * - ``str``
     - Manual expand_limits specification.

       Pass an :ref:`offset alias <pandas:timeseries.offset_aliases>` specify how limits should be rounded. To specify
       by `how much` limits may be rounded, pass two offset aliases separated by a  ``'<'``.

       For example, passing ``expand_limits="d<1h"`` will snap limits to the nearest date, but will not expand limits by more
       than one hour in either direction.

The :func:`~.support.expand_limits` function uses level tuples on the form ``(start_at, round_to, tolerance)`` internally.
These may be passed directly to ``expand_limits()``, but **not** to any other functions. Use the types above instead.
