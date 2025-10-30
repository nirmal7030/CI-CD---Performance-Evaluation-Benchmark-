import urllib.request, sys
url = "http://127.0.0.1:8000/health"
try:
    r = urllib.request.urlopen(url, timeout=5)
    sys.exit(0 if r.status == 200 else 1)
except Exception:
    sys.exit(1)
