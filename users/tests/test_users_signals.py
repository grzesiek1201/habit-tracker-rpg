import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_previous_login_updated_on_login(client):
    User = get_user_model()
    user = User.objects.create_user(
        username="siguser", email="sig@example.com", password="StrongPass123!"
    )

    assert user.previous_login is None
    logged = client.login(username="siguser", password="StrongPass123!")
    assert logged is True

    user.refresh_from_db()
    assert user.last_login is not None
    assert user.previous_login is not None
