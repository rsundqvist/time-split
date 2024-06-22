from ast import literal_eval
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, TypeVar

import pandas as pd
import streamlit as st

from time_split.types import Span

R = TypeVar("R")


class Kind(StrEnum):
    """Schedule input types."""

    STEP = "Step :ladder:"
    DURATION = "Duration :stopwatch:"
    ALL = "All data :100:"
    FREE_FORM = "Free form :memo:"




@dataclass(frozen=True)
class SpanWidget:
    step: int = 5
    """Max value in the user form for integer spans. Set to zero to disable."""
    duration: bool = True
    """Allow duration-based (timedelta) inputs."""
    all: bool = True
    """Allow the `'all'` option."""
    free_from: bool = True
    """Allow free-form input parsed using :func:`ast.literal_eval`."""

    def __post_init__(self) -> None:
        if not self._kinds():
            raise ValueError("Allow at least one input type.")

    def _kinds(self) -> list[Kind]:
        kinds = []
        if self.step:
            kinds.append(Kind.STEP)
        if self.duration:
            kinds.append(Kind.DURATION)
        if self.all:
            kinds.append(Kind.ALL)
        if self.free_from:
            kinds.append(Kind.FREE_FORM)
        return kinds

    def get_span(self, label: str) -> Span:
        """Get before/after input from the user."""
        with st.container(border=True):
            return self._get_span(label)

    def _get_span(self, label: str) -> Span:
        kinds = self._kinds()

        st.subheader(label, divider="rainbow")

        kind: Kind = st.radio("Select schedule type.", kinds, horizontal=True)

        if kind == Kind.ALL:
            return "all"

        if kind == Kind.STEP:
            return st.number_input(label, min_value=1, max_value=self.step, label_visibility="collapsed")

        schedule = st.text_input(
            "Enter schedule value.",
            value=_DEFAULTS_VALUES[kind],
            placeholder=f"Enter {kind.name.replace('_', ' ').capitalize()}-schedule.",
        )

        if not schedule.strip():
            st.stop()

        return self._process_user_input(kind, schedule)

    def _process_user_input(self, kind: Kind, user_input: str) -> Span:
        if kind is Kind.DURATION:
            return _validate(user_input, pd.Timedelta).to_pytimedelta()

        if kind is Kind.FREE_FORM:
            return _validate(user_input, literal_eval)

        raise NotImplementedError(f"{kind=}")


def _validate(value: str, validator: Callable[[str], R]) -> R:
    try:
        return validator(value)
    except Exception as e:
        st.exception(e)
        st.stop()


SpanWidget.Kind = Kind

_DEFAULTS_VALUES = {
    Kind.DURATION: "7 days",
    Kind.FREE_FORM: "['2019-05-11 20:30', '2019-05-16']",
}


def select_spans(before: SpanWidget, *, after: SpanWidget) -> tuple[Span, Span]:
    return before.get_span("Before"), after.get_span("After")
