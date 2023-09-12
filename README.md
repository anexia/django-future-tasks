# Django Future Tasks

[![PyPI version](https://img.shields.io/pypi/v/django-future-tasks.svg)](https://pypi.org/project/django-future-tasks/)
[![Run linter and tests](https://github.com/anexia/django-future-tasks/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/anexia/django-future-tasks/actions/workflows/test.yml)
[![Codecov](https://img.shields.io/codecov/c/gh/anexia/django-future-tasks)](https://codecov.io/gh/anexia/django-future-tasks)

A library to create periodic, cron-like tasks or single tasks with a specified execution/start time and schedule it to run in the future.

## Installation

1. Install using pip:

```sh
pip install django-future-tasks
```

2. Add the library to your INSTALLED_APPS list.

```python
INSTALLED_APPS = [
    ...
    'django_future_tasks',
    ...
]
```

4. Configure the task types in your `settings.py` according to your needs:

```python
# within settings.py

FUTURE_TASK_TYPE_ONE = "task_one"
FUTURE_TASK_TYPE_TWO = "task_two"

FUTURE_TASK_TYPES = (
    (FUTURE_TASK_TYPE_ONE, _("Task 1")),
    (FUTURE_TASK_TYPE_TWO, _("Task 2")),
)
```

## Usage

To receive a signal, register a receiver function using the signal `future_task_signal` and the task type as sender.
The `instance` is the FutureTask object.

```python
@receiver(future_task_signal, sender=intern(settings.FUTURE_TASK_TYPE_ONE))
def my_function(sender, instance, **kwargs):
    # do something
```

**Command for starting the future task processing**
```bash
python manage.py process_future_tasks
```

**Command for starting the periodic future task processing**
```bash
python manage.py populate_periodic_future_tasks
```

## Django Compatibility Matrix

If your project uses an older verison of Django or Django Rest Framework, you can choose an older version of this project.

| This Project | Python Version       | Django Version |
|--------------|----------------------|----------------|
| 1.1.*        | 3.8, 3.9, 3.10, 3.11 | 3.2, 4.1, 4.2  |
| 1.0.*        | 3.8, 3.9, 3.10, 3.11 | 3.2, 4.0, 4.1  |
