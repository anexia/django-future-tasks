from threading import Thread

from django.core.management import call_command
from django.db import connection

from django_future_tasks.management.commands.populate_periodic_future_tasks import (
    Command,
)


class TestThread(Thread):
    def run(self):
        super().run()
        connection.close()


class PeriodicTaskCommandMixin(object):
    @classmethod
    def setUpClass(cls):
        assert (
            not hasattr(cls, "command_instance") or cls.command_instance is None
        ), "populate_periodic_future_tasks has already been started"
        print("Starting populate_periodic_future_tasks...")

        cls.command_instance = Command()
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
