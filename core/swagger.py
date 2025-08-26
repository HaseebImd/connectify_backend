from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Connectify API",
        default_version="v1",
        description="A social media platform API for connecting people through posts and interactions",
        terms_of_service="https://www.connectify.com/terms/",
        contact=openapi.Contact(email="support@connectify.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)
