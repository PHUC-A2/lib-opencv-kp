from django.urls import path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    # Trang tong quan chinh.
    path("dashboard/", views.dashboard_home, name="home"),
    # Placeholder Phase 1 - module anh.
    path(
        "images/upload/",
        views.coming_soon_view,
        {
            "page_title": "Tải ảnh lên",
            "page_description": "Khu vực upload ảnh drag & drop sẽ được triển khai ở Phase 2.",
        },
        name="images_upload",
    ),
    path(
        "images/gallery/",
        views.coming_soon_view,
        {
            "page_title": "Thư viện ảnh",
            "page_description": "Thư viện ảnh và preview sẽ được triển khai ở Phase 2.",
        },
        name="images_gallery",
    ),
    # Placeholder Phase 1 - lich su va pipeline xu ly.
    path(
        "processing/history/",
        views.coming_soon_view,
        {
            "page_title": "Lịch sử xử lý",
            "page_description": "Lịch sử các job xử lý ảnh sẽ được triển khai ở Phase 3.",
        },
        name="processing_history",
    ),
    path(
        "processing/pipeline/",
        views.coming_soon_view,
        {
            "page_title": "Pipeline xử lý",
            "page_description": "Pipeline nhiều bước xử lý ảnh sẽ được triển khai ở Phase 4.",
        },
        name="processing_pipeline",
    ),
]
