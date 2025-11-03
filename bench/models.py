from django.db import models

class Metric(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # --- CI Context (kept from your original model) ---
    source       = models.CharField(max_length=32, default="github")   # github, manual, etc.
    workflow     = models.CharField(max_length=128, blank=True, default="")
    run_id       = models.CharField(max_length=64, blank=True, default="")
    run_attempt  = models.CharField(max_length=16, blank=True, default="")
    branch       = models.CharField(max_length=128, blank=True, default="")
    commit_sha   = models.CharField(max_length=64, blank=True, default="")

    # --- Generic CI/CD Performance Metrics (keep for backward compatibility) ---
    build_duration_s   = models.FloatField(default=0)   # Build time
    test_duration_s    = models.FloatField(default=0)   # Test time
    deploy_duration_s  = models.FloatField(default=0)   # Deploy duration
    app_latency_s      = models.FloatField(default=0)   # Health check latency
    pipeline_total_s   = models.FloatField(default=0)   # Total pipeline duration
    success_flag       = models.FloatField(default=1)   # 1=Success, 0=Failure
    cloud_consistency  = models.FloatField(default=1)   # 1=Consistent, 0=Inconsistent

    # --- Novel Metrics (your thesis focus) ---
    layer_cache_efficiency    = models.FloatField(null=True, blank=True, help_text="Layer Cache Efficiency (LCE, %)")
    pipeline_recovery_time    = models.FloatField(null=True, blank=True, help_text="Pipeline Recovery Time (PRT, s)")
    secrets_mgmt_overhead     = models.FloatField(null=True, blank=True, help_text="Secrets Management Overhead (SMO, s)")
    dynamic_env_time          = models.FloatField(null=True, blank=True, help_text="Dynamic Environment Provisioning Time (DEPT, s)")
    cross_layer_consistency   = models.FloatField(null=True, blank=True, help_text="Cross-Layer Build Consistency (CLBC, %)")

    # --- Optional developer notes ---
    notes = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Metric"
        verbose_name_plural = "Metrics"

    def __str__(self):
        return (
            f"Run {self.id or '?'} | {self.created_at:%Y-%m-%d %H:%M:%S} | "
            f"LCE={self.layer_cache_efficiency or 0} | PRT={self.pipeline_recovery_time or 0} | "
            f"SMO={self.secrets_mgmt_overhead or 0} | DEPT={self.dynamic_env_time or 0} | CLBC={self.cross_layer_consistency or 0}"
        )
