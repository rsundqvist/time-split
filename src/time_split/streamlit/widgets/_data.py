import logging
from dataclasses import dataclass, field
from enum import StrEnum
from time import perf_counter

import pandas as pd
import streamlit as st
from rics.strings import format_bytes

from time_split._compat import fmt_sec

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
    n_samples: int | None = 5
    """Number of sample rows to show.
    
    Set to 0 to hide the sampled data view, or -1 to show all rows. Set to ``None`` to disable entirely.
    """

    # sample_data_glob_path: str | Path = "sample-data/*.csv"

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
            df, seconds = self._load_data(source)

        df = df.convert_dtypes(dtype_backend="pyarrow")

        return df, (df.index.min(), df.index.max()), seconds

    @classmethod
    def brief(cls, df: pd.DataFrame, seconds: float) -> None:
        index_start, index_end = df.index.min(), df.index.max()
        summary = {
            "Rows": len(df),
            "Columns": len(df.columns),
            "Start": index_start,
            "Span": fmt_sec((index_end - index_start).total_seconds()),
            "End": index_end,
            "Time": fmt_sec(seconds),
        }
        st.dataframe(
            pd.Series(summary).to_frame().T,
            hide_index=True,
            use_container_width=True,
            selection_mode="single-column",
        )

    def _load_data(self, source: DataSource) -> tuple[pd.DataFrame, float]:
        df: pd.DataFrame | None = None

        start = perf_counter()
        if source == DataSource.GENERATED:
            assert self.sample_data is not None, "no sample data widget configured"
            df = df if isinstance(self.sample_data, pd.DataFrame) else self.sample_data.select_sample_data()

        if source == DataSource.UPLOADED:
            df = self.select_file()

        if df is None:
            raise NotImplementedError(f"{source=}")

        if not isinstance(df.index, pd.DatetimeIndex):
            df = self._select_index(df)
            # msg = f"Data must have a DatetimeIndex: {df.index}"
            # raise TypeError(msg)

        seconds = perf_counter() - start

        return df, seconds

    def select_file(self) -> pd.DataFrame:
        start = perf_counter()

        logger = logging.getLogger(f"{type(self).__name__}.upload")

        file = st.file_uploader("upload-file", type=["csv", "parquet", "parq", "zip"], label_visibility="collapsed")

        if file is None:
            st.info("Select a file.", icon="ℹ️")
            st.stop()

        df = pd.read_csv(file, compression="zip")

        seconds = perf_counter() - start
        msg = f"Read file `'{file.name}'` of size `{format_bytes(file.size)}` (`shape={df.shape}`) in `{fmt_sec(seconds)}`."
        st.caption(msg)
        logger.info(
            msg,
            extra={
                "file": file.name,
                "id": file.file_id,
                "size": file.size,
                "type": file.type,
                "shape": df.shape,
                "duration_ms": int(1000 * seconds),
            },
        )

        # if file.name.endswith(".csv"):
        # else:
        #    raise NotImplementedError(file)

        return df

    def show_data_details(self, df: pd.DataFrame) -> None:
        st.subheader("Data details", divider="rainbow")

        frames = [
            df.dtypes.rename("dtype"),
            df.isna().mean().map("{:.2%}".format).rename("nan"),
            df.min().rename("min"),
            df.mean().rename("mean"),
            df.max().rename("max"),
            df.sum().rename("sum"),
        ]
        details = pd.concat(frames, axis=1)
        details.index.name = "Column"

        st.caption(f"Overview for `{len(df.columns)}` columns.")
        st.dataframe(details, use_container_width=True)

        if self.n_samples is not None:
            sampled = df.sample(self.n_samples).sort_index() if self.n_samples > 0 else df
            st.caption(f"Showing `{len(sampled)}/{len(df)} ({len(sampled) / len(df):.2%})` random rows.")
            st.dataframe(sampled, use_container_width=True)

    def get_data_sources(self) -> dict[DataSource, str]:
        sources = {}

        if self.sample_data:
            sources[DataSource.GENERATED] = "Timeseries in a selected range."
        if self.upload is not False:
            sources[DataSource.UPLOADED] = "Upload data from your computer."

        return sources

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


class TodoUseUse:
    def select_columns(df: pd.DataFrame) -> pd.DataFrame:
        columns = df.columns.to_list()
        selection = st.multiselect("Columns", columns, columns)
        if not selection:
            selection = columns

        df = df[selection]

        types = (f"{col!r}: {dtype}" for col, dtype in df.dtypes.items())
        st.write(f"Chosen columns ({len(selection)}/{len(columns)}): `{', '.join(types)}`")
        return df
