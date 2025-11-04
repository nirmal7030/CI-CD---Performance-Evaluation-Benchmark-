from django.contrib import admin
from .models import Metric


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "source",
        "workflow",
        "branch",
        "lce",    # Layer Cache Efficiency
        "prt",    # Pipeline Recovery Time
        "smo",    # Secrets Mgmt Overhead
        "dept",   # Dynamic Env Provisioning Time
        "clbc",   # Cross-Layer Build Consistency
    )
    list_filter = ("source", "workflow", "branch", "created_at")
    search_fields = ("run_id", "branch", "commit_sha", "notes")
    ordering = ("-created_at",)
