from django import forms
import re

from apps.algorithms.models import Algorithm
from apps.authentication.models import User
from apps.admin_panel.models import SystemLog
from apps.processing.models import ProcessingJob
from services.opencv.registry import get_supported_codes


INPUT_CLASS = "input input-bordered w-full rounded-xl"
SELECT_CLASS = "select select-bordered w-full rounded-xl"
TEXTAREA_CLASS = "textarea textarea-bordered w-full rounded-xl"


class AdminUserFilterForm(forms.Form):
    # Form loc danh sach nguoi dung admin.
    search = forms.CharField(
        label="Tìm kiếm",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Tên đăng nhập, email, họ tên...",
            }
        ),
    )
    role = forms.ChoiceField(
        label="Vai trò",
        required=False,
        choices=[
            ("", "Tất cả vai trò"),
            ("admin", "Quản trị viên"),
            ("user", "Người dùng"),
        ],
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )
    status = forms.ChoiceField(
        label="Trạng thái",
        required=False,
        choices=[
            ("", "Tất cả trạng thái"),
            ("active", "Đang hoạt động"),
            ("locked", "Đã khóa"),
        ],
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )


class AdminUserForm(forms.ModelForm):
    # Form tao/sua tai khoan nguoi dung trong admin panel.
    password = forms.CharField(
        label="Mật khẩu",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Nhập mật khẩu",
                "autocomplete": "new-password",
            }
        ),
    )
    password_confirm = forms.CharField(
        label="Xác nhận mật khẩu",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Nhập lại mật khẩu",
                "autocomplete": "new-password",
            }
        ),
    )
    role = forms.ChoiceField(
        label="Vai trò",
        choices=[
            ("user", "Người dùng"),
            ("admin", "Quản trị viên"),
        ],
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "full_name", "is_active"]
        labels = {
            "username": "Tên đăng nhập",
            "email": "Địa chỉ email",
            "full_name": "Họ và tên",
            "is_active": "Đang hoạt động",
        }
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Tên đăng nhập",
                    "autocomplete": "username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Địa chỉ email",
                    "autocomplete": "email",
                }
            ),
            "full_name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Họ và tên",
                    "autocomplete": "name",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "checkbox checkbox-primary"}),
        }

    def __init__(self, *args, is_edit: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_edit = is_edit
        if is_edit:
            # Khong cho doi username/email sau khi tao tai khoan.
            self.fields["username"].disabled = True
            del self.fields["email"]
            self.fields["password"].help_text = "Để trống nếu không đổi mật khẩu"
            if self.instance.pk:
                self.fields["role"].initial = self.instance.role
        else:
            self.fields["password"].required = True
            self.fields["password_confirm"].required = True

    def clean_username(self) -> str:
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            raise forms.ValidationError("Vui lòng nhập tên đăng nhập.")
        if len(username) < 3:
            raise forms.ValidationError("Tên đăng nhập phải có ít nhất 3 ký tự.")
        if len(username) > 50:
            raise forms.ValidationError("Tên đăng nhập không được vượt quá 50 ký tự.")
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise forms.ValidationError("Tên đăng nhập chỉ được chứa chữ, số và dấu gạch dưới.")
        if not self.is_edit and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Tên đăng nhập đã tồn tại.")
        return username

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Vui lòng nhập email.")
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise forms.ValidationError("Email không hợp lệ.")

        queryset = User.objects.filter(email__iexact=email)
        if self.is_edit and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Email đã được sử dụng.")
        return email

    def clean_full_name(self) -> str:
        full_name = self.cleaned_data.get("full_name", "").strip()
        if full_name and len(full_name) > 100:
            raise forms.ValidationError("Họ và tên không được vượt quá 100 ký tự.")
        return full_name

    def clean_password(self) -> str:
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError as DjangoValidationError

        password = self.cleaned_data.get("password", "")
        if self.is_edit and not password:
            return password
        if not password:
            raise forms.ValidationError("Vui lòng nhập mật khẩu.")

        user = self.instance if self.is_edit and self.instance.pk else User(
            username=self.cleaned_data.get("username", ""),
            email=self.cleaned_data.get("email", ""),
            full_name=self.cleaned_data.get("full_name", ""),
        )
        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            raise forms.ValidationError(list(exc.messages)) from exc
        return password

    def clean(self) -> dict:
        cleaned_data = super().clean()
        password = cleaned_data.get("password", "")
        password_confirm = cleaned_data.get("password_confirm", "")
        if password or password_confirm:
            if password != password_confirm:
                self.add_error("password_confirm", "Mật khẩu xác nhận không khớp.")
        elif not self.is_edit:
            self.add_error("password", "Vui lòng nhập mật khẩu.")
        return cleaned_data


class AdminImageFilterForm(forms.Form):
    # Form loc danh sach anh he thong.
    search = forms.CharField(
        label="Tìm kiếm",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Tên file ảnh...",
            }
        ),
    )
    user_id = forms.ModelChoiceField(
        label="Người dùng",
        required=False,
        queryset=User.objects.order_by("username"),
        empty_label="Tất cả người dùng",
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )


class AdminAlgorithmFilterForm(forms.Form):
    # Form loc danh sach thuat toan.
    search = forms.CharField(
        label="Tìm kiếm",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Tên hoặc mã thuật toán...",
            }
        ),
    )
    status = forms.ChoiceField(
        label="Trạng thái",
        required=False,
        choices=[
            ("", "Tất cả"),
            ("active", "Đang bật"),
            ("inactive", "Đã tắt"),
        ],
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )


class AdminAlgorithmForm(forms.ModelForm):
    # Form tao/sua thuat toan OpenCV.
    class Meta:
        model = Algorithm
        fields = ["code", "name", "description", "icon", "is_active"]
        labels = {
            "code": "Mã thuật toán",
            "name": "Tên hiển thị",
            "description": "Mô tả",
            "icon": "Biểu tượng",
            "is_active": "Đang hoạt động",
        }
        widgets = {
            "code": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "vd: grayscale",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "vd: Thang xám (Grayscale)",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "rows": 3,
                    "placeholder": "Mô tả ngắn về thuật toán",
                }
            ),
            "icon": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "⚙️",
                    "maxlength": 10,
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "checkbox checkbox-primary"}),
        }

    def __init__(self, *args, is_edit: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_edit = is_edit
        if is_edit:
            # Khong cho sua code khi da tao.
            self.fields["code"].disabled = True

    def clean_code(self) -> str:
        # Kiem tra code thuoc registry OpenCV.
        code = self.cleaned_data.get("code", "").strip()
        if not code:
            raise forms.ValidationError("Vui lòng nhập mã thuật toán.")

        if code not in get_supported_codes():
            supported = ", ".join(get_supported_codes())
            raise forms.ValidationError(f"Mã không hợp lệ. Các mã hỗ trợ: {supported}")

        if not self.is_edit and Algorithm.objects.filter(code=code).exists():
            raise forms.ValidationError("Mã thuật toán đã tồn tại.")

        return code


class AdminJobFilterForm(forms.Form):
    # Form loc danh sach job xu ly.
    search = forms.CharField(
        label="Tìm kiếm",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Tên ảnh, tên đăng nhập, email...",
            }
        ),
    )
    user_id = forms.ModelChoiceField(
        label="Người dùng",
        required=False,
        queryset=User.objects.order_by("username"),
        empty_label="Tất cả người dùng",
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )
    status = forms.ChoiceField(
        label="Trạng thái",
        required=False,
        choices=[("", "Tất cả trạng thái")] + ProcessingJob.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )
    job_type = forms.ChoiceField(
        label="Loại job",
        required=False,
        choices=[
            ("", "Tất cả loại"),
            (ProcessingJob.JOB_TYPE_SINGLE, "Xử lý đơn"),
            (ProcessingJob.JOB_TYPE_PIPELINE, "Luồng xử lý đa bước"),
        ],
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )
    date_from = forms.DateField(
        label="Từ ngày",
        required=False,
        widget=forms.DateInput(attrs={"class": INPUT_CLASS, "type": "date"}),
    )
    date_to = forms.DateField(
        label="Đến ngày",
        required=False,
        widget=forms.DateInput(attrs={"class": INPUT_CLASS, "type": "date"}),
    )

    def clean(self):
        # Kiem tra khoang ngay hop le.
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Ngày bắt đầu không được lớn hơn ngày kết thúc.")
        return cleaned_data


class AdminLogFilterForm(forms.Form):
    # Form loc nhat ky he thong admin.
    search = forms.CharField(
        label="Tìm kiếm",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Nội dung log, tên đăng nhập, mã job...",
            }
        ),
    )
    level = forms.ChoiceField(
        label="Mức độ",
        required=False,
        choices=[("", "Tất cả mức độ")] + SystemLog.LEVEL_CHOICES,
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )
    module = forms.ChoiceField(
        label="Phân hệ",
        required=False,
        choices=[("", "Tất cả phân hệ")] + SystemLog.MODULE_CHOICES,
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )
    date_from = forms.DateField(
        label="Từ ngày",
        required=False,
        widget=forms.DateInput(attrs={"class": INPUT_CLASS, "type": "date"}),
    )
    date_to = forms.DateField(
        label="Đến ngày",
        required=False,
        widget=forms.DateInput(attrs={"class": INPUT_CLASS, "type": "date"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Ngày bắt đầu không được lớn hơn ngày kết thúc.")
        return cleaned_data
