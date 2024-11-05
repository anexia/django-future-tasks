import os
import signal
import time
from datetime import timedelta
from timeit import default_timer

import time_machine
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from django_future_tasks.models import FutureTask
from tests.core import settings
from tests.testapp.mixins import ProcessTasksCommandMixin


class WaitForTaskStatusTimeout(Exception):
    pass


def _wait_for_task_status(task, status, tick_seconds=0.1, timeout_seconds=3):
    start_time = default_timer()
    while task.status != status:
        if default_timer() - start_time >= timeout_seconds:
            raise WaitForTaskStatusTimeout(
                f"Timeout while waiting for task status. Actual: '{task.status}' Expected: '{status}'",
            )
        task.refresh_from_db()
        time.sleep(tick_seconds)


class TestProcessFutureTasks(ProcessTasksCommandMixin, TransactionTestCase):
    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_process_future_tasks_eta_now(self):
        start_time = default_timer()
        task = FutureTask.objects.create(
            task_id="task",
            eta=timezone.now(),
            type=settings.FUTURE_TASK_TYPE_ONE,
        )
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        _wait_for_task_status(task, FutureTask.FUTURE_TASK_STATUS_DONE)
        end_time = default_timer()
        self.assertIsNotNone(task.execution_time)
        self.assertGreater(task.execution_time, 0.0)
        self.assertLess(task.execution_time, end_time - start_time)

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_process_future_tasks_eta_future(self):
        task = FutureTask.objects.create(
            task_id="task",
            eta=timezone.now() + timedelta(microseconds=1),
            type=settings.FUTURE_TASK_TYPE_TWO,
        )
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        try:
            _wait_for_task_status(task, FutureTask.FUTURE_TASK_STATUS_DONE)
        except WaitForTaskStatusTimeout:
            pass
        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_process_future_tasks_error(self):
        task = FutureTask.objects.create(
            task_id="task",
            eta=timezone.now(),
            type=settings.FUTURE_TASK_TYPE_ERROR,
        )
        print(FutureTask.objects.all())
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        _wait_for_task_status(task, FutureTask.FUTURE_TASK_STATUS_ERROR)
        self.assertEqual(task.result["args"], ["task error"])

    @time_machine.travel("2024-01-01 00:00 +0000", tick=True)
    def test_process_future_tasks_eta_ordering(self):
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
        self.assertEqual(task_late.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        self.assertEqual(task_early.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        _wait_for_task_status(task_late, FutureTask.FUTURE_TASK_STATUS_DONE)
        _wait_for_task_status(task_early, FutureTask.FUTURE_TASK_STATUS_DONE)
        self.assertGreater(task_late.result, task_early.result)


class TestProcessFutureTasksInterruption(ProcessTasksCommandMixin, TransactionTestCase):
    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_future_task_process_interruption(self):
        task = FutureTask.objects.create(
            task_id="task",
            eta=timezone.now(),
            type=settings.FUTURE_TASK_TYPE_INTERRUPTION,
        )
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        _wait_for_task_status(task, FutureTask.FUTURE_TASK_STATUS_IN_PROGRESS)
        pid = os.getpid()
        os.kill(pid, signal.SIGINT)
        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_INTERRUPTED)


class TestFutureTasksOnetimeRun(TestCase):
    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_process_future_tasks_onetimerun_no_task(self):
        call_command("process_future_tasks", onetimerun=True)

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_process_future_tasks_onetimerun_eta_now(self):
        start_time = default_timer()
        task = FutureTask.objects.create(
            task_id="task",
            eta=timezone.now(),
            type=settings.FUTURE_TASK_TYPE_ONE,
        )
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        call_command("process_future_tasks", onetimerun=True)
        end_time = default_timer()
        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_DONE)
        self.assertIsNotNone(task.execution_time)
        self.assertGreater(task.execution_time, 0.0)
        self.assertLess(task.execution_time, end_time - start_time)

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_process_future_tasks_onetimerun_eta_future(self):
        _now = timezone.now()
        task = FutureTask.objects.create(
            task_id="task",
            eta=_now + timedelta(microseconds=1),
            type=settings.FUTURE_TASK_TYPE_TWO,
        )
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        call_command("process_future_tasks", onetimerun=True)
        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

    @time_machine.travel("2024-01-01 00:00 +0000", tick=False)
    def test_process_future_tasks_onetimerun_error(self):
        _now = timezone.now()
        task = FutureTask.objects.create(
            task_id="task",
            eta=_now,
            type=settings.FUTURE_TASK_TYPE_ERROR,
        )
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        call_command("process_future_tasks", onetimerun=True)
        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_ERROR)
        self.assertEqual(task.result["args"], ["task error"])

    @time_machine.travel("2024-01-01 00:00 +0000", tick=True)
    def test_process_future_tasks_onetimerun_eta_ordering(self):
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
        self.assertEqual(task_late.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        self.assertEqual(task_early.status, FutureTask.FUTURE_TASK_STATUS_OPEN)
        call_command("process_future_tasks", onetimerun=True)
        task_late.refresh_from_db()
        task_early.refresh_from_db()
        self.assertGreater(task_late.result, task_early.result)
