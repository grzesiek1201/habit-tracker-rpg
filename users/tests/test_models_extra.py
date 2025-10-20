import pytest
from users.models import User


@pytest.mark.django_db
def test_user_str_returns_username():
    u = User.objects.create_user(username="john", email="john@example.com", password="StrongPass123!")
    assert str(u) == "john"


@pytest.mark.django_db
def test_exp_to_next_level_scales_with_level():
    u = User.objects.create_user(username="lvl", email="lvl@example.com", password="StrongPass123!")
    u.current_level = 3
    assert u.exp_to_next_level() == 300


