from ast import literal_eval
from dataclasses import dataclass
from enum import StrEnum

import numpy as np
import pandas as pd
import streamlit as st

from time_split._frontend._to_string import stringify
from time_split.settings import auto_expand_limits as settings
from time_split.support import expand_limits
from time_split.types import ExpandLimits


class Option(StrEnum):
    AUTO = "Automatic :left_right_arrow:"
    DISABLED = "Disabled :no_entry_sign:"
    FREE_FORM = "Free form :memo:"


@dataclass(frozen=True)
class ExpandLimitsWidget:
    auto: bool = True
    """Preselect the `'auto'` option and add a dedicated button for it."""
    disabled: bool = True
    """Enable disabling option."""
    free_from: bool = True
    """Allow free-form input parsed using :func:`ast.literal_eval`."""

    default_value: str = "d<3h"
    """Default (pre-selected) value for the manual input field."""
    change_props: str = "color: black; background-color: rgba(255, 200, 50, 0.5);"
    """Properties used to highlight changed limits. Set to an empty string to disable."""
    no_change_props: str = "color: rgba(200, 200, 200, 0.5)"
    """Properties used to highlight unchanged limits. Set to an empty string to disable."""

    def select_expand_limits(self, limits: tuple[pd.Timestamp, pd.Timestamp]) -> ExpandLimits:
        with st.container(border=True):
            st.header("Data limits expansion", divider="rainbow", help=EXPAND_LIMITS_HELP)
            return self._select_expand_limits(limits)

    def get_options(self) -> list[Option]:
        options = []

        if self.auto:
            options.append(Option.AUTO)
        if self.disabled:
            options.append(Option.DISABLED)
        if self.free_from:
            options.append(Option.FREE_FORM)

        return options

    def _select_expand_limits(self, limits: tuple[pd.Timestamp, pd.Timestamp]) -> ExpandLimits:
        choice = st.radio("Data limits expansion", self.get_options(), horizontal=True, label_visibility="collapsed")

        if choice == Option.DISABLED:
            return False

        if choice == Option.AUTO:
            spec = "auto"
        else:
            user_input = st.text_input(
                "expand-limits",
                value=self.default_value,
                placeholder=str(tuple(settings.day)),
                label_visibility="collapsed",
            )
            try:
                spec = literal_eval(user_input)
            except Exception:
                spec = user_input.strip()

            if not spec:
                st.stop()

        try:
            expanded_limits = expand_limits(limits, spec=spec)
        except Exception as e:
            st.exception(e)
            st.stop()

        expanded_limits = expanded_limits[0], expanded_limits[1]

        if limits == expanded_limits:
            if pd.Timestamp.now().second % 2 == 0:
                st.info("TODO Original limits kept.", icon="ℹ️")  # noqa: RUF001
            return spec

        data = {"Index": ["Start", "End"], "Original": limits, "Expanded": expanded_limits}
        df = pd.DataFrame(data)
        df["Change"] = [stringify(row.Original, new=row.Expanded, diff_only=True) for row in df.itertuples()]

        same = df["Expanded"] == df["Original"]
        # df.loc[same, ["Expanded", "Change"]] = "<same>"

        st.dataframe(
            df.style.apply(lambda _: np.where(~same, self.change_props, self.no_change_props), axis=0),
            use_container_width=True,
            hide_index=True,
        )

        return spec


ExpandLimitsWidget.Option = Option

EXPAND_LIMITS_HELP = (
    "See the [User guide](https://time-split.readthedocs.io/en/stable/guide/expand-limits.html) for help."
    " Automatic expansion is configurable using the global "
    " [`auto_expand_limits`](https://time-split.readthedocs.io/en/stable/generated/time_split.settings.html#time_split.settings.auto_expand_limits)"
    " configuration object. Manual input is validated using the "
    "[`expand_limits()`](https://time-split.readthedocs.io/en/stable/generated/time_split.support.html#time_split.support.expand_limits)"
    " support function."
)
