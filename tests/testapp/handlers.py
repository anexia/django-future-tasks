import time
from sys import intern
from time import monotonic_ns

from django.dispatch import receiver

from django_future_tasks.handlers import future_task_signal
from tests.core import settings


@receiver(future_task_signal, sender=intern(settings.FUTURE_TASK_TYPE_ONE))
def my_task_function1(sender, instance, **kwargs):
    pass


@receiver(future_task_signal, sender=intern(settings.FUTURE_TASK_TYPE_TWO))
def my_task_function2(sender, instance, **kwargs):
    pass


@receiver(future_task_signal, sender=intern(settings.FUTURE_TASK_TYPE_ERROR))
def my_task_function_error(sender, instance, **kwargs):
    raise Exception("task error")


@receiver(future_task_signal, sender=intern(settings.FUTURE_TASK_TYPE_INTERRUPTION))
def my_task_function_interruption(sender, instance, **kwargs):
    time.sleep(10)


@receiver(future_task_signal, sender=intern(settings.FUTURE_TASK_TYPE_ETA_ORDERING))
def my_task_function_eta_ordering(sender, instance, **kwargs):
    instance.result = monotonic_ns()
    instance.save()
