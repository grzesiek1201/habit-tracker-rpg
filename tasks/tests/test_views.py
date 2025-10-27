import datetime

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tasks.enums import HabitType, TasksStatus, TasksStrength
from tasks.models import Daily, Habit, Todo

User = get_user_model()


# -----------------------
# Fixtures
# -----------------------
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="TestPass123!"
    )


@pytest.fixture
def authenticated_client(user, api_client):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def habit(user):
    return Habit.objects.create(
        user=user,
        name="Drink Water",
        notes="8 glasses a day",
        type=HabitType.GOOD,
        strength=TasksStrength.STABLE,
    )


@pytest.fixture
def daily(user):
    return Daily.objects.create(
        user=user,
        name="Morning Exercise",
        notes="30 min cardio",
        repeats="daily",
    )


@pytest.fixture
def todo(user):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return Todo.objects.create(
        user=user,
        name="Complete project",
        notes="Finish by deadline",
        due_date=tomorrow,
    )


# -----------------------
# Habit ViewSet Tests
# -----------------------
@pytest.mark.django_db
def test_habit_list_requires_auth(api_client):
    """Test that listing habits requires authentication"""
    url = reverse("habit-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_habit_list_returns_user_habits_only(authenticated_client, user, habit):
    """Test that users only see their own habits"""
    # Create another user with their own habit
    other_user = User.objects.create_user(
        username="otheruser", email="other@example.com", password="Pass123!"
    )
    Habit.objects.create(
        user=other_user,
        name="Other's Habit",
        type=HabitType.BAD,
    )

    url = reverse("habit-list")
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Drink Water"


@pytest.mark.django_db
def test_habit_create(authenticated_client, user):
    """Test creating a new habit"""
    url = reverse("habit-list")
    data = {
        "name": "Read Daily",
        "notes": "Read for 30 minutes",
        "type": HabitType.GOOD,
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Read Daily"
    assert response.data["user"] == user.id
    assert Habit.objects.filter(user=user, name="Read Daily").exists()


@pytest.mark.django_db
def test_habit_retrieve(authenticated_client, habit):
    """Test retrieving a single habit"""
    url = reverse("habit-detail", args=[habit.id])
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Drink Water"
    assert response.data["id"] == habit.id


@pytest.mark.django_db
def test_habit_update(authenticated_client, habit):
    """Test updating a habit"""
    url = reverse("habit-detail", args=[habit.id])
    data = {"name": "Drink More Water", "status": TasksStatus.INACTIVE}
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Drink More Water"
    assert response.data["status"] == TasksStatus.INACTIVE
    habit.refresh_from_db()
    assert habit.name == "Drink More Water"


@pytest.mark.django_db
def test_habit_delete(authenticated_client, habit):
    """Test deleting a habit"""
    url = reverse("habit-detail", args=[habit.id])
    response = authenticated_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Habit.objects.filter(id=habit.id).exists()


@pytest.mark.django_db
def test_habit_complete_good_habit(authenticated_client, user, habit):
    """Test completing a good habit rewards EXP and increases strength"""
    initial_exp = user.current_exp
    initial_strength = habit.strength

    url = reverse("habit-complete-habit", args=[habit.id])
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert "Good habit completed" in response.data["detail"]
    assert response.data["user"]["current_exp"] == initial_exp + 10

    habit.refresh_from_db()
    assert habit.strength != initial_strength  # Strength increased


@pytest.mark.django_db
def test_habit_complete_bad_habit(authenticated_client, user):
    """Test executing a bad habit reduces HP and decreases strength"""
    bad_habit = Habit.objects.create(
        user=user,
        name="Smoking",
        type=HabitType.BAD,
        strength=TasksStrength.STABLE,
    )
    initial_hp = user.current_hp

    url = reverse("habit-complete-habit", args=[bad_habit.id])
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert "Bad habit recorded" in response.data["detail"]
    assert response.data["user"]["current_hp"] == initial_hp - 5


@pytest.mark.django_db
def test_habit_filter_by_type(authenticated_client, user):
    """Test filtering habits by type"""
    Habit.objects.create(user=user, name="Good1", type=HabitType.GOOD)
    Habit.objects.create(user=user, name="Bad1", type=HabitType.BAD)
    Habit.objects.create(user=user, name="Good2", type=HabitType.GOOD)

    url = reverse("habit-list")
    response = authenticated_client.get(url, {"type": HabitType.GOOD})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_habit_filter_by_status(authenticated_client, user):
    """Test filtering habits by status"""
    Habit.objects.create(
        user=user, name="Active", type=HabitType.GOOD, status=TasksStatus.ACTIVE
    )
    Habit.objects.create(
        user=user, name="Inactive", type=HabitType.GOOD, status=TasksStatus.INACTIVE
    )

    url = reverse("habit-list")
    response = authenticated_client.get(url, {"status": TasksStatus.ACTIVE})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Active"


@pytest.mark.django_db
def test_habit_search(authenticated_client, user):
    """Test searching habits by name"""
    Habit.objects.create(user=user, name="Drink Water", type=HabitType.GOOD)
    Habit.objects.create(user=user, name="Exercise Daily", type=HabitType.GOOD)

    url = reverse("habit-list")
    response = authenticated_client.get(url, {"search": "water"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert "Water" in response.data[0]["name"]


# -----------------------
# Daily ViewSet Tests
# -----------------------
@pytest.mark.django_db
def test_daily_list_requires_auth(api_client):
    """Test that listing dailies requires authentication"""
    url = reverse("daily-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_daily_list_returns_user_dailies_only(authenticated_client, user, daily):
    """Test that users only see their own dailies"""
    other_user = User.objects.create_user(
        username="otheruser", email="other@example.com", password="Pass123!"
    )
    Daily.objects.create(user=other_user, name="Other's Daily", repeats="daily")

    url = reverse("daily-list")
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Morning Exercise"


@pytest.mark.django_db
def test_daily_create(authenticated_client, user):
    """Test creating a new daily task"""
    url = reverse("daily-list")
    data = {
        "name": "Evening Meditation",
        "notes": "15 minutes before bed",
        "repeats": "daily",
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Evening Meditation"
    assert Daily.objects.filter(user=user, name="Evening Meditation").exists()


@pytest.mark.django_db
def test_daily_retrieve(authenticated_client, daily):
    """Test retrieving a single daily task"""
    url = reverse("daily-detail", args=[daily.id])
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Morning Exercise"


@pytest.mark.django_db
def test_daily_update(authenticated_client, daily):
    """Test updating a daily task"""
    url = reverse("daily-detail", args=[daily.id])
    data = {"name": "Morning Yoga", "repeats": "weekly"}
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Morning Yoga"
    daily.refresh_from_db()
    assert daily.repeats == "weekly"


@pytest.mark.django_db
def test_daily_delete(authenticated_client, daily):
    """Test deleting a daily task"""
    url = reverse("daily-detail", args=[daily.id])
    response = authenticated_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Daily.objects.filter(id=daily.id).exists()


@pytest.mark.django_db
def test_daily_complete(authenticated_client, user, daily):
    """Test completing a daily task rewards EXP and increases strength"""
    initial_exp = user.current_exp
    initial_strength = daily.strength

    url = reverse("daily-complete-daily", args=[daily.id])
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert "Daily task completed" in response.data["detail"]
    assert response.data["user"]["current_exp"] == initial_exp + 15

    daily.refresh_from_db()
    assert daily.status == TasksStatus.COMPLETED
    assert daily.strength != initial_strength


@pytest.mark.django_db
def test_daily_complete_already_completed(authenticated_client, user, daily):
    """Test completing an already completed daily returns error"""
    daily.status = TasksStatus.COMPLETED
    daily.save()

    url = reverse("daily-complete-daily", args=[daily.id])
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already completed" in response.data["detail"].lower()


@pytest.mark.django_db
def test_daily_filter_by_status(authenticated_client, user):
    """Test filtering dailies by status"""
    Daily.objects.create(
        user=user, name="Active Daily", repeats="daily", status=TasksStatus.ACTIVE
    )
    Daily.objects.create(
        user=user, name="Completed Daily", repeats="daily", status=TasksStatus.COMPLETED
    )

    url = reverse("daily-list")
    response = authenticated_client.get(url, {"status": TasksStatus.ACTIVE})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Active Daily"


# -----------------------
# Todo ViewSet Tests
# -----------------------
@pytest.mark.django_db
def test_todo_list_requires_auth(api_client):
    """Test that listing todos requires authentication"""
    url = reverse("todo-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_todo_list_returns_user_todos_only(authenticated_client, user, todo):
    """Test that users only see their own todos"""
    other_user = User.objects.create_user(
        username="otheruser", email="other@example.com", password="Pass123!"
    )
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    Todo.objects.create(user=other_user, name="Other's Todo", due_date=tomorrow)

    url = reverse("todo-list")
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Complete project"


@pytest.mark.django_db
def test_todo_create(authenticated_client, user):
    """Test creating a new todo"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    url = reverse("todo-list")
    data = {
        "name": "Buy groceries",
        "notes": "Milk, bread, eggs",
        "due_date": tomorrow.isoformat(),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Buy groceries"
    assert Todo.objects.filter(user=user, name="Buy groceries").exists()


@pytest.mark.django_db
def test_todo_create_past_due_date_rejected(authenticated_client):
    """Test that creating a todo with past due_date is rejected"""
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    url = reverse("todo-list")
    data = {
        "name": "Past Todo",
        "due_date": yesterday.isoformat(),
    }
    response = authenticated_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "due_date" in response.data


@pytest.mark.django_db
def test_todo_retrieve(authenticated_client, todo):
    """Test retrieving a single todo"""
    url = reverse("todo-detail", args=[todo.id])
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Complete project"


@pytest.mark.django_db
def test_todo_update(authenticated_client, todo):
    """Test updating a todo"""
    url = reverse("todo-detail", args=[todo.id])
    data = {"name": "Complete project ASAP"}
    response = authenticated_client.patch(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Complete project ASAP"
    todo.refresh_from_db()
    assert todo.name == "Complete project ASAP"


@pytest.mark.django_db
def test_todo_delete(authenticated_client, todo):
    """Test deleting a todo"""
    url = reverse("todo-detail", args=[todo.id])
    response = authenticated_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Todo.objects.filter(id=todo.id).exists()


@pytest.mark.django_db
def test_todo_complete(authenticated_client, user, todo):
    """Test completing a todo rewards EXP and marks as completed"""
    initial_exp = user.current_exp

    url = reverse("todo-complete-todo", args=[todo.id])
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert "Todo completed" in response.data["detail"]
    assert response.data["user"]["current_exp"] == initial_exp + 20

    todo.refresh_from_db()
    assert todo.is_completed is True


@pytest.mark.django_db
def test_todo_complete_already_completed(authenticated_client, user, todo):
    """Test completing an already completed todo returns error"""
    todo.is_completed = True
    todo.save()

    url = reverse("todo-complete-todo", args=[todo.id])
    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already completed" in response.data["detail"].lower()


@pytest.mark.django_db
def test_todo_filter_by_completed(authenticated_client, user):
    """Test filtering todos by completion status"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    Todo.objects.create(
        user=user, name="Active Todo", due_date=tomorrow, is_completed=False
    )
    Todo.objects.create(
        user=user, name="Completed Todo", due_date=tomorrow, is_completed=True
    )

    url = reverse("todo-list")
    response = authenticated_client.get(url, {"is_completed": "false"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1  # Only the Active Todo we created


@pytest.mark.django_db
def test_todo_filter_active(authenticated_client, user):
    """Test filtering todos with 'active' filter"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    Todo.objects.create(
        user=user, name="Active Todo", due_date=tomorrow, is_completed=False
    )
    Todo.objects.create(
        user=user, name="Completed Todo", due_date=tomorrow, is_completed=True
    )

    url = reverse("todo-list")
    response = authenticated_client.get(url, {"filter": "active"})
    assert response.status_code == status.HTTP_200_OK
    # Should return only incomplete todos
    for item in response.data:
        assert item["is_completed"] is False


@pytest.mark.django_db
def test_todo_filter_completed(authenticated_client, user):
    """Test filtering todos with 'completed' filter"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    Todo.objects.create(
        user=user, name="Active Todo", due_date=tomorrow, is_completed=False
    )
    Todo.objects.create(
        user=user, name="Completed Todo", due_date=tomorrow, is_completed=True
    )

    url = reverse("todo-list")
    response = authenticated_client.get(url, {"filter": "completed"})
    assert response.status_code == status.HTTP_200_OK
    # Should return only completed todos
    for item in response.data:
        assert item["is_completed"] is True
