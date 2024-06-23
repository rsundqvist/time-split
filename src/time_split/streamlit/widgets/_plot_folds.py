from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal

import streamlit as st

from time_split import plot
from time_split.types import DatetimeIndexSplitterKwargs


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
        limits,
    ) -> dict[str, Any]:
        with st.container(border=True):
            st.subheader("Plot parameters", divider="rainbow")
            left, right = st.columns([0.3, 0.7])

            show_removed = self.show_removed
            if show_removed is None:
                show_removed = left.toggle(":ghost: Show removed folds", value=True)

            bar_labels = self._get_bar_labels(right)

        with st.spinner("Plotting folds"):
            ax = plot(**split_kwargs, available=limits, show_removed=show_removed, bar_labels=bar_labels)
            st.pyplot(ax.figure, clear_figure=True)
        return {"show_removed": show_removed, "bar_labels": bar_labels}

    def _get_bar_labels(self, parent) -> str | Literal[False]:
        if not self.bar_labels:
            return False

        bar_labels = parent.radio("bar-labels", self.bar_labels, horizontal=True, label_visibility="collapsed")
        return False if bar_labels == BarLabels.DISABLED else bar_labels.name.lower()


PlotFoldsWidget.BarLabels = BarLabels
