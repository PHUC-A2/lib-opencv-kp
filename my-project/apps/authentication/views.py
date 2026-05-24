from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from apps.authentication.forms import LoginForm, ProfileForm, RegisterForm
from apps.authentication.services.authentication_service import AuthenticationService


@ensure_csrf_cookie
@csrf_protect
def register_view(request: HttpRequest) -> HttpResponse:
    # Chuyen huong neu da dang nhap.
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        # Goi service de tao tai khoan, khong xu ly logic trong view.
        AuthenticationService.register_user(form)
        messages.success(request, "Đăng ký thành công. Vui lòng đăng nhập.")
        return redirect("authentication:login")

    return render(
        request,
        "authentication/register.html",
        {"form": form},
    )


@ensure_csrf_cookie
@csrf_protect
def login_view(request: HttpRequest) -> HttpResponse:
    # Chuyen huong neu da dang nhap.
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    form = LoginForm(request.POST or None, request=request)

    if request.method == "POST" and form.is_valid():
        # Goi service de dang nhap va quan ly session.
        AuthenticationService.login_user(request, form)
        messages.success(request, f"Xin chào, {form.get_user().username}!")
        next_url = request.GET.get("next") or reverse("dashboard:home")
        return redirect(next_url)

    return render(
        request,
        "authentication/login.html",
        {"form": form},
    )


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    # Dang xuat va quay ve trang dang nhap.
    AuthenticationService.logout_user(request)
    messages.info(request, "Bạn đã đăng xuất thành công.")
    return redirect("authentication:login")


@login_required
@ensure_csrf_cookie
@csrf_protect
def profile_view(request: HttpRequest) -> HttpResponse:
    # Trang xem va cap nhat ho so nguoi dung.
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
        current_user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        AuthenticationService.update_profile(request.user, form)
        messages.success(request, "Cập nhật hồ sơ thành công.")
        return redirect("authentication:profile")

    avatar_display_url = None
    if request.user.avatar_url:
        avatar_display_url = request.user.avatar_url

    return render(
        request,
        "authentication/profile.html",
        {
            "page_title": "Hồ sơ",
            "page_subtitle": "Quản lý thông tin cá nhân",
            "form": form,
            "avatar_display_url": avatar_display_url,
        },
    )
