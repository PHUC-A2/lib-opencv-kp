from django.db import models


class Algorithm(models.Model):
    # Ma code dung de goi handler OpenCV.
    code = models.CharField(max_length=50, unique=True, verbose_name="Ma thuat toan")
    # Ten hien thi tieng Viet tren UI.
    name = models.CharField(max_length=100, verbose_name="Ten thuat toan")
    # Mo ta ngan ve tac dung thuat toan.
    description = models.TextField(blank=True, verbose_name="Mo ta")
    # Icon emoji hien thi tren card UI.
    icon = models.CharField(max_length=10, default="⚙️", verbose_name="Icon")
    # Cho phep bat/tat thuat toan tren he thong.
    is_active = models.BooleanField(default=True, verbose_name="Dang hoat dong")
    # Thoi diem tao ban ghi.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngay tao")
    # Thoi diem cap nhat gan nhat.
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngay cap nhat")

    class Meta:
        db_table = "algorithms"
        ordering = ["name"]
        verbose_name = "Thuat toan"
        verbose_name_plural = "Thuat toan"

    def __str__(self) -> str:
        return self.name
