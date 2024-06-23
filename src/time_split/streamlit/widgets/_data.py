from dataclasses import dataclass, field
from enum import StrEnum
from time import perf_counter

import pandas as pd
import streamlit as st
from rics.strings import format_bytes

from time_split._compat import fmt_sec
from time_split.types import DatetimeTypes

from .._logging import log_perf
from ._aggregate import AggregationWidget
from ._sample_data import SampleDataWidget


class DataSource(StrEnum):
    """Data source choices."""

    GENERATED = ":magic_wand: Generate sample data"
    UPLOADED = ":arrow_up: Upload CSV or Parquet"


@dataclass(frozen=True)
class DataWidget:
    sample_data: SampleDataWidget | pd.DataFrame | None = field(default_factory=SampleDataWidget)
    """Set to ``None`` to disable selection of the default timeseries sample data."""
    upload: bool = True
    """Enable to allow user data uploads."""
    n_samples: int = -1
    """Number of sample rows to show.

    Set to 0 to hide the sampled data view, or -1 to show all rows. Set to ``None`` to disable entirely.
    """
    initial_sample_subset_range: tuple[DatetimeTypes, DatetimeTypes] | None = None
    """Initial subset range of the sample data when the data is generated. Set to ``None`` to use actual limits."""

    aggregation: AggregationWidget = field(default_factory=AggregationWidget)
    """Column aggregator."""

    # sample_data_glob_path: str | Path = "sample-data/*.csv"

    def select_data(self) -> tuple[pd.DataFrame, tuple[pd.Timestamp, pd.Timestamp], float]:
        """Prompt user to configure generated data, or to upload their own."""
        st.subheader("Select data source", divider="rainbow")
        sources = self.get_data_sources()
        source = st.radio(
            "data-source",
            sources,
            captions=sources.values(),
            horizontal=True,
            label_visibility="collapsed",
        )

        with st.container(border=True):
            df, seconds, source = self._load_data(source)

        df = self._select_range_subset(df, source)

        df = df.convert_dtypes(dtype_backend="pyarrow")

        return df, (df.index.min(), df.index.max()), seconds

    def load_dummy_data(self) -> tuple[pd.DataFrame, tuple[pd.Timestamp, pd.Timestamp], float]:
        """Returns default generated data."""
        start = perf_counter()
        df = (
            self.sample_data
            if isinstance(self.sample_data, pd.DataFrame)
            else self.sample_data.select_sample_data(prompt=False)
        )
        limits = df.index.min(), df.index.max()

        if not isinstance(df.index, pd.DatetimeIndex):
            msg = f"Data must have a DatetimeIndex: {df.index}"
            raise TypeError(msg)

        seconds = perf_counter() - start
        return df, limits, seconds

    def configure(self, df: pd.DataFrame) -> dict[str, str]:
        return self.aggregation.select_aggregation(df)

    def _load_data(self, source: DataSource) -> tuple[pd.DataFrame, float, DataSource]:
        df: pd.DataFrame | None = None

        start = perf_counter()
        if source == DataSource.GENERATED:
            if self.sample_data is None:
                raise ValueError("No sample data widget configured.")
            df = df if isinstance(self.sample_data, pd.DataFrame) else self.sample_data.select_sample_data()

        if source == DataSource.UPLOADED:
            df = self.select_file()

        if df is None:
            raise NotImplementedError(f"{source=}")

        if not isinstance(df.index, pd.DatetimeIndex):
            df = self._select_index(df)
            # msg = f"Data must have a DatetimeIndex: {df.index}"
            # raise TypeError(msg)

        df = df.sort_index()

        seconds = perf_counter() - start

        return df, seconds, source

    def select_file(self) -> pd.DataFrame:
        start = perf_counter()

        types = ["csv", "parquet", "parq"]
        compressed_types = []
        for c in ["zip", "gzip", "bz2", "zstd", "xz", "tar"]:
            compressed_types.extend(f"{t}.{c}" for t in types)
        file = st.file_uploader("upload-file", type=types + compressed_types, label_visibility="collapsed")

        if file is None:
            st.info("Select a file.", icon="ℹ️")  # noqa: RUF001
            st.stop()

        compression = file.name.rpartition(".")[-1] if file.name.endswith(tuple(compressed_types)) else None
        df = pd.read_csv(file, compression=compression)

        # Record performance
        seconds = perf_counter() - start
        msg = f"Read file `'{file.name}'` of size `{format_bytes(file.size)}` (`shape={df.shape}`) in `{fmt_sec(seconds)}`."
        log_perf(msg, df, seconds, extra={"file": file.name, "id": file.file_id, "type": file.type})
        st.caption(msg)

        return df

    @classmethod
    def show_data_overview(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Create data overview."""
        start = perf_counter()

        st.subheader("Overview", divider="rainbow")

        frames = [
            df.dtypes.rename("dtype"),
            df.memory_usage(index=False, deep=True).rename("memory").map(format_bytes),
            df.isna().mean().map("{:.2%}".format).rename("nan"),
            df.min().rename("min"),
            df.mean().rename("mean"),
            df.max().rename("max"),
            df.sum().rename("sum"),
        ]

        details = pd.concat(frames, axis=1)
        details.index.name = "Column"

        memory = df.memory_usage(index=True, deep=True)
        st.caption(
            f"Data has shape `{len(df)}x{len(df.columns)}` and contains `{df.size:{'_d' if df.size > 9999 else ''}}` "
            f"elements, using `{format_bytes(memory.sum())}` of memory (including `{format_bytes(memory['Index'])}` for"
            f" `index='{df.index.name}'` of type `{type(df.index).__name__}[{df.index.dtype}]`)."
        )
        st.dataframe(details, use_container_width=True)

        # Record performance
        seconds = perf_counter() - start
        msg = f"Created overview for data of `shape={df.shape}` in `{fmt_sec(seconds)}`."
        log_perf(msg, df, seconds, extra={"aggregations": sorted(details), "frame": "data-overview"})
        st.caption(msg)

        return details

    def show_data(self, df: pd.DataFrame) -> None:
        st.subheader("Data", divider="rainbow")

        sampled = df.sample(self.n_samples, random_state=2019_05_11).sort_index() if self.n_samples > 0 else df
        st.dataframe(sampled.reset_index(), hide_index=False, use_container_width=True)

        st.caption(f"Showing `{len(sampled)}/{len(df)} ({len(sampled) / len(df):.2%})` rows.")

    def get_data_sources(self) -> dict[DataSource, str]:
        sources = {}

        if self.sample_data:
            sources[DataSource.GENERATED] = "Timeseries in a selected range."
        if self.upload is not False:
            sources[DataSource.UPLOADED] = "Upload data from your computer."

        return sources

    def _select_range_subset(self, df: pd.DataFrame, source: DataSource) -> pd.DataFrame:
        min_value = df.index[0].to_pydatetime()
        max_value = df.index[-1].to_pydatetime()

        if source == DataSource.GENERATED and self.initial_sample_subset_range:
            start, end = self.initial_sample_subset_range
            value = pd.Timestamp(start).to_pydatetime(), pd.Timestamp(end).to_pydatetime()
        else:
            value = (min_value, max_value)

        start, end = st.slider(
            "Select partial range",
            min_value=min_value,
            max_value=max_value,
            value=value,
            step=pd.Timedelta(minutes=5).to_pytimedelta(),
            format="YYYY-MM-DD HH:mm:ss",
            help="Drag the sliders to use a subset of the original data.",
            # label_visibility="collapsed",
        )

        return df[start:end]

    @staticmethod
    def _select_index(df: pd.DataFrame) -> pd.DataFrame:
        index: None | int = None

        lower: pd.Index = df.columns.map(str.lower)
        for s in "date", "time", "datetime", "timestamp":
            try:
                index = lower.get_loc(s)
                break
            except KeyError:
                pass

        def format_func(column: str) -> str:
            return f"{column} [{df.dtypes[column]}]"

        selection = st.selectbox("Select index column", options=df.columns, format_func=format_func, index=index)

        st.code(df[selection].sample(2).map(repr).to_string())

        try:
            datetime_index = pd.DatetimeIndex(df[selection])
        except Exception as e:
            st.exception(e)
            st.stop()

        df[selection] = datetime_index
        df = df.set_index(selection)

        return df

    @classmethod
    def show_summary(cls, df: pd.DataFrame) -> None:
        index_start, index_end = df.index.min(), df.index.max()
        summary = {
            "Rows": len(df),
            "Cols": len(df.columns),
            "Start": index_start,
            "Span": fmt_sec((index_end - index_start).total_seconds()),
            "End": index_end,
        }
        st.dataframe(
            pd.Series(summary).to_frame().T,
            hide_index=True,
            use_container_width=True,
            selection_mode="single-column",
        )
