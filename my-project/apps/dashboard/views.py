from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.images.services.image_service import ImageService
from apps.processing.models import ProcessingJob
from apps.processing.services.processing_service import ProcessingService


@login_required
def dashboard_home(request: HttpRequest) -> HttpResponse:
    # Trang tong quan hien thi thong ke va hanh dong nhanh.
    total_images = ImageService.count_user_images(request.user)
    processing_jobs = ProcessingService.count_user_jobs(request.user)
    completed_jobs = ProcessingService.count_user_jobs(request.user, ProcessingJob.STATUS_COMPLETED)
    pending_jobs = ProcessingService.count_user_jobs(request.user, ProcessingJob.STATUS_PROCESSING)

    stats = {
        "total_images": total_images,
        "processing_jobs": processing_jobs,
        "completed_jobs": completed_jobs,
        "pending_jobs": pending_jobs,
    }

    quick_actions = [
        {
            "title": "Tải ảnh lên",
            "description": "Upload ảnh để bắt đầu xử lý OpenCV",
            "url_name": "images:upload",
            "icon": "📤",
        },
        {
            "title": "Xử lý ảnh",
            "description": "Chọn thuật toán và xử lý ngay",
            "url_name": "processing:home",
            "icon": "⚙️",
        },
        {
            "title": "Thư viện ảnh",
            "description": "Xem và quản lý ảnh đã upload",
            "url_name": "images:gallery",
            "icon": "🖼️",
        },
    ]

    return render(
        request,
        "dashboard/index.html",
        {
            "page_title": "Tổng quan",
            "stats": stats,
            "quick_actions": quick_actions,
        },
    )


@login_required
def coming_soon_view(request: HttpRequest, page_title: str, page_description: str) -> HttpResponse:
    # Trang placeholder cho cac module chua trien khai.
    return render(
        request,
        "dashboard/coming_soon.html",
        {
            "page_title": page_title,
            "page_description": page_description,
        },
    )
