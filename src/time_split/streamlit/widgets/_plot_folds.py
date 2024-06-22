from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

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
    bar_labels: set[BarLabels] | Literal[False] = field(default_factory=lambda: set(BarLabels))
    """Bar label choices made available to the user. Set to ``False`` to disable."""

    def plot(
        self,
        split_kwargs: DatetimeIndexSplitterKwargs,
        limits,
    ) -> None:
        st.subheader("Folds", divider="rainbow")

        with st.container(border=True):
            left, right = st.columns([0.3, 0.7])

            show_removed = self.show_removed
            if show_removed is None:
                show_removed = left.toggle(":ghost: Show removed folds", value=True)

            bar_labels = self._get_bar_labels(right)

        with st.spinner("Plotting folds"):
            ax = plot(**split_kwargs, available=limits, show_removed=show_removed, bar_labels=bar_labels)
            st.pyplot(ax.figure, clear_figure=True)

    def _get_bar_labels(self, parent) -> str | Literal[False]:
        if not self.bar_labels:
            return False

        order = list(BarLabels)
        bar_labels = parent.radio("Bar labels", sorted(self.bar_labels, key=order.index), horizontal=True)
        return False if bar_labels == BarLabels.DISABLED else bar_labels.name.lower()


PlotFoldsWidget.BarLabels = BarLabels
