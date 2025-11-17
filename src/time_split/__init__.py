"""Time-based k-fold validation splits for heterogeneous data."""

from ._frontend import log_split_progress, plot, split

__all__ = [
    "__version__",  # Make MyPy happy
    "log_split_progress",
    "plot",
    "split",
]

__version__ = "1.0.4.dev1"
