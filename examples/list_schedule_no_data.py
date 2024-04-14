"""List-schedule, without ``available`` data.
=============================================

Using an explicit schedule without data, showing number of hours in each partition.
"""

from rics import configure_stuff
from time_split import log_split_progress, plot, split

configure_stuff(datefmt="")

config = dict(
    schedule=["2022-01-03", "2022-01-07", "2022-01-10", "2022-01-14"],
    after=1,
)

plot(**config)
# %%
# Note that the last timestamp (**'2022-01-14'**) of the schedule was not included; this is because it was used as the
# end date (since ``after=1``) of the second-to-last timestamp (**'2022-01-10'**), which expands the Future data until
# the next scheduled time.

for fold in log_split_progress(split(**config), logger="my-logger"):
    print("Doing work..")
