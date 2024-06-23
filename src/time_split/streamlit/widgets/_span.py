from ast import literal_eval
from dataclasses import dataclass
from enum import StrEnum

import streamlit as st

from time_split.streamlit.widgets import select_duration
from time_split.types import Span


class Kind(StrEnum):
    """Schedule input types."""

    STEP = "Step :ladder:"
    DURATION = "Duration :stopwatch:"
    ALL = "All data :100:"
    FREE_FORM = "Free form :memo:"


@dataclass(frozen=True)
class SpanWidget:
    step: int = 10
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

    def get_span(self, label: str, default_kind: Kind) -> Span:
        """Get before/after input from the user."""
        return self._get_span(label, default_kind)

    def _get_span(self, label: str, default_kind: Kind) -> Span:
        kinds = self._kinds()

        kind: Kind = st.radio(f"Available data ***{label}*** the fold date.", kinds, index=kinds.index(default_kind))

        if kind == Kind.STEP:
            return st.number_input(label, min_value=1, max_value=self.step, label_visibility="collapsed")

        if kind == Kind.DURATION:
            return select_duration(label)

        user_input = st.text_input(
            label,
            value=_DEFAULTS_VALUES[kind],
            label_visibility="collapsed",
            disabled=kind == Kind.ALL,
        )

        if not user_input.strip():
            st.stop()

        return self._process_user_input(kind, user_input)

    def _process_user_input(self, kind: Kind, user_input: str) -> Span:
        if kind == Kind.ALL:
            return "all"

        if kind is Kind.FREE_FORM:
            try:
                return literal_eval(user_input)
            except Exception:
                return user_input.strip()

        raise NotImplementedError(f"{kind=}")


SpanWidget.Kind = Kind
_DEFAULTS_VALUES = {
    Kind.DURATION: "7 days",
    Kind.ALL: "all",
    Kind.FREE_FORM: "10 days 6 hours",
}


def select_spans(before: SpanWidget, *, after: SpanWidget) -> tuple[Span, Span]:
    with st.container(border=True):
        st.subheader(
            "Dataset spans", divider="rainbow", help="https://time-split.readthedocs.io/en/stable/guide/spans.html"
        )

        left, right = st.columns(2, gap="medium")
        with left:
            before_span = before.get_span("before", default_kind=SpanWidget.Kind.DURATION)
        with right:
            after_span = after.get_span("after", default_kind=SpanWidget.Kind.STEP)

    return before_span, after_span
