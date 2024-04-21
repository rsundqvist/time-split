import pandas as pd
import pytest
from time_split import log_split_progress, settings, split


@pytest.mark.parametrize("extra", ["{{escaped-key}}", "{extra0}", "{extra1}", "{extra1} and {extra1}!"])
def test_extra(extra, caplog, monkeypatch):
    monkeypatch.setattr(
        settings.log_split_progress,
        "START_MESSAGE",
        settings.log_split_progress.START_MESSAGE + f"\n - extra={extra}, mutable={{mutable}}",
    )

    user_extra = {"extra0": 0, "extra1": 1, "mutable": "a"}
    for i, _ in enumerate(
        log_split_progress(split(["2022-1", "2022-2", "2022-3"], after="1d"), extra=user_extra),
        start=1,
    ):
        record = caplog.records[-1]
        must_contain = extra.format(**user_extra)
        assert record.message.startswith("Begin fold")
        assert must_contain in record.message
        assert record.extra0 == 0
        assert record.extra1 == 1
        assert record.mutable == "a"

        user_extra["mutable"] = "a" * (i + 1)

    assert user_extra == {"extra0": 0, "extra1": 1, "mutable": "aaaa"}


def test_metrics(caplog):
    metrics = {
        "2022-01-08": {"mean.training": 83.5, "mean.future": 179.5, "perf.fit": 2019_05_11},
        "2022-01-09": {"mean": {"training": 107.5, "future": 203.5}},
    }
    expected_in_message = {
        "2022-01-08": "mean.training          83.5\nmean.future           179.5\nperf.fit         20190511.0",
        "2022-01-09": "mean.training    107.5\nmean.future      203.5",
    }
    assert len(metrics) == len(expected_in_message)

    for _ in log_split_progress(
        split("1d", available=("2022", "2022-01-10")),
        get_metrics=lambda key: metrics[key.date().isoformat()],
    ):
        pass

    print()
    for message in caplog.messages:
        print(message)

    for record in caplog.records:
        if not hasattr(record, "seconds"):
            continue

        key = pd.Timestamp(record.mid).date().isoformat()

        fold_metrics = metrics.pop(key)
        assert fold_metrics == record.metrics
        assert expected_in_message[key] in record.getMessage()
