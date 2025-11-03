from django.contrib import admin
from .models import Metric

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ("created_at", "pipeline_total_s", "build_duration_s", "test_duration_s",
                    "deploy_duration_s", "app_latency_s", "success_flag", "cloud_consistency",
                    "branch", "workflow")
    list_filter  = ("source", "workflow", "branch")
    search_fields = ("commit_sha", "notes")
    ordering = ("-created_at",)
