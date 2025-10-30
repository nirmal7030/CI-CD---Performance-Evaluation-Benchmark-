import json
from django.test import Client

def test_health_endpoint_returns_ok():
    c = Client()
    resp = c.get("/health")
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data["status"] == "ok"
