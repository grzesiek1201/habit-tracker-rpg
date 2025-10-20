import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, min_length=3, max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate_username(self, value):
        v = value.strip()
        if not re.fullmatch(r"[A-Za-z0-9_\-]+", v):
            raise serializers.ValidationError("Username may contain letters, digits, _ and - only.")
        if User.objects.filter(username__iexact=v).exists():
            raise serializers.ValidationError("Username already in use.")
        return v

    def validate_email(self, value):
        email = value.lower().strip()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already in use.")
        return email

    def validate(self, attrs):
        password = attrs.get("password")
        validate_password(password)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data.get("email")
        if email:
            validated_data["email"] = email.lower().strip()
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "current_hp",
            "max_hp",
            "current_exp",
            "current_level",
            "avatar_picture",
            "estate_bonus_hp",
            "estate_bonus_exp",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ["email", "avatar_picture"]

    def validate_email(self, value):
        if value is None:
            return value
        email = value.lower().strip()
        qs = User.objects.filter(email=email)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email already in use.")
        return email

    def validate_avatar_picture(self, file):
        if not file:
            return file
        max_mb = 2
        if file.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError("Avatar exceeds 2MB.")
        valid_types = {"image/jpeg", "image/png", "image/webp"}
        if getattr(file, "content_type", None) not in valid_types:
            raise serializers.ValidationError("Only JPEG/PNG/WebP are allowed.")
        # Optional deep verification using Pillow
        try:
            from PIL import Image

            file.seek(0)
            img = Image.open(file)
            img.verify()
            if img.format not in {"JPEG", "PNG", "WEBP"}:
                raise serializers.ValidationError("Unsupported image format.")
        except ImportError:
            pass
        except Exception:
            raise serializers.ValidationError("Invalid image file.")
        return file


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["new_password1"] != attrs["new_password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        request = self.context.get("request")
        user = getattr(request, "user", None)
        validate_password(attrs["new_password1"], user=user)
        return attrs
