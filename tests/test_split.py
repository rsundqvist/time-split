import pandas as pd
import pytest

from time_split import settings, split
from time_split import types as st

from .conftest import DATA_CASES, NO_DATA_CASES, NO_DATA_SCHEDULE, SPLIT_DATA


@pytest.mark.parametrize("kwargs, expected", *DATA_CASES)
def test_data(kwargs, expected):
    actual = split(**kwargs, available=SPLIT_DATA)

    for i, (left, right) in enumerate(zip(actual, expected, strict=False)):
        assert left == st.DatetimeSplitBounds(*map(pd.Timestamp, right)), i
    assert len(actual) == len(expected)


class TestSnapToEnd:
    @staticmethod
    def _run(monkeypatch, *, snap_to_end):
        monkeypatch.setattr(settings.misc, "snap_to_end", snap_to_end)

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
        (False, True, "2019-05-12 01:00:00"),
        (True, False, "2019-05-11 00:00:00"),
        (True, True, "2019-05-12 00:00:00"),
    ],
)
def test_round_limits_snap_to_end_interaction(monkeypatch, *, round_limits, snap_to_end, expected):
    limits = "2019-04-10 23:55:00", "2019-05-12 01:00:00"

    monkeypatch.setattr(settings.misc, "round_limits", round_limits)
    monkeypatch.setattr(settings.misc, "snap_to_end", snap_to_end)

    folds = split(schedule="7d", before="3d", after="2d", available=limits)
    assert len(folds) == 4
    assert str(folds[-1].end) == expected


def foo(arg):
    from rics.misc import format_kwargs

    return format_kwargs(arg, max_value_length=8) if isinstance(arg, dict) else format_kwargs(dict(expected=arg))


@pytest.mark.parametrize("kwargs, expected", *DATA_CASES, ids=foo)
def test_data_utc(kwargs, expected):
    actual = split(**kwargs, available=SPLIT_DATA.tz_localize("utc"))

    expected = [
        st.DatetimeSplitBounds(pd.Timestamp(start, tz="utc"), pd.Timestamp(mid, tz="utc"), pd.Timestamp(end, tz="utc"))
        for start, mid, end in expected
    ]

    for i, (left, right) in enumerate(zip(actual, expected, strict=False)):
        assert left == right, i
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


def test_filter():
    # Base case - this is DATA_CASES[0]
    kwargs = st.DatetimeIndexSplitterKwargs(schedule="68h", before="5d", after="1d")

    actual = split(available=SPLIT_DATA, **kwargs)
    expected = [
        ("2022-01-02 08:00:00", "2022-01-07 08:00:00", "2022-01-08 08:00:00"),
        ("2022-01-05 04:00:00", "2022-01-10 04:00:00", "2022-01-11 04:00:00"),
        ("2022-01-08 00:00:00", "2022-01-13 00:00:00", "2022-01-14 00:00:00"),
    ]

    for left, right in zip(actual, expected, strict=True):
        assert left == st.DatetimeSplitBounds(*map(pd.Timestamp, right))

    # Test with filter
    kept = expected[1][1]

    n_calls = 0

    def func(_start: pd.Timestamp, mid: pd.Timestamp, _end: pd.Timestamp) -> bool:
        nonlocal n_calls
        n_calls += 1
        return str(mid) == kept

    kwargs["filter"] = func

    actual = split(**kwargs, available=SPLIT_DATA)
    assert len(actual) == 1
    assert str(actual[0][1]) == kept
    assert actual[0] == st.DatetimeSplitBounds(*map(pd.Timestamp, expected[1]))
    assert n_calls == 3

    # Test with filter and ignore_filters = True
    actual = split(**kwargs, available=SPLIT_DATA, ignore_filters=True)
    assert n_calls == 3
    for left, right in zip(actual, expected, strict=True):
        assert left == st.DatetimeSplitBounds(*map(pd.Timestamp, right))


@pytest.mark.parametrize(
    "schedule",
    [
        "0 0 * * MON,FRI",
        ["2022-01-03", "2022-01-07", "2022-01-10", "2022-01-14", "2022-01-17"],
        pd.DatetimeIndex(["2022-01-03", "2022-01-07", "2022-01-10", "2022-01-14", "2022-01-17"]),
    ],
    ids=["cron", "explicit:list", "explicit:DatetimeIndex"],
)
def test_does_not_apply_to_cron_or_explicit(schedule):
    start = "2022-01-01"
    expected = [
        (start, "2022-01-03", "2022-01-06"),
        (start, "2022-01-07", "2022-01-10"),
        (start, "2022-01-10", "2022-01-13"),
        (start, "2022-01-14", "2022-01-17"),
        (start, "2022-01-17", "2022-01-20"),
    ]

    actual = split(
        schedule,
        before="all",
        after="3d",
        available=(start, "2022-01-21"),
    )
    for left, right in zip(actual, expected, strict=True):
        assert left == st.DatetimeSplitBounds(*map(pd.Timestamp, right))
        assert left.mid.day_name() in {"Monday", "Friday"}, f"{left.mid:%Y-%m-%d, %A}"


class TestEmptySpan:
    def test_before(self):
        expected = [
            ("2019-05-01", "2019-05-01", "2019-05-08"),
            ("2019-05-02", "2019-05-02", "2019-05-09"),
            ("2019-05-03", "2019-05-03", "2019-05-10"),
            ("2019-05-04", "2019-05-04", "2019-05-11"),
        ]
        for s in expected:
            assert s[0] == s[1]

        actual = split("1d", available=("2019-05-01", "2019-05-11"), before="empty", after="7d")

        for left, right in zip(actual, expected, strict=True):
            assert left == st.DatetimeSplitBounds(*map(pd.Timestamp, right))

    def test_after(self):
        expected = [
            ("2019-05-01", "2019-05-08", "2019-05-08"),
            ("2019-05-02", "2019-05-09", "2019-05-09"),
            ("2019-05-03", "2019-05-10", "2019-05-10"),
            ("2019-05-04", "2019-05-11", "2019-05-11"),
        ]
        for s in expected:
            assert s[1] == s[2]

        actual = split("1d", available=("2019-05-01", "2019-05-11"), before="7d", after="empty")

        for left, right in zip(actual, expected, strict=True):
            assert left == st.DatetimeSplitBounds(*map(pd.Timestamp, right))
