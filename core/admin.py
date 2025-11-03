from django.contrib import admin
from .models import CICDRun

@admin.register(CICDRun)
class CICDRunAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "LCE", "PRT", "DEPT", "SMO", "CLBC", "APP_LAT", "source", "pipeline_ref")
    list_filter  = ("source",)
    ordering     = ("-timestamp",)
