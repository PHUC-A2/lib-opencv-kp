from django.contrib import admin

from apps.algorithms.models import Algorithm


@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    # Cau hinh trang admin quan ly thuat toan.
    list_display = ("id", "code", "name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
