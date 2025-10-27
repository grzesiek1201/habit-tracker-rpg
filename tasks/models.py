from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .enums import HabitType, RepeatUnit, TasksRepeatOn, TasksRepeats, TasksStatus, TasksStrength


class BaseTask(models.Model):
    """Abstract base model shared by Habit, Daily, and Todo."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    strength = models.CharField(
        max_length=15,
        choices=TasksStrength.choices,
        default=TasksStrength.STABLE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Habit(BaseTask):
    """Represents a user habit, either good or bad."""

    type = models.CharField(
        max_length=15,
        choices=HabitType.choices,
        db_index=True,
    )
    status = models.CharField(
        max_length=15,
        choices=TasksStatus.choices,
        default=TasksStatus.ACTIVE,
        db_index=True,
    )

    def __str__(self):
        return self.name


class Daily(BaseTask):
    """Represents a recurring daily task."""

    repeats = models.CharField(
        max_length=15,
        choices=TasksRepeats.choices,
        default=TasksRepeats.DAILY,
        db_index=True,
    )
    repeat_on = models.CharField(
        max_length=15,
        choices=TasksRepeatOn.choices,
        default=TasksRepeatOn.EVERYDAY,
        db_index=True,
    )
    repeat_interval = models.IntegerField(default=1)
    repeat_unit = models.CharField(
        max_length=15,
        choices=RepeatUnit.choices,
        default=RepeatUnit.DAYS,
    )
    status = models.CharField(
        max_length=15,
        choices=TasksStatus.choices,
        default=TasksStatus.ACTIVE,
        db_index=True,
    )

    def __str__(self):
        return self.name


class Todo(BaseTask):
    """Represents a one-time to-do task."""

    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.due_date < timezone.now().date():
            raise ValidationError("Due date cannot be in the past.")
