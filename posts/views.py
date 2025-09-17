from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db.models import Prefetch
from .models import Post, PostMedia, Hashtag
from .serializers import PostListSerializer, PostCreateSerializer, HashtagSerializer
from .permissions import IsOwnerOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        Post.objects.select_related("user")
        .prefetch_related(
            Prefetch("media", queryset=PostMedia.objects.order_by("order"))
        )
        .all()
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PostCreateSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"], url_path="explore")
    def explore(self, request):
        qs = self.get_queryset().order_by(
            "-like_count", "-comment_count", "-created_at"
        )
        page = self.paginate_queryset(qs)
        ser = PostListSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(ser.data)


class HashtagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hashtag.objects.all().order_by("-usage_count")
    serializer_class = HashtagSerializer
    permission_classes = [permissions.AllowAny]
