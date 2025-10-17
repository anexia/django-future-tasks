import logging
import os
import signal
import time
from datetime import timedelta
from timeit import default_timer

import pytest
import time_machine
from django.core.management import call_command
from django.utils import timezone

from core import settings
from django_future_tasks.models import FutureTask
from testapp.tests.utils import ProcessFutureTasksWorker

logger = logging.getLogger(__name__)


class WaitForTaskStatusTimeout(Exception):
    pass


def _wait_for_task_status(task, status, tick_seconds: float = 0.15, timeout_seconds: float = 3.0):
    start_time = default_timer()
    while task.status != status:
        if default_timer() - start_time >= timeout_seconds:
            raise WaitForTaskStatusTimeout(
                f"Timeout while waiting for task status. Actual: '{task.status}' Expected: '{status}'",
            )
        task.refresh_from_db()
        time.sleep(tick_seconds)


@pytest.mark.django_db(transaction=True)
class TestWorker:
    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_eta_now(self):
        with ProcessFutureTasksWorker():
            start_time = default_timer()
            task = FutureTask.objects.create(
                task_id="task",
                eta=timezone.now(),
                type=settings.FUTURE_TASK_TYPE_ONE,
            )
            assert task.status == FutureTask.FUTURE_TASK_STATUS_OPEN
            _wait_for_task_status(task, FutureTask.FUTURE_TASK_STATUS_DONE)
            end_time = default_timer()
            assert task.execution_time is not None
            assert task.execution_time > 0.0
            assert task.execution_time < end_time - start_time

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_eta_future(self):
        with ProcessFutureTasksWorker():
            task = FutureTask.objects.create(
                task_id="task",
                eta=timezone.now() + timedelta(microseconds=1),
                type=settings.FUTURE_TASK_TYPE_TWO,
            )
            assert task.status == FutureTask.FUTURE_TASK_STATUS_OPEN
            try:
                _wait_for_task_status(task, FutureTask.FUTURE_TASK_STATUS_DONE)
            except WaitForTaskStatusTimeout:
                pass
            task.refresh_from_db()
            assert task.status == FutureTask.FUTURE_TASK_STATUS_OPEN

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_error(self):
        with ProcessFutureTasksWorker():
            task = FutureTask.objects.create(
                task_id="task",
                eta=timezone.now(),
                type=settings.FUTURE_TASK_TYPE_ERROR,
            )
            logger.info(FutureTask.objects.all())
            assert task.status == FutureTask.FUTURE_TASK_STATUS_OPEN
            _wait_for_task_status(task, FutureTask.FUTURE_TASK_STATUS_ERROR)
            assert task.result["args"] == ["task error"]

    @time_machine.travel("2024-01-01 00:00 +0000", tick=True)
    def test_eta_ordering(self):
        with ProcessFutureTasksWorker():
            _now = timezone.now()
            task_late = FutureTask.objects.create(
                task_id="task_late",
                eta=_now,
                type=settings.FUTURE_TASK_TYPE_ETA_ORDERING,
            )
            task_early = FutureTask.objects.create(
                task_id="task_early",
                eta=_now - timedelta(microseconds=1),
                type=settings.FUTURE_TASK_TYPE_ETA_ORDERING,
            )
            assert task_late.status == FutureTask.FUTURE_TASK_STATUS_OPEN
            assert task_early.status == FutureTask.FUTURE_TASK_STATUS_OPEN
            _wait_for_task_status(task_late, FutureTask.FUTURE_TASK_STATUS_DONE)
            _wait_for_task_status(task_early, FutureTask.FUTURE_TASK_STATUS_DONE)
            assert task_late.result > task_early.result

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_interruption(self):
        with ProcessFutureTasksWorker():
            task_1 = FutureTask.objects.create(
                task_id="task-1",
                eta=timezone.now() - timedelta(microseconds=1),
                type=settings.FUTURE_TASK_TYPE_INTERRUPTION,
            )
            task_2 = FutureTask.objects.create(
                task_id="task-2",
                eta=timezone.now(),
                type=settings.FUTURE_TASK_TYPE_ONE,
            )
            assert task_1.status == FutureTask.FUTURE_TASK_STATUS_OPEN
            _wait_for_task_status(task_1, FutureTask.FUTURE_TASK_STATUS_IN_PROGRESS)
            pid = os.getpid()
            os.kill(pid, signal.SIGINT)
            # The command prepares for a potential SIGKILL and sets the status to interrupted.
            _wait_for_task_status(task_1, FutureTask.FUTURE_TASK_STATUS_INTERRUPTED)
            # The command finishes graciously and therefore also the task finishes graciously.
            _wait_for_task_status(task_1, FutureTask.FUTURE_TASK_STATUS_DONE)
            # The command does not start any tasks after finishing the current task.
            with pytest.raises(WaitForTaskStatusTimeout):
                _wait_for_task_status(task_2, FutureTask.FUTURE_TASK_STATUS_DONE, timeout_seconds=1.0)
            task_2.refresh_from_db()
            assert task_2.status == FutureTask.FUTURE_TASK_STATUS_OPEN

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_short_wait_for_tasks_duration(self):
        with ProcessFutureTasksWorker("--wait-for-tasks-duration=0.5"):
            # Small delay to let the command run into the waiting mechanism.
            time.sleep(0.1)
            task = FutureTask.objects.create(
                task_id="task",
                eta=timezone.now(),
                type=settings.FUTURE_TASK_TYPE_ONE,
            )
            # Wait for the task to process.
            time.sleep(0.6)
        task.refresh_from_db()
        assert task.status == FutureTask.FUTURE_TASK_STATUS_DONE

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_long_wait_for_tasks_duration(self):
        with ProcessFutureTasksWorker("--wait-for-tasks-duration=3.0"):
            # Small delay to let the command run into the waiting mechanism.
            time.sleep(0.1)
            task = FutureTask.objects.create(
                task_id="task",
                eta=timezone.now(),
                type=settings.FUTURE_TASK_TYPE_ONE,
            )
            time.sleep(0.2)
        # Worker has been terminated while waiting for tasks. The task is still open.
        task.refresh_from_db()
        assert task.status == FutureTask.FUTURE_TASK_STATUS_OPEN


@pytest.mark.django_db(transaction=True)
class TestOnetimeRun:
    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_no_task(self):
        call_command("process_future_tasks", one_time_run=True)

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_eta_now(self):
        start_time = default_timer()
        task = FutureTask.objects.create(
            task_id="task",
            eta=timezone.now(),
            type=settings.FUTURE_TASK_TYPE_ONE,
        )
        assert task.status == FutureTask.FUTURE_TASK_STATUS_OPEN
        call_command("process_future_tasks", one_time_run=True)
        end_time = default_timer()
        task.refresh_from_db()
        assert task.status == FutureTask.FUTURE_TASK_STATUS_DONE
        assert task.execution_time is not None
        assert task.execution_time > 0.0
        assert task.execution_time < end_time - start_time

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_eta_future(self):
        _now = timezone.now()
        task = FutureTask.objects.create(
            task_id="task",
            eta=_now + timedelta(microseconds=1),
            type=settings.FUTURE_TASK_TYPE_TWO,
        )
        assert task.status == FutureTask.FUTURE_TASK_STATUS_OPEN
        call_command("process_future_tasks", one_time_run=True)
        task.refresh_from_db()
        assert task.status == FutureTask.FUTURE_TASK_STATUS_OPEN

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_error(self):
        _now = timezone.now()
        task = FutureTask.objects.create(
            task_id="task",
            eta=_now,
            type=settings.FUTURE_TASK_TYPE_ERROR,
        )
        assert task.status == FutureTask.FUTURE_TASK_STATUS_OPEN
        call_command("process_future_tasks", one_time_run=True)
        task.refresh_from_db()
        assert task.status == FutureTask.FUTURE_TASK_STATUS_ERROR
        assert task.result["args"] == ["task error"]

    @time_machine.travel("2024-01-01 00:00 +0000", tick=True)
    def test_eta_ordering(self):
        _now = timezone.now()
        task_late = FutureTask.objects.create(
            task_id="task_late",
            eta=_now,
            type=settings.FUTURE_TASK_TYPE_ETA_ORDERING,
        )
        task_early = FutureTask.objects.create(
            task_id="task_early",
            eta=_now - timedelta(microseconds=1),
            type=settings.FUTURE_TASK_TYPE_ETA_ORDERING,
        )
        assert task_late.status == FutureTask.FUTURE_TASK_STATUS_OPEN
        assert task_early.status == FutureTask.FUTURE_TASK_STATUS_OPEN
        call_command("process_future_tasks", one_time_run=True)
        task_late.refresh_from_db()
        task_early.refresh_from_db()
        assert task_late.result > task_early.result
