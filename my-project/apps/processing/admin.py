from django.contrib import admin

from apps.processing.models import ProcessingTask


# Đăng ký model để kiểm tra dữ liệu nhanh trong Django Admin.
@admin.register(ProcessingTask)
class ProcessingTaskAdmin(admin.ModelAdmin):
    # Hiển thị các cột quan trọng khi quản trị.
    list_display = ("id", "task_name", "status", "created_at")
    # Hỗ trợ lọc theo trạng thái để theo dõi tiến trình.
    list_filter = ("status",)
    # Hỗ trợ tìm nhanh theo tên tác vụ.
    search_fields = ("task_name",)
