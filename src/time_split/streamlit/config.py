from os import environ as _environ

import pandas as _pd

from time_split.types import DatetimeIndexSplitterKwargs as _Kwargs

MAX_SPLITS = int(_environ.get("MAX_SPLITS", 100))

PLOT_AGGREGATIONS_PER_FOLD: bool = _environ.get("PLOT_AGGREGATIONS_PER_FOLD", "").lower() != "false"
FIGURE_DPI: int = int(_environ.get("FIGURE_DPI", 75))


def get_server_config_info() -> str:
    return f"""
* `{MAX_SPLITS=}`: Controls the split count before filters are applied.
* `{PLOT_AGGREGATIONS_PER_FOLD=}`: Enable plots in the`📈 Aggregations per fold` tab.
* `{FIGURE_DPI=}`: Controls figure fidelity. Higher values look better, but is a lot slower.
"""


def enforce_max_splits(all_splits: int, kwargs: _Kwargs, limits: tuple[_pd.Timestamp, _pd.Timestamp]) -> None:
    import streamlit as st

    from ._code import get_repro

    if all_splits > MAX_SPLITS:
        st.error(f"Maximum number of splits ({MAX_SPLITS}) exceeded.", icon="🚨")
        st.code(get_repro(kwargs, limits))
        st.write(
            f"The snippet above produces `len(splits)={all_splits} > {MAX_SPLITS}=MAX_SPLITS`."
            " Try using different parameters to reduce the number of folds."
        )
        st.stop()
