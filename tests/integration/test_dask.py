import pytest
from dask.callbacks import Callback
from dask.datasets import timeseries

from time_split import plot, split
from time_split.support import fold_weight, process_available


@pytest.mark.parametrize("kind", ["index", "series"])
def test_dask(kind):
    df = timeseries(end="2000-04", freq="17 min", partition_freq="7D", dtypes={"x": int})

    if kind == "index":
        available = df.index
    else:
        df["time-column"] = df.index
        available = df["time-column"]
    kwargs = dict(schedule="7d", before="all", after="30 days", available=available)

    unlimited_splits = split(**kwargs)
    assert len(unlimited_splits) == 9
    assert unlimited_splits[-1].end.isoformat() == "2000-04-01T00:00:00"

    ax = plot(**kwargs, n_splits=5, show_removed=True, row_count_bin="1d")

    xtick_labels = [t.get_text() for t in ax.get_xticklabels()]
    assert len(xtick_labels) == len(unlimited_splits) + 2
    assert f"dask.dataframe.{kind.capitalize()}" in ax.get_title()

    for i, (left, right) in enumerate(zip(xtick_labels[1:-1], unlimited_splits, strict=True)):
        # Only mid (index 1) is added
        assert left in str(right[1]), i

    splits = split(**kwargs, n_splits=5)
    assert len(splits) == 5
    assert splits[-1].end.isoformat() == "2000-04-01T00:00:00"
    assert splits[0] == unlimited_splits[-5]


def test_index_is_preserved():
    available = timeseries(freq="10 min").index

    actual = process_available(available, expand_limits=False).available_as_index
    assert id(available) == id(actual)


def test_series_is_preserved():
    from dask.dataframe import Series

    available = timeseries(freq="10 min").index

    actual = process_available(available, expand_limits=False).available_as_index
    assert isinstance(actual, Series)


class TestComputeOnce:
    @pytest.mark.xfail(strict=True)
    def test_the_test(self):
        available = self._available()

        with ComputeOnce():
            self._split(available)
            self._split(available)

    def test_split(self):
        available = self._available()

        with ComputeOnce():
            splits = self._split(available)

        assert len(splits) == 9

    def test_fold_weight(self):
        available = self._available()
        splits = self._split(available)

        with ComputeOnce():
            fold_weight(splits, unit="rows", available=available)

    @staticmethod
    def _available():
        return timeseries(end="2000-04", freq="17 min", partition_freq="7D", dtypes={"x": int}).index

    @staticmethod
    def _split(available):
        return split("7d", before="all", after="30 days", available=available)


class ComputeOnce(Callback):
    def __init__(self):
        super().__init__(self._check)
        self._called = False

    def _check(self, _dsk):
        if self._called:
            raise AssertionError("called more than once")
        self._called = True
