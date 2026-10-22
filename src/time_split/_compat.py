import re

from pandas import Timedelta

from time_split.types import TimedeltaTypes

# TODO(pandas>=4): Remove this module.


def fix_pandas4_warning(arg: str) -> str:
    # Uppercase a "d" unit that starts the string or follows a number or space ("d", "1d", "7 d", "1d2h"), not "days".
    return re.sub(r"(?<![^\d\s])d(?![a-z])", "D", arg)


def make_timedelta(arg: TimedeltaTypes) -> Timedelta:
    if isinstance(arg, str):
        arg = fix_pandas4_warning(arg)

    return Timedelta(arg)
