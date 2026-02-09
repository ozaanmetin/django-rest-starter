"""
Logging configuration settings.

Structured logging with trace correlation. When OTEL_ENABLED=true and
OTEL_LOGS_ENABLED=true, logs are also exported via OTLP to the configured
backend.

Console and file handlers are always active as fallback/local debugging.
The OTLP handler is added dynamically by setup_telemetry() when enabled.

Environment variables:
    LOG_LEVEL: Minimum log level (default: INFO)
    LOG_FILE_PATH: Directory for log files (default: logs)
    LOG_FILE_ENABLED: Enable file logging (default: true)
"""

from pathlib import Path

import environ

env = environ.Env()

# Environment-based configuration
LOG_LEVEL = env.str("LOG_LEVEL", default="INFO")
LOG_FILE_ENABLED = env.bool("LOG_FILE_ENABLED", default=True)
LOG_FILE_PATH = Path(env.str("LOG_FILE_PATH", default="logs"))

if LOG_FILE_ENABLED:
    LOG_FILE_PATH.mkdir(parents=True, exist_ok=True)

# Base handlers - console is always enabled
_handlers = {
    "console": {
        "class": "logging.StreamHandler",
        "formatter": "json",
        "filters": ["trace_context"],
    },
}

# Add file handler if enabled (useful for local debugging or as fallback)
if LOG_FILE_ENABLED:
    _handlers["file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": str(LOG_FILE_PATH / "app.log"),
        "maxBytes": 10 * 1024 * 1024,  # 10MB
        "backupCount": 5,
        "formatter": "json",
        "filters": ["trace_context"],
        "encoding": "utf-8",
    }

# Determine which handlers to use
_root_handlers = ["console"]
if LOG_FILE_ENABLED:
    _root_handlers.append("file")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "trace_context": {
            "()": "core.logging.TraceContextFilter",
        },
    },
    "formatters": {
        "json": {
            "()": "core.logging.JsonFormatter",
        },
        "console": {
            "format": "{asctime} {levelname} {name} [trace_id={trace_id}] {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": _handlers,
    "loggers": {
        # Reduce noise from third-party libraries
        "opentelemetry": {"level": "WARNING"},
        "urllib3": {"level": "WARNING"},
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": _root_handlers,
    },
}
