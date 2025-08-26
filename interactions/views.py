from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from posts.models import Post
from .models import Comment, PostLike, Follow
from .serializers import CommentSerializer, LikeStatusSerializer
from .services import toggle_like, add_comment, delete_comment


class CommentViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.request.query_params.get("post")
        qs = (
            Comment.objects.select_related("user")
            .filter(post_id=post_id, is_deleted=False)
            .order_by("created_at")
        )
        return qs

    def perform_create(self, serializer):
        post_id = self.request.data.get("post")
        content = self.request.data.get("content", "")
        parent_id = self.request.data.get("parent", None)
        comment = add_comment(
            user=self.request.user,
            post_id=post_id,
            content=content,
            parent_id=parent_id,
        )
        # re-serialize created object
        serializer.instance = comment

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_comment(user=request.user, comment_id=instance.id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostLikeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        liked = toggle_like(user=request.user, post_id=pk)
        return Response(
            LikeStatusSerializer({"liked": liked}).data, status=status.HTTP_200_OK
        )


class FollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="toggle")
    def toggle_follow(self, request, pk=None):
        # pk = target user id
        if str(request.user.id) == str(pk):
            return Response({"detail": "Cannot follow yourself."}, status=400)
        obj, created = Follow.objects.get_or_create(
            follower=request.user, following_id=pk
        )
        if not created:
            obj.delete()
            return Response({"following": False}, status=200)
        return Response({"following": True, "accepted": obj.accepted}, status=201)
