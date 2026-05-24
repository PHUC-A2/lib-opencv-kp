from django.conf import settings
from django.db import models


class SystemLog(models.Model):
    # Muc do log he thong.
    LEVEL_DEBUG = "debug"
    LEVEL_INFO = "info"
    LEVEL_WARNING = "warning"
    LEVEL_ERROR = "error"

    LEVEL_CHOICES = [
        (LEVEL_DEBUG, "Debug"),
        (LEVEL_INFO, "Info"),
        (LEVEL_WARNING, "Warning"),
        (LEVEL_ERROR, "Error"),
    ]

    # Module phat sinh log.
    MODULE_PROCESSING = "processing"
    MODULE_PIPELINE = "pipeline"
    MODULE_IMAGES = "images"
    MODULE_AUTH = "auth"
    MODULE_ADMIN = "admin"
    MODULE_SYSTEM = "system"

    MODULE_CHOICES = [
        (MODULE_PROCESSING, "Xử lý ảnh"),
        (MODULE_PIPELINE, "Pipeline"),
        (MODULE_IMAGES, "Ảnh"),
        (MODULE_AUTH, "Xác thực"),
        (MODULE_ADMIN, "Admin"),
        (MODULE_SYSTEM, "Hệ thống"),
    ]

    # Muc do log (debug/info/warning/error).
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=LEVEL_INFO, verbose_name="Muc do")
    # Module phat sinh su kien.
    module = models.CharField(max_length=50, choices=MODULE_CHOICES, default=MODULE_SYSTEM, verbose_name="Module")
    # Noi dung log chi tiet.
    message = models.TextField(verbose_name="Noi dung")
    # Thoi gian thuc thi job (ms) neu co.
    execution_time_ms = models.PositiveIntegerField(null=True, blank=True, verbose_name="Thoi gian (ms)")
    # Nguoi dung lien quan (neu co).
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="system_logs",
        verbose_name="Nguoi dung",
    )
    # Job xu ly anh lien quan (neu co).
    job = models.ForeignKey(
        "processing.ProcessingJob",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="system_logs",
        verbose_name="Processing job",
    )
    # Thoi diem ghi log.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thoi gian")

    class Meta:
        db_table = "system_logs"
        ordering = ["-created_at"]
        verbose_name = "System Log"
        verbose_name_plural = "System Logs"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["level", "module"]),
        ]

    def __str__(self) -> str:
        return f"[{self.level}] {self.module}: {self.message[:60]}"

    @property
    def level_label(self) -> str:
        # Nhan tieng Viet cho UI.
        labels = dict(self.LEVEL_CHOICES)
        return labels.get(self.level, self.level)

    @property
    def module_label(self) -> str:
        # Nhan tieng Viet cho UI.
        labels = dict(self.MODULE_CHOICES)
        return labels.get(self.module, self.module)

    @property
    def level_badge_class(self) -> str:
        # CSS badge theo muc do log.
        mapping = {
            self.LEVEL_DEBUG: "badge-ghost",
            self.LEVEL_INFO: "badge-info",
            self.LEVEL_WARNING: "badge-warning",
            self.LEVEL_ERROR: "badge-error",
        }
        return mapping.get(self.level, "badge-ghost")
