from dataclasses import dataclass
from typing import NamedTuple

import streamlit as st


class Filters(NamedTuple):
    """Schedule/fold filtering parameters."""

    limit: int
    step: int


@dataclass(frozen=True)
class ScheduleFilterWidget:
    limit: int = 99
    """Set the maximum fold count. Zero=no limit."""
    step: int = 99
    """Set the maximum fold step. Zero=no limit."""

    def get_fold_filters(self) -> Filters:
        limit = st.number_input(
            "Maximum fold count.",
            value=0,
            min_value=0,
            max_value=self.limit or None,
            help="Keep at most *N* folds. Zero = no limit. Later folds are preferred.",
        )
        step = st.number_input(
            "Schedule step size.",
            min_value=1,
            max_value=self.step or None,
            help="Keep every *N* folds. Later folds are preferred.",
        )

        return Filters(limit=limit, step=step)

    def __post_init__(self) -> None:
        if self.limit < 0:
            raise ValueError(f"{self.limit=} < 0")
        if self.step < 0:
            raise ValueError(f"{self.step=} < 0")


ScheduleFilterWidget.Filters = Filters
