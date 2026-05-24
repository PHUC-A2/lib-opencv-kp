import os
from dataclasses import dataclass

from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@dataclass
class AdminConfig:
    # Cau hinh tai khoan admin doc tu .env.
    username: str
    email: str
    password: str
    full_name: str


class InitDbServiceError(Exception):
    # Exception rieng cho loi khoi tao database.
    pass


class InitDbService:
    @staticmethod
    def get_admin_config() -> AdminConfig:
        # Doc thong tin admin tu bien moi truong (.env).
        username = os.getenv("ADMIN_USERNAME", "admin").strip()
        email = os.getenv("ADMIN_EMAIL", "admin@localhost.com").strip()
        password = os.getenv("ADMIN_PASSWORD", "Admin@1234").strip()
        full_name = os.getenv("ADMIN_FULL_NAME", "Quản trị viên hệ thống").strip()

        if not username:
            raise InitDbServiceError("ADMIN_USERNAME không được để trống.")
        if not email:
            raise InitDbServiceError("ADMIN_EMAIL không được để trống.")
        if not password:
            raise InitDbServiceError("ADMIN_PASSWORD không được để trống.")

        return AdminConfig(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
        )

    @staticmethod
    def validate_admin_password(config: AdminConfig, user: User | None = None) -> None:
        # Kiem tra mat khau admin theo rule he thong.
        try:
            password_validation.validate_password(config.password, user=user)
        except ValidationError as exc:
            messages = " ".join(exc.messages)
            raise InitDbServiceError(f"ADMIN_PASSWORD không hợp lệ: {messages}") from exc

    @staticmethod
    def upsert_admin_user(config: AdminConfig) -> tuple[User, bool]:
        # Tao moi hoac cap nhat tai khoan admin tu cau hinh .env.
        user = User.objects.filter(username=config.username).first()
        if user is None:
            user = User.objects.filter(email=config.email).first()

        created = user is None
        if created:
            user = User(username=config.username)

        InitDbService.validate_admin_password(config, user=user)

        user.username = config.username
        user.email = config.email
        user.full_name = config.full_name
        user.role = "admin"
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(config.password)
        user.save()
        return user, created
