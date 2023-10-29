import logging
import signal
import time

from croniter import croniter_range
from django import db
from django.core.management.base import BaseCommand
from django.utils import timezone

from django_future_tasks.models import FutureTask, PeriodicFutureTask

logger = logging.getLogger("populate_periodic_future_tasks")


class Command(BaseCommand):
    help = "Create single future tasks based on periodic future tasks from database"

    def _handle_termination(self, *args, **kwargs):
        self._running = False

    def _handle_options(self):
        # Currently, no other options are given.
        self.tick = 1

    @staticmethod
    def periodic_tasks_for_processing():
        return PeriodicFutureTask.objects.filter(is_active=True)

    @staticmethod
    def number_of_corresponding_single_tasks(p_task):
        return FutureTask.objects.filter(periodic_parent_task_id=p_task.pk).count()

    def update_last_task_creation(self):
        now = timezone.now()
        for p_task in self.periodic_tasks_for_processing():
            p_task.last_task_creation = now
            p_task.save()

    @staticmethod
    def _convert_exception_args(args):
        return [str(arg) for arg in args]

    def handle_tick(self):
        now = timezone.now()
        periodic_task_list = self.periodic_tasks_for_processing()
        logger.debug(
            "Got {} periodic tasks for processing".format(len(periodic_task_list))
        )

        for p_task in periodic_task_list:
            last_population = p_task.last_task_creation
            relevant_dts = croniter_range(last_population, now, p_task.cron_string)

            for dt in relevant_dts:
                if (
                    p_task.max_number_of_executions is not None
                    and self.number_of_corresponding_single_tasks(p_task)
                    >= p_task.max_number_of_executions
                ) or (p_task.end_time is not None and p_task.end_time < dt):
                    p_task.is_active = False
                    break

                dt_format = "%Y-%m-%d %H:%M%z"
                task_id = f"{p_task.periodic_task_id} ({dt.strftime(dt_format)})"
                FutureTask.objects.create(
                    task_id=task_id,
                    eta=dt,
                    data=p_task.data,
                    type=p_task.type,
                    status=FutureTask.FUTURE_TASK_STATUS_OPEN,
                    periodic_parent_task_id=p_task.pk,
                )
                logger.info(f"FutureTask {task_id} created")

            p_task.last_task_creation = now
            p_task.save()

        time.sleep(self.tick)

    def handle(self, *args, **options):
        # Load given options.
        self._handle_options()

        while self._running:
            time.sleep(self.tick)

            try:
                self.handle_tick()

            except Exception as exc:
                logger.exception(
                    "%s exception occurred ... " % (exc.__class__.__name__,)
                )

                # As the database connection might have failed, we discard it here, so django will
                # create a new one on the next database access.
                db.close_old_connections()

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # The command will run as long as the `_running` attribute is
        # set to `True`. To safely quit the command, just set this attribute to `False` and the
        # command will finish a running tick and quit afterwards.
        self._running = True

        # Register system signal handler to gracefully quit the service when
        # getting a `SIGINT` or `SIGTERM` signal (e.g. by CTRL+C).
        signal.signal(signal.SIGINT, self._handle_termination)
        signal.signal(signal.SIGTERM, self._handle_termination)

        self.update_last_task_creation()
