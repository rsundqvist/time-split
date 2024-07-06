from typing import Any, Literal, overload

from pandas import Timestamp

from .._backend._limits import LimitsTuple
from .._compat import fmt_sec
from ..settings import log_split_progress
from ..types import DatetimeSplitBounds, DatetimeTypes, ExpandLimits


@overload
def to_string(
    bounds: DatetimeTypes,
    __ignored0: DatetimeTypes,
    __ignored1: DatetimeTypes,
    /,
    *,
    format: str | None = None,
) -> str: ...


@overload
def to_string(
    start: tuple[DatetimeTypes, DatetimeTypes, DatetimeTypes],
    mid: Literal[None] = None,
    end: Literal[None] = None,
    /,
    *,
    format: str | None = None,
) -> str: ...


def to_string(
    bounds: DatetimeTypes | DatetimeSplitBounds | tuple[DatetimeTypes, DatetimeTypes, DatetimeTypes],
    mid: DatetimeTypes | None = None,
    end: DatetimeTypes | None = None,
    /,
    *,
    format: str | None = None,
) -> str:
    """Pretty-print a fold.

    .. code-block:: python
       :caption: Sample output.

       ('2021-12-30' <= [schedule: '2022-01-04' (Tuesday)] < '2022-01-04 18:00:00')

    Args:
        bounds: A fold tuple ``(start, mid, end)``, or just `start` (followed by `mid` and `end`).
        mid: Datetime-like. Must be ``None`` when `bounds` is a tuple.
        end: Datetime-like. Must be ``None`` when `bounds` is a tuple.
        format: A custom format to use. Use :attr:`~.settings.log_split_progress.FOLD_FORMAT` if ``None``, but note that
            only the `start`, `mid` and `end` keys are available to this function.

    Returns:
        Formatted bounds string.

    Raises:
        TypeError: If an incorrect number of timestamps are given.

    """
    if isinstance(bounds, tuple):
        if not (mid is None and end is None):
            raise TypeError(f"Too many arguments: {(bounds, mid, end)}.")
        start, mid, end = bounds
    else:
        if mid is None or end is None:
            raise TypeError(f"Too few arguments: {(bounds, mid, end)}.")
        start = bounds

    return (log_split_progress.FOLD_FORMAT if format is None else format).format(
        start=_PrettyTimestamp(start),
        mid=_PrettyTimestamp(mid),
        end=_PrettyTimestamp(end),
    )


def stringify(old: Timestamp, *, new: Timestamp | None = None, diff_only: bool = False) -> str:
    if new is None:
        return _PrettyTimestamp(old).auto

    original = f"{old} -> "
    if old == new:
        no_change = "<no change>"
        if diff_only:
            return no_change
        return original + no_change
    diff = (new - old).total_seconds()
    pretty_diff = f"{'+' if diff > 0 else '-'}{fmt_sec(abs(diff))}"

    if diff_only:
        return pretty_diff

    return original + f"{_PrettyTimestamp(new).auto} ({pretty_diff})"


class _PrettyTimestamp:
    def __init__(self, raw: DatetimeTypes) -> None:
        self.timestamp = Timestamp(raw)
        self._auto: str | None = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self.timestamp, name)

    def __str__(self) -> str:
        return str(self.timestamp)

    def __repr__(self) -> str:
        return repr(self.timestamp)

    def __format__(self, format_spec: str) -> str:
        return format(self.timestamp, format_spec)

    @property
    def auto(self) -> str:
        if self._auto is None:
            timestamp = self.timestamp.round("s")
            format_spec = (
                log_split_progress.AUTO_DATE_FORMAT
                if timestamp.normalize() == timestamp
                else log_split_progress.AUTO_DATETIME_FORMAT
            )
            self._auto = format(timestamp, format_spec)
        return self._auto


def format_expanded_limits(
    original: LimitsTuple,
    *,
    expanded: LimitsTuple | None = None,
    expand_limits: ExpandLimits,
) -> str:
    """Format expanded limits.

    Args:
        original: The original data limits.
        expanded: Expanded data limits. Derived based on `original` and `expanded_limits` if ``None``.
        expand_limits: Limits expansion spec.

    Returns:
        A string.
    """
    if expanded is None:
        from .._backend._limits import expand_limits as expand

        expanded = expand(original, spec=expand_limits)

    return (
        f"Available data limits have been expanded (since {expand_limits=}):\n"
        f"  start: {stringify(original[0], new=expanded[0])}\n"
        f"    end: {stringify(original[1], new=expanded[1])}"
    )
