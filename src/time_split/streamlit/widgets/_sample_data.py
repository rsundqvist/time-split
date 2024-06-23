from dataclasses import dataclass
from pathlib import Path
from typing import Any, final

import pandas as pd
import streamlit as st

from time_split.types import DatetimeTypes, TimedeltaTypes


@dataclass(frozen=True)
class SampleDataWidget:
    datetime_range: bool | tuple[DatetimeTypes, DatetimeTypes] = ("2019-04-11", "2019-05-11 20:30")
    """Control `'data'` selection using time ranges. Disabled if ``False``.

    Based on :meth:`load_sample_data` if ``True``. Otherwise, specify a tuple ``(min_start, max_end)``. Will appear as
    a datetime slider to the user.
    
    This attribute determines the initial value. Use :attr:`datetime_range_limits` to control the limits.
    """
    datetime_range_limits: tuple[DatetimeTypes, DatetimeTypes] | None = ("2019-04-01", "2019-06-01")
    """Controls datetime slider limits. Set to ``None`` to use :attr:`datetime_range`."""
    datetime_range_step: TimedeltaTypes = "1 hour"
    """Controls increment size for the :attr:`datetime_range` widget (if enabled)."""

    datetime_slider_format: str | None = None
    """The https://momentjs.com/docs/#/displaying/format/ format spec to use. Derive if ``None``."""

    freq: str | TimedeltaTypes = "h"
    """Index frequency."""

    def select_sample_data(self, prompt: bool = True) -> pd.DataFrame:
        value = tuple(map(pd.Timestamp.to_pydatetime, self.get_datetime_range()))

        if prompt:
            if self.datetime_range_limits is None:
                min_value, max_value = value
            else:
                min_value, max_value = self.datetime_range_limits
                min_value = pd.Timestamp(min_value).to_pydatetime()
                max_value = pd.Timestamp(max_value).to_pydatetime()

            start, end = st.slider(
                "generate-data-in-range",
                min_value=min_value,
                max_value=max_value,
                value=value,
                step=pd.Timedelta(self.datetime_range_step).to_pytimedelta(),
                format=self._get_slider_format(),
                label_visibility="collapsed",
            )
        else:
            start, end = value

        return self._load_sample_date(n_rows=None, start=start, end=end, freq=self.freq)

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
