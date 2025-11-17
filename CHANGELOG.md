# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed
- No longer adds a `NullHandler` to package root logger on import.

## [1.0.3] - 2025-11-16

### Added
- Python `3.14` is now fully tested and supported in CI/CD.

## [1.0.2] - 2025-10-25

### Fixed
- Fix crashes when using `python -OO` and some other docs issues.

## [1.0.1] - 2025-08-22

### Changed
- Bump app version.

## [1.0.0] - 2025-08-21

### Added
- New sequence-like type `LogSplitProgress`; returned by `log_split_progress` instead of generic iterable.

### Changed
- Convert `settings.filter` to a keyword argument.

## [0.7.1] - 2025-07-17

### Added
- app: Add `time_split.app.reexport`.

## [0.7.0] - 2025-07-16

### Added
- The `time-split[app]` extra; adds `time_split_app` namespace.
  * New `time-split` cli; `python -m time_split`.
- The `create_explorer_link()` function will now hex-encode `bytes` data.
- Add `settings.misc.round_limits=False`. Enable to allow inward rounding of limits.

### Changed
- Make `types.SplitProgressExtras` generic on `MetricsType`.
- Allow passing `Series/DataFrame` as `plot(available=...)`.
- The `to_string()` function now supports using _.delta_ and _.iso_ (like _.auto_) in the format.

## [0.6.0] - 2024-08-31

### Changed
- Move the [Streamlit application](https://time-split.streamlit.app/) into a 
  separate repo: https://github.com/rsundqvist/time-fold-explorer/.

### Removed
- The `time_split.streamlit` submodule.
- Deprecated alias `flex`; use `expand_limits` instead.

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

[Unreleased]: https://github.com/rsundqvist/time-split/compare/v1.0.3...HEAD
[1.0.3]: https://github.com/rsundqvist/time-split/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/rsundqvist/time-split/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/rsundqvist/time-split/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/rsundqvist/time-split/compare/v0.7.1...v1.0.0
[0.7.1]: https://github.com/rsundqvist/time-split/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/rsundqvist/time-split/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/rsundqvist/time-split/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/rsundqvist/time-split/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/rsundqvist/time-split/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/rsundqvist/time-split/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/rsundqvist/time-split/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/rsundqvist/time-split/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/rsundqvist/time-split/compare/v0.0.0...v0.1.0
