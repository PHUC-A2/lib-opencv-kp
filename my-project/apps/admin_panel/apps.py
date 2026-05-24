from django.apps import AppConfig


class AdminPanelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.admin_panel"
    label = "admin_panel"

    def ready(self) -> None:
        # Khoi tao loguru khi Django startup.
        from apps.admin_panel.services.system_log_service import configure_loguru

        configure_loguru()
