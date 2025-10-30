from django import forms
from .models import Run

class RunForm(forms.ModelForm):
    class Meta:
        model = Run
        fields = [
            "pipeline", "branch", "commit_sha", "run_id",
            "lce", "prt_seconds", "dept_seconds", "smo_ratio", "clbc_ratio",
            "notes"
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3})
        }
