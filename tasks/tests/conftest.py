import datetime

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tasks.enums import HabitType, TasksStrength
from tasks.models import Daily, Habit, Todo

User = get_user_model()


@pytest.fixture
def api_client():
    """Returns an unauthenticated API client"""
    return APIClient()


@pytest.fixture
def user(db):
    """Creates and returns a test user"""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="TestPass123!"
    )


@pytest.fixture
def other_user(db):
    """Creates and returns another test user for isolation tests"""
    return User.objects.create_user(
        username="otheruser", email="other@example.com", password="OtherPass123!"
    )


@pytest.fixture
def authenticated_client(user, api_client):
    """Returns an API client authenticated as the test user"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def habit(user):
    """Creates and returns a test habit"""
    return Habit.objects.create(
        user=user,
        name="Drink Water",
        notes="Drink 8 glasses per day",
        type=HabitType.GOOD,
        strength=TasksStrength.STABLE,
    )


@pytest.fixture
def bad_habit(user):
    """Creates and returns a bad habit for testing"""
    return Habit.objects.create(
        user=user,
        name="Smoking",
        notes="Bad habit to break",
        type=HabitType.BAD,
        strength=TasksStrength.WEAK,
    )


@pytest.fixture
def daily(user):
    """Creates and returns a test daily task"""
    return Daily.objects.create(
        user=user,
        name="Morning Exercise",
        notes="30 minutes of cardio",
        repeats="daily",
        strength=TasksStrength.STABLE,
    )


@pytest.fixture
def todo(user):
    """Creates and returns a test todo with future due date"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return Todo.objects.create(
        user=user,
        name="Complete project",
        notes="Finish by deadline",
        due_date=tomorrow,
    )


@pytest.fixture
def completed_todo(user):
    """Creates and returns a completed todo"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return Todo.objects.create(
        user=user,
        name="Completed Task",
        notes="Already done",
        due_date=tomorrow,
        is_completed=True,
    )
