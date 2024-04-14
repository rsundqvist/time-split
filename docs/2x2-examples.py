"""Grid for the README.md header."""

import matplotlib.pyplot as plt
import pandas as pd
from numpy.random import default_rng
from rics import configure_stuff
from time_split import plot, split

configure_stuff()

configs = [
    {
        "schedule": "0 0 * * THU",
        "after": "5d",
        "step": 2,
        "n_splits": 3,
        "available": pd.date_range("2022-01", "2022-03"),
        "bar_labels": "h",
        "show_removed": True,
    },
    {
        "schedule": "0 0 * * MON,FRI",
        "before": "all",
        "after": "3d",
        "available": pd.date_range("2022", "2022-1-21", freq="38min"),
        "bar_labels": False,
    },
    {
        "schedule": "0 0 * * MON,FRI",
        "before": 1,
        "after": 2,
        "available": (pd.date_range("2022", "2022-2", freq="15s")),
        "n_splits": 4,
        "show_removed": True,
    },
]

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(40, 10))

for ax, config in zip(axes.flat, configs):
    plot(ax=ax, **config)

# Add figure with dummy metrics.

data = pd.date_range("2022", "2022-2", freq="38min").to_series()
config = dict(schedule="7d", before="14d", after=1, available=data)

bar_labels = []
random = default_rng(2019_05_11).random
for fold in split(**config):
    before = (
        f"Training metrics ({fold.mid.date()}):\n"  # Header
        + pd.Series({"rmse": 2 * random(), "mae": random(), "r2": -random()}).to_string(float_format="%.2f")
    )
    after = pd.Series({"rmse": 3 * random(), "mae": 1.5 * random()}).to_string(float_format="%.2f")
    bar_labels.append((before, after))

plot(ax=axes.flatten()[-1], **config, bar_labels=bar_labels)

fig.savefig("2x2-examples.jpg")
