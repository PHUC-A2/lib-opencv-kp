from django.contrib import admin

from apps.images.models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    # Cau hinh trang admin quan ly bang images.
    list_display = ("id", "original_filename", "user", "width", "height", "file_size", "created_at")
    list_filter = ("mime_type", "created_at")
    search_fields = ("original_filename", "stored_filename", "user__username")
    readonly_fields = ("created_at", "updated_at")
