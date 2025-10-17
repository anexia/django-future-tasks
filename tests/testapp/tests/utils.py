from django.core.management import call_command

from django_future_tasks.management.commands.process_future_tasks import (
    Command as ProcessTasksCommand,
)
from testapp.mixins import TestThread


class ProcessFutureTasksWorker:
    def __init__(self, *args: str):
        self.command_instance = ProcessTasksCommand()
        self.thread = TestThread(target=call_command, args=(self.command_instance, *args))

    def __enter__(self):
        self.thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.command_instance._handle_termination()
        self.thread.join()
