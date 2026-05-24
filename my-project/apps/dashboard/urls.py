from django.urls import path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("dashboard/", views.dashboard_home, name="home"),
    path(
        "processing/pipeline/",
        views.coming_soon_view,
        {
            "page_title": "Pipeline xử lý",
            "page_description": "Pipeline nhiều bước xử lý ảnh sẽ được triển khai ở Phase 5.",
        },
        name="processing_pipeline",
    ),
]
