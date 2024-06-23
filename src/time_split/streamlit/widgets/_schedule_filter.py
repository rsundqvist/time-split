from dataclasses import dataclass
from typing import NamedTuple

import streamlit as st


class Filters(NamedTuple):
    """Schedule/fold filtering parameters."""

    limit: int
    step: int


@dataclass(frozen=True)
class ScheduleFilterWidget:
    limit: int = 5
    """Set the maximum fold count. Zero=no limit."""
    step: int = 5
    """Set the maximum fold step. Zero=no limit."""

    def get_fold_filters(self) -> Filters:
        left, right = st.columns(2)

        limit = left.number_input(
            "Maximum fold count.", value=0, min_value=0, max_value=self.limit, help="Zero = no limit."
        )
        step = right.number_input("Schedule step.", min_value=1, max_value=self.step)

        return Filters(limit=limit, step=step)

    def __post_init__(self) -> None:
        assert self.limit >= 0
        assert self.step > 0


ScheduleFilterWidget.Filters = Filters
