from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Comment, PostLike

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "post",
            "user",
            "parent",
            "content",
            "is_deleted",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "is_deleted", "created_at", "updated_at")

    def get_user(self, obj):
        return {
            "id": str(obj.user_id),
            "username": obj.user.username,
            "name": obj.user.name,
        }


class LikeStatusSerializer(serializers.Serializer):
    liked = serializers.BooleanField()
