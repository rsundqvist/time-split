from dataclasses import dataclass, field
from enum import StrEnum
from time import perf_counter
from typing import Any, Literal

import pandas as pd
import streamlit as st

from time_split import plot
from time_split._compat import fmt_sec
from time_split.streamlit._logging import log_perf
from time_split.streamlit.config import FIGURE_DPI
from time_split.types import DatetimeIndexSplitterKwargs, DatetimeIterable


class BarLabels(StrEnum):
    """Bar label choices."""

    DAYS = ":calendar: Days"
    HOURS = ":alarm_clock: Hours"
    ROWS = ":bar_chart: Row count"
    DISABLED = ":ghost: Hide"


class RemovedFolds(StrEnum):
    SHOW = ":ghost: Show"
    HIDE = ":no_entry_sign: Hide"


@dataclass(frozen=True)
class PlotFoldsWidget:
    show_removed: bool | None = None
    """Allow users to toggle showing removed folds if ``None``."""
    bar_labels: set[BarLabels] | Literal[False] = field(default_factory=lambda: list(BarLabels))
    """Bar label choices made available to the user. Set to ``False`` to disable."""

    def configure(self) -> dict[str, Any]:
        show_removed = self.show_removed
        if show_removed is None:
            show_removed = st.radio("Removed folds", RemovedFolds, horizontal=True)

        bar_labels = self._get_bar_labels()

        return {"show_removed": show_removed == RemovedFolds.SHOW, "bar_labels": bar_labels}

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
            st.pyplot(ax.figure, clear_figure=True, dpi=FIGURE_DPI)

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
        if not self.bar_labels:
            return False

        bar_labels = st.radio("Bar labels", self.bar_labels, horizontal=True)
        return False if bar_labels == BarLabels.DISABLED else bar_labels.name.lower()


PlotFoldsWidget.BarLabels = BarLabels
