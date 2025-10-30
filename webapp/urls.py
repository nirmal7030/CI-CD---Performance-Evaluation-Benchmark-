from django.contrib import admin
from django.urls import path
from core.views import health, index
from bench import views as bench_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health', health),
    path('', bench_views.dashboard, name="dashboard"),
    path('runs/', bench_views.runs_list, name="runs_list"),
    path('runs/new/', bench_views.run_new, name="run_new"),
    path('runs/<int:pk>/', bench_views.run_detail, name="run_detail"),
    path('api/runs/ingest', bench_views.api_ingest, name="api_ingest"),
    path('hello', index),
]
