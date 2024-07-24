# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Support for seconds in cron-like tasks

### Removed

- Human readable cron name due to incompatibility of [cron-descriptor](https://github.com/Salamek/cron-descriptor) and [croniter](https://github.com/kiorky/croniter) for seconds
- `cron-descriptor` from requirements

## [1.1.2]

### Fixed

- Fixes compatibility between django 3.2 and 4.2 for next planned execution in admin

## [1.1.1]

### Fixed

- Use custom css to fix external depenceny upload restriction

## [1.1.0]

### Added
- Support of periodic, cron-like tasks.

## [1.0.0] - 2023-05-05

### Added
- Initial setup.

[Unreleased]: https://github.com/anexia/django-future-tasks/compare/1.1.2...HEAD
[1.1.2]: https://github.com/anexia/django-future-tasks/releases/tag/1.1.2
[1.1.1]: https://github.com/anexia/django-future-tasks/releases/tag/1.1.1
[1.1.0]: https://github.com/anexia/django-future-tasks/releases/tag/1.1.0
[1.0.0]: https://github.com/anexia/django-future-tasks/releases/tag/1.0.0
