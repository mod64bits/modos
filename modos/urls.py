from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from apps.dashboard import urls as dashboard_urls




urlpatterns = [
    path("", TemplateView.as_view(template_name="base/base.html")),
    path("dashboard/", include(dashboard_urls)),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
