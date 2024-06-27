"""Filters: minimum ``before='all'`` size.
==========================================

Arbitrary filters can be applied for all applications using the :attr:`time_split.settings.misc.filter` option. Must be
a predicate ``(start, mid, end) -> bool``. Consider using :func:`functools.cache` if your predicate is expensive.
"""

from rics import configure_stuff
from time_split import log_split_progress, plot, settings, split

configure_stuff(datefmt="")

data = ("2022-02", "2022-03")
config = dict(schedule="7d", before="all", after="5d", available=data)

plot(**config, bar_labels="days")

for fold in log_split_progress(split(**config), logger="my-logger"):
    print("Doing work..")

# %%
# By setting :attr:`settings.misc.filter <time_split.settings.misc.filter>`, arbitrary conditions may be
# forced on the generated folds.


def at_least_10_days(start, mid, end):
    return (mid - start).days >= 10


# %%
# Enforcing 10 days of training data.


settings.misc.filter = at_least_10_days
plot(**config, bar_labels="days", show_removed=True)

for fold in log_split_progress(split(**config), logger="my-logger"):
    print("Doing work..")

# %%
# The configuration in :mod:`time_split.settings` are global, so changes made will remain in effect for all
# callers until the original value is reset.
settings.misc.filter = None
