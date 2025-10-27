import datetime

import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from tasks.enums import HabitType, TasksStatus, TasksStrength
from tasks.models import Daily, Habit, Todo
from tasks.serializers import DailySerializer, HabitSerializer, TodoSerializer

User = get_user_model()


# -----------------------
# Fixtures
# -----------------------
@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="TestPass123!"
    )


# -----------------------
# HabitSerializer Tests
# -----------------------
@pytest.mark.django_db
def test_habit_serializer_valid_data(user):
    """Test HabitSerializer with valid data"""
    data = {
        "name": "Drink Water",
        "notes": "Drink 8 glasses per day",
        "type": HabitType.GOOD,
        "status": TasksStatus.ACTIVE,
        "strength": TasksStrength.STABLE,
    }
    serializer = HabitSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    habit = serializer.save(user=user)
    assert habit.name == "Drink Water"
    assert habit.type == HabitType.GOOD
    assert habit.user == user


@pytest.mark.django_db
def test_habit_serializer_missing_required_fields():
    """Test HabitSerializer rejects missing required fields"""
    data = {"notes": "Some notes"}
    serializer = HabitSerializer(data=data)
    assert not serializer.is_valid()
    assert "name" in serializer.errors
    assert "type" in serializer.errors


@pytest.mark.django_db
def test_habit_serializer_read_only_fields(user):
    """Test that read-only fields are not writable"""
    habit = Habit.objects.create(
        user=user,
        name="Original Name",
        type=HabitType.GOOD,
    )
    data = {
        "id": 999,  # Should be ignored
        "created_at": "2020-01-01T00:00:00Z",  # Should be ignored
        "name": "Updated Name",
    }
    serializer = HabitSerializer(habit, data=data, partial=True)
    assert serializer.is_valid(), serializer.errors
    updated_habit = serializer.save()
    assert updated_habit.id == habit.id  # ID unchanged
    assert updated_habit.name == "Updated Name"


@pytest.mark.django_db
def test_habit_serializer_default_values(user):
    """Test HabitSerializer applies default values correctly"""
    data = {
        "name": "New Habit",
        "type": HabitType.BAD,
    }
    serializer = HabitSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    habit = serializer.save(user=user)
    assert habit.status == TasksStatus.ACTIVE  # Default
    assert habit.strength == TasksStrength.STABLE  # Default


# -----------------------
# DailySerializer Tests
# -----------------------
@pytest.mark.django_db
def test_daily_serializer_valid_data(user):
    """Test DailySerializer with valid data"""
    data = {
        "name": "Morning Exercise",
        "notes": "30 minutes of cardio",
        "strength": TasksStrength.WEAK,
        "status": TasksStatus.ACTIVE,
        "repeats": "daily",
        "repeat_on": "everyday",
    }
    serializer = DailySerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    daily = serializer.save(user=user)
    assert daily.name == "Morning Exercise"
    assert daily.user == user


@pytest.mark.django_db
def test_daily_serializer_missing_required_fields():
    """Test DailySerializer rejects missing required fields"""
    data = {"notes": "Just notes"}
    serializer = DailySerializer(data=data)
    assert not serializer.is_valid()
    assert "name" in serializer.errors


@pytest.mark.django_db
def test_daily_serializer_update(user):
    """Test updating a daily task"""
    daily = Daily.objects.create(
        user=user,
        name="Original Daily",
        repeats="daily",
    )
    data = {
        "name": "Updated Daily",
        "status": TasksStatus.COMPLETED,
    }
    serializer = DailySerializer(daily, data=data, partial=True)
    assert serializer.is_valid(), serializer.errors
    updated_daily = serializer.save()
    assert updated_daily.name == "Updated Daily"
    assert updated_daily.status == TasksStatus.COMPLETED


@pytest.mark.django_db
def test_daily_serializer_default_values(user):
    """Test DailySerializer applies default values"""
    data = {
        "name": "New Daily",
    }
    serializer = DailySerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    daily = serializer.save(user=user)
    assert daily.status == TasksStatus.ACTIVE
    assert daily.strength == TasksStrength.STABLE
    assert daily.repeats == "daily"


# -----------------------
# TodoSerializer Tests
# -----------------------
@pytest.mark.django_db
def test_todo_serializer_valid_data(user):
    """Test TodoSerializer with valid future due_date"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    data = {
        "name": "Complete project",
        "notes": "Finish by end of week",
        "due_date": tomorrow.isoformat(),
    }
    serializer = TodoSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    todo = serializer.save(user=user)
    assert todo.name == "Complete project"
    assert todo.due_date == tomorrow
    assert todo.user == user


@pytest.mark.django_db
def test_todo_serializer_past_due_date_validation():
    """Test TodoSerializer rejects past due_date"""
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    data = {
        "name": "Past Todo",
        "due_date": yesterday.isoformat(),
    }
    serializer = TodoSerializer(data=data)
    assert not serializer.is_valid()
    assert "due_date" in serializer.errors
    assert "past" in str(serializer.errors["due_date"]).lower()


@pytest.mark.django_db
def test_todo_serializer_today_due_date_valid(user):
    """Test TodoSerializer accepts today as due_date"""
    today = datetime.date.today()
    data = {
        "name": "Today's Todo",
        "due_date": today.isoformat(),
    }
    serializer = TodoSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    todo = serializer.save(user=user)
    assert todo.due_date == today


@pytest.mark.django_db
def test_todo_serializer_missing_required_fields():
    """Test TodoSerializer rejects missing required fields"""
    data = {"notes": "Just notes"}
    serializer = TodoSerializer(data=data)
    assert not serializer.is_valid()
    assert "name" in serializer.errors
    assert "due_date" in serializer.errors


@pytest.mark.django_db
def test_todo_serializer_default_is_completed(user):
    """Test TodoSerializer default is_completed is False"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    data = {
        "name": "New Todo",
        "due_date": tomorrow.isoformat(),
    }
    serializer = TodoSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    todo = serializer.save(user=user)
    assert todo.is_completed is False


@pytest.mark.django_db
def test_todo_serializer_update(user):
    """Test updating a todo task"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    todo = Todo.objects.create(
        user=user,
        name="Original Todo",
        due_date=tomorrow,
    )
    data = {
        "name": "Updated Todo",
        "is_completed": True,
    }
    serializer = TodoSerializer(todo, data=data, partial=True)
    assert serializer.is_valid(), serializer.errors
    updated_todo = serializer.save()
    assert updated_todo.name == "Updated Todo"
    assert updated_todo.is_completed is True


@pytest.mark.django_db
def test_todo_serializer_read_only_fields(user):
    """Test that read-only fields cannot be modified"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    todo = Todo.objects.create(
        user=user,
        name="Test Todo",
        due_date=tomorrow,
    )
    original_created_at = todo.created_at
    data = {
        "created_at": "2020-01-01T00:00:00Z",  # Should be ignored
        "name": "Modified Name",
    }
    serializer = TodoSerializer(todo, data=data, partial=True)
    assert serializer.is_valid(), serializer.errors
    updated_todo = serializer.save()
    assert updated_todo.created_at == original_created_at
    assert updated_todo.name == "Modified Name"
