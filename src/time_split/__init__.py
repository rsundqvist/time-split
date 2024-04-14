"""Create temporal k-folds for cross-validation with heterogeneous data."""

import logging as _logging

from ._frontend import log_split_progress, plot, split

__all__ = [
    "log_split_progress",
    "plot",
    "split",
    "__version__",  # Make MyPy happy
]

__version__ = "0.0.0.dev1"

_logging.getLogger(__name__).addHandler(_logging.NullHandler())
