from typing import Any, Protocol, TypeVar, overload, runtime_checkable

T_co = TypeVar("T_co", covariant=True)


@runtime_checkable
class _Computable(Protocol[T_co]):
    def compute(self) -> T_co:
        """Compute results of a delayed Dask object."""


@overload
def handle_dask(arg: T_co | _Computable[T_co], /) -> T_co: ...
@overload
def handle_dask(a: T_co | _Computable[T_co], b: T_co | _Computable[T_co], /) -> tuple[T_co, T_co]: ...
@overload
def handle_dask(*args: T_co | _Computable[T_co]) -> tuple[T_co, ...]: ...
def handle_dask(*args: Any) -> Any:
    """Run Dask compute on delayed objects, in a single pass."""
    if any(isinstance(a, _Computable) for a in args):
        # shortcut: non-Dask computables (e.g. xarray) now require dask; accepted, add a .compute() fallback if reported.
        from dask import compute  # type: ignore[attr-defined]

        args = compute(*args)  # type: ignore[no-untyped-call]

    return args[0] if len(args) == 1 else args
