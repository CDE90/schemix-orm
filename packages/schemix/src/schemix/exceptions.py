"""Custom exceptions for the Schemix ORM."""

from __future__ import annotations


class SchemixError(Exception):
    """Base exception for all Schemix ORM errors."""

    pass


class SchemixConnectionError(SchemixError):
    """Raised when there are database connection issues."""

    pass


class QueryError(SchemixError):
    """Raised when there are query execution issues."""

    pass


class ConfigurationError(SchemixError):
    """Raised when there are configuration issues."""

    pass


class SerializationError(SchemixError):
    """Raised when there are JSON serialization/deserialization issues."""

    pass
