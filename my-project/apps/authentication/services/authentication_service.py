from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.core.files.storage import default_storage
from django.http import HttpRequest

from apps.authentication.forms import LoginForm, ProfileForm, RegisterForm
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

    @staticmethod
    def update_profile(user: User, form: ProfileForm) -> User:
        # Cap nhat ho so va avatar; email giu nguyen sau khi dang ky.
        user.full_name = form.cleaned_data.get("full_name", "")

        avatar_file = form.cleaned_data.get("avatar")
        if avatar_file:
            # Luu avatar vao thu muc media/avatars/.
            extension = avatar_file.name.rsplit(".", 1)[-1].lower()
            avatar_path = f"avatars/user_{user.pk}.{extension}"
            if user.avatar_url and default_storage.exists(user.avatar_url):
                default_storage.delete(user.avatar_url)
            saved_path = default_storage.save(avatar_path, avatar_file)
            user.avatar_url = saved_path

        user.save()
        return user
