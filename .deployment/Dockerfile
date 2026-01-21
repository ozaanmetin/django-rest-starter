# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM base AS production

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd --gid 1000 django \
    && useradd --uid 1000 --gid django --shell /bin/bash --create-home django

# Copy application code
COPY --chown=django:django . .

# Create directories for static/media files
RUN mkdir -p /app/staticfiles /app/media /app/.logs \
    && chown -R django:django /app/staticfiles /app/media /app/.logs

# Copy and set permissions for scripts
COPY --chown=django:django .deployment/entrypoint.sh /entrypoint.sh
COPY --chown=django:django .deployment/start.sh /start.sh
RUN chmod +x /entrypoint.sh /start.sh

USER django

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]
