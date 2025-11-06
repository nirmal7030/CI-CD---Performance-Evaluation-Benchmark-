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
        # request.body is bytes; decode safely
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Simple API key check for security
    api_key = request.headers.get("X-Bench-Key")
    if api_key != settings.BENCH_API_KEY:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # ✅ Use your actual model fields (short names)
    metric = Metric.objects.create(
        source=payload.get("source", "manual"),
        workflow=payload.get("workflow", ""),
        run_id=payload.get("run_id", ""),
        branch=payload.get("branch", ""),
        commit_sha=payload.get("commit_sha", ""),

        # Match actual DB field names exactly
        lce=payload.get("lce"),
        prt=payload.get("prt"),
        smo=payload.get("smo"),
        dept=payload.get("dept"),
        clbc=payload.get("clbc"),

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

    rows = [
        {
            "t": m.created_at.isoformat(),
            "lce": m.lce,
            "prt": m.prt,
            "smo": m.smo,
            "dept": m.dept,
            "clbc": m.clbc,
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
