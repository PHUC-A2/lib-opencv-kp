from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.authentication.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Hien thi cac cot quan trong trong admin.
    list_display = ("id", "username", "email", "full_name", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "full_name")
    ordering = ("-created_at",)

    fieldsets = UserAdmin.fieldsets + (
        ("Thong tin bo sung", {"fields": ("full_name", "avatar_url", "role")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Thong tin bo sung", {"fields": ("full_name", "email", "role")}),
    )
