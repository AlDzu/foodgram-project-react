"""foodgram URL Configuration"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("api.urls")),
    path(
        "redoc/",
        TemplateView.as_view(
            template_name="redoc.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="redoc",
    ),
    path(
        "redoc/openapi-schema.yml",
        TemplateView.as_view(
            template_name="openapi-schema.yml",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="redoc",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
