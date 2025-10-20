import io
import sys
import types
from unittest import mock
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers

from users.serializers import (
    ChangePasswordSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from users.models import User


@pytest.mark.django_db
def test_user_create_serializer_normalizes_email_and_creates_user():
    data = {
        "username": "John_Doe",
        "email": "John@Example.COM ",
        "password": "StrongPass123!",
    }
    ser = UserCreateSerializer(data=data)
    assert ser.is_valid(), ser.errors
    user = ser.save()
    assert user.email == "john@example.com"
    assert user.check_password("StrongPass123!")


@pytest.mark.django_db
def test_user_update_serializer_rejects_duplicate_email(user_factory):
    user_factory(username="u1", email="u1@example.com")
    u2 = user_factory(username="u2", email="u2@example.com")
    ser = UserUpdateSerializer(
        instance=u2, data={"email": "U1@EXAMPLE.com"}, partial=True
    )
    assert not ser.is_valid()
    assert "Email already in use." in str(ser.errors)


@pytest.mark.django_db
def test_user_update_serializer_accepts_valid_avatar(user_factory, image_file_jpeg):
    user = user_factory()
    ser = UserUpdateSerializer(
        instance=user, data={"avatar_picture": image_file_jpeg}, partial=True
    )
    assert ser.is_valid(), ser.errors
    inst = ser.save()
    assert inst.avatar_picture.name.startswith("avatars/")


@pytest.mark.django_db
def test_user_update_serializer_rejects_big_file(user_factory, big_image_png):
    user = user_factory()
    ser = UserUpdateSerializer(
        instance=user, data={"avatar_picture": big_image_png}, partial=True
    )
    assert not ser.is_valid()
    assert "Avatar exceeds 2MB." in str(ser.errors)


def test_change_password_serializer_mismatch():
    data = {
        "old_password": "x",
        "new_password1": "abcdefgh",
        "new_password2": "ijklmnop",
    }
    ser = ChangePasswordSerializer(
        data=data, context={"request": type("R", (), {"user": None})}
    )
    assert not ser.is_valid()
    assert "Passwords do not match." in str(ser.errors)


@pytest.mark.django_db
def test_user_create_serializer_username_already_exists(user_factory):
    """Test case-insensitive username validation - covers line 23"""
    user_factory(username="existing", email="e@ex.com")
    data = {"username": "Existing", "email": "a@b.com", "password": "password123"}
    ser = UserCreateSerializer(data=data)
    assert not ser.is_valid()
    assert "Username already in use." in str(ser.errors["username"])


@pytest.mark.django_db
def test_user_create_serializer_email_already_exists(user_factory):
    """Test case-insensitive email validation - covers line 29"""
    user_factory(username="u1", email="test@example.com")
    data = {"username": "newu", "email": "TEST@example.com", "password": "password123"}
    ser = UserCreateSerializer(data=data)
    assert not ser.is_valid()
    assert "Email already in use." in str(ser.errors["email"])


@pytest.mark.django_db
def test_user_create_serializer_create_method_with_email(user_factory):
    """Test create method email lowercasing - covers lines 40-42"""
    data = {
        "username": "newuser",
        "email": "CAPS@EXAMPLE.COM",
        "password": "StrongPass123!",
    }
    ser = UserCreateSerializer(data=data)
    assert ser.is_valid(), f"Serializer errors: {ser.errors}"
    user = ser.save()
    assert user.email == "caps@example.com"


def test_user_update_serializer_validate_email_none():
    """Test email validation with None value - covers line 73"""
    user = User(username="test", email="test@test.com", pk=1)
    ser = UserUpdateSerializer(instance=user)
    result = ser.validate_email(None)
    assert result is None


@pytest.mark.django_db
def test_user_update_serializer_validate_email_exclude_self(user_factory):
    """Test email validation excludes current user - covers lines 76-78"""
    u1 = user_factory(username="user1", email="u1@example.com")
    u2 = user_factory(username="user2", email="u2@example.com")

    ser = UserUpdateSerializer(instance=u1)
    # Should allow same user's email
    result = ser.validate_email("u1@example.com")
    assert result == "u1@example.com"

    # Should reject different user's email
    with pytest.raises(serializers.ValidationError):
        ser.validate_email("u2@example.com")


def test_user_update_serializer_validate_avatar_none():
    """Test avatar validation with None/empty file - covers line 80"""
    ser = UserUpdateSerializer()
    result = ser.validate_avatar_picture(None)
    assert result is None

    result = ser.validate_avatar_picture("")
    assert result == ""


def test_user_update_serializer_validate_avatar_wrong_content_type():
    """Test avatar validation with wrong content type - covers line 84"""
    ser = UserUpdateSerializer()
    fake_file = SimpleUploadedFile("test.gif", b"fake", content_type="image/gif")

    with pytest.raises(serializers.ValidationError) as exc_info:
        ser.validate_avatar_picture(fake_file)
    assert "Only JPEG/PNG/WebP are allowed." in str(exc_info.value)


def test_user_update_serializer_validate_avatar_missing_pil():
    """Test avatar validation when PIL is not available - covers ImportError path"""
    ser = UserUpdateSerializer()
    fake_file = SimpleUploadedFile("test.jpg", b"fake", content_type="image/jpeg")

    # Mock PIL to not be available (ImportError)
    with mock.patch.dict(sys.modules, {"PIL": None}):
        # Should not raise since ImportError is caught and passed
        result = ser.validate_avatar_picture(fake_file)
        assert result == fake_file


def test_user_update_serializer_validate_avatar_corrupted_image():
    """Test avatar validation with actual corrupted image data - covers exception path"""
    ser = UserUpdateSerializer()
    # Create a file with invalid image data that will cause PIL to raise an exception
    fake_file = SimpleUploadedFile(
        "test.jpg",
        b"not-a-valid-image-definitely-will-cause-pil-to-fail",
        content_type="image/jpeg",
    )

    # PIL should raise an exception when trying to open this invalid data
    with pytest.raises(serializers.ValidationError) as exc_info:
        ser.validate_avatar_picture(fake_file)
    assert "Invalid image file." in str(exc_info.value)
