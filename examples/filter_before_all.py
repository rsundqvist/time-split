"""Filters: minimum ``before='all'`` size.
==========================================

Remove bad folds by using the `filter` parameter. Must be a predicate ``(start, mid, end) -> bool``.
"""

from rics import configure_stuff
from time_split import log_split_progress, plot, split

configure_stuff(datefmt="")

data = ("2022-02", "2022-03")
config = dict(schedule="7d", before="all", after="5d", available=data)

plot(**config, bar_labels="days")

for fold in log_split_progress(split(**config), logger="my-logger"):
    print("Doing work..")

# %%
# By using a :attr:`~time_split.types.Filter`, arbitrary conditions may be forced on the generated folds.


def at_least_10_days(start, mid, end):
    # end: fixed distance from `mid` since after="5d"
    return (mid - start).days >= 10


# %%
# Enforcing 10 days of training data.

plot(**config, filter=at_least_10_days, bar_labels="days", show_removed=True)

for fold in log_split_progress(
    split(**config, filter=at_least_10_days),
    logger="my-logger",
):
    print("Doing work..")
