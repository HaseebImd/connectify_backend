from rest_framework.routers import DefaultRouter
from .views import PostViewSet, HashtagViewSet

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"hashtags", HashtagViewSet, basename="hashtag")

urlpatterns = router.urls
