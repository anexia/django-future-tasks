import time
from datetime import timedelta

from django.test import TransactionTestCase
from django.utils import timezone

from django_future_tasks.models import FutureTask, PeriodicFutureTask
from tests.core import settings
from tests.testapp.mixins import PeriodicTaskCommandMixin

SLEEP_TIME = 1.1


class TestPeriodicFutureTasks(PeriodicTaskCommandMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()

        last_task_creation = timezone.now() - timedelta(hours=2)

        self.task_active = PeriodicFutureTask.objects.create(
            periodic_task_id="periodic task",
            type=settings.FUTURE_TASK_TYPE_ONE,
            cron_string="42 * * * *",
        )

        p_task = PeriodicFutureTask.objects.get(pk=self.task_active.pk)
        p_task.last_task_creation = last_task_creation
        p_task.save()

        self.task_not_active = PeriodicFutureTask.objects.create(
            periodic_task_id="periodic inactive task",
            type=settings.FUTURE_TASK_TYPE_ONE,
            cron_string="42 * * * *",
            last_task_creation=last_task_creation,
            is_active=False,
        )

    def test_periodic_future_task_populate_active_task(self):
        p_task = PeriodicFutureTask.objects.get(pk=self.task_active.pk)
        last_task_creation = p_task.last_task_creation

        # Make sure that task population has been processed.
        time.sleep(SLEEP_TIME)

        p_task.refresh_from_db()
        self.assertTrue(p_task.last_task_creation > last_task_creation)
        self.assertEqual(
            FutureTask.objects.filter(periodic_parent_task_id=p_task.pk).count(), 2
        )

        for task in FutureTask.objects.filter(periodic_parent_task_id=p_task.pk):
            self.assertEqual(task.type, p_task.type)
            self.assertEqual(task.status, FutureTask.FUTURE_TASK_STATUS_OPEN)

    def test_periodic_future_task_populate_inactive_task(self):
        p_task = PeriodicFutureTask.objects.get(pk=self.task_not_active.pk)
        last_task_creation = p_task.last_task_creation

        # Make sure that task population has been processed.
        time.sleep(SLEEP_TIME)

        p_task.refresh_from_db()
        self.assertEqual(p_task.last_task_creation, last_task_creation)
        self.assertFalse(
            FutureTask.objects.filter(periodic_parent_task_id=p_task.pk).exists()
        )

    def test_periodic_future_task_deactivation_and_activation(self):
        p_task = PeriodicFutureTask.objects.get(pk=self.task_active.pk)
        last_task_creation = p_task.last_task_creation

        p_task.is_active = False
        p_task.save()
        p_task.refresh_from_db()
        self.assertEqual(p_task.last_task_creation, last_task_creation)

        p_task.is_active = True
        p_task.save()
        p_task.refresh_from_db()
        self.assertTrue(p_task.last_task_creation > last_task_creation)
