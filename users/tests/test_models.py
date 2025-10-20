import pytest
from django.core.exceptions import ValidationError
from users.models import User


@pytest.mark.django_db
def test_user_hp_cannot_exceed_max():
    u = User.objects.create_user(username="u1", email="u1@example.com", password="StrongPass123!")
    u.max_hp = 10
    u.current_hp = 11
    with pytest.raises(ValidationError):
        u.save()


@pytest.mark.django_db
def test_gain_exp_levels_up_and_heals():
    u = User.objects.create_user(username="u2", email="u2@example.com", password="StrongPass123!")
    u.current_exp = 95
    u.current_level = 1
    u.max_hp = 10
    u.current_hp = 3

    u.gain_exp(110)
    u.refresh_from_db()

    assert u.current_level >= 2
    assert u.current_hp == u.max_hp
    assert u.current_exp < u.exp_to_next_level()


