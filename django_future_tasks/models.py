import datetime
import uuid

import croniter
from cron_descriptor import (
    CasingTypeEnum,
    DescriptionTypeEnum,
    ExpressionDescriptor,
    Options,
)
from cronfield.models import CronField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField, Q
from django.utils.dateformat import format
from django.utils.timezone import utc
from django.utils.translation import gettext_lazy as _


class FutureTask(models.Model):
    FUTURE_TASK_STATUS_OPEN = "open"
    FUTURE_TASK_STATUS_IN_PROGRESS = "in_progress"
    FUTURE_TASK_STATUS_INTERRUPTED = "interrupted"
    FUTURE_TASK_STATUS_DONE = "done"
    FUTURE_TASK_STATUS_ERROR = "error"

    FUTURE_TASK_STATUS = (
        (FUTURE_TASK_STATUS_OPEN, _("Status open")),
        (FUTURE_TASK_STATUS_IN_PROGRESS, _("Status in progress")),
        (FUTURE_TASK_STATUS_INTERRUPTED, _("Status interrupted")),
        (FUTURE_TASK_STATUS_DONE, _("Status done")),
        (FUTURE_TASK_STATUS_ERROR, _("Status error")),
    )

    task_id = models.CharField(_("task ID"), max_length=255, unique=True)
    eta = models.DateTimeField(
        _("ETA"),
        help_text=_("The date and time when the task should be executed"),
    )
    data = JSONField(
        _("Various execution data"),
        blank=True,
        null=True,
    )
    type = models.CharField(
        _("Task type"),
        max_length=255,
        blank=False,
        null=False,
    )
    status = models.CharField(
        _("Status"),
        max_length=255,
        choices=FUTURE_TASK_STATUS,
        default=FUTURE_TASK_STATUS_OPEN,
    )
    # Result of the task execution
    result = JSONField(
        _("Result"),
        blank=True,
        null=True,
    )
    execution_time = models.FloatField(blank=True, null=True, help_text="in seconds")

    periodic_parent_task = models.ForeignKey(
        "PeriodicFutureTask", on_delete=models.CASCADE, null=True, default=None
    )


class PeriodicFutureTask(models.Model):
    periodic_task_id = models.CharField(
        _("periodic task ID"), max_length=255, unique=True
    )
    type = models.CharField(
        _("Task type"),
        max_length=255,
        blank=False,
        null=False,
    )
    data = JSONField(
        _("Various execution data"),
        blank=True,
        null=True,
    )
    cron_string = CronField()
    is_active = models.BooleanField(_("Active"), default=True)
    max_number_of_executions = models.IntegerField(
        _("Maximal number of executions"), null=True, blank=True
    )
    end_time = models.DateTimeField(_("Executions until"), null=True, blank=True)
    __original_is_active = None
    last_task_creation = models.DateTimeField(
        _("Last single task creation"),
        help_text=_("The last time corresponding single tasks where created."),
        auto_now_add=True,
    )

    def next_planned_execution(self):
        now = datetime.datetime.now()
        next_planned_execution = utc.localize(
            croniter.croniter(self.cron_string, now).get_next(datetime.datetime)
        )
        if (
            not self.is_active
            or (
                self.max_number_of_executions is not None
                and FutureTask.objects.filter(periodic_parent_task=self.pk).count()
                >= self.max_number_of_executions
            )
            or (
                self.end_time is not None
                and self.end_time
                < utc.localize(
                    croniter.croniter(self.cron_string, now).get_next(datetime.datetime)
                )
            )
        ):
            return None

        return format(
            next_planned_execution,
            settings.DATETIME_FORMAT,
        )

    def cron_humnan_readable(self):
        descriptor = ExpressionDescriptor(
            expression=self.cron_string,
            casing_type=CasingTypeEnum.Sentence,
            use_24hour_time_format=False,
        )
        return descriptor.get_description()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_is_active = self.is_active

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.is_active and not self.__original_is_active:
            self.last_task_creation = datetime.datetime.now()

        self.clean()
        super().save()
        self.__original_is_active = self.is_active

    def __str__(self):
        return f"{self.periodic_task_id} ({self.cron_string})"

    def clean(self):
        if self.end_time is not None and self.max_number_of_executions is not None:
            raise ValidationError(
                {
                    "end_time": _(
                        "Cannot be set together with maximal number of executions, at least one must be empty."
                    ),
                    "max_number_of_executions": _(
                        "Cannot be set together with execution end time, at least one must be empty."
                    ),
                }
            )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(end_time__isnull=True)
                | Q(max_number_of_executions__isnull=True),
                name="not_both_not_null",
            )
        ]
