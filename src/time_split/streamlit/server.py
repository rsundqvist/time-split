import logging

import streamlit as st
from rics.plotting import configure as configure_plotting

from time_split import split
from time_split._compat import fmt_sec
from time_split.integration.pandas import split_pandas
from time_split.streamlit._code import show_code
from time_split.streamlit.widgets import (
    DataWidget,
    ExpandLimitsWidget,
    PlotFoldsWidget,
    ScheduleWidget,
    SpanWidget,
    select_spans,
)
from time_split.support import to_string
from time_split.types import DatetimeIndexSplitterKwargs, LogSplitProgressKwargs

st.set_page_config(
    page_title="Time fold explorer",
    page_icon="https://raw.githubusercontent.com/rsundqvist/time-split/master/docs/logo-icon.png",
    # layout="wide",
    menu_items=None,
    initial_sidebar_state="expanded",
)

LOGGER = logging.getLogger(__name__)

DATA_WIDGET = DataWidget()
SCHEDULE_WIDGET = ScheduleWidget()
PLOT_FOLDS_WIDGET = PlotFoldsWidget()
EXPAND_LIMITS_WIDGET = ExpandLimitsWidget()
SPAN_BEFORE_WIDGET = SpanWidget()
SPAN_AFTER_WIDGET = SpanWidget()

LOGGER.setLevel(logging.INFO)
configure_plotting()

with st.sidebar:

    left, right = st.columns(2)
    with left, st.popover(":arrow_up: Select dataset"):
        df, limits, seconds = DATA_WIDGET.load_data()

    with right:
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


plot_folds_tab, dataset_details_tab, code_tab = st.tabs([":bar_chart: Show folds", ":sleuth_or_spy: Dataset details", ":desktop_computer: Code", ])
with plot_folds_tab:
    plot_kwargs = PLOT_FOLDS_WIDGET.plot(split_kwargs, df.index)

with dataset_details_tab:
    DATA_WIDGET.show_data_details(df)

with code_tab:
    show_code(split_kwargs, plot_kwargs=plot_kwargs, limits=limits)





progress_kwargs = LogSplitProgressKwargs(logger=LOGGER)

try:
    n_splits = len(split(**split_kwargs, available=limits))
except Exception as e:
    st.exception(e)
    st.stop()

percent_complete = 0.0
# pbar = st.progress(percent_complete, f"Iterating over {n_splits} folds.")


with st.status("Working"):
    for data, future_data, bounds in split_pandas(df, **split_kwargs, log_progress=progress_kwargs):
        pretty = to_string(bounds)
        # pbar.progress(percent_complete, text=pretty)

        msg = f"{pretty}:\n - {len(data)=}\n - {len(future_data)=}"
        st.write(msg)
        st.write(str(bounds))

        percent_complete += 1 / n_splits
        # pbar.progress(percent_complete)
