import sys
from importlib.util import find_spec

import pytest


def test_import() -> None:
    from time_split import split

    print(f"imported: {split}")


@pytest.fixture(autouse=True)
def reimport_time_split(monkeypatch):
    names = [name for name in sys.modules if name.startswith("time_split")]
    print(reimport_time_split)
    for name in names:
        print(f"{name=}")
        monkeypatch.delitem(sys.modules, name, raising=False)


@pytest.fixture(autouse=True)
def pandas_missing(monkeypatch):
    name = "pandas"
    monkeypatch.setitem(sys.modules, name, None)
    assert find_spec(name) is None
