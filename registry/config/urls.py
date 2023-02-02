from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

V1 = 'v1'

schema = get_schema_view(
    openapi.Info(
        title="Registry API",
        default_version=V1,
        description="Api documentation for Registry.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@x.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        f"api/{V1}/",
        include(
            [
                path(
                    'authentication/',
                    include('authentication.api.base.urls')
                ),
            ]
        )
    ),

    path(
        'docs/',
        schema.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
