import io
import os

import django
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "habit_tracker_rpg.settings")
django.setup()

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from rest_framework.test import APIClient  # noqa: E402


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(django_user_model):
    def create_user(**kwargs):
        defaults = {
            "username": "user",
            "email": "user@example.com",
            "password": "StrongPass123!",
        }
        defaults.update(kwargs)
        return django_user_model.objects.create_user(
            username=defaults["username"],
            email=defaults["email"],
            password=defaults["password"],
        )

    return create_user


def _pil_png_file(name="avatar.png", size=(16, 16)):
    buf = io.BytesIO()
    img = Image.new("RGB", size, (255, 0, 0))
    img.save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


def _pil_jpeg_file(name="avatar.jpg", size=(32, 32)):
    buf = io.BytesIO()
    img = Image.new("RGB", size, (0, 128, 255))
    img.save(buf, format="JPEG", quality=90)
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/jpeg")


@pytest.fixture
def image_file_jpeg():
    return _pil_jpeg_file()


@pytest.fixture
def big_image_png():
    # Generate a large noisy PNG (>2MB). ImageField accepts it; our size check should reject it.
    rng = np.random.default_rng(42)
    arr = rng.integers(0, 256, size=(2000, 2000, 3), dtype=np.uint8)
    img = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    assert len(data) > 2_000_000
    return SimpleUploadedFile("big.png", data, content_type="image/png")


@pytest.fixture
def auth_tokens(api_client, user_factory):
    user_factory(username="authuser", email="auth@example.com")
    url = reverse("token_obtain_pair")
    resp = api_client.post(
        url,
        {"username": "authuser", "password": "StrongPass123!"},
        format="json",
    )
    assert resp.status_code == 200
    return {"access": resp.data["access"], "refresh": resp.data["refresh"]}


@pytest.fixture
def auth_client(api_client, auth_tokens):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_tokens['access']}")
    return api_client
