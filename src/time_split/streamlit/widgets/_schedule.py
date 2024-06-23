import datetime
from ast import literal_eval
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Callable, Collection, TypeVar

import pandas as pd
import streamlit as st
from croniter import croniter

from ._duration import select_duration
from ._schedule_filter import Filters, ScheduleFilterWidget

ProcessedSchedule = str | datetime.timedelta | list[str] | tuple[str, ...]
R = TypeVar("R")


class Kind(StrEnum):
    """Schedule input types."""

    CRON = "Cron :calendar:"
    DURATION = "Duration :stopwatch:"
    FREE_FORM = "Free form :memo:"


@dataclass(frozen=True)
class ScheduleWidget:
    free_from: bool = True
    """Allow free-form input parsed using :func:`ast.literal_eval`."""
    duration: bool = True
    """Allow duration-based (timedelta) inputs."""
    cron: bool = True
    """Allow `cron <https://pypi.org/project/croniter/>`_ expressions."""
    filter: ScheduleFilterWidget | None = field(default_factory=ScheduleFilterWidget)
    """Fold filter parameters. Set to ``None`` to disable fold filtering."""

    def __post_init__(self) -> None:
        if not self._kinds():
            raise ValueError("Allow at least one input type.")

    def _kinds(self) -> list[Kind]:
        kinds = []
        if self.cron:
            kinds.append(Kind.CRON)
        if self.duration:
            kinds.append(Kind.DURATION)
        if self.free_from:
            kinds.append(Kind.FREE_FORM)
        return kinds

    def get_schedule(self) -> tuple[ProcessedSchedule, Filters]:
        """Get schedule input from the user."""
        with st.container(border=True):
            return self._get_schedule()

    def _get_schedule(self) -> tuple[ProcessedSchedule, Filters]:
        kinds = self._kinds()

        st.subheader(
            "Schedule", divider="rainbow", help="https://time-split.readthedocs.io/en/stable/guide/schedules.html"
        )
        kind: Kind = st.radio("schedule-type", kinds, horizontal=True, label_visibility="collapsed")

        if kind == Kind.DURATION:
            schedule = select_duration("schedule")
        else:
            user_input = st.text_input(
                "schedule",
                value=_DEFAULTS_VALUES[kind],
                placeholder=f"Enter {kind.name.replace('_', ' ').capitalize()}-schedule.",
                label_visibility="collapsed",
            )

            if not user_input.strip():
                st.stop()

            schedule = self._process_user_input(kind, user_input)

        filters = self.filter.get_fold_filters() if self.filter else None

        return schedule, filters

    def _process_user_input(self, kind: Kind, user_input: str) -> ProcessedSchedule:
        if kind is Kind.CRON:
            _validate(user_input, croniter.expand)
            return user_input

        if kind is Kind.DURATION:
            return _validate(user_input, pd.Timedelta).to_pytimedelta()

        if kind is Kind.FREE_FORM:
            return _validate(user_input, _validate_literal)

        raise NotImplementedError(f"{kind=}")


def _validate(value: str, validator: Callable[[str], R]) -> R:
    try:
        return validator(value)
    except Exception as e:
        st.exception(e)
        st.stop()


def _validate_literal(s: str) -> ProcessedSchedule:
    val = literal_eval(s)

    if isinstance(val, Collection) and not isinstance(val, str):
        pd.DatetimeIndex(val)

    return val


ScheduleWidget.Kind = Kind

_DEFAULTS_VALUES = {
    Kind.CRON: "0 0 * * MON,FRI",
    Kind.DURATION: "7 days",
    Kind.FREE_FORM: "['2019-05-11 20:30', '2019-05-16']",
}
