from django.contrib import admin

from apps.admin_panel.models import SystemLog


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ("id", "level", "module", "message_short", "execution_time_ms", "user", "job", "created_at")
    list_filter = ("level", "module", "created_at")
    search_fields = ("message", "user__username")
    readonly_fields = ("created_at",)

    @admin.display(description="Noi dung")
    def message_short(self, obj: SystemLog) -> str:
        return obj.message[:80]
