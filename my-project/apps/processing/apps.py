from django.apps import AppConfig


class ProcessingConfig(AppConfig):
    # Khai báo kiểu primary key mặc định cho model.
    default_auto_field = "django.db.models.BigAutoField"
    # Tên đầy đủ của app để Django nhận diện đúng package.
    name = "apps.processing"
    # Tên hiển thị trong admin/site map nội bộ.
    verbose_name = "Xu ly anh"
