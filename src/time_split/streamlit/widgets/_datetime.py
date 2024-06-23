import datetime

import streamlit as st


def select_datetime(label: str, initial: datetime.datetime | None = None) -> datetime.datetime:
    if initial is None:
        initial = datetime.datetime.now()

    st.header(label)
    date = st.date_input(
        f"select-{label}-date",
        value=initial,
        min_value=datetime.date(1970, 1, 1),
        max_value=datetime.date(2100, 1, 1),
        label_visibility="collapsed",
    )
    time = st.time_input(
        f"select-{label}-time",
        value=initial.time(),
        label_visibility="collapsed",
        step=datetime.timedelta(hours=1),
    )
    return datetime.datetime.combine(date, time)
