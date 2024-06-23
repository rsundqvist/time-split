from pprint import pformat
from typing import Any

import numpy as np
import streamlit as st

from time_split._frontend._to_string import stringify
from time_split.types import DatetimeTypes
from rics.misc import format_kwargs


def show_code(split_kwargs: dict[str, Any], *, plot_kwargs: dict[str, Any], limits: tuple[DatetimeTypes, DatetimeTypes]) -> None:
    st.caption(
        "Keyword dict (see [`DatetimeIndexSplitterKwargs`](https://time-split.readthedocs.io/en/stable/generated/time_split.types.html#time_split.types.DatetimeIndexSplitterKwargs))."
    )
    st.code(f"kwargs = {pformat(split_kwargs)}")

    keys = np.array_split(list(split_kwargs), 2)
    split_rows = [f"\n  {format_kwargs({k: split_kwargs[k] for k in kk})}," for kk in keys]
    available = tuple(map(stringify, limits))
    split_rows.append(f"\n  available={available},")

    st.caption(
        "Using [`time_split.split()`](https://time-split.readthedocs.io/en/stable/generated/time_split.html#time_split.split)."
    )
    st.code(f"splits = time_split.split({''.join(split_rows)}\n)")

    st.caption(
        "Using [`time_split.plot()`](https://time-split.readthedocs.io/en/stable/generated/time_split.html#time_split.plot)."
    )
    extra = f"\n  # Plot-specific arguments.\n  {format_kwargs(plot_kwargs)}"
    st.code(f"splits = time_split.split({''.join(split_rows)}{extra}\n)")
