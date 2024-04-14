def _patch_dask_timeseries():
    import functools

    import dask.datasets
    import pytest

    original = dask.datasets.timeseries

    @functools.wraps(original)
    def wrapped(*args, **kwargs):
        with pytest.warns(UserWarning, match="dask_expr does not support the DataFrameIOFunction protocol"):
            return original(*args, **kwargs)

    dask.datasets.timeseries = wrapped


_patch_dask_timeseries()
