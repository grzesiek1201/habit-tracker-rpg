import pytest

from users.serializers import ChangePasswordSerializer, UserCreateSerializer, UserUpdateSerializer


@pytest.mark.django_db
def test_user_create_serializer_normalizes_email_and_creates_user():
    data = {"username": "John_Doe", "email": "John@Example.COM ", "password": "StrongPass123!"}
    ser = UserCreateSerializer(data=data)
    assert ser.is_valid(), ser.errors
    user = ser.save()
    assert user.email == "john@example.com"
    assert user.check_password("StrongPass123!")


@pytest.mark.django_db
def test_user_update_serializer_rejects_duplicate_email(user_factory):
    user_factory(username="u1", email="u1@example.com")
    u2 = user_factory(username="u2", email="u2@example.com")
    ser = UserUpdateSerializer(instance=u2, data={"email": "U1@EXAMPLE.com"}, partial=True)
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
    ser = UserUpdateSerializer(instance=user, data={"avatar_picture": big_image_png}, partial=True)
    assert not ser.is_valid()
    assert "Avatar exceeds 2MB." in str(ser.errors)


def test_change_password_serializer_mismatch():
    data = {"old_password": "x", "new_password1": "abcdefgh", "new_password2": "ijklmnop"}
    ser = ChangePasswordSerializer(data=data, context={"request": type("R", (), {"user": None})})
    assert not ser.is_valid()
    assert "Passwords do not match." in str(ser.errors)
