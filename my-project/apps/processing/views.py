from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from apps.images.services.image_service import ImageService
from apps.processing.forms import HistoryFilterForm, PipelineRunForm, ProcessingRunForm
from apps.processing.models import ProcessingJob
from apps.processing.services.history_service import ProcessingHistoryService
from apps.processing.services.pipeline_service import PipelineService
from apps.processing.services.processing_service import ProcessingService, ProcessingServiceError


@login_required
def processing_home(request: HttpRequest) -> HttpResponse:
    # Trang chon anh + thuat toan de xu ly OpenCV.
    user_images = ImageService.get_user_images(request.user)
    algorithms = ProcessingService.get_active_algorithms()
    recent_jobs = (
        ProcessingJob.objects.filter(user=request.user, status=ProcessingJob.STATUS_COMPLETED)
        .select_related("algorithm", "source_image", "processed_image")[:6]
    )

    return render(
        request,
        "processing/index.html",
        {
            "page_title": "Xử lý ảnh",
            "page_subtitle": "Chọn ảnh và thuật toán OpenCV",
            "user_images": user_images,
            "algorithms": algorithms,
            "recent_jobs": recent_jobs,
            "form": ProcessingRunForm(),
        },
    )


@login_required
@csrf_protect
@require_POST
def processing_run_view(request: HttpRequest) -> HttpResponse:
    # Thuc thi xu ly anh qua HTMX.
    form = ProcessingRunForm(request.POST)

    if not form.is_valid():
        first_error = next(iter(form.errors.values()))[0]
        return render(
            request,
            "processing/partials/process_error.html",
            {"message": first_error},
            status=400,
        )

    try:
        job = ProcessingService.run_processing(
            request.user,
            form.cleaned_data["image_id"],
            form.cleaned_data["algorithm_id"],
        )
    except ProcessingServiceError as exc:
        return render(
            request,
            "processing/partials/process_error.html",
            {"message": str(exc)},
            status=400,
        )

    # Tai lai job kem anh ket qua de partial hien thi dung URL media.
    job = ProcessingService.get_user_job(request.user, job.pk)

    return render(
        request,
        "processing/partials/process_result.html",
        {"job": job},
    )


@login_required
def processing_result_view(request: HttpRequest, pk: int) -> HttpResponse:
    # Trang xem ket qua Before/After.
    try:
        job = ProcessingService.get_user_job(request.user, pk)
    except ProcessingJob.DoesNotExist as exc:
        raise Http404("Không tìm thấy kết quả xử lý.") from exc

    if job.status != ProcessingJob.STATUS_COMPLETED:
        return redirect("processing:home")

    try:
        job.processed_image
    except ObjectDoesNotExist:
        return redirect("processing:home")

    return render(
        request,
        "processing/result.html",
        {
            "page_title": "Kết quả xử lý",
            "page_subtitle": f"{job.get_display_algorithms()} · {job.source_image.original_filename}",
            "job": job,
        },
    )


@login_required
def processing_download_view(request: HttpRequest, pk: int) -> HttpResponse:
    # Tai anh ket qua xu ly ve may client.
    try:
        job = ProcessingService.get_user_job(request.user, pk)
    except ProcessingJob.DoesNotExist as exc:
        raise Http404("Không tìm thấy kết quả xử lý.") from exc

    if job.status != ProcessingJob.STATUS_COMPLETED:
        raise Http404("Job chưa hoàn thành, không thể tải ảnh.")

    try:
        processed_image = job.processed_image
    except ObjectDoesNotExist as exc:
        raise Http404("Không tìm thấy ảnh kết quả.") from exc

    if not default_storage.exists(processed_image.file_path):
        raise Http404("File ảnh kết quả không tồn tại.")

    file_path = default_storage.path(processed_image.file_path)
    response = FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=processed_image.download_filename,
    )
    response["Content-Type"] = processed_image.mime_type
    return response


@login_required
def processing_history_view(request: HttpRequest) -> HttpResponse:
    # Trang lich su xu ly anh voi bo loc.
    filter_form = HistoryFilterForm(request.GET or None)
    algorithm_id = None
    status = ""
    date_from = None
    date_to = None
    search = ""

    if filter_form.is_valid():
        algorithm = filter_form.cleaned_data.get("algorithm_id")
        algorithm_id = algorithm.pk if algorithm else None
        status = filter_form.cleaned_data.get("status") or ""
        date_from = filter_form.cleaned_data.get("date_from")
        date_to = filter_form.cleaned_data.get("date_to")
        search = filter_form.cleaned_data.get("search") or ""
    elif filter_form.errors:
        # Reset bo loc ngay neu form loi de tranh loc sai am.
        date_from = None
        date_to = None

    jobs = ProcessingHistoryService.get_user_jobs(
        request.user,
        algorithm_id=algorithm_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )

    context = {
        "page_title": "Lịch sử xử lý",
        "page_subtitle": f"{jobs.count()} job trong lịch sử",
        "filter_form": filter_form,
        "jobs": jobs,
        "search": search,
        "status": status,
        "date_from": date_from,
        "date_to": date_to,
        "filter_errors": filter_form.non_field_errors(),
    }

    if request.headers.get("HX-Request"):
        return render(request, "processing/partials/history_table.html", context)

    return render(request, "processing/history.html", context)


@login_required
def processing_pipeline_view(request: HttpRequest) -> HttpResponse:
    # Trang cau hinh pipeline nhieu buoc.
    user_images = ImageService.get_user_images(request.user)
    algorithms = ProcessingService.get_active_algorithms()

    return render(
        request,
        "processing/pipeline.html",
        {
            "page_title": "Luồng xử lý đa bước",
            "page_subtitle": "Chọn nhiều thuật toán và chạy theo chuỗi",
            "user_images": user_images,
            "algorithms": algorithms,
        },
    )


@login_required
@csrf_protect
@require_POST
def processing_pipeline_run_view(request: HttpRequest) -> HttpResponse:
    # Thuc thi pipeline qua HTMX.
    form = PipelineRunForm(request.POST)

    if not form.is_valid():
        first_error = next(iter(form.errors.values()))[0]
        return render(
            request,
            "processing/partials/pipeline_error.html",
            {"message": first_error},
            status=400,
        )

    try:
        job = PipelineService.run_pipeline(
            request.user,
            form.cleaned_data["image_id"],
            form.cleaned_data["algorithm_ids"],
        )
    except ProcessingServiceError as exc:
        return render(
            request,
            "processing/partials/pipeline_error.html",
            {"message": str(exc)},
            status=400,
        )

    # Tai lai job kem anh ket qua de partial hien thi dung URL media.
    job = ProcessingService.get_user_job(request.user, job.pk)

    return render(
        request,
        "processing/partials/pipeline_result.html",
        {"job": job},
    )
