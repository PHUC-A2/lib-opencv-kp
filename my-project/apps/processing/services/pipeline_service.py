import time

from django.db import transaction
from django.utils import timezone

from apps.algorithms.models import Algorithm
from apps.authentication.models import User
from apps.images.services.image_service import ImageService
from apps.processing.models import PipelineStep, ProcessedImage, ProcessingHistory, ProcessingJob
from apps.processing.services.history_service import ProcessingHistoryService
from apps.processing.services.processing_service import ProcessingServiceError
from services.opencv.exceptions import OpenCVProcessingError
from services.opencv.opencv_service import OpenCVService
from services.opencv.registry import process_image


class PipelineService:
    @staticmethod
    @transaction.atomic
    def run_pipeline(user: User, image_id: int, algorithm_ids: list[int]) -> ProcessingJob:
        # Chay chuoi thuat toan OpenCV theo thu tu da chon.
        if len(algorithm_ids) < 2:
            raise ProcessingServiceError("Pipeline cần ít nhất 2 thuật toán.")

        try:
            source_image = ImageService.get_user_image(user, image_id)
        except Exception as exc:
            raise ProcessingServiceError("Không tìm thấy ảnh nguồn.") from exc

        algorithms = []
        for algo_id in algorithm_ids:
            try:
                algorithm = Algorithm.objects.get(pk=algo_id, is_active=True)
            except Algorithm.DoesNotExist as exc:
                raise ProcessingServiceError("Thuật toán trong pipeline không hợp lệ.") from exc
            algorithms.append(algorithm)

        job = ProcessingJob.objects.create(
            user=user,
            source_image=source_image,
            algorithm=None,
            job_type=ProcessingJob.JOB_TYPE_PIPELINE,
            status=ProcessingJob.STATUS_PROCESSING,
        )

        step_labels = " → ".join(algo.name for algo in algorithms)
        ProcessingHistoryService.log(
            job,
            ProcessingHistory.ACTION_STARTED,
            f"Bắt đầu pipeline: {step_labels}",
        )

        for order, algorithm in enumerate(algorithms, start=1):
            PipelineStep.objects.create(
                job=job,
                algorithm=algorithm,
                step_order=order,
            )
            ProcessingHistoryService.save_parameters(job, algorithm.code, step_order=order)

        started_at = time.perf_counter()

        try:
            current_image = OpenCVService.read_image(source_image.file_path)

            for algorithm in algorithms:
                current_image = process_image(algorithm.code, current_image)

            relative_path = OpenCVService.build_processed_path(user.pk, job.pk)
            saved_path, width, height, file_size = OpenCVService.save_image(current_image, relative_path)
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
                f"Pipeline hoàn thành trong {elapsed_ms} ms · {step_labels}",
            )

        except (OpenCVProcessingError, ProcessingServiceError) as exc:
            job.status = ProcessingJob.STATUS_FAILED
            job.error_message = str(exc)
            job.completed_at = timezone.now()
            job.save(update_fields=["status", "error_message", "completed_at", "updated_at"])
            ProcessingHistoryService.log(job, ProcessingHistory.ACTION_ERROR, str(exc))
            raise ProcessingServiceError(str(exc)) from exc
        except Exception as exc:
            job.status = ProcessingJob.STATUS_FAILED
            job.error_message = "Pipeline xử lý thất bại. Vui lòng thử lại."
            job.completed_at = timezone.now()
            job.save(update_fields=["status", "error_message", "completed_at", "updated_at"])
            ProcessingHistoryService.log(job, ProcessingHistory.ACTION_ERROR, job.error_message)
            raise ProcessingServiceError("Pipeline xử lý thất bại. Vui lòng thử lại.") from exc

        return job
