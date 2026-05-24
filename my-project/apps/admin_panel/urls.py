from django.urls import path

from apps.admin_panel import views

app_name = "admin_panel"

urlpatterns = [
    path("", views.admin_home, name="home"),
    path(
        "users/",
        views.admin_placeholder,
        {"page_title": "Quản lý người dùng", "page_description": "Quản lý user sẽ được triển khai ở Phase 5."},
        name="users",
    ),
    path(
        "images/",
        views.admin_placeholder,
        {"page_title": "Quản lý ảnh hệ thống", "page_description": "Quản lý ảnh toàn hệ thống sẽ được triển khai ở Phase 5."},
        name="images",
    ),
    path(
        "algorithms/",
        views.admin_placeholder,
        {"page_title": "Quản lý thuật toán", "page_description": "Cấu hình thuật toán OpenCV sẽ được triển khai ở Phase 5."},
        name="algorithms",
    ),
    path(
        "jobs/",
        views.admin_placeholder,
        {"page_title": "Processing Jobs", "page_description": "Giám sát job xử lý sẽ được triển khai ở Phase 5."},
        name="jobs",
    ),
    path(
        "logs/",
        views.admin_placeholder,
        {"page_title": "System Logs", "page_description": "Nhật ký hệ thống sẽ được triển khai ở Phase 5."},
        name="logs",
    ),
]
