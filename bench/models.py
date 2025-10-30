from django.db import models

class Run(models.Model):
    PIPELINE_CHOICES = [
        ('jenkins', 'Jenkins'),
        ('github', 'GitHub Actions'),
        ('codepipeline', 'AWS CodePipeline'),
    ]
    pipeline = models.CharField(max_length=20, choices=PIPELINE_CHOICES)
    branch = models.CharField(max_length=100, default='main')
    commit_sha = models.CharField(max_length=64, blank=True, default='')
    run_id = models.CharField(max_length=100, blank=True, default='')  # pipeline run id

    # Novel metrics (floats; store seconds or ratio 0..1 as noted)
    lce = models.FloatField(null=True, blank=True)           # 0..1
    prt_seconds = models.FloatField(null=True, blank=True)   # seconds
    dept_seconds = models.FloatField(null=True, blank=True)  # seconds
    smo_ratio = models.FloatField(null=True, blank=True)     # relative overhead 0..1
    clbc_ratio = models.FloatField(null=True, blank=True)    # 0..1

    created_at = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.get_pipeline_display()} #{self.id} ({self.branch})"
