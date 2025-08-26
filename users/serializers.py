# accounts/serializers.py
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Representation returned to clients. Keep minimal safe fields.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "name",
            "bio",
            "profile_image",
            "cover_image",
            "is_verified",
            "is_private",
            "date_joined",
            "location",
            "website",
        )
        read_only_fields = ("id", "is_verified")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "password",
            "password2",
            "name",
            "bio",
            "profile_image",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"username": {"required": True}}

    def validate_email(self, value):
        # Normalize email + extra validation if needed
        return User.objects.normalize_email(value)

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError(
                {"password": "The two password fields didn't match."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        # Use manager to create user (ensures consistent behavior)
        user = User.objects.create_user(password=password, **validated_data)
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customize token claims to include useful user details in the access token.
    Keep claims small — do NOT include secrets.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["email"] = user.email
        token["username"] = user.username
        token["user_id"] = str(user.id)
        token["is_verified"] = user.is_verified
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # include user data in response besides tokens
        data["user"] = UserSerializer(self.user).data
        return data
