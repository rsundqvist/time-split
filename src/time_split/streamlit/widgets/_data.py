from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from time import perf_counter
from typing import Any, final

import pandas as pd
import streamlit as st

from time_split._compat import fmt_sec
from time_split.types import DatetimeTypes, TimedeltaTypes

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

    def load_data(self) -> tuple[pd.DataFrame, tuple[pd.Timestamp, pd.Timestamp], float]:
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
            st.file_uploader("upload-file", type=["csv", "parquet", "parq"])
            raise NotImplementedError

        if df is None:
            raise NotImplementedError(f"{source=}")

        if not isinstance(df.index, pd.DatetimeIndex):
            msg = f"Data must have a DatetimeIndex: {df.index}"
            raise TypeError(msg)

        seconds = perf_counter() - start

        return df, seconds

    def show_data_details(self, df: pd.DataFrame) -> None:
        st.subheader("Data details", divider="rainbow")

        frames = [
            df.dtypes.rename("dtype"),
            df.isna().mean().map("{:.2%}".format).rename("nan"),
            df.sum().rename("sum"),
            df.min().rename("min"),
            df.mean().rename("mean"),
            df.max().rename("max"),
        ]
        details = pd.concat(frames, axis=1)
        details.index.name = "Column"

        st.caption(f"Overview for `{len(df.columns)}` columns.")
        st.dataframe(details, use_container_width=True)

        if self.n_samples is not None:
            sampled = df.sample(self.n_samples) if self.n_samples > 0 else df
            st.caption(f"Showing `{len(sampled)}/{len(df)} ({len(sampled) / len(df):.2%})` random rows.")
            st.dataframe(sampled, use_container_width=True)

    def get_data_sources(self) -> dict[DataSource, str]:
        sources = {}

        if self.sample_data:
            sources[DataSource.GENERATED] = "Timeseries in a selected range."
        if self.upload is not False:
            sources[DataSource.UPLOADED] = "Upload data from your computer."

        return sources


@dataclass(frozen=True)
class SampleDataWidget:
    datetime_range: bool | tuple[DatetimeTypes, DatetimeTypes] = True
    """Control `'data'` selection using time ranges. Disabled if ``False``.

    Based on :meth:`load_sample_data` if ``True``. Otherwise, specify a tuple ``(min_start, max_end)``. Will appear as
    a datetime slider to the user.
    """
    datetime_range_step: TimedeltaTypes = "1 hour"
    """Controls increment size for the :attr:`datetime_range` widget (if enabled)."""

    datetime_slider_format: str | None = None
    """The https://momentjs.com/docs/#/displaying/format/ format spec to use. Derive if ``None``."""

    def get_datetime_range(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        """Returns configured limits for the available data range slider."""
        if isinstance(self.datetime_range, bool):
            index = self._load_sample_date().index
            return index[0], index[-1]
        else:
            lo, hi = self.datetime_range
            return pd.Timestamp(lo), pd.Timestamp(hi)

    @final
    @st.cache_data
    def _load_sample_date(self, **kwargs: Any) -> pd.DataFrame:
        return self.load_sample_data(**kwargs)

    @classmethod
    def load_sample_data(
        cls,
        n_rows: int | None = 397,
        *,
        start: DatetimeTypes | None = None,
        end: DatetimeTypes | None = "2019-05-11 20:30",
        freq: str | TimedeltaTypes = "h",
    ) -> pd.DataFrame:
        """Load timeseries sample data.

        The original timeseries has 397 rows. If `length` is greater, the original timeseries is repeated. Every other
        frames is reversed in order to preserve continuity. Index is generated using :func:`pandas.date_range`, using
        ``periods=n_rows``.

        Args:
            n_rows: Desired timeseries length.
            start: Index start.
            end: Index end.
            freq: Index frequency.

        Returns:
            Sample timeseries data.
        """
        timeseries = pd.read_csv(Path(__file__).parent / "timeseries.csv", header=None)
        reverse_timeseries = timeseries.iloc[::-1]

        index = cls._create_index(n_rows, start=start, end=end, freq=freq)

        frames = []
        while len(frames) * len(timeseries) < len(index):
            frames.append(reverse_timeseries if len(frames) % 2 else timeseries)
        df = pd.concat(frames, ignore_index=True)

        if len(df) > len(index):
            df = df.tail(len(index))

        df.columns = [f"Column {i}" for i in df]
        df.index = index

        return df

    @classmethod
    def _create_index(
        cls,
        n_rows: int = 397,
        *,
        start: DatetimeTypes | None = None,
        end: DatetimeTypes | None = "2019-05-11 20:30",
        freq: str | TimedeltaTypes = "h",
    ) -> pd.DatetimeIndex:
        return pd.date_range(start, end, freq=freq, periods=n_rows, name="timestamp")

    def _get_slider_format(self) -> str:
        return self.datetime_slider_format or "YYYY-MM-DD HH:mm:ss"


class TodoUseUse:
    def select_index(df: pd.DataFrame) -> tuple[pd.DataFrame, tuple[pd.Timestamp, pd.Timestamp]]:
        index: None | int = None

        lower: pd.Index = df.columns.map(str.lower)
        for s in "date", "time", "datetime", "timestamp":
            try:
                index = lower.get_loc(s)
                break
            except KeyError:
                pass

        selection = st.selectbox("Choose index", options=df.columns, index=index)

        # df[selection] = df[selection].map(date.fromisoformat)
        # TypeError: Cannot compare Timestamp with datetime.date. Use ts == pd.Timestamp(date) or ts.date() == date instead.
        df[selection] = df[selection].map(pd.Timestamp)

        df = df.set_index(selection)

        st.write(f"Index column: `{selection!r}:{df.index.dtype}`")

        return df, (df.index.min(), df.index.max())


    def select_columns(df: pd.DataFrame) -> pd.DataFrame:
        columns = df.columns.to_list()
        selection = st.multiselect("Columns", columns, columns)
        if not selection:
            selection = columns

        df = df[selection]

        types = (f"{col!r}: {dtype}" for col, dtype in df.dtypes.items())
        st.write(f"Chosen columns ({len(selection)}/{len(columns)}): `{', '.join(types)}`")
        return df
