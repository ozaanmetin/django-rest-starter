"""
OpenTelemetry logging handler for Python's logging module.

This handler bridges Python's standard logging to OpenTelemetry's logging SDK,
allowing logs to be exported via OTLP alongside traces and metrics.
"""

import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry._logs.severity import SeverityNumber
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import get_current_span

# Map Python log levels to OpenTelemetry severity numbers
_SEVERITY_MAP = {
    logging.DEBUG: SeverityNumber.DEBUG,
    logging.INFO: SeverityNumber.INFO,
    logging.WARNING: SeverityNumber.WARN,
    logging.ERROR: SeverityNumber.ERROR,
    logging.CRITICAL: SeverityNumber.FATAL,
}


class OTLPLoggingHandler(LoggingHandler):
    """
    A logging handler that exports logs via OTLP.

    This handler automatically:
    - Correlates logs with active traces (trace_id, span_id)
    - Maps Python log levels to OpenTelemetry severity
    - Batches and exports logs efficiently

    Usage:
        handler = OTLPLoggingHandler.create(
            endpoint="http://localhost:4317",
            resource=resource,
        )
        logging.getLogger().addHandler(handler)
    """

    @classmethod
    def create(
        cls,
        endpoint: str,
        resource: Resource,
        level: int = logging.NOTSET,
    ) -> "OTLPLoggingHandler":
        """
        Create and configure an OTLP logging handler.

        Args:
            endpoint: OTLP gRPC endpoint (e.g., "http://localhost:4317")
            resource: OpenTelemetry resource with service info
            level: Minimum log level to export

        Returns:
            Configured OTLPLoggingHandler instance
        """
        # Create the OTLP log exporter
        exporter = OTLPLogExporter(
            endpoint=endpoint,
            insecure=True,
        )

        # Create logger provider with batch processor
        # Configure batch processor for timely export:
        # - schedule_delay_millis: Export every 1 second (default 5000ms)
        # - max_export_batch_size: Export after 32 logs (default 512)
        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(
                exporter,
                schedule_delay_millis=1000,
                max_export_batch_size=32,
            )
        )

        # Set as global logger provider
        set_logger_provider(logger_provider)

        # Create handler with the provider
        handler = cls(level=level, logger_provider=logger_provider)
        return handler

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to OpenTelemetry.

        Automatically injects trace context if available.
        """
        # Enrich record with trace context if not already present
        if not hasattr(record, "otelSpanID"):
            span = get_current_span()
            if span:
                ctx = span.get_span_context()
                if ctx.is_valid:
                    record.otelTraceID = format(ctx.trace_id, "032x")
                    record.otelSpanID = format(ctx.span_id, "016x")

        super().emit(record)


def get_logger_provider() -> LoggerProvider | None:
    """Get the current OpenTelemetry logger provider if configured."""
    from opentelemetry._logs import get_logger_provider as _get_provider

    provider = _get_provider()
    if isinstance(provider, LoggerProvider):
        return provider
    return None


def shutdown_logging() -> None:
    """Shutdown the OTLP logging provider gracefully."""
    provider = get_logger_provider()
    if provider:
        provider.shutdown()
