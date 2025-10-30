FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Create a non-root user (best practice)
RUN useradd -ms /bin/bash appuser

# ---- dependencies layer (cacheable) ----
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# ---- app layer ----
COPY . .

# Normalize Windows line endings in entrypoint.sh and make it executable
# (no sed / dos2unix needed; pure Python one-liner)
RUN python -c "import pathlib; p=pathlib.Path('/app/entrypoint.sh'); \
b=p.read_bytes() if p.exists() else b''; \
b=b[3:] if b.startswith(b'\xef\xbb\xbf') else b; \
b=b.replace(b'\r\n', b'\n'); \
(p.write_bytes(b),) if b else None" && \
    chmod +x /app/entrypoint.sh

# Tiny Python healthcheck script (written without heredoc)
RUN /bin/sh -c 'printf "%s\n" \
"import urllib.request,sys" \
"u=\"http://127.0.0.1:8000/health\"" \
"try:" \
"    r=urllib.request.urlopen(u, timeout=5)" \
"    sys.exit(0 if r.status==200 else 1)" \
"except Exception:" \
"    sys.exit(1)" > /app/healthcheck.py'

# Permissions and runtime user
RUN chown -R appuser:appuser /app
USER appuser

# Healthcheck (no shell tricks)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["python", "/app/healthcheck.py"]

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
