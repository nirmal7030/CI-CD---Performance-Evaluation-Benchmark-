from django.db import models


class Metric(models.Model):
    # ---- pipeline sources ----
    SOURCE_GITHUB = "github"
    SOURCE_JENKINS = "jenkins"
    SOURCE_CODEPIPELINE = "codepipeline"

    SOURCE_CHOICES = [
        (SOURCE_GITHUB, "GitHub Actions"),
        (SOURCE_JENKINS, "Jenkins"),
        (SOURCE_CODEPIPELINE, "AWS CodePipeline"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)

    # CI/CD context
    source = models.CharField(
        max_length=32,
        choices=SOURCE_CHOICES,
        default=SOURCE_GITHUB,
    )
    workflow = models.CharField(max_length=128, blank=True, default="")
    run_id = models.CharField(max_length=64, blank=True, default="")
    run_attempt = models.CharField(max_length=16, blank=True, default="")
    branch = models.CharField(max_length=128, blank=True, default="")
    commit_sha = models.CharField(max_length=64, blank=True, default="")

    # ✅ ORIGINAL long names that match the existing DB columns
    layer_cache_efficiency = models.FloatField(default=0.0)
    pipeline_recovery_time = models.FloatField(default=0.0)
    secrets_mgmt_overhead = models.FloatField(default=0.0)
    dynamic_env_time = models.FloatField(default=0.0)
    cross_layer_consistency = models.FloatField(default=0.0)

    notes = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.created_at:%Y-%m-%d %H:%M:%S} "
            f"[{self.source}] LCE={self.layer_cache_efficiency}"
        )
