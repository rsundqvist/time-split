"""Create temporal k-folds for cross-validation with heterogeneous data."""

import logging as _logging

from ._frontend import log_split_progress, plot, split

__all__ = [
    "log_split_progress",
    "plot",
    "split",
    "__version__",  # Make MyPy happy
]

__version__ = "0.1.0"

_logging.getLogger(__name__).addHandler(_logging.NullHandler())
