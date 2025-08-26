from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, PostMedia, Hashtag

User = get_user_model()


class UserMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "name", "profile_image")


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = (
            "id",
            "media_type",
            "file",
            "order",
            "thumbnail",
            "duration_seconds",
            "width",
            "height",
        )


class PostListSerializer(serializers.ModelSerializer):
    user = UserMinSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)
    hashtags = serializers.SlugRelatedField(
        slug_field="name", many=True, read_only=True
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "caption",
            "location",
            "visibility",
            "like_count",
            "comment_count",
            "view_count",
            "is_edited",
            "created_at",
            "updated_at",
            "media",
            "hashtags",
        )


class PostCreateSerializer(serializers.Serializer):
    caption = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(
        choices=Post.VIS_CHOICES, default=Post.VIS_PUBLIC
    )
    files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False), required=False
    )
    types = serializers.ListField(
        child=serializers.ChoiceField(choices=[("image", "image"), ("video", "video")]),
        required=False,
    )

    def validate(self, attrs):
        files = attrs.get("files") or []
        types = attrs.get("types") or []
        if files and len(files) != len(types):
            raise serializers.ValidationError(
                {"files": "files and types length must match"}
            )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        files = validated_data.pop("files", [])
        types = validated_data.pop("types", [])
        payload = []
        for idx, f in enumerate(files):
            payload.append({"file": f, "media_type": types[idx], "order": idx})
        from .services import create_post_with_media

        return create_post_with_media(user=user, files=payload, **validated_data)


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name", "usage_count")
