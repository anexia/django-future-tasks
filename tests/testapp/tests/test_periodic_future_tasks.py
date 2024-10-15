import time
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TransactionTestCase
from django.utils import timezone

from django_future_tasks.models import FutureTask, PeriodicFutureTask
from tests.core import settings
from tests.testapp.mixins import PopulatePeriodicTaskCommandMixin

SLEEP_TIME = 1.8


class TestPeriodicFutureTasks(PopulatePeriodicTaskCommandMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()

        now = timezone.now()
        self.original_last_task_creation = now - timedelta(hours=2)

        self.task_active = PeriodicFutureTask.objects.create(
            periodic_task_id="periodic task",
            type=settings.FUTURE_TASK_TYPE_ONE,
            cron_string="42 * * * *",
        )

        p_task = PeriodicFutureTask.objects.get(pk=self.task_active.pk)
        p_task.last_task_creation = self.original_last_task_creation
        p_task.save()

        self.task_not_active = PeriodicFutureTask.objects.create(
            periodic_task_id="periodic inactive task",
            type=settings.FUTURE_TASK_TYPE_ONE,
            cron_string="42 * * * *",
            is_active=False,
        )

        self.task_max_one_execution = PeriodicFutureTask.objects.create(
            periodic_task_id="periodic task with maximal one execution",
            type=settings.FUTURE_TASK_TYPE_ONE,
            cron_string="42 * * * *",
            max_number_of_executions=1,
        )

        p_task = PeriodicFutureTask.objects.get(pk=self.task_max_one_execution.pk)
        p_task.last_task_creation = self.original_last_task_creation
        p_task.save()

        end_time = now - timedelta(hours=1)
        self.task_with_end_time = PeriodicFutureTask.objects.create(
            periodic_task_id="periodic task with end time",
            type=settings.FUTURE_TASK_TYPE_ONE,
            cron_string="42 * * * *",
            end_time=end_time,
        )

        p_task = PeriodicFutureTask.objects.get(pk=self.task_with_end_time.pk)
        p_task.last_task_creation = self.original_last_task_creation
        p_task.save()

        self.task_for_validation_test = PeriodicFutureTask.objects.create(
            periodic_task_id="periodic task for validation test",
            type=settings.FUTURE_TASK_TYPE_ONE,
            cron_string="42 * * * *",
        )

    def test_periodic_future_task_populate_active_task(self):
        p_task = PeriodicFutureTask.objects.get(pk=self.task_active.pk)

        # Make sure that task population has been processed.
        time.sleep(SLEEP_TIME)

        p_task.refresh_from_db()
        self.assertTrue(p_task.last_task_creation > self.original_last_task_creation)
        self.assertEqual(
            FutureTask.objects.filter(periodic_parent_task_id=p_task.pk).count(),
            2,
        )

        for task in FutureTask.objects.filter(periodic_parent_task_id=p_task.pk):
            self.assertEqual(task.type, p_task.type)
            self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

    def test_periodic_future_task_populate_inactive_task(self):
        p_task = PeriodicFutureTask.objects.get(pk=self.task_not_active.pk)

        # Make sure that task population has been processed.
        time.sleep(SLEEP_TIME)

        p_task.refresh_from_db()
        self.assertFalse(
            FutureTask.objects.filter(periodic_parent_task_id=p_task.pk).exists(),
        )

    def test_periodic_future_task_deactivation_and_activation(self):
        p_task = PeriodicFutureTask.objects.get(pk=self.task_active.pk)

        p_task.is_active = False
        p_task.save()
        p_task.refresh_from_db()
        self.assertEqual(p_task.last_task_creation, self.original_last_task_creation)

        p_task.is_active = True
        p_task.save()
        p_task.refresh_from_db()
        self.assertTrue(p_task.last_task_creation > self.original_last_task_creation)

    def test_periodic_future_task_max_one_exection(self):
        p_task = PeriodicFutureTask.objects.get(pk=self.task_max_one_execution.pk)

        # Make sure that task population has been processed.
        time.sleep(SLEEP_TIME)

        p_task.refresh_from_db()
        self.assertEqual(
            FutureTask.objects.filter(periodic_parent_task_id=p_task.pk).count(),
            1,
        )
        self.assertFalse(p_task.is_active)

    def test_periodic_future_task_end_time(self):
        p_task = PeriodicFutureTask.objects.get(pk=self.task_with_end_time.pk)

        # Make sure that task population has been processed.
        time.sleep(SLEEP_TIME)

        p_task.refresh_from_db()
        self.assertEqual(
            FutureTask.objects.filter(periodic_parent_task_id=p_task.pk).count(),
            1,
        )
        self.assertFalse(p_task.is_active)

    def test_end_time_and_max_number_of_executions_validation(self):
        p_task = PeriodicFutureTask.objects.get(pk=self.task_for_validation_test.pk)
        p_task.max_number_of_executions = 42
        p_task.end_time = timezone.now()
        self.assertRaises(ValidationError, p_task.save)
