import pandas as pd
import pytest

from time_split import split
from time_split import types as st

from .conftest import DATA_CASES, NO_DATA_CASES, NO_DATA_SCHEDULE, SPLIT_DATA


@pytest.mark.parametrize("kwargs, expected", *DATA_CASES)
def test_data(kwargs, expected):
    actual = split(**kwargs, available=SPLIT_DATA)

    for i, (left, right) in enumerate(zip(actual, expected, strict=True)):
        assert left == st.DatetimeSplitBounds(*map(pd.Timestamp, right)), i
    assert len(actual) == len(expected)


class TestSnapToEnd:
    @staticmethod
    def _run(monkeypatch, *, snap_to_end):
        from time_split.settings import misc as settings

        monkeypatch.setattr(settings, "snap_to_end", snap_to_end)

        dates = []
        for bounds in split(schedule="3d", before="3d", after="2d", available=SPLIT_DATA):
            for ts in bounds:
                assert ts.normalize() == ts
            dates.append(tuple(ts.date().isoformat() for ts in bounds))
        return dates

    def test_true(self, monkeypatch):
        actual = self._run(monkeypatch, snap_to_end=True)
        assert actual == [
            ("2022-01-03", "2022-01-06", "2022-01-08"),
            ("2022-01-06", "2022-01-09", "2022-01-11"),
            ("2022-01-09", "2022-01-12", "2022-01-14"),
        ]

    def test_false(self, monkeypatch):
        actual = self._run(monkeypatch, snap_to_end=False)
        assert actual == [
            ("2022-01-01", "2022-01-04", "2022-01-06"),
            ("2022-01-04", "2022-01-07", "2022-01-09"),
            ("2022-01-07", "2022-01-10", "2022-01-12"),
        ]


@pytest.mark.parametrize(
    "round_limits, snap_to_end, expected",
    [
        (False, False, "2019-05-10 23:55:00"),
        (False, True, "2019-05-11 23:55:00"),
        (True, False, "2019-05-11 00:00:00"),
        (True, True, "2019-05-12 00:00:00"),
    ],
)
def test_round_limits_snap_to_end_interaction(monkeypatch, *, round_limits, snap_to_end, expected):
    from time_split.settings import misc as settings

    limits = "2019-04-10 23:55:00", "2019-05-12 01:00:00"

    monkeypatch.setattr(settings, "round_limits", round_limits)
    monkeypatch.setattr(settings, "snap_to_end", snap_to_end)

    folds = split(schedule="7d", before="3d", after="2d", available=limits)
    assert len(folds) == 4
    assert str(folds[-1].end) == expected


@pytest.mark.parametrize("kwargs, expected", *DATA_CASES)
def test_data_utc(kwargs, expected):
    actual = split(**kwargs, available=SPLIT_DATA.tz_localize("utc"))

    for i, (left, right) in enumerate(zip(actual, expected, strict=False)):
        assert left == st.DatetimeSplitBounds(*(pd.Timestamp(ts, tz="utc") for ts in right)), i
    assert len(actual) == len(expected)


@pytest.mark.parametrize(
    "after, expected",
    NO_DATA_CASES,
)
def test_no_data(after, expected):
    actual = list(split(schedule=NO_DATA_SCHEDULE, before="5d", after=after))

    for i, (left, right) in enumerate(zip(actual, expected, strict=False)):
        assert left == st.DatetimeSplitBounds(*map(pd.Timestamp, right)), i
    assert len(expected) == len(actual)


@pytest.mark.parametrize(
    "step, expected",
    [
        (
            1,
            [
                "2022-01-13",
                "2022-01-20",
                "2022-01-27",
                "2022-02-03",
                "2022-02-10",
                "2022-02-17",
                "2022-02-24",
            ],
        ),
        (2, ["2022-01-13", "2022-01-27", "2022-02-10", "2022-02-24"]),
        (3, ["2022-01-13", "2022-02-03", "2022-02-24"]),
        (4, ["2022-01-27", "2022-02-24"]),
        (7, ["2022-02-24"]),
        (8, ["2022-02-24"]),
    ],
)
class TestStep:
    @staticmethod
    def split(step, n_splits):
        return split(
            "0 0 * * THU",
            after="5d",
            available=pd.date_range("2022-01", "2022-03"),
            step=step,
            n_splits=n_splits,
        )

    def test_positive_and_negative(self, step, expected):
        assert [f.mid for f in self.split(step, n_splits=0)] == [pd.Timestamp(e) for e in expected]
        assert [f.mid for f in self.split(-step, n_splits=0)] == [pd.Timestamp(e) for e in reversed(expected)]

    @pytest.mark.parametrize("n_splits", [2, 3])
    def test_n_split(self, n_splits, step, expected):
        expected = expected[-n_splits:]
        assert [f.mid for f in self.split(step, n_splits=n_splits)] == [pd.Timestamp(e) for e in expected]
        assert [f.mid for f in self.split(-step, n_splits=n_splits)] == [pd.Timestamp(e) for e in reversed(expected)]


def test_filter(monkeypatch):
    # Base case - this is DATA_CASES[0]
    actual = split(schedule="68h", before="5d", after="1d", available=SPLIT_DATA)
    expected = [
        ("2022-01-02 20:00:00", "2022-01-07 20:00:00", "2022-01-08 20:00:00"),
        ("2022-01-05 16:00:00", "2022-01-10 16:00:00", "2022-01-11 16:00:00"),
        ("2022-01-08 12:00:00", "2022-01-13 12:00:00", "2022-01-14 12:00:00"),
    ]

    for left, right in zip(actual, expected, strict=True):
        assert left == st.DatetimeSplitBounds(*map(pd.Timestamp, right))

    # Test with filter
    kept = "2022-01-10 16:00:00"

    n_calls = 0

    def func(start: pd.Timestamp, mid: pd.Timestamp, end: pd.Timestamp) -> bool:  # noqa: ARG001
        nonlocal n_calls
        n_calls += 1
        return str(mid) == kept

    monkeypatch.setattr("time_split.settings.misc.filter", func)

    actual = split(schedule="68h", before="5d", after="1d", available=SPLIT_DATA)
    assert len(actual) == 1
    assert str(actual[0][1]) == "2022-01-10 16:00:00"
    assert actual[0] == st.DatetimeSplitBounds(*map(pd.Timestamp, expected[1]))
    assert n_calls == 3

    # Test with filter and ignore_filters = True
    actual = split(schedule="68h", before="5d", after="1d", available=SPLIT_DATA, ignore_filters=True)
    assert n_calls == 3
    for left, right in zip(actual, expected, strict=True):
        assert left == st.DatetimeSplitBounds(*map(pd.Timestamp, right))
