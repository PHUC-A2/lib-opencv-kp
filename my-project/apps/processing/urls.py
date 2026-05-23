from django.urls import path

from apps.processing.views import processing_home

app_name = "processing"

urlpatterns = [
    # Route gốc của module processing.
    path("", processing_home, name="home"),
]
