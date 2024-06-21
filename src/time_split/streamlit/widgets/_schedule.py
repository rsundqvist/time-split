import datetime
from ast import literal_eval
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Collection, TypeVar

import pandas as pd
import streamlit as st
from croniter import croniter

ProcessedSchedule = str | datetime.timedelta | list[str] | tuple[str, ...]
R = TypeVar("R")


class Kind(StrEnum):
    """Schedule input types."""

    CRON = ":calendar: Cron"
    DURATION = ":stopwatch: Duration"
    FREE_FORM = ":memo: Free form"


@dataclass(frozen=True)
class ScheduleWidget:
    free_from: bool = True
    """Allow free-form input parsed using :func:`ast.literal_eval`."""
    duration: bool = True
    """Allow duration-based inputs."""
    cron: bool = True
    """Allow `cron <https://pypi.org/project/croniter/>`_ expressions."""

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
            kinds.append(Kind.CRON.FREE_FORM)
        return kinds

    def get_schedule(self) -> ProcessedSchedule:
        """Get schedule input from the user."""
        with st.container(border=True):
            return self._get_schedule()

    def _get_schedule(self) -> ProcessedSchedule:
        kinds = self._kinds()

        st.subheader("Configure schedule", divider="rainbow")
        kind: Kind = st.radio("Select schedule type.", kinds, horizontal=True)
        schedule = st.text_input(
            "Enter schedule value.",
            value=_DEFAULTS_VALUES[kind],
            placeholder=f"Enter {kind.name.replace('_', ' ').capitalize()}-schedule.",
        )

        if not schedule.strip():
            st.stop()

        return self._process_user_input(kind, schedule)

    def _process_user_input(self, kind: Kind, schedule: str) -> ProcessedSchedule:
        if kind is Kind.CRON:
            _validate(schedule, croniter.expand)
            return schedule

        if kind is Kind.DURATION:
            return _validate(schedule, pd.Timedelta).to_pytimedelta()

        if kind is Kind.FREE_FORM:
            return _validate(schedule, _validate_literal)

        raise NotImplementedError(f"{kind=}")


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


def _validate(value: str, validator: Callable[[str], R]) -> R:
    try:
        return validator(value)
    except Exception as e:
        st.exception(e)
        st.stop()
