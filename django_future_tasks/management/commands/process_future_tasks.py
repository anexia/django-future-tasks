import logging
import signal
import time
from sys import intern

from django import db
from django.core.management.base import BaseCommand
from django.utils import timezone

from django_future_tasks.handlers import future_task_signal
from django_future_tasks.models import FutureTask

logger = logging.getLogger("process_future_tasks")


class Command(BaseCommand):
    help = "Process future tasks from database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--onetimerun",
            action="append",
            type=bool,
            default=False,
            help="Run command only one times",
        )

    def _handle_termination(self, *args, **kwargs):
        self._running = False

    def _handle_options(self, options):
        self.tick = 1
        self.one_time_run = options["onetimerun"]

    @staticmethod
    def tasks_for_processing():
        return FutureTask.objects.filter(
            eta__lte=timezone.now(), status=FutureTask.FUTURE_TASK_STATUS_OPEN
        )

    @staticmethod
    def process_task(task):
        results = future_task_signal.send(sender=intern(task.type), instance=task)
        for receiver, response in results:
            if isinstance(response, Exception):
                logger.exception(
                    "Exception occurred while processing task {} of type {}".format(
                        task.id, task.type
                    )
                )
                task.status = FutureTask.FUTURE_TASK_STATUS_ERROR
                task.result = {
                    "error": str(response),
                }
                return False
        return True

    def handle_tick(self):
        task_list = self.tasks_for_processing()
        logger.debug("Got {} tasks for processing".format(len(task_list)))

        for task in task_list:
            task.status = FutureTask.FUTURE_TASK_STATUS_IN_PROGRESS
            task.save()
            if self.process_task(task):
                task.status = FutureTask.FUTURE_TASK_STATUS_DONE
            task.save()

        time.sleep(self.tick)

    def handle(self, *args, **options):
        # Load given options.
        self._handle_options(options)

        while self._running:
            time.sleep(self.tick)

            try:
                self.handle_tick()
                if self.one_time_run:
                    break

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
