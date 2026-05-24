from django import forms

from apps.algorithms.models import Algorithm
from apps.authentication.models import User
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
                "placeholder": "Username, email, họ tên...",
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
            "icon": "Icon",
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
                    "placeholder": "Tên thuật toán",
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
                "placeholder": "Tên ảnh, username, email...",
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
            (ProcessingJob.JOB_TYPE_PIPELINE, "Pipeline"),
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
