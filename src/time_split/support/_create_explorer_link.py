from datetime import datetime
from typing import Any, Unpack
from urllib.parse import ParseResult, urlencode, urlparse, urlunparse

from .._backend import DatetimeIndexSplitter
from .._docstrings import docs
from ..types import DatetimeIndexSplitterKwargs, DatetimeIterable


@docs
def create_explorer_link(
    host: str,
    data: DatetimeIterable | str | None = None,
    available: DatetimeIterable | str | None = None,
    *,
    show_removed: bool = True,
    skip_default: bool = False,
    **kwargs: Unpack[DatetimeIndexSplitterKwargs],
) -> str:
    """Create a `Time Fold Explorer` application URL.

    Args:
        host: Base address where the application is hosted.
        data: {available} Regular `available` arguments (as passed to e.g. :func:`time_split.split`) are encoded as
            a date range to generate dummy data for. Pass a ``str`` to use dataset bundled by the server instead. Note
            that this function cannot verify the `kwargs` if `available` is a ``str`` dataset.
        available: Alias of `data`.
        skip_default: If ``True``, do not include default split params in the link.
        show_removed: {show_removed}
        kwargs: Keyword arguments for the :func:`time_split.split`-function.

    Returns:
        An encoded URL.

    Examples:
        Getting the URL for a local host.

        >>> create_explorer_link(
        ...     host="http://localhost:8501",
        ...     available=("2019-04-11 00:35:00", "2019-05-11 21:30:00"),
        ...     schedule="0 0 * * MON,FRI",
        ... )
        'http://localhost:8501?data=1554942900-1557610200&schedule=0+0+%2A+%2A+MON%2CFRI&show_removed=True'

        To start the application using locally using |image| Docker, run

        .. code-block:: bash

           docker run -p 8501:8501 rsundqvist/time-split

        in the terminal.

        .. |image| image:: https://img.shields.io/docker/image-size/rsundqvist/time-split/latest?logo=docker&label=time-split
                   :target: https://hub.docker.com/r/rsundqvist/time-split/
                   :alt: Docker Image Size (tag)
    """
    if sum([data is None, available is None]) != 1:
        raise ValueError("Exactly one of `data` and `available` must be given.")
    if data is None:
        data = available

    assert data is not None  # noqa: S101
    pr = _create_explorer_link(host, data, show_removed=show_removed, skip_default=skip_default, **kwargs)
    return urlunparse(pr)


def _create_explorer_link(
    host: str,
    data: DatetimeIterable | str,
    *,
    show_removed: bool = True,
    skip_default: bool = False,
    **kwargs: Unpack[DatetimeIndexSplitterKwargs],
) -> ParseResult:
    query = _create_query(data, skip_default=skip_default, show_removed=show_removed, kwargs=kwargs)

    pr: ParseResult = urlparse(host)  # scheme netloc path params query fragment
    if pr.query:
        raise ValueError(f"Bad {host=}; query={pr.query!r} is not allowed.")
    return pr._replace(query=urlencode(query))


def _create_query(
    data: DatetimeIterable | str,
    *,
    skip_default: bool,
    show_removed: bool,
    kwargs: DatetimeIndexSplitterKwargs,
) -> dict[str, Any]:
    query: dict[str, Any] = {}

    if isinstance(data, str):
        query = {"data": data, **kwargs}
    else:
        splitter = DatetimeIndexSplitter(**kwargs)
        _, ms = splitter.get_plot_data(data)
        query["data"] = _get_data_param(*ms.available_metadata.limits)

        if skip_default:
            schedule = kwargs["schedule"]
            query["schedule"] = schedule

            default = DatetimeIndexSplitter(schedule).as_dict()
            no_defaults = {
                key: value
                for key, value in kwargs.items()
                if value != default[key]  # type: ignore[literal-required]
            }
            query.update(no_defaults)
        else:
            query.update(kwargs)

    query["show_removed"] = show_removed
    return query


def _get_data_param(start: datetime, end: datetime) -> str:
    return f"{int(start.timestamp())}-{int(end.timestamp())}"
