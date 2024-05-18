Data limits
===========
.. currentmodule:: time_split

Data :attr:`~types.ExpandLimits` allows bounds inferred from and `available` data argument to stretch
**outward** slightly, toward the likely "real" limits of the data.

.. hint::

    See :func:`.support.expand_limits` for examples and manual experimentation.

.. list-table:: ExpandLimits options.
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

.. seealso:: The :doc:`../auto_examples/index` page.
