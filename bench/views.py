from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count
from django.http import JsonResponse, HttpResponseForbidden
from .models import Run
from .forms import RunForm
from django.conf import settings

def dashboard(request):
    # KPIs
    kpis = Run.objects.aggregate(
        avg_lce=Avg('lce'),
        avg_prt=Avg('prt_seconds'),
        avg_dept=Avg('dept_seconds'),
        avg_smo=Avg('smo_ratio'),
        avg_clbc=Avg('clbc_ratio'),
        count=Count('id'),
    )
    # Data for charts: average per pipeline
    by_pipeline = (Run.objects
                   .values('pipeline')
                   .annotate(avg_lce=Avg('lce'),
                             avg_prt=Avg('prt_seconds'),
                             avg_dept=Avg('dept_seconds'),
                             avg_smo=Avg('smo_ratio'),
                             avg_clbc=Avg('clbc_ratio'),
                             cnt=Count('id'))
                   .order_by('pipeline'))
    return render(request, "bench/dashboard.html", {"kpis": kpis, "by_pipeline": list(by_pipeline)})

def runs_list(request):
    pipeline = request.GET.get('pipeline')
    runs = Run.objects.all().order_by("-created_at")
    if pipeline:
        runs = runs.filter(pipeline=pipeline)
    return render(request, "bench/runs_list.html", {"runs": runs, "pipeline": pipeline})

def run_detail(request, pk):
    run = get_object_or_404(Run, pk=pk)
    return render(request, "bench/run_detail.html", {"run": run})

def run_new(request):
    if request.method == "POST":
        form = RunForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("runs_list")
    else:
        form = RunForm()
    return render(request, "bench/run_form.html", {"form": form})

# Simple ingest API: send JSON with an API key
def api_ingest(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    api_key = request.headers.get("X-API-KEY") or request.GET.get("api_key")
    expected = getattr(settings, "BENCH_API_KEY", None)
    if not expected or api_key != expected:
        return HttpResponseForbidden("Invalid API key")

    import json
    data = json.loads(request.body or "{}")
    run = Run.objects.create(
        pipeline=data.get("pipeline", "github"),
        branch=data.get("branch", "main"),
        commit_sha=data.get("commit_sha", ""),
        run_id=data.get("run_id", ""),
        lce=data.get("lce"),
        prt_seconds=data.get("prt_seconds"),
        dept_seconds=data.get("dept_seconds"),
        smo_ratio=data.get("smo_ratio"),
        clbc_ratio=data.get("clbc_ratio"),
        notes=data.get("notes", ""),
    )
    return JsonResponse({"status": "ok", "id": run.id})
