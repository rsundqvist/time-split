import logging
import os

import pandas as pd
import streamlit as st
from rics.logs import basic_config
from rics.plotting import configure as configure_plotting

from time_split import split
from time_split._compat import fmt_sec
from time_split.streamlit._code import get_repro, show_code
from time_split.streamlit.widgets import (
    DataWidget,
    ExpandLimitsWidget,
    PlotFoldsWidget,
    ScheduleWidget,
    SpanWidget,
    select_spans,
)
from time_split.types import DatetimeIndexSplitterKwargs

MAX_SPLITS = int(os.environ.get("MAX_SPLITS", 50))

st.set_page_config(
    page_title="Time fold explorer",
    page_icon="https://raw.githubusercontent.com/rsundqvist/time-split/master/docs/logo-icon.png",
    layout="wide",
    menu_items=None,
    initial_sidebar_state="expanded",
)

DATA_WIDGET = DataWidget(initial_sample_subset_range=("2019-04-01", "2019-05-11 21:30"))
SCHEDULE_WIDGET = ScheduleWidget()
PLOT_FOLDS_WIDGET = PlotFoldsWidget()
EXPAND_LIMITS_WIDGET = ExpandLimitsWidget()
SPAN_BEFORE_WIDGET = SpanWidget()
SPAN_AFTER_WIDGET = SpanWidget()

configure_plotting()
basic_config(time_split_level=logging.WARNING, time_split__streamlit_level=logging.INFO)


@st.experimental_dialog("Title")
def select_data() -> tuple[pd.DataFrame, tuple[pd.Timestamp, pd.Timestamp], float]:
    with st.form("select-data-dialog"):
        retval = DATA_WIDGET.select_data()
        st.form_submit_button(":rocket: LOAD DATASET :rocket:", type="primary", use_container_width=True)
    return retval


with st.sidebar:
    with st.expander(":arrow_up: Select dataset or upload a file"):
        df, limits, seconds = DATA_WIDGET.select_data()
    # st.button("LOAD DATASET", use_container_width=True, type="primary", on_click=select_data)

    n_rows, n_cols = df.shape
    st.caption(f"Finished loading data of shape `{n_rows}x{n_cols}` in `{fmt_sec(seconds)}`.")

    DATA_WIDGET.brief(df, seconds)

    # st.file_uploader
    # data: st.file_uploader / range / demo (below)
    # with st.form("data"):
    expand_limits = EXPAND_LIMITS_WIDGET.select_expand_limits(limits)
    schedule, filters = SCHEDULE_WIDGET.get_schedule()

    before, after = select_spans(SPAN_BEFORE_WIDGET, after=SPAN_AFTER_WIDGET)

split_kwargs: DatetimeIndexSplitterKwargs = DatetimeIndexSplitterKwargs(
    schedule=schedule,
    before=before,
    after=after,
    expand_limits=expand_limits,
)
if filters:
    split_kwargs["n_splits"] = filters.limit
    split_kwargs["step"] = filters.step

n_splits = len(split(**split_kwargs, available=limits))

if n_splits > MAX_SPLITS:
    st.error(f"Maximum number of splits ({MAX_SPLITS}) exceeded.", icon="🚨")
    st.code(get_repro(split_kwargs, limits))
    st.write(
        f"The snippet above produces `len(splits)={n_splits} > {MAX_SPLITS}=MAX_SPLITS`."
        " Try using different parameters to reduce the number of folds."
    )
    st.stop()

plot_folds_tab, aggregations_tab, code_tab = st.tabs(
    [
        ":bar_chart: Show folds",
        ":chart_with_upwards_trend: Aggregations",
        ":desktop_computer: Code",
    ]
)
with plot_folds_tab:
    plot_kwargs = PLOT_FOLDS_WIDGET.plot(split_kwargs, df)

with aggregations_tab:
    aggregations = DATA_WIDGET.show_data_details(df)
    DATA_WIDGET.aggregation.plot_aggregations(df, split_kwargs=split_kwargs, aggregations=aggregations)
    DATA_WIDGET.show_data(df)


with code_tab:
    show_code(split_kwargs, plot_kwargs=plot_kwargs, limits=limits)
