# bench/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard (root path "/")
    path("", views.dashboard, name="dashboard"),

    # Novel metrics APIs
    path("api/metrics/data", views.api_metrics_data, name="api_metrics_data"),
    path("api/metrics/ingest", views.api_ingest, name="api_ingest"),
]
