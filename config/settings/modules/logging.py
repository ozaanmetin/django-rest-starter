"""
Logging configuration settings for the Django application.
"""


import os
from enum import Enum
from pathlib import Path

import environ

env = environ.Env()


# Enums
# ---------------------------------------------------

class LogLevel(str, Enum):
    """Log level constants for type-safe configuration."""
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


class LogFormatter(str, Enum):
    """Available log formatters."""
    JSON = 'json'
    DETAILED = 'detailed'
    SIMPLE = 'simple'


# Logging Handlers
# ---------------------------------------------------

def rotating_file_handler(
    logger_name: str,
    level: LogLevel = LogLevel.INFO,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5,
    formatter: LogFormatter = LogFormatter.DETAILED,
) -> str:
    """
    Creates a RotatingFileHandler configuration.

    Args:
        logger_name: Name of the logger (used to create subdirectory path)
        level: Minimum log level for this handler
        max_bytes: Maximum size per log file before rotation (default: 5MB)
        backup_count: Number of backup files to keep (default: 5)
        formatter: Log formatter to use

    Returns:
        Handler name to be used in logger configuration
    """
    LOG_DIR = Path(env.str('LOG_FILE_PATH', default='logs'))
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    log_path = LOG_DIR / logger_name.replace('.', os.sep)
    log_path.mkdir(parents=True, exist_ok=True)

    handler_name = f'{logger_name}_{level.lower()}_rotating'
    HANDLERS[handler_name] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': str(log_path / f'{level.lower()}.log'),
        'maxBytes': max_bytes,
        'backupCount': backup_count,
        'formatter': formatter.value,
        'encoding': 'utf-8',
        'level': level.value,
    }
    return handler_name


# Logger Creation Function
# ---------------------------------------------------

def create_logger(
    level: LogLevel = LogLevel.INFO,
    console: bool = True,
    handlers: list = None,
) -> dict:
    """
    Creates a logger configuration dictionary.

    Args:
        level: Minimum log level for this logger
        console: Whether to output to console (default: True)
        handlers: List of callables that return handler names

    Returns:
        Logger configuration dictionary
    """
    handler_list = []

    if console:
        handler_list.append('console')

    if handlers:
        for handler_fn in handlers:
            handler_name = handler_fn()
            handler_list.append(handler_name)

    return {
        'level': level.value,
        'handlers': handler_list,
        'propagate': False,
    }   


# Logging Configuration
# ---------------------------------------------------

FORMATTERS = {
    'json': {
        '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        'format': '%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s',
    },
    'detailed': {
        'format': '{asctime} {levelname} {name} [{module}:{funcName}:{lineno}] {message}',
        'style': '{',
        'datefmt': '%Y-%m-%d %H:%M:%S',
    },
    'simple': {
        'format': '{asctime} {levelname} {name} {message}',
        'style': '{',
        'datefmt': '%Y-%m-%d %H:%M:%S',
    },
}

# rotating file handlers will be added dynamically
HANDLERS = {
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': LogFormatter.SIMPLE.value,
        'level': LogLevel.DEBUG.value,
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': FORMATTERS,
    'handlers': HANDLERS,
    'loggers': {
        # django loggers
        'django': create_logger(handlers=[
            lambda: rotating_file_handler('django', level=LogLevel.INFO, formatter=LogFormatter.SIMPLE),
            lambda: rotating_file_handler('django', level=LogLevel.ERROR),
        ]),
        'django.request': create_logger(handlers=[
            lambda: rotating_file_handler('django.request', level=LogLevel.INFO),
            lambda: rotating_file_handler('django.request', level=LogLevel.ERROR),
        ]),
        # celery loggers
        'celery': create_logger(handlers=[
            lambda: rotating_file_handler('celery', level=LogLevel.INFO),
            lambda: rotating_file_handler('celery', level=LogLevel.ERROR),
        ]),
    },
    'root': {
        'level': LogLevel.INFO.value,
        'handlers': ['console'],
    },
}
