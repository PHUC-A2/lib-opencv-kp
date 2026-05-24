from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


def home_redirect(request):
    # Chuyen huong trang chu theo trang thai dang nhap.
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return redirect("authentication:login")


urlpatterns = [
    path("", home_redirect, name="home"),
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
