# J.A.R.V.I.S — Dockerfile
# Production-ready container for local WebSocket + audio mode

FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libportaudio2 \
    portaudio19-dev \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

FROM base AS dependencies

COPY requirements-local.txt .
RUN pip install --no-cache-dir -r requirements-local.txt

FROM dependencies AS application

COPY . .
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8765
EXPOSE 9765

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:9765/health/live || exit 1

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
