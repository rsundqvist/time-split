"""Types related to splitting data."""

import datetime as _dt
import typing as _t

import numpy as _np
import pandas as _pd

DatetimeTypes: _t.TypeAlias = str | _pd.Timestamp | _dt.datetime | _dt.date | _np.datetime64
"""Types that may be cast to :class:`pandas.Timestamp`."""
DatetimeIterable = _t.Iterable[DatetimeTypes]
"""Iterable that may be cast to :class:`pandas.DatetimeIndex`."""
TimedeltaTypes: _t.TypeAlias = str | _pd.Timedelta | _dt.timedelta | _np.timedelta64
"""Types that may be cast to :class:`pandas.Timedelta`."""

Schedule: _t.TypeAlias = _pd.DatetimeIndex | DatetimeIterable | TimedeltaTypes
"""User schedule type."""
Span = int | _t.Literal["all"] | TimedeltaTypes
"""User span type. Used to determine limits from the timestamps given by a :attr:`Schedule`."""
Flex = bool | _t.Literal["auto"] | str
"""Flexibility frequency string for ``floor/ceil``. Pass ``False`` to disable."""


class DatetimeSplitBounds(_t.NamedTuple):
    """A 3-tuple which denotes two adjacent datetime ranges."""

    start: _pd.Timestamp
    """Left (inclusive) limit of the `data` range."""
    mid: _pd.Timestamp
    """Schedule timestamp; simulated :attr:`~.DatetimeSplit.training_date`.

    Right (exclusive) limit of the `data` range, left (inclusive) limit of the `future_data` range.

    When using :mod:`.integration` functions, These are available as :attr:`.DatetimeSplit.data` and
    :attr:`.DatetimeSplit.future_data`, respectively.
    """
    end: _pd.Timestamp
    """Right (exclusive) limit of the `future_data` range."""


DatetimeSplits = list[DatetimeSplitBounds]
"""A list of bounds."""


class DatetimeSplitCounts(_t.NamedTuple):
    """Relative importance of `data` and `future_data`."""

    data: int
    future_data: int


class DatetimeIndexSplitterKwargs(_t.TypedDict, total=False):
    """Keyword arguments for :class:`~time_split.support.DatetimeIndexSplitter`.

    The ``DatetimeIndexSplitter`` is a backend implementation. In most cases, it should not be used directly. See
    :func:`time_split.split` or one of the related functions for user-facing APIs.
    """

    schedule: _t.Required[Schedule]
    before: Span
    after: Span
    step: int
    n_splits: int
    flex: Flex
