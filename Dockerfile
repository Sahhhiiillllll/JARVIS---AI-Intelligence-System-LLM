# J.A.R.V.I.S — Dockerfile
# ========================
# Production-ready container for JARVIS AI assistant

# ---- Base Image ----
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    portaudio19-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# ---- Dependencies ----
FROM base AS dependencies

# Install Python dependencies
COPY requirements-local.txt .
RUN pip install --no-cache-dir -r requirements-local.txt

# ---- Application ----
FROM dependencies AS application

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8765  # WebSocket server
EXPOSE 8080  # HTTP health/metrics server (if we add one)

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8765/health/live || exit 1

# ---- Runtime ----
FROM application AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "main.py"]