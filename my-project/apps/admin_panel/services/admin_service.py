from datetime import datetime, time

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.storage import default_storage
from django.db.models import Count, Q, QuerySet
from django.utils import timezone

from apps.algorithms.models import Algorithm
from apps.authentication.models import User
from apps.admin_panel.models import SystemLog
from apps.images.models import Image
from apps.processing.models import ProcessedImage, ProcessingJob
from services.opencv.registry import get_supported_codes


class AdminServiceError(Exception):
    # Exception rieng cho service admin panel.
    pass


class AdminService:
    @staticmethod
    def get_dashboard_stats() -> dict:
        # Tong hop thong ke tong quan he thong cho trang admin.
        recent_errors = (
            ProcessingJob.objects.filter(status=ProcessingJob.STATUS_FAILED)
            .select_related("user", "source_image", "algorithm")
            .prefetch_related("pipeline_steps__algorithm")
            .order_by("-completed_at")[:5]
        )

        return {
            "total_users": User.objects.count(),
            "total_images": Image.objects.count(),
            "total_jobs": ProcessingJob.objects.count(),
            "active_jobs": ProcessingJob.objects.filter(status=ProcessingJob.STATUS_PROCESSING).count(),
            "failed_jobs": ProcessingJob.objects.filter(status=ProcessingJob.STATUS_FAILED).count(),
            "total_logs": SystemLog.objects.count(),
            "error_logs": SystemLog.objects.filter(level=SystemLog.LEVEL_ERROR).count(),
            "recent_errors": recent_errors,
        }

    @staticmethod
    def get_users(search: str = "", role: str = "", status: str = "") -> QuerySet[User]:
        # Truy van danh sach nguoi dung voi bo loc.
        queryset = User.objects.annotate(
            image_count=Count("images", distinct=True),
            job_count=Count("processing_jobs", distinct=True),
        ).order_by("-created_at")

        if search:
            term = search.strip()
            queryset = queryset.filter(
                Q(username__icontains=term)
                | Q(email__icontains=term)
                | Q(full_name__icontains=term)
            )

        if role:
            queryset = queryset.filter(role=role)

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "locked":
            queryset = queryset.filter(is_active=False)

        return queryset

    @staticmethod
    def toggle_user_active(admin_user: User, user_id: int) -> User:
        # Khoa hoac mo khoa tai khoan nguoi dung.
        if admin_user.pk == user_id:
            raise AdminServiceError("Không thể khóa tài khoản của chính bạn.")

        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise AdminServiceError("Không tìm thấy người dùng.") from exc

        target_user.is_active = not target_user.is_active
        target_user.save(update_fields=["is_active", "updated_at"])
        return target_user

    @staticmethod
    def _validate_user_password(password: str, user: User) -> None:
        # Kiem tra mat khau theo rule Django truoc khi luu.
        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            raise AdminServiceError(" ".join(exc.messages)) from exc

    @staticmethod
    def create_user(data: dict) -> User:
        # Tao tai khoan moi tu admin panel.
        username = data["username"].strip()
        email = data["email"].strip().lower()
        full_name = data.get("full_name", "").strip()
        role = data.get("role", "user")
        is_active = data.get("is_active", True)
        password = data.get("password", "")

        if User.objects.filter(username__iexact=username).exists():
            raise AdminServiceError("Tên đăng nhập đã tồn tại.")
        if User.objects.filter(email__iexact=email).exists():
            raise AdminServiceError("Email đã được sử dụng.")
        if role not in {"admin", "user"}:
            raise AdminServiceError("Vai trò không hợp lệ.")
        if not password:
            raise AdminServiceError("Vui lòng nhập mật khẩu.")

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            is_active=is_active,
        )
        AdminService._validate_user_password(password, user)
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def update_user(actor: User, user_id: int, data: dict) -> User:
        # Cap nhat thong tin tai khoan nguoi dung (khong doi email).
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise AdminServiceError("Không tìm thấy người dùng.") from exc

        full_name = data.get("full_name", "").strip()
        role = data.get("role", target_user.role)
        is_active = data.get("is_active", target_user.is_active)
        password = data.get("password", "").strip()

        if role not in {"admin", "user"}:
            raise AdminServiceError("Vai trò không hợp lệ.")

        if actor.pk == user_id:
            if role != "admin":
                raise AdminServiceError("Không thể hạ quyền tài khoản của chính bạn.")
            if not is_active:
                raise AdminServiceError("Không thể khóa tài khoản của chính bạn.")

        if target_user.role == "admin" and role != "admin":
            remaining_admins = User.objects.filter(role="admin").exclude(pk=user_id).count()
            if remaining_admins == 0:
                raise AdminServiceError("Hệ thống cần ít nhất một quản trị viên.")

        target_user.full_name = full_name
        target_user.role = role
        target_user.is_active = is_active

        if password:
            AdminService._validate_user_password(password, target_user)
            target_user.set_password(password)
            target_user.save()
        else:
            target_user.save(update_fields=["full_name", "role", "is_active", "updated_at"])

        return target_user

    @staticmethod
    def delete_user(actor: User, user_id: int) -> None:
        # Xoa tai khoan khoi he thong (kem du lieu lien quan CASCADE).
        if actor.pk == user_id:
            raise AdminServiceError("Không thể xóa tài khoản của chính bạn.")

        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise AdminServiceError("Không tìm thấy người dùng.") from exc

        if target_user.role == "admin":
            remaining_admins = User.objects.filter(role="admin").exclude(pk=user_id).count()
            if remaining_admins == 0:
                raise AdminServiceError("Không thể xóa quản trị viên cuối cùng.")

        target_user.delete()

    @staticmethod
    def get_images(search: str = "", user_id: int | None = None) -> QuerySet[Image]:
        # Truy van tat ca anh trong he thong.
        queryset = Image.objects.select_related("user").order_by("-created_at")

        if search:
            queryset = queryset.filter(original_filename__icontains=search.strip())

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    @staticmethod
    def delete_system_image(image_id: int) -> None:
        # Xoa anh he thong kem file processed neu co.
        try:
            image = Image.objects.get(pk=image_id)
        except Image.DoesNotExist as exc:
            raise AdminServiceError("Không tìm thấy ảnh.") from exc

        for processed in ProcessedImage.objects.filter(job__source_image=image):
            if default_storage.exists(processed.file_path):
                default_storage.delete(processed.file_path)

        if default_storage.exists(image.file_path):
            default_storage.delete(image.file_path)

        image.delete()

    @staticmethod
    def get_algorithms(search: str = "", status: str = "") -> QuerySet[Algorithm]:
        # Truy van danh sach thuat toan.
        queryset = Algorithm.objects.annotate(
            job_count=Count("processing_jobs", distinct=True),
        ).order_by("name")

        if search:
            term = search.strip()
            queryset = queryset.filter(
                Q(name__icontains=term) | Q(code__icontains=term) | Q(description__icontains=term)
            )

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset

    @staticmethod
    def create_algorithm(data: dict) -> Algorithm:
        # Tao thuat toan moi neu code ton tai trong registry OpenCV.
        code = data["code"].strip()
        if code not in get_supported_codes():
            raise AdminServiceError(f"Mã thuật toán '{code}' chưa được hỗ trợ trong OpenCV.")

        if Algorithm.objects.filter(code=code).exists():
            raise AdminServiceError("Mã thuật toán đã tồn tại.")

        return Algorithm.objects.create(
            code=code,
            name=data["name"].strip(),
            description=data.get("description", "").strip(),
            icon=data.get("icon", "⚙️").strip() or "⚙️",
            is_active=data.get("is_active", True),
        )

    @staticmethod
    def update_algorithm(algorithm_id: int, data: dict) -> Algorithm:
        # Cap nhat thong tin thuat toan (khong doi code).
        try:
            algorithm = Algorithm.objects.get(pk=algorithm_id)
        except Algorithm.DoesNotExist as exc:
            raise AdminServiceError("Không tìm thấy thuật toán.") from exc

        algorithm.name = data["name"].strip()
        algorithm.description = data.get("description", "").strip()
        algorithm.icon = data.get("icon", "⚙️").strip() or "⚙️"
        algorithm.is_active = data.get("is_active", algorithm.is_active)
        algorithm.save(update_fields=["name", "description", "icon", "is_active", "updated_at"])
        return algorithm

    @staticmethod
    def toggle_algorithm_active(algorithm_id: int) -> Algorithm:
        # Bat/tat thuat toan tren he thong.
        try:
            algorithm = Algorithm.objects.get(pk=algorithm_id)
        except Algorithm.DoesNotExist as exc:
            raise AdminServiceError("Không tìm thấy thuật toán.") from exc

        algorithm.is_active = not algorithm.is_active
        algorithm.save(update_fields=["is_active", "updated_at"])
        return algorithm

    @staticmethod
    def get_jobs(
        search: str = "",
        status: str = "",
        job_type: str = "",
        user_id: int | None = None,
        date_from=None,
        date_to=None,
    ) -> QuerySet[ProcessingJob]:
        # Truy van toan bo job xu ly anh trong he thong.
        queryset = (
            ProcessingJob.objects.select_related("user", "algorithm", "source_image", "processed_image")
            .prefetch_related("pipeline_steps__algorithm")
            .order_by("-created_at")
        )

        if search:
            term = search.strip()
            queryset = queryset.filter(
                Q(source_image__original_filename__icontains=term)
                | Q(user__username__icontains=term)
                | Q(user__email__icontains=term)
            )

        if status:
            queryset = queryset.filter(status=status)

        if job_type:
            queryset = queryset.filter(job_type=job_type)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if date_from:
            start_dt = timezone.make_aware(datetime.combine(date_from, time.min))
            queryset = queryset.filter(created_at__gte=start_dt)

        if date_to:
            end_dt = timezone.make_aware(datetime.combine(date_to, time.max))
            queryset = queryset.filter(created_at__lte=end_dt)

        return queryset
