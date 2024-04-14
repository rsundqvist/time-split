"""Plotting metrics per fold and data set.
==========================================

Using an unbounded timedelta-schedule, with custom bar labels.
"""

import pandas
from numpy.random import default_rng
from rics import configure_stuff
from time_split import plot, split

configure_stuff(datefmt="")

data = pandas.date_range("2022", "2022-2", freq="38min").to_series()
config = dict(schedule="7d", before="14d", after=1, available=data)

# %%
# Unbounded (timedelta-string or CRON) schedules require available data to materialize the schedule. When using the
# ``plot``-function, this data is also used to create bar labels unless they're explicitly given. We would like to
# plot metrics instead of just dataset sizes. Let's create some dummy metrics.

metrics = {}
random = default_rng(2019_05_11).random
for fold in split(**config):
    metrics[fold.mid.date()] = {
        "before": {"rmse": 2 * random(), "mae": random(), "r2": -random()},
        "after": {"rmse": 3 * random(), "mae": 1.5 * random()},
    }

# %%
# The `bar_labels`-arguments expects a list of tuples on the form ``[("left-label", "right-label")]``, plotting string
# tuples in the same order in which they were originally returned by the :func:`~.split`-method.

bar_labels = [
    (
        (
            f"Training metrics ({date}):\n"  # Header
            + pandas.Series(fold_metrics["before"]).to_string(float_format="%.2f")
        ),
        pandas.Series(fold_metrics["after"]).to_string(float_format="%.2f"),
    )
    for date, fold_metrics in metrics.items()
]

ax = plot(**config, bar_labels=bar_labels)

# %%
# Bar height is not based on `bar_labels`, so make sure to configure e.g. ``rcParams["figure.figsize"]`` beforehand when
# the `bar_labels` text is large. Alternatively, you may pass a pre-initialized :class:`matplotlib.axes.Axes`-instance
# using the `ax` keyword-argument.
