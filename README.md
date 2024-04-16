# Time Split  <!-- omit in toc -->
Time-based k-fold validation splits for heterogeneous data.

-----------------
[![PyPI - Version](https://img.shields.io/pypi/v/time-split.svg)](https://pypi.python.org/pypi/time-split)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/time-split.svg)](https://pypi.python.org/pypi/time-split)
[![Tests](https://github.com/rsundqvist/time-split/workflows/tests/badge.svg)](https://github.com/rsundqvist/time-split/actions?workflow=tests)
[![Codecov](https://codecov.io/gh/rsundqvist/time-split/branch/master/graph/badge.svg)](https://codecov.io/gh/rsundqvist/time-split)
[![Read the Docs](https://readthedocs.org/projects/time-split/badge/)](https://time-split.readthedocs.io/)
[![PyPI - License](https://img.shields.io/pypi/l/time-split.svg)](https://pypi.python.org/pypi/time-split)

<div align="center">
  <img alt="Plotted folds on a two-by-two grid." 
       title="Examples" height="300" width="1200" 
  src="https://raw.githubusercontent.com/rsundqvist/time-split/master/docs/2x2-examples.jpg"><br>
</div>

Folds plotted on a two-by-two grid. See the
[examples](https://time-split.readthedocs.io/en/stable/auto_examples/index.html) page for more.

## What is it?
A library for creating time-based cross-validation splits of _heterogeneous_ data, such as raw transaction data with 
strong non-stationary characteristics.

## Highlighted Features
- [Splitting schedules](https://time-split.readthedocs.io/en/stable/guide/schedules.html) based on a fixed interval, 
  a CRON-expression, or a pre-defined list.
- [Data selection](https://time-split.readthedocs.io/en/stable/guide/spans.html) based on a timedelta, or the splitting 
  schedule itself.
- Automatically extract and [normalize](https://time-split.readthedocs.io/en/stable/guide/flex.html) data limits for 
  supported data types.
- [Plotting function](https://time-split.readthedocs.io/en/stable/generated/time_split.html#time_split.plot) for
  visualization of folds. Display fold sizes (hour/row count), or 
  [use custom text](https://time-split.readthedocs.io/en/stable/auto_examples/plotting_with_metrics.html).
- [Integrations](https://time-split.readthedocs.io/en/stable/generated/time_split.integration.html) for popular 
  libraries such as `pandas`, `polars` and `scikit-learn`.

## Installation
The package is published through the [Python Package Index (PyPI)]. Source code
is available on GitHub: https://github.com/rsundqvist/time-split

```sh
pip install -U time-split
```

This is the preferred method to install ``time-split``, as it will always install the
most recent stable release.

If you don't have [pip] installed, this [Python installation guide] can guide
you through the process.

## License
[MIT](LICENSE.md)

## Documentation
Hosted on Read the Docs: https://time-split.readthedocs.io

## Contributing

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome. To get 
started, see the [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

[Python Package Index (PyPI)]: https://pypi.org/project/time-split
[pip]: https://pip.pypa.io
[Python installation guide]: http://docs.python-guide.org/en/stable/starting/installation/
