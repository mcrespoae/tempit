# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-13

### Added

- PEP 561 `py.typed` marker so the type hints are visible to static analysis and editors.
- `tempit.__version__` attribute, read from the installed package metadata.
- `make test-all` target and a test suite for the different multiprocessing start methods.
- CI matrix running the test suite on Python 3.11–3.14 across Linux, macOS and Windows, with code coverage reporting.
- Regression tests for recursion handling, exception safety, time formatting, concurrency timing and method detection.

### Changed

- Development tooling migrated from pip/Pipenv to [uv](https://docs.astral.sh/uv/) (Pipfile removed).
- Added Python 3.13 support and updated the GitHub Actions versions.
- README accuracy fixes (reproducible verbose example, concurrency wording, error propagation, feature list).

### Fixed

- Recursion state left on the call stack after an exception, which poisoned every subsequent call of the same decorated function.
- `time_wasted` not being reset between top-level calls, which made later measurements report bogus zero values.
- Thread-safety of recursion detection: per-thread state replaces the previously shared stack and accumulator, removing spurious "recursive function detected" warnings on concurrent calls.
- `format_time` no longer emits invalid values such as `60s` or `60m` when rounding to the next unit.
- Concurrent runs now report the real per-run execution times, so verbose statistics (`min`/`max`/`median`/`std dev`) are meaningful instead of a replicated average.
- Method detection no longer mistakes a same-named attribute on the first argument for a `self`/`cls` binding.

[Unreleased]: https://github.com/mcrespoae/tempit/compare/1.0.0...HEAD
[1.0.0]: https://github.com/mcrespoae/tempit/releases/tag/1.0.0
