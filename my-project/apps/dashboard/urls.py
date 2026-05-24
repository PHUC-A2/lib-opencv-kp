from django.urls import path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("dashboard/", views.dashboard_home, name="home"),
]
