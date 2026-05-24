from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from core.permissions import admin_required


@admin_required
def admin_home(request: HttpRequest) -> HttpResponse:
    # Trang tong quan admin panel.
    stats = {
        "total_users": 0,
        "total_images": 0,
        "active_jobs": 0,
        "system_logs": 0,
    }

    return render(
        request,
        "admin_panel/index.html",
        {
            "page_title": "Admin Tổng quan",
            "stats": stats,
        },
    )


@admin_required
def admin_placeholder(request: HttpRequest, page_title: str, page_description: str) -> HttpResponse:
    # Trang placeholder cho cac module admin chua trien khai.
    return render(
        request,
        "admin_panel/coming_soon.html",
        {
            "page_title": page_title,
            "page_description": page_description,
        },
    )
