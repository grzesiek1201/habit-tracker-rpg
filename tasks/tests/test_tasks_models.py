import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from tasks.enums import HabitType, TasksRepeatOn, TasksRepeats, TasksStatus, TasksStrength
from tasks.models import Daily, Habit, Todo

User = get_user_model()


# -----------------------
# Fixtures
# -----------------------
@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="u1", email="u1@example.com", password="StrongPass123!"
    )


@pytest.fixture
def habit(user):
    return Habit.objects.create(
        user=user,
        name="Drink Water",
        notes="Drink 8 glasses of water per day",
        type=HabitType.GOOD,
    )


@pytest.fixture
def daily(user):
    return Daily.objects.create(
        user=user,
        name="Brush teeth",
        notes="Brush teeth twice a day",
        strength=TasksStrength.STABLE,
        repeats=TasksRepeats.DAILY,
        repeat_on=TasksRepeatOn.EVERYDAY,
    )


@pytest.fixture
def todo(user):
    return Todo.objects.create(
        user=user,
        name="Take out the trash",
        notes="Take out the trash before bed",
        due_date=datetime.date.today() + datetime.timedelta(days=1),
    )


# -----------------------
# Habit Tests
# -----------------------
@pytest.mark.django_db
def test_habit_creation(habit, user):
    assert habit.name == "Drink Water"
    assert habit.type == HabitType.GOOD
    assert habit.status == TasksStatus.ACTIVE  # default value
    assert habit.user == user
    assert habit.created_at is not None


@pytest.mark.django_db
def test_habit_str_method(habit):
    assert str(habit) == "Drink Water"


@pytest.mark.django_db
def test_habit_missing_required(user):
    habit = Habit(user=user)
    with pytest.raises(ValidationError):
        habit.full_clean()


# -----------------------
# Daily Tests
# -----------------------
@pytest.mark.django_db
def test_daily_creation(daily, user):
    assert daily.name == "Brush teeth"
    assert daily.notes == "Brush teeth twice a day"
    assert daily.strength == TasksStrength.STABLE
    assert daily.repeats == TasksRepeats.DAILY
    assert daily.repeat_on == TasksRepeatOn.EVERYDAY
    assert daily.user == user
    assert daily.status == TasksStatus.ACTIVE  # default value


@pytest.mark.django_db
def test_daily_missing_required(user):
    daily = Daily(user=user)
    with pytest.raises(ValidationError):
        daily.full_clean()


# -----------------------
# Todo Tests
# -----------------------
@pytest.mark.django_db
def test_todo_creation(todo, user):
    assert todo.name == "Take out the trash"
    assert todo.notes == "Take out the trash before bed"
    assert todo.due_date > datetime.date.today() - datetime.timedelta(days=1)
    assert todo.is_completed is False  # default value
    assert todo.user == user


@pytest.mark.django_db
def test_todo_str_method(todo):
    assert str(todo) == todo.name


@pytest.mark.django_db
def test_todo_due_date_validation(user):
    """Test that a past due_date raises ValidationError"""
    past_date = datetime.date.today() - datetime.timedelta(days=1)
    todo = Todo(user=user, name="Past task", due_date=past_date)
    with pytest.raises(ValidationError):
        todo.full_clean()


@pytest.mark.django_db
def test_todo_is_completed_default(user):
    todo = Todo.objects.create(
        user=user, name="New task", due_date=datetime.date.today() + datetime.timedelta(days=1)
    )
    assert todo.is_completed is False
