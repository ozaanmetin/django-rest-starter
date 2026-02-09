"""
Custom logging filters for the application.

Why this still exists when we have OTLP logging:

This filter adds trace_id/span_id to console and file logs.
OTLP handler (core/telemetry/handlers.py) does its own trace correlation via the SDK.
Both run in parallel - they don't replace each other.

We keep this because:
- You want to see trace IDs in terminal output when debugging
- Local log files should have trace correlation too
- When OTEL_ENABLED=False, this is the only way to get trace IDs in logs
"""

import logging


class TraceContextFilter(logging.Filter):
    """
    Adds trace_id and span_id to log records for console/file output.

    Not related to OTLP export - that's handled separately in core/telemetry/handlers.py.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Inject trace context into log record."""
        try:
            from opentelemetry import trace

            span = trace.get_current_span()
            span_context = span.get_span_context()

            if span_context.is_valid:
                record.trace_id = format(span_context.trace_id, "032x")
                record.span_id = format(span_context.span_id, "016x")
            else:
                record.trace_id = ""
                record.span_id = ""
        except ImportError:
            # OpenTelemetry not installed
            record.trace_id = ""
            record.span_id = ""

        return True
