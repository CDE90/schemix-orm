"""Custom exceptions for the Schemix ORM."""

from __future__ import annotations

from schemix.logging import get_logger


class SchemixError(Exception):
    """Base exception for all Schemix ORM errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        logger = get_logger("exceptions")
        logger.error("SchemixError: %s", message)


class SchemixConnectionError(SchemixError):
    """Raised when there are database connection issues."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Connection Error: {message}")


class QueryError(SchemixError):
    """Raised when there are query execution issues."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Query Error: {message}")


class ConfigurationError(SchemixError):
    """Raised when there are configuration issues."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Configuration Error: {message}")


class SerializationError(SchemixError):
    """Raised when there are JSON serialization/deserialization issues."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Serialization Error: {message}")
