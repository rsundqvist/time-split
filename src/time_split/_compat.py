from pandas import Timedelta

from time_split.types import TimedeltaTypes


def fix_pandas4_warning(arg: str) -> str:
    return arg[:-1] + "D" if arg.endswith("d") else arg


def make_timedelta(arg: TimedeltaTypes) -> Timedelta:
    if isinstance(arg, str):
        arg = fix_pandas4_warning(arg)

    return Timedelta(arg)
