from dataclasses import dataclass, field
from enum import StrEnum
from time import perf_counter
from typing import Any, Literal

import pandas as pd
import streamlit as st

from time_split import plot
from time_split._compat import fmt_sec
from time_split.streamlit._logging import log_perf
from time_split.types import DatetimeIndexSplitterKwargs, DatetimeIterable


class BarLabels(StrEnum):
    """Bar label choices."""

    DAYS = ":calendar: Days"
    HOURS = ":alarm_clock: Hours"
    ROWS = ":bar_chart: Row count"
    DISABLED = ":ghost: Hide"


@dataclass(frozen=True)
class PlotFoldsWidget:
    show_removed: bool | None = None
    """Allow users to toggle showing removed folds if ``None``."""
    bar_labels: set[BarLabels] | Literal[False] = field(default_factory=lambda: list(BarLabels))
    """Bar label choices made available to the user. Set to ``False`` to disable."""

    def plot(
        self,
        split_kwargs: DatetimeIndexSplitterKwargs,
        available: pd.DataFrame | DatetimeIterable,
    ) -> dict[str, Any]:
        start = perf_counter()

        with st.popover("Configure plot"):
            show_removed = self.show_removed
            if show_removed is None:
                show_removed = st.toggle(":ghost: Show removed folds", value=True)

            bar_labels = self._get_bar_labels()

        with st.spinner("Plotting folds"):
            ax = plot(
                **split_kwargs,
                available=available.index if isinstance(available, (pd.DataFrame, pd.Series)) else available,
                show_removed=show_removed,
                bar_labels=bar_labels,
            )
            st.pyplot(ax.figure, clear_figure=True)

        seconds = perf_counter() - start

        # Record performance
        if isinstance(available, pd.DataFrame):
            msg = f"Created figure for data of (`shape={available.shape}`) in `{fmt_sec(seconds)}`."
            log_perf(msg, available, seconds, extra={"show_removed": show_removed, "bar_labels": bar_labels})
            st.caption(msg)

        return {"show_removed": show_removed, "bar_labels": bar_labels}

    def _get_bar_labels(self) -> str | Literal[False]:
        if not self.bar_labels:
            return False

        bar_labels = st.radio("Bar labels", self.bar_labels, horizontal=True)
        return False if bar_labels == BarLabels.DISABLED else bar_labels.name.lower()


PlotFoldsWidget.BarLabels = BarLabels
