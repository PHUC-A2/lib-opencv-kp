from django import forms

from apps.algorithms.models import Algorithm
from apps.processing.models import ProcessingJob


class HistoryFilterForm(forms.Form):
    # Form loc lich su xu ly anh.
    search = forms.CharField(
        label="Tìm kiếm",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full rounded-xl",
                "placeholder": "Tên file ảnh...",
            }
        ),
    )
    algorithm_id = forms.ModelChoiceField(
        label="Thuật toán",
        required=False,
        queryset=Algorithm.objects.filter(is_active=True).order_by("name"),
        empty_label="Tất cả thuật toán",
        widget=forms.Select(attrs={"class": "select select-bordered w-full rounded-xl"}),
    )
    status = forms.ChoiceField(
        label="Trạng thái",
        required=False,
        choices=[("", "Tất cả trạng thái")] + ProcessingJob.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "select select-bordered w-full rounded-xl"}),
    )
    date_from = forms.DateField(
        label="Từ ngày",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "input input-bordered w-full rounded-xl",
                "type": "date",
            }
        ),
    )
    date_to = forms.DateField(
        label="Đến ngày",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "input input-bordered w-full rounded-xl",
                "type": "date",
            }
        ),
    )

    def clean(self):
        # Kiem tra khoang ngay hop le.
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Ngày bắt đầu không được lớn hơn ngày kết thúc.")
        return cleaned_data


class ProcessingRunForm(forms.Form):
    # Form chon anh va thuat toan de xu ly.
    image_id = forms.IntegerField(
        label="Ảnh nguồn",
        error_messages={"required": "Vui lòng chọn ảnh cần xử lý.", "invalid": "Ảnh không hợp lệ."},
    )
    algorithm_id = forms.IntegerField(
        label="Thuật toán",
        error_messages={"required": "Vui lòng chọn thuật toán.", "invalid": "Thuật toán không hợp lệ."},
    )

    def clean_algorithm_id(self) -> int:
        # Kiem tra thuat toan ton tai va dang active.
        algorithm_id = self.cleaned_data["algorithm_id"]
        if not Algorithm.objects.filter(pk=algorithm_id, is_active=True).exists():
            raise forms.ValidationError("Thuật toán không tồn tại hoặc đã bị tắt.")
        return algorithm_id


class PipelineRunForm(forms.Form):
    # Form chay pipeline nhieu buoc.
    image_id = forms.IntegerField(
        label="Ảnh nguồn",
        error_messages={"required": "Vui lòng chọn ảnh.", "invalid": "Ảnh không hợp lệ."},
    )
    algorithm_ids = forms.CharField(
        label="Danh sách thuật toán",
        error_messages={"required": "Vui lòng chọn ít nhất 2 thuật toán."},
    )

    def clean_algorithm_ids(self) -> list[int]:
        # Parse chuoi id thuat toan theo thu tu pipeline.
        raw_value = self.cleaned_data.get("algorithm_ids", "").strip()
        if not raw_value:
            raise forms.ValidationError("Vui lòng chọn ít nhất 2 thuật toán.")

        try:
            algorithm_ids = [int(item.strip()) for item in raw_value.split(",") if item.strip()]
        except ValueError as exc:
            raise forms.ValidationError("Danh sách thuật toán không hợp lệ.") from exc

        if len(algorithm_ids) < 2:
            raise forms.ValidationError("Pipeline cần ít nhất 2 thuật toán.")

        active_count = Algorithm.objects.filter(pk__in=algorithm_ids, is_active=True).count()
        if active_count != len(set(algorithm_ids)):
            raise forms.ValidationError("Có thuật toán không tồn tại hoặc đã bị tắt.")

        return algorithm_ids
