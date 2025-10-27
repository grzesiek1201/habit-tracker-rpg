import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_register_creates_user(api_client):
    url = reverse("user-register")
    payload = {"username": "john_doe", "email": "john@example.com", "password": "StrongPass123!"}
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 201
    assert resp.data["id"]


@pytest.mark.django_db
def test_login_returns_tokens(api_client, user_factory):
    user_factory(username="john", email="john@example.com")
    url = reverse("token_obtain_pair")
    resp = api_client.post(url, {"username": "john", "password": "StrongPass123!"}, format="json")
    assert resp.status_code == 200
    assert "access" in resp.data and "refresh" in resp.data


@pytest.mark.django_db
def test_refresh_returns_new_tokens(api_client, auth_tokens):
    url = reverse("token_refresh")
    resp = api_client.post(url, {"refresh": auth_tokens["refresh"]}, format="json")
    assert resp.status_code == 200
    assert "access" in resp.data


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    url = reverse("user-me")
    resp = api_client.get(url)
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_me_returns_profile(auth_client):
    url = reverse("user-me")
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert {"id", "username", "current_hp", "max_hp", "current_level"}.issubset(resp.data.keys())


@pytest.mark.django_db
def test_profile_update_email_collision(auth_client, user_factory):
    user_factory(username="other", email="other@example.com")
    url = reverse("user-update")
    resp = auth_client.patch(url, {"email": "OTHER@example.com"}, format="multipart")
    assert resp.status_code == 400
    assert "Email already in use." in str(resp.data)


@pytest.mark.django_db
def test_profile_update_avatar(auth_client, image_file_jpeg):
    url = reverse("user-update")
    resp = auth_client.patch(url, {"avatar_picture": image_file_jpeg}, format="multipart")
    assert resp.status_code == 200
    assert resp.data["avatar_picture"]


@pytest.mark.django_db
def test_change_password_flow_invalid_old(auth_client):
    url = reverse("change-password")
    payload = {
        "old_password": "Wrong!",
        "new_password1": "NewStrongPass123!",
        "new_password2": "NewStrongPass123!",
    }
    resp = auth_client.post(url, payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_change_password_flow_success(auth_client, api_client, auth_tokens):
    url = reverse("change-password")
    payload = {
        "old_password": "StrongPass123!",
        "new_password1": "NewStrongPass123!",
        "new_password2": "NewStrongPass123!",
    }
    resp = auth_client.post(url, payload, format="json")
    assert resp.status_code == 204

    refresh_url = reverse("token_refresh")
    bad = api_client.post(refresh_url, {"refresh": auth_tokens["refresh"]}, format="json")
    assert bad.status_code in (401, 400)


@pytest.mark.django_db
def test_logout_blacklists_refresh(auth_client, auth_tokens):
    url = reverse("token_logout")
    resp = auth_client.post(url, {"refresh": auth_tokens["refresh"]}, format="json")
    assert resp.status_code in (205, 200)
