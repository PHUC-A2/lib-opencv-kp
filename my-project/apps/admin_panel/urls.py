from django.urls import path

from apps.admin_panel import views

app_name = "admin_panel"

urlpatterns = [
    path("", views.admin_home, name="home"),
    path("users/", views.admin_users_view, name="users"),
    path("users/create/", views.admin_user_create_view, name="user_create"),
    path("users/<int:pk>/edit/", views.admin_user_edit_view, name="user_edit"),
    path("users/<int:pk>/delete/", views.admin_user_delete_view, name="user_delete"),
    path("users/<int:pk>/toggle/", views.admin_user_toggle_view, name="user_toggle"),
    path("images/", views.admin_images_view, name="images"),
    path("images/<int:pk>/delete/", views.admin_image_delete_view, name="image_delete"),
    path("algorithms/", views.admin_algorithms_view, name="algorithms"),
    path("algorithms/create/", views.admin_algorithm_create_view, name="algorithm_create"),
    path("algorithms/<int:pk>/edit/", views.admin_algorithm_edit_view, name="algorithm_edit"),
    path("algorithms/<int:pk>/toggle/", views.admin_algorithm_toggle_view, name="algorithm_toggle"),
    path("jobs/", views.admin_jobs_view, name="jobs"),
    path("logs/", views.admin_logs_view, name="logs"),
]
