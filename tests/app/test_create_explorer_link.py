from urllib.parse import ParseResult, urlparse

import pytest

from time_split.app import create_explorer_link

LIMITS = ("2019-04-11 00:35:00", "2019-05-11 21:30:00")


def test_docs_link():
    link = create_explorer_link(
        "https://time-split.streamlit.app",
        LIMITS,
        schedule="0 0 * * MON,FRI",
        n_splits=2,
        step=2,
    )
    assert urlparse(link) == ParseResult(
        scheme="https",
        netloc="time-split.streamlit.app",
        path="",
        params="",
        query="data=1554942900-1557610200&schedule=0+0+%2A+%2A+MON%2CFRI&n_splits=2&step=2&show_removed=True",
        fragment="",
    )


@pytest.mark.parametrize("skip, mid", [(True, ""), (False, "&after=1")])
def test_defaults(skip, mid):
    expected = f"http://localhost:8501/?data=1554942900-1557610200&schedule=1d{mid}&show_removed=True"
    actual = create_explorer_link("http://localhost:8501/", LIMITS, schedule="1d", after=1, skip_default=skip)
    assert actual == expected


def test_bytes_data():
    from time_split.app._create_explorer_link import encode_binary_data  # type: ignore[attr-defined]

    data = b"arbitrary user data"
    encoded_data = b"61726269747261727920757365722064617461"
    assert encode_binary_data(data) == encoded_data

    expected = f"http://localhost:8501/?data=0x{encoded_data.decode()}&schedule=1d&show_removed=True"
    actual = create_explorer_link("http://localhost:8501/", data, schedule="1d")
    assert actual == expected
