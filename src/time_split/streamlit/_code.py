from pprint import pformat
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st
from rics.misc import format_kwargs

from time_split import split
from time_split._frontend._to_string import stringify
from time_split.types import DatetimeTypes


def show_code(
    split_kwargs: dict[str, Any],
    *,
    plot_kwargs: dict[str, Any],
    limits: tuple[DatetimeTypes, DatetimeTypes],
) -> None:
    st.subheader("Code", divider="rainbow")
    st.write(
        "Keyword dict (see [`DatetimeIndexSplitterKwargs`](https://time-split.readthedocs.io/en/stable/generated/time_split.types.html#time_split.types.DatetimeIndexSplitterKwargs))."
    )
    st.code(f"kwargs = {pformat(split_kwargs)}")

    split_rows = _get_rows(split_kwargs, limits)

    st.write(
        "Using [`time_split.split()`](https://time-split.readthedocs.io/en/stable/generated/time_split.html#time_split.split)."
    )
    st.code(f"splits = time_split.split({''.join(split_rows)}\n)")

    st.write(
        "Using [`time_split.plot()`](https://time-split.readthedocs.io/en/stable/generated/time_split.html#time_split.plot)."
    )
    extra = f"\n  # Plot-specific arguments.\n  {format_kwargs(plot_kwargs)}"
    st.code(f"splits = time_split.split({''.join(split_rows)}{extra}\n)")

    st.code(get_copy_paste(split_kwargs, limits=limits))


def get_copy_paste(
    split_kwargs: dict[str, Any],
    *,
    limits: tuple[DatetimeTypes, DatetimeTypes],
) -> str:
    module, _, cls = st.radio(
        "Select type for copy-paste output.",
        ["pandas.Timestamp", "datetime.datetime", "str"],
        horizontal=True,
    ).rpartition(".")

    if cls == "Timestamp":
        mapper = lambda ts: ts
    elif cls == "datetime":
        mapper = pd.Timestamp.to_pydatetime
    else:
        mapper = str

    splits = "".join(f"\n    {tuple(map(mapper, s))}," for s in split(**split_kwargs, available=limits))
    result = f"splits = [{splits}\n]"

    if module:
        result = f"from {module} import {cls}\n\n" + result

    if module == "datetime":
        result = result.replace("datetime.datetime", "datetime")

    return result


def _get_rows(split_kwargs: dict[str, Any], limits: tuple[DatetimeTypes, DatetimeTypes]) -> list[str]:
    keys = np.array_split(list(split_kwargs), 2)
    split_rows = [f"\n  {format_kwargs({k: split_kwargs[k] for k in kk})}," for kk in keys]
    available = tuple(map(stringify, limits))
    split_rows.append(f"\n  available={available},")
    return split_rows


def get_repro(split_kwargs: dict[str, Any], limits: tuple[DatetimeTypes, DatetimeTypes]) -> str:
    """Used in error messages."""
    split_rows = _get_rows(split_kwargs, limits)
    return f"splits = time_split.split({''.join(split_rows)}\n)"
