from django.conf import settings
from django.db import models


class Image(models.Model):
    # Lien ket anh voi nguoi dung so huu.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Nguoi dung",
    )
    # Ten file goc khi nguoi dung upload.
    original_filename = models.CharField(max_length=255, verbose_name="Ten file goc")
    # Ten file luu tren o cung (unique).
    stored_filename = models.CharField(max_length=255, unique=True, verbose_name="Ten file luu tru")
    # Duong dan tuong doi tu MEDIA_ROOT.
    file_path = models.CharField(max_length=500, verbose_name="Duong dan file")
    # Kich thuoc file tinh bang byte.
    file_size = models.PositiveIntegerField(verbose_name="Kich thuoc (bytes)")
    # Chieu rong anh pixel.
    width = models.PositiveIntegerField(verbose_name="Chieu rong")
    # Chieu cao anh pixel.
    height = models.PositiveIntegerField(verbose_name="Chieu cao")
    # Loai MIME cua file anh.
    mime_type = models.CharField(max_length=100, verbose_name="Loai MIME")
    # Thoi diem upload.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngay tao")
    # Thoi diem cap nhat metadata gan nhat.
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngay cap nhat")

    class Meta:
        db_table = "images"
        ordering = ["-created_at"]
        verbose_name = "Anh"
        verbose_name_plural = "Anh"

    def __str__(self) -> str:
        return self.original_filename

    @property
    def file_size_display(self) -> str:
        # Hien thi kich thuoc file dang doc duoc.
        size = float(self.file_size)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                if unit == "B":
                    return f"{int(size)} {unit}"
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{self.file_size} B"

    @property
    def media_url(self) -> str:
        # Tra ve URL truy cap anh qua Django media.
        return f"/media/{self.file_path}"
