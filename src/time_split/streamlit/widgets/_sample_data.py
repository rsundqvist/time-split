from dataclasses import dataclass
from pathlib import Path
from typing import Any, final

import pandas as pd
import streamlit as st

from time_split.types import DatetimeTypes, TimedeltaTypes

from ._datetime import select_datetime


@dataclass(frozen=True)
class SampleDataWidget:
    initial_range: bool | tuple[DatetimeTypes, DatetimeTypes] = ("2019-01-01", "2019-06-01")
    """Control `'data'` selection using time ranges. Disabled if ``False``.

    Based on :meth:`load_sample_data` if ``True``. Otherwise, specify a tuple ``(min_start, max_end)``. Will appear as
    a datetime slider to the user.
    
    This attribute determines the initial value. Use :attr:`datetime_range_limits` to control the limits.
    """

    freq: str | TimedeltaTypes = "h"
    """Index frequency."""

    def select_sample_data(self, prompt: bool = True) -> pd.DataFrame:
        start, end = map(pd.Timestamp, self.initial_range)

        if prompt:
            left, right = st.columns(2)
            with left:
                start = select_datetime("Start", start.to_pydatetime())
            with right:
                end = select_datetime("End", end.to_pydatetime())

        if start >= end:
            st.error(f"Bad range: `start='{start}'` must be before `end='{end}'`", icon="🚨")
            st.stop()

        return self._load_sample_date(n_rows=None, start=start, end=end, freq=self.freq)

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
        end: DatetimeTypes | None,
        freq: str | TimedeltaTypes | None = "h",
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

        df.columns = [f"column {i}" for i in df]
        df.index = index

        return df

    @classmethod
    def _create_index(
        cls,
        n_rows: int = 397,
        *,
        start: DatetimeTypes | None = None,
        end: DatetimeTypes | None = None,
        freq: str | TimedeltaTypes | None = None,
    ) -> pd.DatetimeIndex:
        return pd.date_range(start, end, freq=freq, periods=n_rows, name="timestamp")

    def _get_slider_format(self) -> str:
        return self.datetime_slider_format or "YYYY-MM-DD HH:mm:ss"
