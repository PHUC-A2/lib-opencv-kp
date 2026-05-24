import re

from django.core.exceptions import ValidationError


class VietnameseMinimumLengthValidator:
    def __init__(self, min_length: int = 8) -> None:
        # Luu do dai toi thieu cho mat khau.
        self.min_length = min_length

    def validate(self, password: str, user=None) -> None:
        # Kiem tra mat khau dat do dai toi thieu.
        if len(password) < self.min_length:
            raise ValidationError(
                f"Mật khẩu phải có ít nhất {self.min_length} ký tự.",
                code="password_too_short",
            )

    def get_help_text(self) -> str:
        # Huong dan hien thi cho nguoi dung.
        return f"Mật khẩu phải có ít nhất {self.min_length} ký tự."


class VietnameseUserAttributeSimilarityValidator:
    def validate(self, password: str, user=None) -> None:
        # Kiem tra mat khau khong qua giong thong tin ca nhan.
        if user is None:
            return

        attribute_values = []
        for attribute in ("username", "email", "full_name", "first_name", "last_name"):
            value = getattr(user, attribute, None)
            if value:
                attribute_values.append(str(value).lower())

        password_lower = password.lower()
        for value in attribute_values:
            if value and value in password_lower:
                raise ValidationError(
                    "Mật khẩu quá giống với thông tin cá nhân.",
                    code="password_too_similar",
                )

    def get_help_text(self) -> str:
        return "Mật khẩu không được quá giống với thông tin cá nhân."


class VietnameseCommonPasswordValidator:
    COMMON_PASSWORDS = {
        "password",
        "123456",
        "12345678",
        "123456789",
        "qwerty",
        "abc123",
        "password123",
        "admin123",
        "iloveyou",
        "111111",
    }

    def validate(self, password: str, user=None) -> None:
        # Chan cac mat khau pho bien de tang bao mat.
        if password.lower() in self.COMMON_PASSWORDS:
            raise ValidationError(
                "Mật khẩu quá phổ biến, vui lòng chọn mật khẩu khác.",
                code="password_too_common",
            )

    def get_help_text(self) -> str:
        return "Mật khẩu không được dùng các mật khẩu phổ biến."


class VietnameseNumericPasswordValidator:
    def validate(self, password: str, user=None) -> None:
        # Khong cho mat khau chi gom toan so.
        if password.isdigit():
            raise ValidationError(
                "Mật khẩu không được chỉ gồm toàn số.",
                code="password_entirely_numeric",
            )

    def get_help_text(self) -> str:
        return "Mật khẩu không được chỉ gồm toàn số."


class VietnamesePasswordComplexityValidator:
    def validate(self, password: str, user=None) -> None:
        # Yeu cau mat khau co it nhat chu hoa, chu thuong va so.
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "Mật khẩu phải có ít nhất một chữ in hoa.",
                code="password_no_upper",
            )
        if not re.search(r"[a-z]", password):
            raise ValidationError(
                "Mật khẩu phải có ít nhất một chữ thường.",
                code="password_no_lower",
            )
        if not re.search(r"\d", password):
            raise ValidationError(
                "Mật khẩu phải có ít nhất một chữ số.",
                code="password_no_digit",
            )

    def get_help_text(self) -> str:
        return "Mật khẩu phải có chữ hoa, chữ thường và số."
