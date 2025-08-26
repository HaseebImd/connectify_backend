from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, PostLikeViewSet, FollowViewSet

router = DefaultRouter()
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"likes", PostLikeViewSet, basename="like")
router.register(r"follows", FollowViewSet, basename="follow")

urlpatterns = router.urls
