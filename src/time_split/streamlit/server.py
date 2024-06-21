import logging
from datetime import datetime
from pprint import pformat

import numpy as np
import pandas as pd
import streamlit as st
from rics.misc import format_kwargs
from rics.plotting import configure as configure_plotting

from time_split import split
from time_split.integration.pandas import split_pandas
from time_split.streamlit import data
from time_split.streamlit.widgets import PlotFoldsWidget, ScheduleWidget
from time_split.support import to_string
from time_split.types import DatetimeIndexSplitterKwargs, LogSplitProgressKwargs

st.set_page_config(
    page_title="Time folds",
    page_icon="https://raw.githubusercontent.com/rsundqvist/time-split/master/docs/logo-icon.png",
    # layout="wide",
    menu_items=None,
    initial_sidebar_state="expanded",
)

LOGGER = logging.getLogger(__name__)
SCHEDULE_WIDGET = ScheduleWidget()
PLOT_FOLDS_WIDGET = PlotFoldsWidget()

LOGGER.setLevel(logging.INFO)
configure_plotting()

with st.sidebar:
    # st.file_uploader
    # data: st.file_uploader / range / demo (below)
    with st.form("data"):
        st.write("# Data configuration")
        df: pd.DataFrame = data.load()
        df, limits = data.select_index(df)
        df = data.select_columns(df)
        st.form_submit_button("Load data", use_container_width=True)

    st.write("# Fold configuration")

    split_kwargs: DatetimeIndexSplitterKwargs = DatetimeIndexSplitterKwargs(
        schedule=SCHEDULE_WIDGET.get_schedule(),
        n_splits=st.slider("n_splits", value=3, min_value=0, max_value=10),
        before=st.slider("before", value=20, min_value=1, max_value=300),
        # after=st.slider("after", value=30, min_value=1, max_value=300),
        step=st.slider("step", value=2, min_value=1, max_value=10),
        # expand_limits=st.toggle("expand_limits", True),
    )

    # split_kwargs["schedule"] = "30 days"
    split_kwargs["before"] = f"{split_kwargs['before']} days"
    # split_kwargs["after"] = f"{split_kwargs['after']} days"

st.code(pformat(split_kwargs))
# st.stop()

PLOT_FOLDS_WIDGET.plot(split_kwargs, df.index)

progress_kwargs = LogSplitProgressKwargs(logger=LOGGER)

try:
    n_splits = len(split(**split_kwargs, available=limits))
except Exception as e:
    st.exception(e)
    st.stop()

percent_complete = 0.0
# pbar = st.progress(percent_complete, f"Iterating over {n_splits} folds.")

keys = np.array_split(list(split_kwargs), 2)
rows = "\n".join(f"  {format_kwargs({k:split_kwargs[k] for k in kk})}," for kk in keys)
code = f"time_split.split(\n{rows}\n  available={tuple(map(str, limits))},\n)"
st.code(code, language="python")

PLOT_FOLDS_WIDGET.plot(split_kwargs, limits)

with st.status("Working"):
    for data, future_data, bounds in split_pandas(df, **split_kwargs, log_progress=progress_kwargs):
        pretty = to_string(bounds)
        # pbar.progress(percent_complete, text=pretty)

        msg = f"{pretty}:\n - {len(data)=}\n - {len(future_data)=}"
        st.write(msg)
        st.write(str(bounds))

        percent_complete += 1 / n_splits
        # pbar.progress(percent_complete)

st.success("This is a success message!", icon="✅")

st.balloons()
st.snow()

appointment = st.slider(
    "Schedule your appointment:",
    value=(
        datetime(2019, 5, 11, 20, 30),
        datetime(2019, 6, 11, 20, 30),
    ),
)
