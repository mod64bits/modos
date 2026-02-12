from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from apps.dashboard import urls as dashboard_urls
from apps.orders import urls as chamados_urls
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView


urlpatterns = [
    # path("", TemplateView.as_view(template_name="base/base.html")),
    path("", include(dashboard_urls)),
    path("chamados", include(chamados_urls)),
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
