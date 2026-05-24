from django.urls import path

from apps.images import views

app_name = "images"

urlpatterns = [
    path("upload/", views.upload_view, name="upload"),
    path("upload/process/", views.upload_process_view, name="upload_process"),
    path("gallery/", views.gallery_view, name="gallery"),
    path("<int:pk>/delete/", views.delete_view, name="delete"),
    path("<int:pk>/download/", views.download_view, name="download"),
]
