"""Centralized logging configuration for Schemix ORM."""

import logging
import os
import sys
from typing import Any


def stream_supports_colour(stream: Any) -> bool:
    """Check if the given stream supports ANSI color codes.

    Based on discord.py's implementation for cross-platform color support.
    """
    is_a_tty = hasattr(stream, "isatty") and stream.isatty()
    if sys.platform != "win32":
        return is_a_tty

    # ANSICON checks for things like ConEmu
    # WT_SESSION checks if this is Windows Terminal
    # VSCode built-in terminal supports colour too
    return is_a_tty and (
        "ANSICON" in os.environ
        or "WT_SESSION" in os.environ
        or os.environ.get("TERM_PROGRAM") == "vscode"
    )


class _ColourFormatter(logging.Formatter):
    """Color formatter for terminal output with ANSI escape codes."""

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    LEVEL_COLOURS = [
        (logging.DEBUG, "\x1b[36;1m"),  # Cyan for debug
        (logging.INFO, "\x1b[34;1m"),  # Blue for info
        (logging.WARNING, "\x1b[33;1m"),  # Yellow for warning
        (logging.ERROR, "\x1b[31;1m"),  # Red for error
        (logging.CRITICAL, "\x1b[41m"),  # Red background for critical
    ]

    FORMATS = {
        level: logging.Formatter(
            f"\x1b[90m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record: Any) -> str:
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module name.

    Args:
        name: The module name (typically __name__)

    Returns:
        A configured logger instance
    """
    return logging.getLogger(f"schemix.{name}")


def configure_logging(
    level: int = logging.INFO,
    format_string: str | None = None,
    handler: logging.Handler | None = None,
    use_colors: bool | None = None,
) -> None:
    """Configure logging for the Schemix ORM with optional color support.

    Args:
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages (ignored if use_colors=True)
        handler: Custom handler, defaults to StreamHandler
        use_colors: Whether to use colored output. If None, auto-detects terminal support
    """
    if handler is None:
        handler = logging.StreamHandler(sys.stdout)

    # Auto-detect color support if not specified
    if use_colors is None:
        # Check if handler has a stream attribute (StreamHandler does)
        stream = getattr(handler, 'stream', None)
        use_colors = stream is not None and stream_supports_colour(stream)

    # Configure the root schemix logger
    logger = logging.getLogger("schemix")
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for existing_handler in logger.handlers[:]:
        logger.removeHandler(existing_handler)

    # Choose formatter based on color support
    if use_colors:
        formatter: logging.Formatter = _ColourFormatter()
    else:
        if format_string is None:
            format_string = "[{asctime}] [{levelname:<8}] {name}: {message}"
        formatter = logging.Formatter(format_string, "%Y-%m-%d %H:%M:%S", style="{")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False


def log_sql_query(logger: logging.Logger, sql: str, params: list[Any]) -> None:
    """Log an SQL query with parameters at DEBUG level.

    Args:
        logger: The logger instance
        sql: The SQL query string
        params: The query parameters
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Executing SQL: %s", sql)
        if params:
            logger.debug("Parameters: %s", params)


def log_performance(logger: logging.Logger, operation: str, duration: float) -> None:
    """Log performance information at INFO level.

    Args:
        logger: The logger instance
        operation: Description of the operation
        duration: Duration in seconds
    """
    logger.info("Operation '%s' completed in %.3f seconds", operation, duration)


def log_connection_event(logger: logging.Logger, event: str, details: str | None = None) -> None:
    """Log connection-related events at INFO level.

    Args:
        logger: The logger instance
        event: The connection event (e.g., 'connected', 'disconnected')
        details: Optional additional details
    """
    if details:
        logger.info("Connection %s: %s", event, details)
    else:
        logger.info("Connection %s", event)
