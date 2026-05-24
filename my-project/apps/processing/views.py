from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.processing.services.processing_service import ProcessingService


@login_required
def processing_home(request: HttpRequest) -> HttpResponse:
    # Trang xu ly anh chinh - Phase 1 hien thi shell, Phase 3 se trien khai day du.
    hello_message = ProcessingService.get_hello_message()

    return render(
        request,
        "processing/index.html",
        {
            "page_title": "Xử lý ảnh",
            "page_subtitle": "Chọn thuật toán OpenCV và xử lý ảnh",
            "hello_message": hello_message,
        },
    )
