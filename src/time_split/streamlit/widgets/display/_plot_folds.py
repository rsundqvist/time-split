from time import perf_counter
from typing import Any, Collection, Literal

import pandas as pd
import streamlit as st
from matplotlib.figure import Figure

from time_split import plot
from time_split._compat import fmt_sec
from time_split.streamlit._logging import log_perf
from time_split.streamlit import config
from time_split.streamlit.widgets.types import BarLabels, RemovedFolds, QueryParams
from time_split.types import DatetimeIndexSplitterKwargs, DatetimeIterable


class PlotFoldsWidget:
    def __init__(
        self,
        show_removed: bool | None = None,
        bar_labels: Collection[BarLabels] = (*BarLabels,),
    ) -> None:
        """Args:
        show_removed: Allow users to toggle showing removed folds if ``None``.
        bar_labels: Bar label choices made available to the user.
        """
        self._show_removed = show_removed
        self._bar_labels = tuple(bar_labels)

    def select(self) -> dict[str, Any]:
        query_show_removed = QueryParams.get().show_removed

        if self._show_removed is None:
            options = (False, True)
            if query_show_removed is None:
                options.index(False)

            show_removed = st.radio(
                "Show removed folds",
                options,
                index=options.index(False) if query_show_removed is None else options.index(query_show_removed),
                format_func=lambda b: RemovedFolds.SHOW if b else RemovedFolds.HIDE,
                horizontal=False,
            )
        else:
            show_removed = self._show_removed
            if query_show_removed is not None and query_show_removed != show_removed:
                raise ValueError(f"{QueryParams.get().show_removed=} is not allowed.")

        bar_labels = self._get_bar_labels()
        return {
            "show_removed": show_removed,
            "bar_labels": bar_labels,
        }

    @classmethod
    def plot(
        cls,
        split_kwargs: DatetimeIndexSplitterKwargs,
        available: pd.DataFrame | DatetimeIterable,
        show_removed: bool = True,
        bar_labels: str | list[tuple[str, str]] | bool = True,
    ) -> None:
        start = perf_counter()

        with st.spinner("Plotting folds"):
            ax = plot(
                **split_kwargs,
                available=available.index if isinstance(available, (pd.DataFrame, pd.Series)) else available,
                show_removed=show_removed,
                bar_labels=bar_labels,
            )
            assert isinstance(ax.figure, Figure)
            st.pyplot(ax.figure, clear_figure=True, dpi=config.FIGURE_DPI)

        seconds = perf_counter() - start

        # Record performance
        if isinstance(available, pd.DataFrame):
            msg = f"Created `fold` figure for data of `shape={available.shape}` in `{fmt_sec(seconds)}`."
            log_perf(
                msg,
                available,
                seconds,
                extra={"show_removed": show_removed, "bar_labels": bar_labels, "figure": "folds"},
            )
            st.caption(msg)

    def _get_bar_labels(self) -> str | Literal[False]:
        options = self._bar_labels
        bar_labels = st.radio("Select bar labels", options, index=options.index(BarLabels.HOURS), horizontal=False)
        assert bar_labels is not None
        return False if bar_labels == BarLabels.DISABLED else bar_labels.name.lower()
