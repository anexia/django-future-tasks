import time
from sys import intern

from django.dispatch import receiver

from django_future_tasks.handlers import future_task_signal
from tests.core import settings


@receiver(future_task_signal, sender=intern(settings.FUTURE_TASK_TYPE_ONE))
def my_task_function1(sender, instance, **kwargs):
    time.sleep(0.5)


@receiver(future_task_signal, sender=intern(settings.FUTURE_TASK_TYPE_TWO))
def my_task_function2(sender, instance, **kwargs):
    pass


@receiver(future_task_signal, sender=intern(settings.FUTURE_TASK_TYPE_ERROR))
def my_task_function_error(sender, instance, **kwargs):
    raise Exception("task error")


@receiver(future_task_signal, sender=intern(settings.FUTURE_TASK_TYPE_INTERRUPTION))
def my_task_function_interruption(sender, instance, **kwargs):
    time.sleep(10)
