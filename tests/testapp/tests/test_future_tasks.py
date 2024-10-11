import os
import signal
import time
from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from django_future_tasks.models import FutureTask
from tests.core import settings
from tests.testapp.mixins import ProcessTasksCommandMixin

SLEEP_TIME = 2.2


class TestFutureTasks(ProcessTasksCommandMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()

        today = timezone.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        self.task1 = FutureTask.objects.create(
            task_id="task1",
            eta=yesterday,
            type=settings.FUTURE_TASK_TYPE_ONE,
        )

        self.task2 = FutureTask.objects.create(
            task_id="task2",
            eta=tomorrow,
            type=settings.FUTURE_TASK_TYPE_TWO,
        )

        self.task_error = FutureTask.objects.create(
            task_id="task_error",
            eta=yesterday,
            type=settings.FUTURE_TASK_TYPE_ERROR,
        )

    def test_future_task_process_task(self):
        task = FutureTask.objects.get(pk=self.task1.pk)
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

        # Make sure that task has been processed.
        time.sleep(SLEEP_TIME)

        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_DONE)
        self.assertIsNotNone(task.execution_time)
        self.assertGreater(task.execution_time, 0.5)
        self.assertLess(task.execution_time, 1)

    def test_future_task_no_task_to_process(self):
        task = FutureTask.objects.get(pk=self.task2.pk)
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

        # Make sure that task has been processed.
        time.sleep(SLEEP_TIME)

        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

    def test_future_task_process_error(self):
        task = FutureTask.objects.get(pk=self.task_error.pk)
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

        # Make sure that task has been processed.
        time.sleep(SLEEP_TIME)

        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_ERROR)
        self.assertEqual(task.result["args"], ["task error"])


class TestFutureTaskInterruption(ProcessTasksCommandMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()

        yesterday = timezone.now() - timedelta(days=1)

        self.task1 = FutureTask.objects.create(
            task_id="task",
            eta=yesterday,
            type=settings.FUTURE_TASK_TYPE_INTERRUPTION,
        )

    def test_future_task_process_task(self):
        task = FutureTask.objects.get(pk=self.task1.pk)
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

        # Make sure that task is in progression.
        time.sleep(SLEEP_TIME)

        pid = os.getpid()
        os.kill(pid, signal.SIGINT)

        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_INTERRUPTED)


class TestFutureTasksOnetimeRun(TestCase):
    def setUp(self):
        super().setUp()

        today = timezone.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        self.task1 = FutureTask.objects.create(
            task_id="onetimerun_task1",
            eta=yesterday,
            type=settings.FUTURE_TASK_TYPE_ONE,
        )

        self.task2 = FutureTask.objects.create(
            task_id="onetimerun_task2",
            eta=tomorrow,
            type=settings.FUTURE_TASK_TYPE_TWO,
        )

        self.task_error = FutureTask.objects.create(
            task_id="onetimerun_task_error",
            eta=yesterday,
            type=settings.FUTURE_TASK_TYPE_ERROR,
        )

    def test_future_task_process_task_onetimerun(self):
        task = FutureTask.objects.get(pk=self.task1.pk)
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

        call_command("process_future_tasks", onetimerun=True)

        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_DONE)
        self.assertGreater(task.execution_time, 0.5)
        self.assertLess(task.execution_time, 1)

    def test_future_task_no_task_to_process_onetimerun(self):
        task = FutureTask.objects.get(pk=self.task2.pk)
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

        call_command("process_future_tasks", onetimerun=True)

        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

    def test_future_task_process_error_onetimerun(self):
        task = FutureTask.objects.get(pk=self.task_error.pk)
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

        call_command("process_future_tasks", onetimerun=True)

        task.refresh_from_db()
        self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_ERROR)
        self.assertEqual(task.result["args"], ["task error"])
