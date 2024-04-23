import re

from cronfield.models import CronField
from django.core.exceptions import ValidationError


def _validate_CRON_string(value):
    """Validation routine for CRON string in TestingPlan"""

    if value.strip() != value:
        raise ValidationError("Leading nor trailing spaces are allowed")
    columns = value.split()
    if columns != value.split(" "):
        raise ValidationError("Use only a single space as a column separator")

    if len(columns) not in [5, 6]:
        raise ValidationError("Entry has to consist of 5 or 6 columns")

    pattern = r"^(\*|\d+(-\d+)?(,\d+(-\d+)?)*)(/\d+)?$"
    p = re.compile(pattern)
    for i, c in enumerate(columns):
        if not p.match(c):
            raise ValidationError("Incorrect value {} in column {}".format(c, i + 1))


class FutureTaskCronField(CronField):
    def validate(self, value, model_instance):
        super(CronField, self).validate(value, model_instance)
        if self.editable:  # Skip validation for non-editable fields.
            _validate_CRON_string(value)

    def __init__(self, *args, **kwargs):
        kwargs["default"] = "* * * * * *"
        kwargs["help_text"] = "Minute Hour Day Month Weekday Second"
        super().__init__(*args, **kwargs)
