from django.urls import path

from apps.authentication import views

app_name = "authentication"

urlpatterns = [
    path("dang-ky/", views.register_view, name="register"),
    path("dang-nhap/", views.login_view, name="login"),
    path("dang-xuat/", views.logout_view, name="logout"),
]
