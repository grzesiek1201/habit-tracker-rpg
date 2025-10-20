import pytest

from users.serializers import UserCreateSerializer, UserUpdateSerializer


@pytest.mark.django_db
def test_user_create_serializer_invalid_username_characters():
    data = {"username": "bad name", "email": "x@example.com", "password": "StrongPass123!"}
    ser = UserCreateSerializer(data=data)
    assert not ser.is_valid()
    assert "Username may contain" in str(ser.errors)


@pytest.mark.django_db
def test_user_update_serializer_avatar_invalid_mime(user_factory):
    user = user_factory()
    from django.core.files.uploadedfile import SimpleUploadedFile

    bad_file = SimpleUploadedFile("doc.pdf", b"not-an-image", content_type="application/pdf")
    ser = UserUpdateSerializer(instance=user, data={"avatar_picture": bad_file}, partial=True)
    assert not ser.is_valid()
    msg = str(ser.errors)
    assert (
        "Only JPEG/PNG/WebP" in msg
        or "Upload a valid image" in msg
        or "invalid image" in msg.lower()
    )
