from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from apps.dashboard import views as dashboard_views


def home_entry_view(request):
    # Trang "/" — guest xem truoc UI, user da dang nhap vao dashboard.
    return dashboard_views.public_landing_view(request)


urlpatterns = [
    path("", home_entry_view, name="home"),
    path("", include("apps.authentication.urls")),
    path("", include("apps.dashboard.urls")),
    path("images/", include("apps.images.urls")),
    path("processing/", include("apps.processing.urls")),
    path("admin-panel/", include("apps.admin_panel.urls")),
    path("admin/", admin.site.urls),
]

# Chi phuc vu media local khi chay development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
