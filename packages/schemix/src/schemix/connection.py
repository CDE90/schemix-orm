from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Never

from schemix.dialects import Dialect
from schemix.exceptions import ConnectionError


# Trick the type checker into thinking that these imports are never None
# while maintaining runtime safety
def _never() -> Never:  # type: ignore
    pass


try:
    import aiosqlite
except ImportError:
    if TYPE_CHECKING:
        _never()
    else:
        aiosqlite = None

try:
    import asyncpg
except ImportError:
    if TYPE_CHECKING:
        _never()
    else:
        asyncpg = None


class AsyncConnection(ABC):
    """Abstract base class for database connections."""

    dialect: Dialect

    @abstractmethod
    async def execute(
        self, query: str, params: Sequence[Any] | None = None
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        ...

    @abstractmethod
    async def executemany(
        self, query: str, params: Sequence[Sequence[Any]]
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        ...


class SQLiteConnection(AsyncConnection):
    """Wrapper for SQLite connections using aiosqlite."""

    dialect = Dialect.SQLITE

    def __init__(self, connection: aiosqlite.Connection) -> None:
        assert aiosqlite is not None, "aiosqlite is not installed"
        self._conn = connection

    def _deserialize_json_fields(self, row_dict: dict[str, Any]) -> dict[str, Any]:
        """Deserialize JSON fields in SQLite results."""
        for key, value in row_dict.items():
            if isinstance(value, str):
                try:
                    # Try to parse as JSON if it looks like JSON
                    if value.strip().startswith(("{", "[")):
                        row_dict[key] = json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    # If it fails, keep as string
                    pass
        return row_dict

    async def execute(
        self, query: str, params: Sequence[Any] | None = None
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        if params is None:
            params = []

        try:
            cursor = await self._conn.execute(query, params)
            rows = await cursor.fetchall()

            # Get column names from cursor description
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []

            # Convert rows to a list of dictionaries
            results = []
            for row in rows:
                row_dict = dict(zip(column_names, row, strict=False))
                # Deserialize JSON fields for SQLite
                row_dict = self._deserialize_json_fields(row_dict)
                results.append(row_dict)

            await cursor.close()
            return results
        except Exception as e:
            raise ConnectionError(f"Failed to execute query: {e}") from e

    async def executemany(
        self, query: str, params: Sequence[Sequence[Any]]
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        try:
            cursor = await self._conn.executemany(query, params)
            rows = await cursor.fetchall()

            # Get column names from cursor description
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []

            # Convert rows to a list of dictionaries
            results = []
            for row in rows:
                row_dict = dict(zip(column_names, row, strict=False))
                # Deserialize JSON fields for SQLite
                row_dict = self._deserialize_json_fields(row_dict)
                results.append(row_dict)

            await cursor.close()
            return results
        except Exception as e:
            raise ConnectionError(f"Failed to execute many: {e}") from e


class PostgreSQLConnection(AsyncConnection):
    """Wrapper for PostgreSQL connections using asyncpg."""

    dialect = Dialect.POSTGRESQL

    def __init__(self, connection: asyncpg.Connection | asyncpg.Pool) -> None:
        assert asyncpg is not None, "asyncpg is not installed"
        self._conn = connection

    async def execute(
        self, query: str, params: Sequence[Any] | None = None
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        if params is None:
            params = []

        try:
            # Handle both Connection and Pool
            if isinstance(self._conn, asyncpg.Pool):
                async with self._conn.acquire() as conn:
                    rows = await conn.fetch(query, *params)
            else:
                rows = await self._conn.fetch(query, *params)

            # asyncpg returns Record objects, convert to dicts
            results = [dict(row) for row in rows]
            return results
        except Exception as e:
            raise ConnectionError(f"Failed to execute query: {e}") from e

    async def executemany(
        self, query: str, params: Sequence[Sequence[Any]]
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        try:
            # Handle both Connection and Pool
            if isinstance(self._conn, asyncpg.Pool):
                async with self._conn.acquire() as conn:
                    await conn.executemany(query, params)
            else:
                await self._conn.executemany(query, params)
            return None
        except Exception as e:
            raise ConnectionError(f"Failed to execute many: {e}") from e
