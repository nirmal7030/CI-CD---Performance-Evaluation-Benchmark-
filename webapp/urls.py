# webapp/urls.py

from django.contrib import admin
from django.urls import path, include
from core.views import health, index

urlpatterns = [
    path("admin/", admin.site.urls),

    # Core endpoints
    path("health", health),   # /health
    path("hello", index),     # /hello

    # Bench app (dashboard + metrics APIs)
    path("", include("bench.urls")),
]
