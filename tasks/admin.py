from django.contrib import admin

from tasks.models import Daily, Habit, Todo


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "type", "status", "strength", "created_at"]
    list_filter = ["type", "status", "strength", "created_at"]
    search_fields = ["name", "notes", "user__username"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]


@admin.register(Daily)
class DailyAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "user",
        "status",
        "strength",
        "repeats",
        "repeat_on",
        "created_at",
    ]
    list_filter = ["status", "strength", "repeats", "repeat_on", "created_at"]
    search_fields = ["name", "notes", "user__username"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "user",
        "due_date",
        "is_completed",
        "strength",
        "created_at",
    ]
    list_filter = ["is_completed", "strength", "due_date", "created_at"]
    search_fields = ["name", "notes", "user__username"]
    ordering = ["due_date", "-created_at"]
    readonly_fields = ["created_at"]
