from django.db import models

# Create your models here.
# accounts/models.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def user_media_upload_to(instance, filename):
    # safe path pattern; keeps uploads organized by user id (not username)
    return f"users/{instance.id}/profile/{filename}"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        Enforce email normalization; raise helpful errors on missing params.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        username = username or email.split("@")[0]
        now = timezone.now()
        extra_fields.setdefault("is_active", True)
        user = self.model(
            email=email, username=username, date_joined=now, **extra_fields
        )
        user.set_password(password)
        # Save within manager to keep atomic behavior in the caller
        user.save(using=self._db)
        return user

    def create_user(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model:
    - UUID primary key (safer for public APIs)
    - email unique & used as USERNAME_FIELD
    - additional profile fields (media-ready)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        _("email address"), unique=True, help_text="Required. Unique."
    )
    name = models.CharField(_("full name"), max_length=150, blank=True)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    profile_image = models.ImageField(
        upload_to=user_media_upload_to, null=True, blank=True
    )
    cover_image = models.ImageField(
        upload_to=user_media_upload_to, null=True, blank=True
    )
    is_private = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # keep the default username field for backward compatibility but authenticate by email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]

    def __str__(self):
        return self.email
