# ==============================================================================
# AIRA Production Backend Dockerfile
# Multi-threaded Gunicorn WSGI runtime on Python 3.10 slim base with non-root user.
# ==============================================================================

FROM python:3.10-slim AS runtime

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000 \
    HOST=0.0.0.0

# Install runtime dependencies (curl for container health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-privileged system user and group
RUN groupadd --gid 10001 aira && \
    useradd --uid 10001 --gid aira --shell /bin/sh --create-home aira

# Set working directory
WORKDIR /app

# Install Python production dependencies first for optimal layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source, migrations, run entrypoint, and docker scripts
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY run.py .
COPY docker/ ./docker/

# Ensure entrypoint script is executable and set correct file ownership
RUN chmod +x ./docker/entrypoint.sh && \
    chown -R aira:aira /app

# Switch to non-root user
USER aira

# Expose backend service port
EXPOSE 5000

# Container healthcheck against process liveness endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health/live || exit 1

# Configure entrypoint and default command (Gunicorn WSGI)
ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--worker-class", "gthread", "--worker-tmp-dir", "/dev/shm", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
