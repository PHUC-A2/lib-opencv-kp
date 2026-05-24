import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from apps.authentication.models import User


class RegisterForm(forms.ModelForm):
    # Xac nhan mat khau de tranh nhap sai.
    password_confirm = forms.CharField(
        label="Xác nhận mật khẩu",
        error_messages={
            "required": "Vui lòng nhập lại mật khẩu.",
        },
        widget=forms.PasswordInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Nhập lại mật khẩu",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "full_name", "password"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Tên đăng nhập",
                    "autocomplete": "username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Email",
                    "autocomplete": "email",
                }
            ),
            "full_name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Họ và tên",
                    "autocomplete": "name",
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Mật khẩu",
                    "autocomplete": "new-password",
                }
            ),
        }
        labels = {
            "username": "Tên đăng nhập",
            "email": "Email",
            "full_name": "Họ và tên",
            "password": "Mật khẩu",
        }
        error_messages = {
            "username": {
                "required": "Vui lòng nhập tên đăng nhập.",
                "max_length": "Tên đăng nhập không được vượt quá 150 ký tự.",
            },
            "email": {
                "required": "Vui lòng nhập email.",
                "invalid": "Email không hợp lệ.",
            },
            "full_name": {
                "max_length": "Họ và tên không được vượt quá 100 ký tự.",
            },
            "password": {
                "required": "Vui lòng nhập mật khẩu.",
            },
        }

    def clean_username(self) -> str:
        # Kiem tra username khong rong va dung dinh dang.
        username = self.cleaned_data.get("username", "").strip()
        if len(username) < 3:
            raise ValidationError("Tên đăng nhập phải có ít nhất 3 ký tự.")
        if len(username) > 50:
            raise ValidationError("Tên đăng nhập không được vượt quá 50 ký tự.")
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValidationError("Tên đăng nhập chỉ được chứa chữ, số và dấu gạch dưới.")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Tên đăng nhập đã tồn tại.")
        return username

    def clean_email(self) -> str:
        # Kiem tra email hop le va chua ton tai.
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise ValidationError("Vui lòng nhập email.")
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValidationError("Email không hợp lệ.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email đã được sử dụng.")
        return email

    def clean_full_name(self) -> str:
        # Kiem tra ho ten neu nguoi dung nhap.
        full_name = self.cleaned_data.get("full_name", "").strip()
        if full_name and len(full_name) > 100:
            raise ValidationError("Họ và tên không được vượt quá 100 ký tự.")
        return full_name

    def clean_password(self) -> str:
        # Ap dung validator mat khau tieng Viet.
        password = self.cleaned_data.get("password", "")
        if not password:
            raise ValidationError("Vui lòng nhập mật khẩu.")

        user = User(
            username=self.cleaned_data.get("username", ""),
            email=self.cleaned_data.get("email", ""),
            full_name=self.cleaned_data.get("full_name", ""),
        )

        try:
            validate_password(password, user=user)
        except ValidationError as exc:
            raise ValidationError(list(exc.messages)) from exc

        return password

    def clean(self) -> dict:
        # Kiem tra mat khau va xac nhan trung khop.
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Mật khẩu xác nhận không khớp.")
        return cleaned_data


class LoginForm(forms.Form):
    # Cho phep dang nhap bang username hoac email.
    username = forms.CharField(
        label="Tên đăng nhập hoặc Email",
        max_length=150,
        error_messages={
            "required": "Vui lòng nhập tên đăng nhập hoặc email.",
            "max_length": "Thông tin đăng nhập không được vượt quá 150 ký tự.",
        },
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Tên đăng nhập hoặc email",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Mật khẩu",
        error_messages={
            "required": "Vui lòng nhập mật khẩu.",
        },
        widget=forms.PasswordInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Mật khẩu",
                "autocomplete": "current-password",
            }
        ),
    )
    # Ghi nho dang nhap (session dai han).
    remember_me = forms.BooleanField(
        label="Ghi nhớ đăng nhập",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "checkbox checkbox-primary"}),
    )

    def __init__(self, *args, **kwargs):
        # Nhan request de xac thuc sau khi validate field.
        self.request = kwargs.pop("request", None)
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self) -> dict:
        # Xac thuc thong tin dang nhap.
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get("username", "").strip()
        password = cleaned_data.get("password", "")

        if not username_or_email or not password:
            raise ValidationError("Vui lòng nhập đầy đủ thông tin đăng nhập.")

        user = authenticate(
            request=self.request,
            username=username_or_email,
            password=password,
        )

        if user is None and "@" in username_or_email:
            # Thu dang nhap bang email neu username khong khop.
            try:
                email_user = User.objects.get(email__iexact=username_or_email)
                user = authenticate(
                    request=self.request,
                    username=email_user.username,
                    password=password,
                )
            except User.DoesNotExist:
                user = None

        if user is None:
            raise ValidationError("Tên đăng nhập/email hoặc mật khẩu không đúng.")

        if not user.is_active:
            raise ValidationError("Tài khoản đã bị vô hiệu hóa.")

        self.user_cache = user
        return cleaned_data

    def get_user(self) -> User | None:
        # Tra user da xac thuc thanh cong.
        return self.user_cache


class ProfileForm(forms.ModelForm):
    # Form cap nhat ho so nguoi dung da dang nhap.
    avatar = forms.ImageField(
        label="Ảnh đại diện",
        required=False,
        error_messages={
            "invalid_image": "File ảnh không hợp lệ.",
        },
        widget=forms.FileInput(
            attrs={
                "class": "file-input file-input-bordered w-full rounded-xl",
                "accept": "image/png,image/jpeg,image/webp",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["full_name", "email"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full rounded-xl",
                    "placeholder": "Họ và tên",
                    "autocomplete": "name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "input input-bordered w-full rounded-xl",
                    "placeholder": "Email",
                    "autocomplete": "email",
                }
            ),
        }
        labels = {
            "full_name": "Họ và tên",
            "email": "Email",
        }
        error_messages = {
            "full_name": {
                "max_length": "Họ và tên không được vượt quá 100 ký tự.",
            },
            "email": {
                "required": "Vui lòng nhập email.",
                "invalid": "Email không hợp lệ.",
            },
        }

    def __init__(self, *args, **kwargs):
        # Luu user hien tai de kiem tra email trung lap.
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

    def clean_email(self) -> str:
        # Kiem tra email hop le va khong trung user khac.
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise ValidationError("Vui lòng nhập email.")

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValidationError("Email không hợp lệ.")

        if self.current_user and User.objects.filter(email__iexact=email).exclude(pk=self.current_user.pk).exists():
            raise ValidationError("Email đã được sử dụng.")

        return email

    def clean_full_name(self) -> str:
        # Kiem tra do dai ho ten.
        full_name = self.cleaned_data.get("full_name", "").strip()
        if full_name and len(full_name) > 100:
            raise ValidationError("Họ và tên không được vượt quá 100 ký tự.")
        return full_name

    def clean_avatar(self):
        # Gioi han kich thuoc va dinh dang avatar upload.
        avatar = self.cleaned_data.get("avatar")
        if not avatar:
            return avatar

        if avatar.size > 2 * 1024 * 1024:
            raise ValidationError("Ảnh đại diện không được vượt quá 2MB.")

        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if avatar.content_type not in allowed_types:
            raise ValidationError("Chỉ chấp nhận file JPG, PNG hoặc WEBP.")

        return avatar
