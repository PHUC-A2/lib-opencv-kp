from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from apps.admin_panel.forms import (
    AdminAlgorithmFilterForm,
    AdminAlgorithmForm,
    AdminImageFilterForm,
    AdminJobFilterForm,
    AdminUserFilterForm,
)
from apps.admin_panel.services.admin_service import AdminService, AdminServiceError
from apps.algorithms.models import Algorithm
from core.permissions import admin_required


def _parse_filter_form(form, field_names: list[str]) -> dict:
    # Trich xuat gia tri filter sau khi validate form.
    values = {}
    for field in field_names:
        value = form.cleaned_data.get(field)
        if hasattr(value, "pk"):
            values[field] = value.pk if value else None
        else:
            values[field] = value or ""
    return values


@admin_required
def admin_home(request: HttpRequest) -> HttpResponse:
    # Trang tong quan admin panel.
    stats = AdminService.get_dashboard_stats()

    return render(
        request,
        "admin_panel/index.html",
        {
            "page_title": "Admin Tổng quan",
            "page_subtitle": "Quản lý toàn bộ hệ thống xử lý ảnh",
            "stats": stats,
        },
    )


@admin_required
def admin_users_view(request: HttpRequest) -> HttpResponse:
    # Trang quan ly nguoi dung.
    filter_form = AdminUserFilterForm(request.GET or None)
    search = ""
    role = ""
    status = ""

    if filter_form.is_valid():
        filters = _parse_filter_form(filter_form, ["search", "role", "status"])
        search = filters["search"]
        role = filters["role"]
        status = filters["status"]

    users = AdminService.get_users(search=search, role=role, status=status)

    context = {
        "page_title": "Quản lý người dùng",
        "page_subtitle": f"{users.count()} tài khoản trong hệ thống",
        "filter_form": filter_form,
        "users": users,
        "search": search,
        "role": role,
        "status": status,
    }

    if request.headers.get("HX-Request"):
        return render(request, "admin_panel/partials/users_table.html", context)

    return render(request, "admin_panel/users.html", context)


@admin_required
@csrf_protect
@require_POST
def admin_user_toggle_view(request: HttpRequest, pk: int) -> HttpResponse:
    # Khoa hoac mo khoa tai khoan nguoi dung.
    try:
        target_user = AdminService.toggle_user_active(request.user, pk)
    except AdminServiceError as exc:
        if request.headers.get("HX-Request"):
            return render(
                request,
                "admin_panel/partials/action_error.html",
                {"message": str(exc)},
                status=400,
            )
        messages.error(request, str(exc))
        return redirect("admin_panel:users")

    action_label = "mở khóa" if target_user.is_active else "khóa"
    messages.success(request, f"Đã {action_label} tài khoản {target_user.username}.")

    if request.headers.get("HX-Request"):
        user = AdminService.get_users().get(pk=target_user.pk)
        return render(
            request,
            "admin_panel/partials/user_row.html",
            {"user_item": user},
        )

    return redirect("admin_panel:users")


@admin_required
def admin_images_view(request: HttpRequest) -> HttpResponse:
    # Trang quan ly anh toan he thong.
    filter_form = AdminImageFilterForm(request.GET or None)
    search = ""
    user_id = None

    if filter_form.is_valid():
        filters = _parse_filter_form(filter_form, ["search", "user_id"])
        search = filters["search"]
        user_id = filters["user_id"]

    images = AdminService.get_images(search=search, user_id=user_id)

    context = {
        "page_title": "Quản lý ảnh hệ thống",
        "page_subtitle": f"{images.count()} ảnh trên toàn hệ thống",
        "filter_form": filter_form,
        "images": images,
        "search": search,
        "user_id": user_id,
    }

    if request.headers.get("HX-Request"):
        return render(request, "admin_panel/partials/images_table.html", context)

    return render(request, "admin_panel/images.html", context)


@admin_required
@csrf_protect
@require_POST
def admin_image_delete_view(request: HttpRequest, pk: int) -> HttpResponse:
    # Xoa anh khoi he thong.
    try:
        AdminService.delete_system_image(pk)
    except AdminServiceError as exc:
        if request.headers.get("HX-Request"):
            return render(
                request,
                "admin_panel/partials/action_error.html",
                {"message": str(exc)},
                status=400,
            )
        messages.error(request, str(exc))
        return redirect("admin_panel:images")

    if request.headers.get("HX-Request"):
        return HttpResponse("")

    messages.success(request, "Đã xóa ảnh khỏi hệ thống.")
    return redirect("admin_panel:images")


@admin_required
def admin_algorithms_view(request: HttpRequest) -> HttpResponse:
    # Trang quan ly thuat toan.
    filter_form = AdminAlgorithmFilterForm(request.GET or None)
    search = ""
    status = ""

    if filter_form.is_valid():
        filters = _parse_filter_form(filter_form, ["search", "status"])
        search = filters["search"]
        status = filters["status"]

    algorithms = AdminService.get_algorithms(search=search, status=status)

    context = {
        "page_title": "Quản lý thuật toán",
        "page_subtitle": f"{algorithms.count()} thuật toán OpenCV",
        "filter_form": filter_form,
        "algorithms": algorithms,
        "search": search,
        "status": status,
    }

    if request.headers.get("HX-Request"):
        return render(request, "admin_panel/partials/algorithms_table.html", context)

    return render(request, "admin_panel/algorithms.html", context)


@admin_required
@csrf_protect
def admin_algorithm_create_view(request: HttpRequest) -> HttpResponse:
    # Tao thuat toan moi.
    form = AdminAlgorithmForm(request.POST or None, is_edit=False)

    if request.method == "POST" and form.is_valid():
        try:
            AdminService.create_algorithm(form.cleaned_data)
        except AdminServiceError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Đã thêm thuật toán mới.")
            return redirect("admin_panel:algorithms")

    return render(
        request,
        "admin_panel/algorithm_form.html",
        {
            "page_title": "Thêm thuật toán",
            "page_subtitle": "Đăng ký thuật toán OpenCV mới",
            "form": form,
            "is_edit": False,
        },
    )


@admin_required
@csrf_protect
def admin_algorithm_edit_view(request: HttpRequest, pk: int) -> HttpResponse:
    # Cap nhat thuat toan.
    algorithm = get_object_or_404(Algorithm, pk=pk)
    form = AdminAlgorithmForm(request.POST or None, instance=algorithm, is_edit=True)

    if request.method == "POST" and form.is_valid():
        try:
            AdminService.update_algorithm(
                algorithm.pk,
                {
                    "name": form.cleaned_data["name"],
                    "description": form.cleaned_data["description"],
                    "icon": form.cleaned_data["icon"],
                    "is_active": form.cleaned_data["is_active"],
                },
            )
        except AdminServiceError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Đã cập nhật thuật toán.")
            return redirect("admin_panel:algorithms")

    return render(
        request,
        "admin_panel/algorithm_form.html",
        {
            "page_title": "Sửa thuật toán",
            "page_subtitle": algorithm.name,
            "form": form,
            "is_edit": True,
            "algorithm": algorithm,
        },
    )


@admin_required
@csrf_protect
@require_POST
def admin_algorithm_toggle_view(request: HttpRequest, pk: int) -> HttpResponse:
    # Bat/tat thuat toan.
    try:
        toggled = AdminService.toggle_algorithm_active(pk)
        algorithm = AdminService.get_algorithms().get(pk=toggled.pk)
    except AdminServiceError as exc:
        if request.headers.get("HX-Request"):
            return render(
                request,
                "admin_panel/partials/action_error.html",
                {"message": str(exc)},
                status=400,
            )
        messages.error(request, str(exc))
        return redirect("admin_panel:algorithms")

    state_label = "bật" if algorithm.is_active else "tắt"
    messages.success(request, f"Đã {state_label} thuật toán {algorithm.name}.")

    if request.headers.get("HX-Request"):
        return render(
            request,
            "admin_panel/partials/algorithm_row.html",
            {"algorithm": algorithm},
        )

    return redirect("admin_panel:algorithms")


@admin_required
def admin_jobs_view(request: HttpRequest) -> HttpResponse:
    # Trang theo doi job xu ly.
    filter_form = AdminJobFilterForm(request.GET or None)
    search = ""
    status = ""
    job_type = ""
    user_id = None
    date_from = None
    date_to = None
    filter_errors = []

    if filter_form.is_valid():
        filters = _parse_filter_form(
            filter_form,
            ["search", "user_id", "status", "job_type", "date_from", "date_to"],
        )
        search = filters["search"]
        status = filters["status"]
        job_type = filters["job_type"]
        user_id = filters["user_id"]
        date_from = filters["date_from"] or None
        date_to = filters["date_to"] or None
    elif filter_form.errors:
        filter_errors = filter_form.non_field_errors()
        date_from = None
        date_to = None

    jobs = AdminService.get_jobs(
        search=search,
        status=status,
        job_type=job_type,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )

    context = {
        "page_title": "Processing Jobs",
        "page_subtitle": f"{jobs.count()} job trong hệ thống",
        "filter_form": filter_form,
        "jobs": jobs,
        "search": search,
        "status": status,
        "job_type": job_type,
        "user_id": user_id,
        "date_from": date_from,
        "date_to": date_to,
        "filter_errors": filter_errors,
    }

    if request.headers.get("HX-Request"):
        return render(request, "admin_panel/partials/jobs_table.html", context)

    return render(request, "admin_panel/jobs.html", context)


@admin_required
def admin_placeholder(request: HttpRequest, page_title: str, page_description: str) -> HttpResponse:
    # Trang placeholder cho module chua trien khai (Phase 8 logs).
    return render(
        request,
        "admin_panel/coming_soon.html",
        {
            "page_title": page_title,
            "page_description": page_description,
        },
    )
