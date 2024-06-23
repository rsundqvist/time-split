from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum
from typing import Collection

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitAPIException


class DataSource(StrEnum):
    """Data source choices."""

    GENERATED = ":magic_wand: Generate sample data"
    UPLOADED = ":arrow_up: Upload CSV or Parquet"


@dataclass(frozen=True)
class DurationWidget:
    periods: int = 7
    """Default period count. Must be positive."""
    units: Collection[str] = ("days", "hours", "minutes", "seconds")
    """Permitted units, e.g. ``['days']``."""

    def select(self, label: str) -> timedelta:
        """Prompt user to select duration."""
        container = st.container(border=False)

        try:
            left, right = container.columns(2)
        except StreamlitAPIException:
            # streamlit.errors.StreamlitAPIException: Columns cannot be placed inside other columns in the sidebar. This
            # is only possible in the main area of the app.
            left, right = container, container

        periods = left.number_input(
            "select-periods",
            key=f"{label}-periods",
            min_value=1,
            max_value=59,
            value=self.periods,
            label_visibility="collapsed",
        )
        unit = right.selectbox(
            "select-unit",
            key=f"{label}-unit",
            options=self.units,
            # horizontal=True,
            label_visibility="collapsed",
        )

        return pd.Timedelta(f"{periods} {unit}").to_pytimedelta()

    def __post_init__(self) -> None:
        if not self.units:
            raise ValueError("Need at least one unit.")
        if self.periods <= 0:
            raise ValueError(f"periods={self.periods} must be > 0")


INSTANCE = DurationWidget()


def select_duration(label: str) -> pd.Timedelta:
    """Prompt user to select duration using the default widget."""
    return INSTANCE.select(label)
