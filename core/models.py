from django.db import models

class CICDRun(models.Model):
    # When the record was ingested
    timestamp = models.DateTimeField(auto_now_add=True)

    # Novel metrics (all optional floats defaulting to 0)
    LCE      = models.FloatField(default=0)   # Lead/Cycle Efficiency (s)
    PRT      = models.FloatField(default=0)   # Pipeline Runtime (s)
    DEPT     = models.FloatField(default=0)   # Deploy Time (s)
    SMO      = models.FloatField(default=0)   # Stability / success flag
    CLBC     = models.FloatField(default=0)   # Cloud Build Consistency (1=ok)
    APP_LAT  = models.FloatField(default=0)   # Latency (s)

    # Optional fields for provenance
    source       = models.CharField(max_length=50, default="github")
    pipeline_ref = models.CharField(max_length=100, blank=True, default="")
    commit_sha   = models.CharField(max_length=64, blank=True, default="")

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M:%S} PRT={self.PRT}s"
