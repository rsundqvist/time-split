"""This is `very` limited.

There are loads of ways that the app can fail that this doesn't even begin to cover. Use the dev/*.sh-scripts to verify
changes.
"""

import os
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest
from time_split.streamlit import config
from time_split.streamlit.widgets.types import QueryParams

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true" and sys.platform != "linux",
    reason="Should be ran as a (Linux-based) Docker container.",
    # Fails in CI/CD for macOS:
    #   Fatal Python error: Aborted. (Somewhere inside matplotlib)
    # Not sure if it works on Windows. I don't care enough to find out, this is
    # not intended to run bare-metal.
)


@pytest.mark.filterwarnings("ignore")
def test_app(monkeypatch):
    _speed_things_up(monkeypatch)  # AppTest timeout is 3 seconds

    path = Path(__file__).parent.parent / "app.py"
    runner = AppTest.from_file(str(path)).run()

    verify_sections(runner)
    verify_frames(runner)


def verify_sections(runner: AppTest) -> None:
    actual = {container.value for container in runner.subheader}
    expected = {"Schedule", "Dataset spans", "Performance tweaker", "Select data"}  # Just a subset
    assert expected & actual == expected


def verify_frames(runner: AppTest) -> None:
    frames = [(len(container.value), container.value.columns.to_list()) for container in runner.dataframe]

    n = config.RAW_DATA_SAMPLES
    assert n == 100

    assert frames == [
        (1, ["Fold counts", "Data time", "Future data time"]),
        (12, ["fold_no", "fold", "dataset", "column 0", "column 1", "column 2", "n_rows", "n_hours"]),
        (100, ["timestamp", "column 0", "column 1", "column 2"]),
        (2, ["FIGURE_DPI", "PLOT_RAW_TIMESERIES", "PLOT_AGGREGATIONS_PER_FOLD", "MAX_SPLITS"]),
        (1, ["Rows", "Cols", "Start", "Span", "End", "Size"]),
        (2, ["Index", "Original", "Change", "Expanded"]),
    ]


def _speed_things_up(monkeypatch):
    monkeypatch.setattr(config, "PLOT_RAW_TIMESERIES", False)
    monkeypatch.setattr(config, "PLOT_AGGREGATIONS_PER_FOLD", False)
    monkeypatch.setattr(config, "FIGURE_DPI", 10)
    monkeypatch.setattr(config, "RAW_DATA_SAMPLES", 100)


class TestQueryParams:
    @pytest.mark.parametrize(
        "data, expected",
        [
            # Trivial zeroing of all fields except the minute
            # start=2019-05-01 00:00:31
            ("1556668831-1557606871", ("2019-05-01 00:00:00", "2019-05-11 20:35:00")),  # end=20:34:31
            ("1556668831-1557606749", ("2019-05-01 00:00:00", "2019-05-11 20:30:00")),  # end=20:32:29
            # Flipping hours/dates
            # start=(2019-04-30 23:59:40, 2019-05-11 20:59:31)
            ("1556668780-1557608371", ("2019-05-01 00:00:00", "2019-05-11 21:00:00")),
            # Exact
            ("1556668800-1557606600", ("2019-05-01 00:00:00", "2019-05-11 20:30:00")),
        ],
    )
    def test_timestamps(self, data: str, expected: tuple[str, str]) -> None:
        expected_start, expected_end = expected

        actual = QueryParams.make(data=data).data  # naive utc
        assert isinstance(actual, tuple) and len(actual) == 2
        start, end = map(str, actual)

        assert start == expected_start
        assert end == expected_end
