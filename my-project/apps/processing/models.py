from django.conf import settings
from django.db import models
from django.utils import timezone


class ProcessingJob(models.Model):
    # Loai job: xu ly don hoac pipeline nhieu buoc.
    JOB_TYPE_SINGLE = "single"
    JOB_TYPE_PIPELINE = "pipeline"
    JOB_TYPE_CHOICES = [
        (JOB_TYPE_SINGLE, "Xử lý đơn"),
        (JOB_TYPE_PIPELINE, "Luồng xử lý đa bước"),
    ]

    # Trang thai job xu ly anh.
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Chờ xử lý"),
        (STATUS_PROCESSING, "Đang xử lý"),
        (STATUS_COMPLETED, "Hoàn thành"),
        (STATUS_FAILED, "Thất bại"),
    ]

    # Nguoi dung tao job.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="processing_jobs",
        verbose_name="Nguoi dung",
    )
    # Anh nguon can xu ly.
    source_image = models.ForeignKey(
        "images.Image",
        on_delete=models.CASCADE,
        related_name="processing_jobs",
        verbose_name="Anh nguon",
    )
    # Thuat toan duoc chon (null neu la pipeline).
    algorithm = models.ForeignKey(
        "algorithms.Algorithm",
        on_delete=models.PROTECT,
        related_name="processing_jobs",
        verbose_name="Thuat toan",
        null=True,
        blank=True,
    )
    # Loai job xu ly.
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default=JOB_TYPE_SINGLE,
        verbose_name="Loai job",
    )
    # Trang thai xu ly hien tai.
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Trang thai",
    )
    # Thong bao loi neu job that bai.
    error_message = models.TextField(blank=True, verbose_name="Loi")
    # Thoi gian thuc thi tinh bang ms.
    execution_time_ms = models.PositiveIntegerField(null=True, blank=True, verbose_name="Thoi gian (ms)")
    # Thoi diem tao job.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngay tao")
    # Thoi diem cap nhat.
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngay cap nhat")
    # Thoi diem hoan thanh.
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngay hoan thanh")

    class Meta:
        db_table = "processing_jobs"
        ordering = ["-created_at"]
        verbose_name = "Processing Job"
        verbose_name_plural = "Processing Jobs"

    def __str__(self) -> str:
        if self.is_pipeline:
            return f"Pipeline #{self.pk} - {self.status}"
        algo_name = self.algorithm.name if self.algorithm else "N/A"
        return f"Job #{self.pk} - {algo_name} - {self.status}"

    @property
    def is_completed(self) -> bool:
        return self.status == self.STATUS_COMPLETED

    @property
    def is_pipeline(self) -> bool:
        return self.job_type == self.JOB_TYPE_PIPELINE

    def get_display_algorithms(self) -> str:
        # Hien thi ten thuat toan tren UI (don hoac chuoi pipeline).
        if self.is_pipeline:
            steps = self.pipeline_steps.select_related("algorithm").order_by("step_order")
            labels = [f"{step.algorithm.icon} {step.algorithm.name}" for step in steps]
            return " → ".join(labels) if labels else "Luồng xử lý đa bước"
        if self.algorithm:
            return f"{self.algorithm.icon} {self.algorithm.name}"
        return "—"


class ProcessedImage(models.Model):
    # Job tuong ung voi anh ket qua.
    job = models.OneToOneField(
        ProcessingJob,
        on_delete=models.CASCADE,
        related_name="processed_image",
        verbose_name="Processing job",
    )
    # Ten file luu tren SSD.
    stored_filename = models.CharField(max_length=255, unique=True, verbose_name="Ten file luu tru")
    # Duong dan tuong doi tu MEDIA_ROOT.
    file_path = models.CharField(max_length=500, verbose_name="Duong dan file")
    # Kich thuoc file byte.
    file_size = models.PositiveIntegerField(verbose_name="Kich thuoc (bytes)")
    # Chieu rong/cao anh ket qua.
    width = models.PositiveIntegerField(verbose_name="Chieu rong")
    height = models.PositiveIntegerField(verbose_name="Chieu cao")
    # Loai MIME file ket qua.
    mime_type = models.CharField(max_length=100, default="image/jpeg", verbose_name="Loai MIME")
    # Thoi diem luu ket qua.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngay tao")

    class Meta:
        db_table = "processed_images"
        ordering = ["-created_at"]
        verbose_name = "Anh da xu ly"
        verbose_name_plural = "Anh da xu ly"

    def __str__(self) -> str:
        return self.stored_filename

    @property
    def media_url(self) -> str:
        return f"/media/{self.file_path}"


class ProcessingParameter(models.Model):
    # Job tuong ung voi tham so da su dung.
    job = models.ForeignKey(
        ProcessingJob,
        on_delete=models.CASCADE,
        related_name="parameters",
        verbose_name="Processing job",
    )
    # Ten tham so (vi du: kernel_size, threshold1).
    param_key = models.CharField(max_length=100, verbose_name="Ten tham so")
    # Gia tri tham so dang chuoi de luu DB don gian.
    param_value = models.CharField(max_length=255, verbose_name="Gia tri")

    class Meta:
        db_table = "processing_parameters"
        verbose_name = "Processing Parameter"
        verbose_name_plural = "Processing Parameters"
        unique_together = [["job", "param_key"]]

    def __str__(self) -> str:
        return f"{self.param_key}={self.param_value}"


class ProcessingHistory(models.Model):
    # Hanh dong ghi log trong qua trinh xu ly.
    ACTION_STARTED = "started"
    ACTION_FINISHED = "finished"
    ACTION_ERROR = "error"

    ACTION_CHOICES = [
        (ACTION_STARTED, "Bat dau"),
        (ACTION_FINISHED, "Hoan thanh"),
        (ACTION_ERROR, "Loi"),
    ]

    # Job lien quan den log.
    job = models.ForeignKey(
        ProcessingJob,
        on_delete=models.CASCADE,
        related_name="history_logs",
        verbose_name="Processing job",
    )
    # Loai hanh dong (started/finished/error).
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Hanh dong")
    # Mo ta chi tiet su kien.
    message = models.TextField(blank=True, verbose_name="Noi dung")
    # Thoi diem ghi log.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thoi gian")

    class Meta:
        db_table = "processing_history"
        ordering = ["-created_at"]
        verbose_name = "Processing History"
        verbose_name_plural = "Processing History"

    def __str__(self) -> str:
        return f"{self.job_id} - {self.action}"

    @property
    def action_label(self) -> str:
        # Nhan tieng Viet cho UI.
        labels = {
            self.ACTION_STARTED: "Bắt đầu",
            self.ACTION_FINISHED: "Hoàn thành",
            self.ACTION_ERROR: "Lỗi",
        }
        return labels.get(self.action, self.action)


class PipelineStep(models.Model):
    # Mot buoc trong pipeline xu ly nhieu thuat toan.
    job = models.ForeignKey(
        ProcessingJob,
        on_delete=models.CASCADE,
        related_name="pipeline_steps",
        verbose_name="Processing job",
    )
    # Thuat toan cua buoc nay.
    algorithm = models.ForeignKey(
        "algorithms.Algorithm",
        on_delete=models.PROTECT,
        related_name="pipeline_steps",
        verbose_name="Thuat toan",
    )
    # Thu tu thuc thi (bat dau tu 1).
    step_order = models.PositiveIntegerField(verbose_name="Thu tu buoc")

    class Meta:
        db_table = "pipeline_steps"
        ordering = ["step_order"]
        verbose_name = "Pipeline Step"
        verbose_name_plural = "Pipeline Steps"
        unique_together = [["job", "step_order"]]

    def __str__(self) -> str:
        return f"Bước {self.step_order}: {self.algorithm.name}"
