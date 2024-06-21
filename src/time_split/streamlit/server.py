import time

import numpy as np
import pandas as pd
import streamlit as st
from rics import configure_stuff
from rics.misc import format_kwargs

from time_split import plot, split
from time_split.integration.pandas import split_pandas
from time_split.streamlit import data
from time_split.support import to_string
from time_split.types import DatetimeIndexSplitterKwargs, LogSplitProgressKwargs

configure_stuff()

with st.sidebar:
    with st.form("data"):
        st.write("# Data configuration")
        df: pd.DataFrame = data.load()
        df, limits = data.select_index(df)
        df = data.select_columns(df)
        st.form_submit_button("Load data", use_container_width=True)

    with st.form("split"):
        st.write("# Fold configuration")
        split_kwargs: DatetimeIndexSplitterKwargs = DatetimeIndexSplitterKwargs(
            schedule=st.text_input("schedule", "0 0 * * MON,FRI", max_chars=32),
            n_splits=st.slider("n_splits", value=3, min_value=0, max_value=10),
            before=st.slider("before", value=100, min_value=1, max_value=300),
            # after=st.slider("after", value=30, min_value=1, max_value=300),
            step=st.slider("step", value=2, min_value=1, max_value=10),
            expand_limits=st.toggle("expand_limits", True),
        )
        split_kwargs["schedule"] = "30 days"
        split_kwargs["before"] = f"{split_kwargs['before']} days"
        # split_kwargs["after"] = f"{split_kwargs['after']} days"
        st.form_submit_button("Show folds", use_container_width=True)


progress_kwargs = LogSplitProgressKwargs(logger="my-logger")

n_splits = len(split(**split_kwargs, available=limits))
percent_complete = 0.0
pbar = st.progress(percent_complete, f"Iterating over {n_splits} folds.")

keys = np.array_split(list(split_kwargs), 2)
rows = "\n".join(f"  {format_kwargs({k:split_kwargs[k] for k in kk})}," for kk in keys)
code = f"time_split.split(\n{rows}\n  available={tuple(map(str, limits))}\n)"
st.code(code, language="python")

ax = plot(**split_kwargs, available=limits, show_removed=True)
st.pyplot(ax.figure, clear_figure=True)

for data, future_data, bounds in split_pandas(df, **split_kwargs, log_progress=progress_kwargs):
    pbar.progress(percent_complete, text=to_string(bounds))

    msg = f"{to_string(bounds)}:\n - {len(data)=}\n - {len(future_data)=}"
    st.write(msg)
    st.write(str(bounds))

    time.sleep(3)

    percent_complete += 1 / n_splits
    pbar.progress(percent_complete)

st.success("This is a success message!", icon="✅")
st.info("This is a purely informational message", icon="ℹ️")
st.warning("This is a warning", icon="⚠️")
st.error("This is an error", icon="🚨")
st.exception(ValueError("aaah!"))

st.balloons()
st.snow()

with st.spinner("Wait for it..."):
    time.sleep(5)
st.success("Done!")

from datetime import time

appointment = st.slider("Schedule your appointment:", value=(time(11, 30), time(12, 45)))
st.write("You're scheduled for:", appointment)
