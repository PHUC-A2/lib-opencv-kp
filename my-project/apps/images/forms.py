from django import forms


class ImageUploadForm(forms.Form):
    # Form upload nhieu file anh (su dung truc tiep input HTML trong template).
    pass


class GalleryFilterForm(forms.Form):
    # Form loc va tim kiem trong thu vien anh.
    search = forms.CharField(
        label="Tìm kiếm",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full rounded-xl",
                "placeholder": "Tìm theo tên file...",
            }
        ),
    )
    sort = forms.ChoiceField(
        label="Sắp xếp",
        required=False,
        choices=[
            ("newest", "Mới nhất"),
            ("oldest", "Cũ nhất"),
            ("name", "Tên A-Z"),
            ("size", "Kích thước lớn nhất"),
        ],
        widget=forms.Select(
            attrs={
                "class": "select select-bordered w-full rounded-xl",
            }
        ),
    )
