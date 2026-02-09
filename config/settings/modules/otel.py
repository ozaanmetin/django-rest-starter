"""
OpenTelemetry configuration settings.

This module contains the core settings for OpenTelemetry.
When OTEL_ENABLED=false, no overhead is incurred.

All three signals (traces, metrics, logs) are exported via OTLP protocol,
making the application backend-agnostic.

Environment variables:
    OTEL_ENABLED: Enable/disable telemetry (default: false)
    OTEL_SERVICE_NAME: Service name shown in traces/metrics/logs
    OTEL_SERVICE_VERSION: Service version for resource identification
    OTEL_EXPORTER_OTLP_ENDPOINT: Collector endpoint for all signals (default: http://localhost:4317)
    OTEL_TRACES_SAMPLER_RATIO: Sampling ratio (0.0-1.0, 0.1 recommended for prod)
    OTEL_METRICS_ENABLED: Enable/disable metrics export (default: true)
    OTEL_LOGS_ENABLED: Enable/disable logs export via OTLP (default: true)
    OTEL_SYSTEM_METRICS_ENABLED: Enable CPU/memory/disk metrics (default: true)
"""

import environ

env = environ.Env()

# Main switch - when false, no instrumentation is loaded
OTEL_ENABLED = env.bool("OTEL_ENABLED", default=False)

# Service identity - appears in traces, metrics, and logs
OTEL_SERVICE_NAME = env.str("OTEL_SERVICE_NAME", default="drf-starter")
OTEL_SERVICE_VERSION = env.str("OTEL_SERVICE_VERSION", default="1.0.0")
OTEL_DEPLOYMENT_ENVIRONMENT = env.str("OTEL_DEPLOYMENT_ENVIRONMENT", default="development")

# OTLP exporter endpoint (gRPC) - single endpoint for all signals
OTEL_EXPORTER_OTLP_ENDPOINT = env.str("OTEL_EXPORTER_OTLP_ENDPOINT", default="http://localhost:4317")

# Sampling ratio: 1.0 = all requests, 0.1 = 10%
# Use 1.0 for development, 0.1-0.5 for production
OTEL_TRACES_SAMPLER_RATIO = env.float("OTEL_TRACES_SAMPLER_RATIO", default=1.0)

# Metrics configuration - exported via OTLP (not Prometheus pull model)
OTEL_METRICS_ENABLED = env.bool("OTEL_METRICS_ENABLED", default=True)
OTEL_METRICS_EXPORT_INTERVAL_MS = env.int("OTEL_METRICS_EXPORT_INTERVAL_MS", default=10000)

# Logs configuration - exported via OTLP
OTEL_LOGS_ENABLED = env.bool("OTEL_LOGS_ENABLED", default=True)

# System metrics (CPU, memory, disk, network)
OTEL_SYSTEM_METRICS_ENABLED = env.bool("OTEL_SYSTEM_METRICS_ENABLED", default=True)
