"""
Custom log formatters for structured logging.

Why this still exists when we have OTLP logging:

This formatter handles console and file output (stdout, app.log).
OTLP handler (core/telemetry/handlers.py) is separate and sends logs to the collector.
Both run in parallel - they don't replace each other.

We keep this because:
- You still want to see logs in your terminal when developing
- Local log files are useful when OTLP collector is down
- When OTEL_ENABLED=False, this is the only log output
"""

import logging
from datetime import UTC, datetime

from pythonjsonlogger import jsonlogger


class JsonFormatter(jsonlogger.JsonFormatter):
    """
    Formats logs as JSON for console and file output.

    Not related to OTLP export - that's handled separately in core/telemetry/handlers.py.
    """

    def __init__(self, *args, service_name: str = "drf-starter", **kwargs):
        self.service_name = service_name
        super().__init__(*args, **kwargs)

    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        super().add_fields(log_record, record, message_dict)

        # Standard timestamp field
        log_record["@timestamp"] = datetime.now(UTC).isoformat()

        # Standard fields
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["service"] = self.service_name

        # Location info
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Trace context (set by TraceContextFilter)
        log_record["trace_id"] = getattr(record, "trace_id", "")
        log_record["span_id"] = getattr(record, "span_id", "")

        # Remove empty trace fields
        if not log_record["trace_id"]:
            del log_record["trace_id"]
        if not log_record["span_id"]:
            del log_record["span_id"]

        # Clean up redundant fields
        log_record.pop("asctime", None)
        log_record.pop("levelname", None)
        log_record.pop("name", None)
