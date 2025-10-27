import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_logout_missing_refresh_returns_400(auth_client):
    url = reverse("token_logout")
    resp = auth_client.post(url, {}, format="json")
    assert resp.status_code == 400
    assert "missing refresh token" in str(resp.data).lower()


@pytest.mark.django_db
def test_logout_invalid_refresh_returns_400(auth_client):
    url = reverse("token_logout")
    resp = auth_client.post(url, {"refresh": "not-a-valid-token"}, format="json")
    assert resp.status_code == 400
    assert "invalid token" in str(resp.data).lower()
