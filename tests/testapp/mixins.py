from threading import Thread

from django.core.management import call_command
from django.db import connection

from django_future_tasks.management.commands.populate_periodic_future_tasks import (
    Command as PopulatePeriodicTasksCommand,
)
from django_future_tasks.management.commands.process_future_tasks import (
    Command as ProcessTasksCommand,
)


class TestThread(Thread):
    def run(self):
        super().run()
        connection.close()


class ProcessTasksCommandMixin(object):
    @classmethod
    def setUpClass(cls):
        assert (
            not hasattr(cls, "command_instance") or cls.command_instance is None
        ), "process_future_tasks has already been started"
        print("Starting process_future_tasks...")

        cls.command_instance = ProcessTasksCommand()
        cls.thread = TestThread(target=call_command, args=(cls.command_instance,))
        cls.thread.start()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        assert (
            cls.command_instance is not None
        ), "process_future_tasks has not been started and can therefore not be stopped"
        print("Stopping process_future_tasks...")

        super().tearDownClass()
        cls.command_instance._handle_termination()
        cls.thread.join()


class PopulatePeriodicTaskCommandMixin(object):
    @classmethod
    def setUpClass(cls):
        assert (
            not hasattr(cls, "command_instance") or cls.command_instance is None
        ), "populate_periodic_future_tasks has already been started"
        print("Starting populate_periodic_future_tasks...")

        cls.command_instance = PopulatePeriodicTasksCommand()
        cls.thread = TestThread(target=call_command, args=(cls.command_instance,))
        cls.thread.start()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        assert (
            cls.command_instance is not None
        ), "populate_periodic_future_tasks has not been started and can therefore not be stopped"
        print("Stopping populate_periodic_future_tasks...")

        super().tearDownClass()
        cls.command_instance._handle_termination()
        cls.thread.join()
