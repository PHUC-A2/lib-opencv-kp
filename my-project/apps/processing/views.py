from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.processing.services.processing_service import ProcessingService


def processing_home(request: HttpRequest) -> HttpResponse:
    # Lấy thông điệp từ service để giữ view mỏng và dễ mở rộng.
    hello_message = ProcessingService.get_hello_message()
    # Render trang processing cơ bản để xác nhận module hoạt động.
    return render(
        request,
        "processing/index.html",
        {
            "hello_message": hello_message,
        },
    )
