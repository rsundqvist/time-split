Data limits
===========
.. currentmodule:: time_split

Data :attr:`~types.Flex` allows bounds inferred from and `available` data argument to stretch
**outward** slightly, toward the likely "real" limits of the data.

.. hint::

    See :func:`.support.expand_limits` for examples and manual experimentation.

.. list-table:: Flex options.
   :header-rows: 1
   :widths: 20 80

   * - Type
     - Description
   * - ``False``
     - Disable flex; use real limits instead.
   * - ``True`` or ``'auto'``
     - Auto-flex using :attr:`settings.auto_flex <settings.auto_flex>`-settings.

       Snap limits to the nearest :attr:`~.settings.auto_flex.hour` or :attr:`~.settings.auto_flex.day`, depending on
       the amount of `available` data. Use :meth:`settings.auto_flex.set_level <.settings.auto_flex.set_level>` to
       modify auto-flex behavior.

   * - ``str``
     - Manual flex specification.

       Pass an :ref:`offset alias <pandas:timeseries.offset_aliases>` specify how limits should be rounded. To specify
       by `how much` limits may be rounded, pass two offset aliases separated by a  ``'<'``.

       For example, passing ``flex="d<1h"`` will snap limits to the nearest date, but will not expand limits by more
       than one hour in either direction.
