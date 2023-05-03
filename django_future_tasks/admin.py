from django import forms
from django.conf import settings
from django.contrib import admin

from django_future_tasks.models import FutureTask


class FutureTaskAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FutureTaskAdminForm, self).__init__(*args, **kwargs)
        self.fields["type"].widget = forms.Select(choices=settings.FUTURE_TASK_TYPES)

    class Meta:
        model = FutureTask
        exclude = ()


@admin.register(FutureTask)
class FutureTaskAdmin(admin.ModelAdmin):
    list_display = [
        "task_id",
        "eta",
        "type",
        "status",
    ]
    form = FutureTaskAdminForm
