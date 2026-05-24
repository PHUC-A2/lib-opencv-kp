import sys
from pathlib import Path

from django.conf import settings
from loguru import logger

from apps.admin_panel.models import SystemLog

_configured = False


def configure_loguru() -> None:
    # Cau hinh loguru 1 lan khi Django khoi dong.
    global _configured
    if _configured:
        return

    logs_dir = Path(settings.BASE_DIR) / "logs"
    logs_dir.mkdir(exist_ok=True)

    logger.remove()
    logger.configure(extra={"module": "system"})
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[module]}</cyan> | {message}",
    )
    logger.add(
        logs_dir / "app.log",
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[module]} | {message}",
    )
    _configured = True


class SystemLogService:
    @staticmethod
    def log(
        level: str,
        module: str,
        message: str,
        *,
        user=None,
        job=None,
        execution_time_ms: int | None = None,
    ) -> SystemLog:
        # Ghi log vao DB va loguru file/console.
        configure_loguru()

        log_entry = SystemLog.objects.create(
            level=level,
            module=module,
            message=message,
            execution_time_ms=execution_time_ms,
            user=user,
            job=job,
        )

        log_fn = getattr(logger.bind(module=module), level, logger.info)
        extra_parts = []
        if execution_time_ms is not None:
            extra_parts.append(f"{execution_time_ms}ms")
        if job:
            extra_parts.append(f"job#{job.pk}")
        if user:
            extra_parts.append(f"user={user.username}")

        full_message = message
        if extra_parts:
            full_message = f"{message} ({', '.join(extra_parts)})"

        log_fn(full_message)
        return log_entry

    @staticmethod
    def info(module: str, message: str, **kwargs) -> SystemLog:
        return SystemLogService.log(SystemLog.LEVEL_INFO, module, message, **kwargs)

    @staticmethod
    def warning(module: str, message: str, **kwargs) -> SystemLog:
        return SystemLogService.log(SystemLog.LEVEL_WARNING, module, message, **kwargs)

    @staticmethod
    def error(module: str, message: str, **kwargs) -> SystemLog:
        return SystemLogService.log(SystemLog.LEVEL_ERROR, module, message, **kwargs)

    @staticmethod
    def get_logs(
        search: str = "",
        level: str = "",
        module: str = "",
        date_from=None,
        date_to=None,
    ):
        # Truy van log he thong voi bo loc admin.
        from datetime import datetime, time

        from django.db.models import Q
        from django.utils import timezone

        queryset = SystemLog.objects.select_related("user", "job").order_by("-created_at")

        if search:
            term = search.strip()
            queryset = queryset.filter(
                Q(message__icontains=term)
                | Q(user__username__icontains=term)
                | Q(job__id__icontains=term)
            )

        if level:
            queryset = queryset.filter(level=level)

        if module:
            queryset = queryset.filter(module=module)

        if date_from:
            start_dt = timezone.make_aware(datetime.combine(date_from, time.min))
            queryset = queryset.filter(created_at__gte=start_dt)

        if date_to:
            end_dt = timezone.make_aware(datetime.combine(date_to, time.max))
            queryset = queryset.filter(created_at__lte=end_dt)

        return queryset

    @staticmethod
    def get_slow_processing_logs(limit: int = 5):
        # Lay cac job cham nhat de admin phan tich thuat toan.
        return (
            SystemLog.objects.filter(
                execution_time_ms__isnull=False,
                module__in=[SystemLog.MODULE_PROCESSING, SystemLog.MODULE_PIPELINE],
            )
            .select_related("user", "job")
            .order_by("-execution_time_ms")[:limit]
        )
