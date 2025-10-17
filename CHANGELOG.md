# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Use `timezone.now()` instead of `datetime.now()` in `PeriodicFutureTask.save()`.
- Use `condition` instead of `check` attribute in `CheckConstraint` with `django>=5.1`.

### Changed

- Improve `process_future_tasks` command.
  - Terminate after processing the current task instead of the current task batch if SIGINT/SIGTERM is received.
  - Remove unnecessary waiting for new tasks when there are already tasks that can be processed.
  - Configurable waiting duration for new tasks.

### Added

- Support for Python 3.14.
- Support for Django 5.2.

### Removed

- Support for Python 3.9.
- Support for Django 5.0.

## [1.3.2]

### Changed

- Migrate to `pytest`.
- Migrate to `pyproject.toml`.

## [1.3.1]

### Fixed

- Fix infinite loop in populate_periodic_future_tasks on IntegrityError

## [1.3.0]

### Added

- Support for Django 5.0 and 5.1.
- Support for Python 3.12 and 3.13.

### Changed

- pre-commit configuration

### Removed

- Support for Django 3.2 and 4.1.
- Support for Python 3.8.

## [1.2.1]

### Added

- Log exceptions in handle_tick in process_future_tasks

## [1.2.0]

### Added

- Allow seconds in cron string settings

## [1.1.2]

### Fixed

- Fixes compatibility between Django 3.2 and 4.2 for next planned execution in admin

## [1.1.1]

### Fixed

- Use custom css to fix external depenceny upload restriction

## [1.1.0]

### Added

- Support of periodic, cron-like tasks.

## [1.0.0] - 2023-05-05

### Added

- Initial setup.

[Unreleased]: https://github.com/anexia/django-future-tasks/compare/1.3.2...HEAD
[1.3.2]: https://github.com/anexia/django-future-tasks/releases/tag/1.3.2
[1.3.1]: https://github.com/anexia/django-future-tasks/releases/tag/1.3.1
[1.3.0]: https://github.com/anexia/django-future-tasks/releases/tag/1.3.0
[1.2.1]: https://github.com/anexia/django-future-tasks/releases/tag/1.2.1
[1.2.0]: https://github.com/anexia/django-future-tasks/releases/tag/1.2.0
[1.1.2]: https://github.com/anexia/django-future-tasks/releases/tag/1.1.2
[1.1.1]: https://github.com/anexia/django-future-tasks/releases/tag/1.1.1
[1.1.0]: https://github.com/anexia/django-future-tasks/releases/tag/1.1.0
[1.0.0]: https://github.com/anexia/django-future-tasks/releases/tag/1.0.0
