"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


def home_redirect(request):
    # Chuyen huong trang chu theo trang thai dang nhap.
    if request.user.is_authenticated:
        return redirect("processing:home")
    return redirect("authentication:login")


urlpatterns = [
    path("", home_redirect, name="home"),
    path("auth/", include("apps.authentication.urls")),
    path("processing/", include("apps.processing.urls")),
    path("admin/", admin.site.urls),
]

# Chi phuc vu media local khi chay development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
