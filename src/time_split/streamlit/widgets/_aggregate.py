from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Collection

import numpy as np
import pandas as pd
import streamlit as st

from time_split._compat import fmt_sec
from time_split._frontend._to_string import stringify
from time_split.integration.pandas import split_pandas
from time_split.streamlit._logging import log_perf
from time_split.types import DatetimeIndexSplitterKwargs


@dataclass(frozen=True)
class AggregationWidget:
    aggregations: Collection[str] = ("mean", "sum")
    """Aggregation options."""

    odd_row_props = "background-color: rgba(100, 100, 100, 0.5)"
    """Properties for oddly-numbered fold rows in the output table."""

    def plot_aggregations(
        self,
        df: pd.DataFrame,
        *,
        split_kwargs: DatetimeIndexSplitterKwargs,
        aggregations: dict[str, str] | None = None,
    ) -> None:
        if aggregations is None:
            aggregations = self.select_aggregation(df)

        with (st.spinner("Aggregating data...")):
            st.subheader("Aggregated folds", divider="rainbow")
            table, figure = st.tabs([":chart_with_upwards_trend: Table", ":bar_chart: Figure",])

            with table:
                agg = self.aggregate(df, split_kwargs=split_kwargs, aggregations=aggregations)

            with figure:
                import seaborn as sns

                melt = agg.melt(ignore_index=False).reset_index()
                melt["dataset"] = melt["dataset"].astype("category")

                g = sns.FacetGrid(melt, aspect=4, row="variable", hue="dataset", sharex=True, sharey=False)
                g.map_dataframe(sns.lineplot, x="fold", y="value", marker="o")
                # g.set_titles()
                g.set_ylabels("")
                g.set_titles(row_template="{row_name}")

                g.figure.autofmt_xdate(ha="center", rotation=15)
                g.add_legend(loc="upper right", bbox_to_anchor=(0.8, 1.01)) # TODO

                st.pyplot(g.figure, clear_figure=True)


                # st.dataframe(long)

    def aggregate(
        self,
        df: pd.DataFrame,
        *,
        split_kwargs: DatetimeIndexSplitterKwargs,
        aggregations: dict[str, str],
    ) -> pd.DataFrame:
        """Aggregate datasets resulting from a split of `df`.

        Args:
            df: A dataframe. Must have a ``DatetimeIndex``.
            split_kwargs: Keyword arguments for :func:`time_split.split`.
            aggregations: A dict ``{column: agg_fn}``.

        Returns:
            A frame with the same columns as `df` and a `MultiIndex` with levels
            ``fold_no[int], fold[pd.Timestamp], dataset[str]``.
        """
        start = perf_counter()

        agg = self._aggregate(df, split_kwargs, aggregations)

        pretty = agg.reset_index()
        pretty["fold"] = pretty["fold"].map(lambda ts: f"{stringify(ts)} ({ts.day_name()})")
        st.dataframe(
            pretty.style.apply(
                lambda row: np.where([row["fold_no"] % 2 == 1] * len(row), self.odd_row_props, ""),
                axis=1,
            ),
            use_container_width=True,
        )

        # Record performance
        n_folds = agg.index.get_level_values("fold").nunique()
        seconds = perf_counter() - start
        msg = f"Aggregated datasets in {n_folds} folds for data of (`shape={df.shape}`) in `{fmt_sec(seconds)}`."
        log_perf(msg, df, seconds, extra={"n_folds": n_folds, "aggregations": aggregations})
        st.caption(msg)

        return agg

    @classmethod
    def _aggregate(
        cls, df: pd.DataFrame, split_kwargs: DatetimeIndexSplitterKwargs, aggregations: dict[[int, str], str]
    ) -> pd.DataFrame:
        frames = {}

        for fold in split_pandas(df, **split_kwargs):
            data = fold.data.agg(aggregations).rename("Data")
            future_data = fold.future_data.agg(aggregations).rename("Future data")

            agg = pd.concat([data, future_data], axis=1)
            agg.loc["n_rows", [data.name, future_data.name]] = list(map(len, (fold.data, fold.future_data)))
            agg.loc["n_hours", [data.name, future_data.name]] = list(map(_get_timedelta, (fold.data, fold.future_data)))

            frames[(len(frames), fold.training_date)] = agg.T

        return pd.concat(frames, names=["fold_no", "fold", "dataset"])

    def select_aggregation(self, df: pd.DataFrame) -> dict[str, str]:
        with st.popover("Column configuration"):
            st.subheader("Column configuration", divider="rainbow")
            return self._select_aggregation(df)

    def _select_aggregation(self, df: pd.DataFrame) -> dict[str, str]:
        tabs = st.tabs(df.columns.to_list())

        aggregations = {}
        for name, tab in zip(df.columns, tabs, strict=True):
            column = df[name]

            agg = tab.radio(
                "Aggregation function",
                self.aggregations,
                horizontal=True,
                key=f"{column}-aggregation",
                # help=f"Select aggregation for the `{name}` column with dtype=`{column.dtype}`.",
            )
            aggregations[name] = agg

        return aggregations


def make_formatter(s: pd.Series) -> Callable[[float], str]:
    a = s.abs().mean()

    if a > 999:
        spec = "_d" if a > 9999 else "d"
        return lambda f: f"{int(f):{spec}}"

    if a > 10:
        fmt = "{:.1f}"
    elif a > 1:
        fmt = "{:.2f}"
    else:
        fmt = "{:.4g}"
    return fmt.format


def _get_timedelta(s: pd.Series) -> pd.Timedelta:
    return (s.index.max() - s.index.min()).total_seconds() / 60
