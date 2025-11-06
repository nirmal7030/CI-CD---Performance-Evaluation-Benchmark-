import json
import statistics

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Metric


@csrf_exempt
def api_ingest(request):
    """Receive metric data from CI/CD pipeline or API client."""
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        raw = request.body.decode("utf-8") or "{}"
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Simple API key check for security
    api_key = request.headers.get("X-Bench-Key")
    if api_key != settings.BENCH_API_KEY:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Helper: support both short and long keys in payload
    def get_metric_val(short_key: str, long_key: str):
        if short_key in payload:
            return payload.get(short_key)
        if long_key in payload:
            return payload.get(long_key)
        return None

    metric = Metric.objects.create(
        source=payload.get("source", "github"),
        workflow=payload.get("workflow", ""),
        run_id=payload.get("run_id", ""),
        run_attempt=payload.get("run_attempt", ""),
        branch=payload.get("branch", ""),
        commit_sha=payload.get("commit_sha", ""),

        # ✅ write into long field names that match DB columns
        layer_cache_efficiency=get_metric_val("lce", "layer_cache_efficiency"),
        pipeline_recovery_time=get_metric_val("prt", "pipeline_recovery_time"),
        secrets_mgmt_overhead=get_metric_val("smo", "secrets_mgmt_overhead"),
        dynamic_env_time=get_metric_val("dept", "dynamic_env_time"),
        cross_layer_consistency=get_metric_val("clbc", "cross_layer_consistency"),

        notes=payload.get("notes", ""),
    )

    return JsonResponse({"status": "stored", "id": metric.id})


def api_metrics_data(request):
    """
    Return aggregated metrics for dashboard display.
    Optional query param:
      ?source=github|jenkins|codepipeline
    """
    source = request.GET.get("source")
    qs = Metric.objects.order_by("-created_at")

    if source:
        qs = qs.filter(source=source)

    qs = qs[:100]

    # Read from long field names on the model and expose short keys in JSON
    rows = [
        {
            "t": m.created_at.isoformat(),
            "lce": m.layer_cache_efficiency,
            "prt": m.pipeline_recovery_time,
            "smo": m.secrets_mgmt_overhead,
            "dept": m.dynamic_env_time,
            "clbc": m.cross_layer_consistency,
        }
        for m in reversed(qs)
    ]

    def avg(vals):
        clean = [v for v in vals if v is not None]
        return round(statistics.fmean(clean), 2) if clean else 0.0

    data = {
        "count": Metric.objects.count(),
        "avg_lce": avg([r["lce"] for r in rows]),
        "avg_prt": avg([r["prt"] for r in rows]),
        "avg_smo": avg([r["smo"] for r in rows]),
        "avg_dept": avg([r["dept"] for r in rows]),
        "avg_clbc": avg([r["clbc"] for r in rows]),
        "rows": rows,
    }
    return JsonResponse(data)


def dashboard(request):
    """
    Render the dashboard shell (HTML/JS).
    The page itself is static; it calls /api/metrics/data via JS.
    """
    return render(request, "bench/dashboard.html")
