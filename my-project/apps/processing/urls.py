from django.urls import path

from apps.processing import views

app_name = "processing"

urlpatterns = [
    path("", views.processing_home, name="home"),
    path("run/", views.processing_run_view, name="run"),
    path("result/<int:pk>/", views.processing_result_view, name="result"),
    path("history/", views.processing_history_view, name="history"),
    path("pipeline/", views.processing_pipeline_view, name="pipeline"),
    path("pipeline/run/", views.processing_pipeline_run_view, name="pipeline_run"),
]
