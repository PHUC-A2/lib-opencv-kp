from datetime import datetime, time

from django.db.models import Q
from django.utils import timezone

from apps.processing.models import ProcessingHistory, ProcessingJob, ProcessingParameter

# Tham so mac dinh theo tung thuat toan Phase 3/4.
DEFAULT_ALGORITHM_PARAMS: dict[str, dict[str, str]] = {
    "grayscale": {},
    "gaussian_blur": {"kernel_size": "15"},
    "canny": {"threshold1": "100", "threshold2": "200"},
    "binary_threshold": {"threshold": "127"},
    "median_blur": {"kernel_size": "15"},
    "morphology": {"kernel_size": "5", "operation": "MORPH_OPEN"},
    "histogram_equalization": {},
}


class ProcessingHistoryService:
    @staticmethod
    def get_default_params(algorithm_code: str) -> dict[str, str]:
        # Lay bo tham so mac dinh theo code thuat toan.
        return DEFAULT_ALGORITHM_PARAMS.get(algorithm_code, {}).copy()

    @staticmethod
    def save_parameters(job: ProcessingJob, algorithm_code: str, step_order: int | None = None) -> None:
        # Luu tham so xu ly vao bang processing_parameters.
        params = ProcessingHistoryService.get_default_params(algorithm_code)
        for key, value in params.items():
            # Pipeline nhieu buoc co the trung ten tham so -> them prefix theo thu tu buoc.
            if job.is_pipeline and step_order is not None:
                param_key = f"step{step_order}.{key}"
            else:
                param_key = key
            ProcessingParameter.objects.create(
                job=job,
                param_key=param_key,
                param_value=str(value),
            )

    @staticmethod
    def log(job: ProcessingJob, action: str, message: str = "") -> ProcessingHistory:
        # Ghi log hanh dong vao bang processing_history.
        return ProcessingHistory.objects.create(
            job=job,
            action=action,
            message=message,
        )

    @staticmethod
    def get_user_jobs(
        user,
        algorithm_id: int | None = None,
        status: str = "",
        date_from=None,
        date_to=None,
        search: str = "",
    ):
        # Truy van lich su job cua user voi bo loc.
        queryset = (
            ProcessingJob.objects.filter(user=user)
            .select_related("algorithm", "source_image")
            .prefetch_related("processed_image", "history_logs", "pipeline_steps__algorithm")
        )

        if algorithm_id:
            queryset = queryset.filter(
                Q(algorithm_id=algorithm_id) | Q(pipeline_steps__algorithm_id=algorithm_id)
            ).distinct()

        if status:
            queryset = queryset.filter(status=status)

        if date_from:
            # Loc theo múi giờ local (Asia/Ho_Chi_Minh), tranh loi __date voi UTC trong MySQL.
            start_dt = timezone.make_aware(datetime.combine(date_from, time.min))
            queryset = queryset.filter(created_at__gte=start_dt)

        if date_to:
            # Bao gom tron ngay den 23:59:59 theo gio local.
            end_dt = timezone.make_aware(datetime.combine(date_to, time.max))
            queryset = queryset.filter(created_at__lte=end_dt)

        if search:
            queryset = queryset.filter(source_image__original_filename__icontains=search.strip())

        return queryset.order_by("-created_at")
