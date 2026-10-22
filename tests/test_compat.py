import pytest

from time_split._compat import fix_pandas4_warning


@pytest.mark.parametrize(
    "arg, expected",
    [
        ("d", "D"),
        ("1d", "1D"),
        ("7 d", "7 D"),
        ("1.5d", "1.5D"),
        ("1d2h", "1D2h"),
        ("1 days", "1 days"),
        ("2 hours", "2 hours"),
    ],
)
def test_fix_pandas4_warning(arg, expected):
    assert fix_pandas4_warning(arg) == expected
