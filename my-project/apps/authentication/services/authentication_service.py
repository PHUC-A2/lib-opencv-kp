from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.http import HttpRequest

from apps.authentication.forms import LoginForm, RegisterForm
from apps.authentication.models import User


class AuthenticationService:
    @staticmethod
    def register_user(form: RegisterForm) -> User:
        # Tao tai khoan moi va ma hoa mat khau.
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.role = "user"
        user.is_active = True
        user.save()
        return user

    @staticmethod
    def login_user(request: HttpRequest, form: LoginForm) -> User:
        # Dang nhap va dieu chinh thoi han session theo remember_me.
        user = form.get_user()
        if user is None:
            raise ValueError("Khong tim thay nguoi dung hop le.")

        django_login(request, user)

        remember_me = form.cleaned_data.get("remember_me", False)
        if remember_me:
            # Session ton tai 30 ngay khi chon ghi nho.
            request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            # Session het han khi dong trinh duyet.
            request.session.set_expiry(0)

        return user

    @staticmethod
    def logout_user(request: HttpRequest) -> None:
        # Dang xuat va xoa session hien tai.
        django_logout(request)
