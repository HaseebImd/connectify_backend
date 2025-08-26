from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.conf import settings


def post_media_upload_to(instance, filename):
    user_id = getattr(instance.post, "user_id", "anon")
    return f"posts/{user_id}/{filename}"


class Hashtag(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=120, unique=True, db_index=True)
    usage_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"#{self.name}"


class Post(models.Model):
    VIS_PUBLIC = "public"
    VIS_FOLLOWERS = "followers"
    VIS_PRIVATE = "private"
    VIS_CHOICES = [
        (VIS_PUBLIC, "Public"),
        (VIS_FOLLOWERS, "Followers"),
        (VIS_PRIVATE, "Private"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    caption = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    visibility = models.CharField(
        max_length=20, choices=VIS_CHOICES, default=VIS_PUBLIC
    )
    hashtags = models.ManyToManyField(Hashtag, related_name="posts", blank=True)

    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} • {self.caption[:40]}"


class PostMedia(models.Model):
    TYPE_IMAGE = "image"
    TYPE_VIDEO = "video"
    TYPE_CHOICES = [(TYPE_IMAGE, "Image"), (TYPE_VIDEO, "Video")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to=post_media_upload_to)
    media_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    order = models.PositiveSmallIntegerField(default=0)
    thumbnail = models.ImageField(upload_to=post_media_upload_to, null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["post", "order"]
        indexes = [models.Index(fields=["post", "order"])]

    def __str__(self):
        return f"{self.media_type}:{self.id}"
