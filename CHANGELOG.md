# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Make `types.SplitProgressExtras` generic on `MetricsType`.

## [0.6.0] - 2024-08-31

### Changed
- Move the [Streamlit application](https://time-split.streamlit.app/) into a 
  separate repo: https://github.com/rsundqvist/time-fold-explorer/.

### Removed
- The `time_split.streamlit` submodule.

## [0.5.0] - 2024-07-06

### Added
- Add `settings.misc.filter` and `ignore_filters` argument.
- A new Streamlit application (see `time_split.streamlit`): https://hub.docker.com/r/rsundqvist/time-split/.

### Changed
- The `plot()`-function now treats data of length two as a limits-tuple for display purposes.
- Reduce the number of the INFO-level limits expansion messages emitted.

## [0.4.0] - 2024-06-17

### Deprecated
- The `flex` argument is now called `expand_limits` in all user-facing functions. The support function with the same 
  name now uses `spec` for the equivalent argument.

### Fixed
- Remove uses of deprecated functions.

## [0.3.0] - 2024-05-18

### Added
- The `log_split_progress()`-function now accepts an optional _get_metrics()_ callback method. Metrics returned are 
  formatted based on type (if using the new `default_metrics_formatter()`), then added to the fold-end log message.
- New property `settings.log_split_progress.FORMAT_METRICS`; formats _get_metrics()_ output.
- Added several new `time_split.types` members, all related to `log_split_progress()`.

### Changed
- Module `integration.split_data` is now `integration.base` to better reflect intent. Member names are unchanged.

### Removed
- The `settings.log_split_progress.SECONDS_FORMATTER` setting no longer accepts `str` arguments.
- The `log_split_progress(extra)`-argument is no longer mutable.

## [0.2.1] - 2024-04-20

### Fixed
- Various documentation issues; broken links, naming/formatting conformity.

## [0.2.0] - 2024-04-20

### Added
* [Parameter overview](https://time-split.readthedocs.io/en/latest/guide/parameters.html) table to docs.

### Changed
* Link to relevant examples on the
  [Before and after arguments](https://time-split.readthedocs.io/en/latest/guide/spans.html)-page.
* Expose more internals in the `time_split.support` module (unstable API).
* Rename parts of the internal (unstable) API.

### Fixed
* Fix project description.
* Various other documentation issues.

## [0.1.0] - 2024-04-14

* Branch from [rics@v4.0.1](https://github.com/rsundqvist/rics/blob/v4.0.1/CHANGELOG.md).

### Changed
* Move out of `rics` namespace.

### Fixed
* Fixed a few documentation and examples issues.

[Unreleased]: https://github.com/rsundqvist/time-split/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/rsundqvist/time-split/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/rsundqvist/time-split/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/rsundqvist/time-split/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/rsundqvist/time-split/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/rsundqvist/time-split/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/rsundqvist/time-split/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/rsundqvist/time-split/compare/v0.0.0...v0.1.0
