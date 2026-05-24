import os
import uuid

from django.core.files.storage import default_storage
from django.db.models import QuerySet
from PIL import Image as PILImage

from apps.authentication.models import User
from apps.images.models import Image

# Dinh dang anh duoc phep upload.
ALLOWED_MIME_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
# Gioi han kich thuoc file upload (10MB).
MAX_FILE_SIZE = 10 * 1024 * 1024


class ImageUploadError(Exception):
    # Exception rieng cho loi upload anh.
    pass


class ImageService:
    @staticmethod
    def validate_uploaded_file(uploaded_file) -> None:
        # Kiem tra loai file va kich thuoc truoc khi luu.
        if not uploaded_file:
            raise ImageUploadError("Không có file được chọn.")

        if uploaded_file.size > MAX_FILE_SIZE:
            raise ImageUploadError("Ảnh không được vượt quá 10MB.")

        content_type = getattr(uploaded_file, "content_type", "")
        if content_type not in ALLOWED_MIME_TYPES:
            raise ImageUploadError("Chỉ chấp nhận file JPG, PNG hoặc WEBP.")

        try:
            uploaded_file.seek(0)
            with PILImage.open(uploaded_file) as img:
                img.verify()
            uploaded_file.seek(0)
        except Exception as exc:
            raise ImageUploadError("File ảnh không hợp lệ hoặc bị hỏng.") from exc

    @staticmethod
    def extract_metadata(uploaded_file) -> tuple[int, int]:
        # Lay chieu rong/chieu cao anh bang Pillow.
        uploaded_file.seek(0)
        with PILImage.open(uploaded_file) as img:
            width, height = img.size
        uploaded_file.seek(0)
        return width, height

    @staticmethod
    def generate_stored_filename(user: User, extension: str) -> str:
        # Tao ten file unique de tranh ghi de tren SSD.
        unique_id = uuid.uuid4().hex
        return f"{user.pk}_{unique_id}.{extension}"

    @staticmethod
    def upload_image(user: User, uploaded_file) -> Image:
        # Luu anh len SSD va ghi metadata vao DB.
        ImageService.validate_uploaded_file(uploaded_file)

        content_type = uploaded_file.content_type
        extension = ALLOWED_MIME_TYPES[content_type]
        stored_filename = ImageService.generate_stored_filename(user, extension)
        relative_path = f"original/{user.pk}/{stored_filename}"

        width, height = ImageService.extract_metadata(uploaded_file)

        uploaded_file.seek(0)
        saved_path = default_storage.save(relative_path, uploaded_file)

        original_name = os.path.basename(uploaded_file.name)

        return Image.objects.create(
            user=user,
            original_filename=original_name,
            stored_filename=stored_filename,
            file_path=saved_path,
            file_size=uploaded_file.size,
            width=width,
            height=height,
            mime_type=content_type,
        )

    @staticmethod
    def get_user_images(user: User, search: str = "", sort: str = "newest") -> QuerySet[Image]:
        # Lay danh sach anh cua user, ho tro tim kiem va sap xep.
        queryset = Image.objects.filter(user=user)

        if search:
            queryset = queryset.filter(original_filename__icontains=search.strip())

        if sort == "oldest":
            return queryset.order_by("created_at")
        if sort == "name":
            return queryset.order_by("original_filename")
        if sort == "size":
            return queryset.order_by("-file_size")
        return queryset.order_by("-created_at")

    @staticmethod
    def get_user_image(user: User, image_id: int) -> Image:
        # Lay 1 anh thuoc ve user hien tai.
        return Image.objects.get(pk=image_id, user=user)

    @staticmethod
    def delete_image(user: User, image_id: int) -> None:
        # Xoa file tren SSD va record trong DB.
        image = ImageService.get_user_image(user, image_id)
        if default_storage.exists(image.file_path):
            default_storage.delete(image.file_path)
        image.delete()

    @staticmethod
    def count_user_images(user: User) -> int:
        # Dem so anh da upload cua user.
        return Image.objects.filter(user=user).count()

    @staticmethod
    def get_absolute_file_path(image: Image) -> str:
        # Tra ve duong dan tuyet doi de download file.
        return default_storage.path(image.file_path)
