from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def dashboard_home(request: HttpRequest) -> HttpResponse:
    # Trang tong quan hien thi thong ke va hanh dong nhanh.
    stats = {
        "total_images": 0,
        "processing_jobs": 0,
        "completed_jobs": 0,
        "pending_jobs": 0,
    }

    quick_actions = [
        {
            "title": "Tải ảnh lên",
            "description": "Upload ảnh để bắt đầu xử lý OpenCV",
            "url_name": "dashboard:images_upload",
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
            "url_name": "dashboard:images_gallery",
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
