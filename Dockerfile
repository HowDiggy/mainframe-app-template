# ==============================================================================
# Build Stage: Install dependencies and compile virtualenv
# ==============================================================================
FROM python:3.13-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip "poetry==2.0.1"

COPY pyproject.toml poetry.lock* README.md ./

# Configure poetry to create virtualenv inside /app/.venv
RUN poetry config virtualenvs.in-project true && \
    poetry install --only main --no-root --no-interaction

COPY src ./src
RUN poetry install --only main --no-interaction

# ==============================================================================
# Runtime Stage: Minimal attack surface & non-root user
# ==============================================================================
FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8000

WORKDIR /app

# Create non-root group and user (UID/GID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/false -m appuser

# Copy virtualenv and application from builder
COPY --from=builder --chown=10001:10001 /app/.venv /app/.venv
COPY --from=builder --chown=10001:10001 /app/src /app/src

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8000/healthz", timeout=2)' || exit 1

ENTRYPOINT ["python3", "-m", "mainframe_template.main"]
