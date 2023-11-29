from django import forms
from django.conf import settings
from django.contrib import admin

from django_future_tasks.models import FutureTask, PeriodicFutureTask


class FutureTaskAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FutureTaskAdminForm, self).__init__(*args, **kwargs)
        self.fields["type"].widget = forms.Select(choices=settings.FUTURE_TASK_TYPES)

    class Meta:
        model = FutureTask
        exclude = ()


@admin.register(FutureTask)
class FutureTaskAdmin(admin.ModelAdmin):
    list_display = ["task_id", "eta", "type", "status", "periodic_parent_task"]
    readonly_fields = ["periodic_parent_task"]
    list_filter = ["type", "status", "periodic_parent_task"]
    form = FutureTaskAdminForm


class PeriodicFutureTaskAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PeriodicFutureTaskAdminForm, self).__init__(*args, **kwargs)
        self.fields["type"].widget = forms.Select(choices=settings.FUTURE_TASK_TYPES)

    class Meta:
        model = PeriodicFutureTask
        exclude = ()

    class Media:
        css = {"all": ("django_future_tasks/cronfield.css",)}


class FutureTaskInline(admin.TabularInline):
    verbose_name = "Corresponding single task"
    verbose_name_plural = "Corresponding single tasks"
    model = FutureTask
    fields = ["task_id", "eta", "status"]
    readonly_fields = ["task_id", "eta", "status"]
    extra = 0
    classes = ["collapse"]
    ordering = ["-eta"]
    max_num = 100


@admin.register(PeriodicFutureTask)
class PeriodicFutureTaskAdmin(admin.ModelAdmin):
    readonly_fields = [
        "cron_humnan_readable",
        "last_task_creation",
        "next_planned_execution",
    ]
    list_display = [
        "periodic_task_id",
        "cron_string",
        "cron_humnan_readable",
        "is_active",
        "type",
        "next_planned_execution",
    ]
    list_editable = ["cron_string", "is_active"]
    inlines = [FutureTaskInline]
    list_filter = ["type", "is_active"]
    form = PeriodicFutureTaskAdminForm
