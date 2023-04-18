from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _


class FutureTask(models.Model):
    FUTURE_TASK_STATUS_OPEN = "open"
    FUTURE_TASK_STATUS_IN_PROGRESS = "in_progress"
    FUTURE_TASK_STATUS_DONE = "done"
    FUTURE_TASK_STATUS_ERROR = "error"

    FUTURE_TASK_STATUS = (
        (FUTURE_TASK_STATUS_OPEN, _("Status open")),
        (FUTURE_TASK_STATUS_IN_PROGRESS, _("Status in progress")),
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
