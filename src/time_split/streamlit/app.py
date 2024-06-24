"""Streamlit application file."""

import logging
from time import perf_counter

import streamlit as st
from rics.logs import basic_config
from rics.plotting import configure as configure_plotting

from time_split import split
from time_split._compat import fmt_sec
from time_split.streamlit._code import show_code
from time_split.streamlit._logging import log_perf
from time_split.streamlit.config import enforce_max_splits, get_server_config_info
from time_split.streamlit.widgets import (
    AggregationWidget,
    DataWidget,
    FoldOverviewWidget,
    PlotFoldsWidget,
    SplitterKwargsWidget,
)

start = perf_counter()

st.set_page_config(
    page_title="Time fold explorer",
    page_icon="https://raw.githubusercontent.com/rsundqvist/time-split/master/docs/logo-icon.png",
    layout="wide",
    menu_items=None,
    initial_sidebar_state="expanded",
)

ABOUT = """
## Time Fold explorer
This applications is designed to help experiment with `time-split` splitting parameters. 

See https://time-split.readthedocs.io/ library for documentation.

#### 🚀 Getting started
1. Use the `⬆️ Select dataset or upload a file` tab to configure data.
2. Use the `sidebar` other widgets to control the data is split.
3. Use the tabs below to explore the effects.

Please visit the [GitHub page](https://github.com/rsundqvist/time-split) for questions or feedback.

#### ⚙️ Server configuration
These values cannot be changed. 

{config}

See https://hub.docker.com/repository/docker/rsundqvist/time-split/ to spawn custom servers.
"""

DATA_WIDGET = DataWidget(initial_sample_subset_range=("2019-04-01", "2019-05-11 21:30"))
SPLITTER_KWARGS_WIDGET = SplitterKwargsWidget()
PLOT_FOLDS_WIDGET = PlotFoldsWidget()
FOLD_OVERVIEW_WIDGET = FoldOverviewWidget()
AGGREGATION_WIDGET = AggregationWidget()

configure_plotting()
basic_config(time_split_level=logging.WARNING, time_split__streamlit_level=logging.INFO)

with st.sidebar:
    sidebar_top = st.container()
    split_kwargs = SPLITTER_KWARGS_WIDGET.select_params()


tabs = [
    ":bar_chart: Folds",
    ":chart_with_upwards_trend: Aggregations per fold",
    ":desktop_computer: Code",
    "⬆️ Select or upload data",
    ":grey_question: About",
]
plot_folds_tab, aggregations_tab, code_tab, data_tab, about_tab = st.tabs(tabs)

with about_tab:
    st.write(ABOUT.format(config=get_server_config_info()))

with data_tab:
    left, right = st.columns([1, 2])
    with left:
        df, _, data_source = DATA_WIDGET.select_data()
    with right:
        DATA_WIDGET.show_data(df)

with sidebar_top:
    with st.popover("⚙️ Configure data", use_container_width=True), st.form("configure-data", border=False):
        st.subheader("Configure data", divider="rainbow")
        st.write(f"Use the `{tabs[-2]}` tab to upload your own data!")
        df, limits = DATA_WIDGET.select_range_subset(df, data_source)
        aggregations = DATA_WIDGET.configure(df)
        st.form_submit_button("Apply new configuration", use_container_width=True, type="primary")
    DATA_WIDGET.show_summary(df)

with st.sidebar:
    SPLITTER_KWARGS_WIDGET.limits_widget.show_expand_limits(limits, split_kwargs["expand_limits"])

SPLITS = split(**split_kwargs, available=limits)
ALL_SPLITS = split(**split_kwargs, available=limits, ignore_filters=True)

enforce_max_splits(len(ALL_SPLITS), split_kwargs, limits)

with plot_folds_tab:
    left, right = st.columns([3, 1])
    with right:
        st.subheader("Configuration", divider="rainbow")
        plot_kwargs = PLOT_FOLDS_WIDGET.configure()

    plot = st.container(border=True)
    with left:
        PLOT_FOLDS_WIDGET.plot(split_kwargs, df, **plot_kwargs)

    with right:
        st.subheader("Overview", divider="rainbow")
        FOLD_OVERVIEW_WIDGET.show_overview(SPLITS, all_splits=ALL_SPLITS)
        used, avail = FOLD_OVERVIEW_WIDGET.get_data_utilization(SPLITS, limits)
        st.write(f"Using `{fmt_sec(used)}/{fmt_sec(avail)}` (`{used / avail :.1%}`) of the available data range.")

with code_tab:
    show_code(split_kwargs, plot_kwargs=plot_kwargs, limits=limits)

with aggregations_tab:
    DATA_WIDGET.aggregation.plot_aggregations(df, split_kwargs=split_kwargs, aggregations=aggregations)

# Record performance
seconds = perf_counter() - start
msg = f"Finished all tasks in {1000 * seconds:.1f} ms."
msg = log_perf(msg, df, seconds, extra={"n_splits": len(SPLITS), "n_splits_removed": len(ALL_SPLITS) - len(SPLITS)})
with sidebar_top:
    st.success(msg, icon="⏱️")
