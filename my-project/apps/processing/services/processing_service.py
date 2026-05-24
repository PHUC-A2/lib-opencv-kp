import time

from django.db import transaction
from django.utils import timezone

from apps.algorithms.models import Algorithm
from apps.authentication.models import User
from apps.images.services.image_service import ImageService
from apps.processing.models import ProcessedImage, ProcessingHistory, ProcessingJob
from apps.processing.services.history_service import ProcessingHistoryService
from apps.admin_panel.models import SystemLog
from apps.admin_panel.services.system_log_service import SystemLogService
from services.opencv.exceptions import OpenCVProcessingError
from services.opencv.opencv_service import OpenCVService


class ProcessingServiceError(Exception):
    # Exception rieng cho service xu ly anh.
    pass


class ProcessingService:
    @staticmethod
    def get_active_algorithms():
        # Lay danh sach thuat toan dang hoat dong.
        return Algorithm.objects.filter(is_active=True).order_by("name")

    @staticmethod
    def get_user_job(user: User, job_id: int) -> ProcessingJob:
        # Lay job thuoc ve user; admin duoc xem job cua moi nguoi (tu logs/history).
        queryset = ProcessingJob.objects.select_related(
            "source_image",
            "algorithm",
            "processed_image",
        ).prefetch_related("parameters", "history_logs", "pipeline_steps__algorithm")

        if getattr(user, "role", "") == "admin":
            return queryset.get(pk=job_id)
        return queryset.get(pk=job_id, user=user)

    @staticmethod
    def count_user_jobs(user: User, status: str | None = None) -> int:
        # Dem so job theo trang thai.
        queryset = ProcessingJob.objects.filter(user=user)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.count()

    @staticmethod
    @transaction.atomic
    def run_processing(user: User, image_id: int, algorithm_id: int) -> ProcessingJob:
        # Thuc thi job xu ly anh OpenCV end-to-end.
        try:
            source_image = ImageService.get_user_image(user, image_id)
        except Exception as exc:
            raise ProcessingServiceError("Không tìm thấy ảnh nguồn.") from exc

        try:
            algorithm = Algorithm.objects.get(pk=algorithm_id, is_active=True)
        except Algorithm.DoesNotExist as exc:
            raise ProcessingServiceError("Thuật toán không hợp lệ.") from exc

        job = ProcessingJob.objects.create(
            user=user,
            source_image=source_image,
            algorithm=algorithm,
            job_type=ProcessingJob.JOB_TYPE_SINGLE,
            status=ProcessingJob.STATUS_PROCESSING,
        )

        # Ghi tham so va log bat dau xu ly.
        ProcessingHistoryService.save_parameters(job, algorithm.code)
        ProcessingHistoryService.log(
            job,
            ProcessingHistory.ACTION_STARTED,
            f"Bắt đầu xử lý ảnh {source_image.original_filename} bằng {algorithm.name}",
        )
        SystemLogService.info(
            SystemLog.MODULE_PROCESSING,
            f"Bắt đầu xử lý ảnh {source_image.original_filename} bằng {algorithm.name}",
            user=user,
            job=job,
        )

        started_at = time.perf_counter()

        try:
            input_image = OpenCVService.read_image(source_image.file_path)
            output_image = OpenCVService.run_algorithm(algorithm.code, input_image)

            relative_path = OpenCVService.build_processed_path(user.pk, job.pk)
            saved_path, width, height, file_size = OpenCVService.save_image(output_image, relative_path)
            stored_filename = saved_path.split("/")[-1]

            ProcessedImage.objects.create(
                job=job,
                stored_filename=stored_filename,
                file_path=saved_path,
                file_size=file_size,
                width=width,
                height=height,
                mime_type="image/jpeg",
            )

            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            job.status = ProcessingJob.STATUS_COMPLETED
            job.execution_time_ms = elapsed_ms
            job.completed_at = timezone.now()
            job.save(update_fields=["status", "execution_time_ms", "completed_at", "updated_at"])

            ProcessingHistoryService.log(
                job,
                ProcessingHistory.ACTION_FINISHED,
                f"Hoàn thành trong {elapsed_ms} ms",
            )
            SystemLogService.info(
                SystemLog.MODULE_PROCESSING,
                f"Hoàn thành {algorithm.name} · {source_image.original_filename}",
                user=user,
                job=job,
                execution_time_ms=elapsed_ms,
            )

        except (OpenCVProcessingError, ProcessingServiceError) as exc:
            job.status = ProcessingJob.STATUS_FAILED
            job.error_message = str(exc)
            job.completed_at = timezone.now()
            job.save(update_fields=["status", "error_message", "completed_at", "updated_at"])
            ProcessingHistoryService.log(job, ProcessingHistory.ACTION_ERROR, str(exc))
            SystemLogService.error(
                SystemLog.MODULE_PROCESSING,
                str(exc),
                user=user,
                job=job,
            )
            raise ProcessingServiceError(str(exc)) from exc
        except Exception as exc:
            job.status = ProcessingJob.STATUS_FAILED
            job.error_message = "Xử lý ảnh thất bại. Vui lòng thử lại."
            job.completed_at = timezone.now()
            job.save(update_fields=["status", "error_message", "completed_at", "updated_at"])
            ProcessingHistoryService.log(job, ProcessingHistory.ACTION_ERROR, job.error_message)
            SystemLogService.error(
                SystemLog.MODULE_PROCESSING,
                job.error_message,
                user=user,
                job=job,
            )
            raise ProcessingServiceError("Xử lý ảnh thất bại. Vui lòng thử lại.") from exc

        return job
