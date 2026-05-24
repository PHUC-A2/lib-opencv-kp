from django.contrib import admin

from apps.processing.models import ProcessedImage, ProcessingHistory, ProcessingJob, ProcessingParameter


@admin.register(ProcessingJob)
class ProcessingJobAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "algorithm", "status", "execution_time_ms", "created_at")
    list_filter = ("status", "algorithm")
    search_fields = ("user__username", "source_image__original_filename")
    readonly_fields = ("created_at", "updated_at", "completed_at")


@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "stored_filename", "width", "height", "file_size", "created_at")
    search_fields = ("stored_filename", "job__user__username")


@admin.register(ProcessingParameter)
class ProcessingParameterAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "param_key", "param_value")
    search_fields = ("param_key", "job__id")


@admin.register(ProcessingHistory)
class ProcessingHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "action", "created_at")
    list_filter = ("action",)
    search_fields = ("message", "job__id")
