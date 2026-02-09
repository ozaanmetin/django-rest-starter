"""
OpenTelemetry initialization module.

Call setup_telemetry() once at application startup (wsgi.py, celery.py).

Provides unified OTLP export for all three observability signals:
- Traces: Distributed tracing with automatic instrumentation
- Metrics: Application and system metrics
- Logs: Python logging integration with trace correlation

All signals are exported via OTLP protocol, making the application
backend-agnostic.
"""

import logging

logger = logging.getLogger(__name__)

_initialized = False


def setup_telemetry() -> bool:
    """
    Initialize OpenTelemetry instrumentation for traces, metrics, and logs.

    All signals are exported via OTLP to the configured endpoint.
    This makes the application backend-agnostic - switch from Jaeger
    to Signoz by just changing OTEL_EXPORTER_OTLP_ENDPOINT.

    Note: The OTLP logging handler is attached AFTER Django's dictConfig runs
    (via setup_otlp_logging) to prevent Django from overwriting it.
    In wsgi.py, call setup_telemetry() before Django, then setup_otlp_logging() after.
    In celery.py, call setup_telemetry() in worker_process_init (Django is already loaded).

    Returns:
        bool: True if telemetry was initialized, False if skipped or already initialized.

    Example:
        # In wsgi.py
        from core.telemetry import setup_telemetry, setup_otlp_logging
        setup_telemetry()
        application = get_wsgi_application()  # Django's dictConfig runs here
        setup_otlp_logging()                  # Add OTLP handler after dictConfig
    """
    global _initialized

    if _initialized:
        return False

    from django.conf import settings

    if not getattr(settings, "OTEL_ENABLED", False):
        logger.info("OpenTelemetry disabled (OTEL_ENABLED=false)")
        return False

    try:
        resource = _create_resource(settings)
        _configure_tracing(settings, resource)
        _configure_metrics(settings, resource)
        _instrument_libraries()
        _initialized = True
        logger.info(
            "OpenTelemetry initialized - exporting to %s",
            settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        )
        return True
    except Exception as e:
        logger.warning("Failed to initialize OpenTelemetry: %s", e)
        return False


_logging_initialized = False


def setup_otlp_logging() -> bool:
    """
    Attach the OTLP logging handler to the root logger.

    Must be called AFTER Django's LOGGING dictConfig has been applied
    (i.e., after get_wsgi_application()), otherwise Django will overwrite
    the handler during its logging setup.

    Returns:
        bool: True if the handler was added, False if skipped.
    """
    global _logging_initialized

    if _logging_initialized or not _initialized:
        return False

    from django.conf import settings

    if not getattr(settings, "OTEL_ENABLED", False):
        return False

    try:
        resource = _create_resource(settings)
        _configure_logging(settings, resource)
        _logging_initialized = True
        logger.debug("OTLP logging handler attached to root logger")
        return True
    except Exception as e:
        logger.warning("Failed to setup OTLP logging: %s", e)
        return False


def _create_resource(settings):
    """Create shared resource for all signals (traces, metrics, logs)."""
    from opentelemetry.sdk.resources import Resource

    # Using string keys directly instead of deprecated ResourceAttributes
    # See: https://opentelemetry.io/docs/specs/semconv/resource/
    return Resource.create(
        {
            "service.name": settings.OTEL_SERVICE_NAME,
            "service.version": getattr(settings, "OTEL_SERVICE_VERSION", "1.0.0"),
            "deployment.environment": getattr(settings, "OTEL_DEPLOYMENT_ENVIRONMENT", "development"),
        }
    )


def _configure_tracing(settings, resource) -> None:
    """Configure distributed tracing with OTLP export."""
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.propagate import set_global_textmap
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    # Sampler controls what percentage of traces are recorded
    sampler = TraceIdRatioBased(settings.OTEL_TRACES_SAMPLER_RATIO)

    # TracerProvider is the main entry point for tracing
    provider = TracerProvider(resource=resource, sampler=sampler)
    trace.set_tracer_provider(provider)

    # W3C TraceContext propagator - extracts trace ID from 'traceparent' header
    set_global_textmap(TraceContextTextMapPropagator())

    # OTLP exporter sends traces to collector via gRPC
    exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True,
    )

    # BatchSpanProcessor batches spans before sending (more efficient)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    logger.debug("Tracing configured with OTLP export")


def _configure_metrics(settings, resource) -> None:
    """Configure metrics with OTLP export (push model, not Prometheus pull)."""
    if not getattr(settings, "OTEL_METRICS_ENABLED", True):
        logger.info("OpenTelemetry metrics disabled")
        return

    from opentelemetry import metrics
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

    # OTLP metric exporter - pushes metrics to collector
    exporter = OTLPMetricExporter(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True,
    )

    # PeriodicExportingMetricReader pushes metrics at regular intervals
    export_interval = getattr(settings, "OTEL_METRICS_EXPORT_INTERVAL_MS", 10000)
    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=export_interval,
    )

    # MeterProvider is the main entry point for metrics
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)

    # Initialize system metrics (CPU, memory, etc.)
    _configure_system_metrics(settings)
    logger.debug("Metrics configured with OTLP export (interval: %dms)", export_interval)


def _configure_system_metrics(settings) -> None:
    """Configure system metrics collection (CPU, memory, disk, network)."""
    if not getattr(settings, "OTEL_SYSTEM_METRICS_ENABLED", True):
        return

    try:
        from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor

        SystemMetricsInstrumentor().instrument()
    except Exception as e:
        logger.warning("Failed to enable system metrics: %s", e)


def _configure_logging(settings, resource) -> None:
    """Configure Python logging to export via OTLP."""
    if not getattr(settings, "OTEL_LOGS_ENABLED", True):
        logger.info("OpenTelemetry logs disabled")
        return

    from core.telemetry.handlers import OTLPLoggingHandler

    # Create OTLP logging handler
    handler = OTLPLoggingHandler.create(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        resource=resource,
        level=logging.INFO,
    )

    # Add to root logger so all logs are captured
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    logger.debug("Logging configured with OTLP export")


def _instrument_libraries() -> None:
    """Apply auto-instrumentation to supported libraries."""
    from opentelemetry.instrumentation.celery import CeleryInstrumentor
    from opentelemetry.instrumentation.django import DjangoInstrumentor
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor

    # Django: traces HTTP requests, middleware, views
    DjangoInstrumentor().instrument()

    # Celery: traces task execution, retries
    CeleryInstrumentor().instrument()

    # Redis: traces cache operations
    RedisInstrumentor().instrument()

    # PostgreSQL: traces database queries
    Psycopg2Instrumentor().instrument()


def shutdown_telemetry() -> None:
    """
    Gracefully shutdown all telemetry providers.

    Call this on application shutdown to ensure all buffered
    data is flushed to the backend.
    """
    from opentelemetry import metrics, trace

    from core.telemetry.handlers import shutdown_logging

    # Shutdown tracing
    tracer_provider = trace.get_tracer_provider()
    if hasattr(tracer_provider, "shutdown"):
        tracer_provider.shutdown()

    # Shutdown metrics
    meter_provider = metrics.get_meter_provider()
    if hasattr(meter_provider, "shutdown"):
        meter_provider.shutdown()

    # Shutdown logging
    shutdown_logging()

    logger.info("OpenTelemetry shutdown complete")
