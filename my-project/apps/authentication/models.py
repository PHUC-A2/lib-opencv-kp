from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Email bat buoc va duy nhat theo thiet ke bang users.
    email = models.EmailField(unique=True, verbose_name="Email")
    # Luu ho va ten nguoi dung theo thiet ke bang users.
    full_name = models.CharField(max_length=100, blank=True, verbose_name="Họ và tên")
    # Luu duong dan avatar tren SSD/file system.
    avatar_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="Avatar")
    # Phan quyen tai khoan: admin hoac user.
    role = models.CharField(max_length=20, default="user", verbose_name="Vai tro")
    # Thoi diem tao tai khoan.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngay tao")
    # Thoi diem cap nhat gan nhat.
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngay cap nhat")

    class Meta:
        # Dat ten bang dung theo tai lieu pt-db.md.
        db_table = "users"
        verbose_name = "Nguoi dung"
        verbose_name_plural = "Nguoi dung"

    def __str__(self) -> str:
        # Hien thi username khi debug/admin.
        return self.username
