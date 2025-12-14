"""No future data
=======================================================

Setting ``after="empty"`` may be used to create folds without regard for a `Future data` dataset.
"""

import pandas
from rics import configure_stuff
from time_split import log_split_progress, plot, split

configure_stuff(datefmt="")

data = pandas.date_range("2022", "2022-1-21", freq="38min")
config = dict(
    schedule="0 0 * * MON,FRI",
    before="3d",
    after="empty",
    available=data,
)

plot(**config, show_removed=True)
# %%
# The vertical, dashed lines shown denote the outer bounds of the data, beyond which the schedule may not extend.

for fold in log_split_progress(split(**config), logger="my-logger"):
    print("Doing work..")
