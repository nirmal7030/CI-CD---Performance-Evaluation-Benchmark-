from django.contrib import admin
from .models import Run

@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ("id", "pipeline", "branch", "lce", "prt_seconds", "dept_seconds", "smo_ratio", "clbc_ratio", "created_at")
    list_filter = ("pipeline", "branch", "created_at")
    search_fields = ("commit_sha", "run_id", "notes")
