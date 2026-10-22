import logging
import sys
from typing import Any

import pandas as pd
import pytest

from time_split.integration._log_progress import handle_log_progress_arg
from time_split.types import DatetimeSplitBounds, DatetimeSplits


@pytest.mark.parametrize(
    "arg, name",
    [
        (True, "time_split"),
        ("handle-log-progress-arg", "handle-log-progress-arg"),
    ],
)
def test_handle_log_progress_arg(arg, name, caplog):
    _run(arg, name, caplog)


def test_logger_adapter(caplog):
    # merge_extra only exists on 3.13+; https://github.com/python/cpython/pull/107292

    logger = logging.getLogger("test-logger-adapter")
    extra = {"foo": "bar"}
    if sys.version_info < (3, 13):
        arg = logging.LoggerAdapter(logger, extra=extra)
    else:
        arg = logging.LoggerAdapter(logger, extra=extra, merge_extra=True)

    _run(arg, "test-logger-adapter", caplog)
    for record in caplog.records:
        assert record.foo == "bar"


@pytest.mark.parametrize("extra", [None, {"foo": "bar"}])
def test_plain_logger_adapter_keeps_progress_extras(extra, caplog):
    # No merge_extra; progress extras (n, start, mid, end, seconds) must survive anyway.
    logger = logging.getLogger("test-plain-logger-adapter")

    _run(logging.LoggerAdapter(logger, extra=extra), "test-plain-logger-adapter", caplog)
    for record in caplog.records:
        assert record.n_splits == 3
        if extra:
            assert record.foo == "bar"


def test_custom_logger_adapter_process_is_kept(caplog):
    class PrefixAdapter(logging.LoggerAdapter[Any]):
        def process(self, msg, kwargs):
            msg, kwargs = super().process(msg, kwargs)
            kwargs["extra"] = {**kwargs["extra"], "custom": True}
            return f"[prefix] {msg}", kwargs

    logger = logging.getLogger("test-custom-logger-adapter")

    _run(PrefixAdapter(logger, extra={"foo": "bar"}), "test-custom-logger-adapter", caplog)
    for record in caplog.records:
        assert record.getMessage().startswith("[prefix] ")
        assert record.custom is True
        assert record.foo == "bar"
        assert record.n_splits == 3


def _run(arg, name, caplog):
    splits: DatetimeSplits = [
        DatetimeSplitBounds(*map(pd.Timestamp, [f"1991-{i}", f"1999-{i}", f"2019-{i}"])) for i in [2, 4, 6]
    ]
    assert handle_log_progress_arg(False, splits=splits) is None
    tracked_splits = handle_log_progress_arg(arg, splits=splits)
    assert tracked_splits is not None
    assert len(list(tracked_splits)) == len(splits)
    assert len(caplog.records) == 2 * len(splits)
    for i, record in enumerate(caplog.records):
        fold = splits[i // 2]
        assert fold.start.isoformat() == record.start
        assert fold.mid.isoformat() == record.mid
        assert fold.end.isoformat() == record.end
        assert record.name == name
