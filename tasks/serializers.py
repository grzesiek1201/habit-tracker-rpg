from rest_framework import serializers
from .models import Habit, Daily, Todo


class HabitSerializer(serializers.ModelSerializer):
    """Serializer for Habit model"""

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "name",
            "notes",
            "type",
            "status",
            "strength",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]


class DailySerializer(serializers.ModelSerializer):
    """Serializer for Daily model"""

    class Meta:
        model = Daily
        fields = [
            "id",
            "user",
            "name",
            "notes",
            "strength",
            "status",
            "repeats",
            "repeat_on",
            "repeat_interval",
            "repeat_unit",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]


class TodoSerializer(serializers.ModelSerializer):
    """Serializer for Todo model"""

    class Meta:
        model = Todo
        fields = [
            "id",
            "user",
            "name",
            "notes",
            "strength",
            "due_date",
            "is_completed",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]

    def validate_due_date(self, value):
        """Ensure due_date is not in the past"""
        from django.utils import timezone

        if value < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
