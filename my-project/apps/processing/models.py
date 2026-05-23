from django.db import models


class ProcessingTask(models.Model):
    # Lưu tên tác vụ để theo dõi lịch sử xử lý ảnh cơ bản.
    task_name = models.CharField(max_length=100)
    # Lưu trạng thái tác vụ (pending/running/success/failed).
    status = models.CharField(max_length=20, default="pending")
    # Lưu thời điểm tạo tác vụ phục vụ truy vết.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Đặt tên bảng tường minh để đồng bộ convention DB.
        db_table = "processing_tasks"
        # Sắp xếp mới nhất trước để dễ quan sát.
        ordering = ["-created_at"]

    def __str__(self) -> str:
        # Chuỗi hiển thị ngắn gọn khi debug/admin.
        return f"{self.task_name} - {self.status}"
