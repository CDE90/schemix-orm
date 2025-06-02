from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Never

from schemix.dialects import Dialect
from schemix.exceptions import SchemixConnectionError
from schemix.logging import get_logger, log_connection_event, log_performance, log_sql_query


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
    async def executemany(self, query: str, params: Sequence[Sequence[Any]]) -> None:
        """Execute a batch query without returning results."""
        ...


class SQLiteConnection(AsyncConnection):
    """Wrapper for SQLite connections using aiosqlite."""

    dialect = Dialect.SQLITE

    def __init__(self, connection: aiosqlite.Connection) -> None:
        assert aiosqlite is not None, "aiosqlite is not installed"
        self._conn = connection
        self._logger = get_logger("connection.sqlite")
        log_connection_event(self._logger, "initialized", f"SQLite connection to {connection}")

    async def execute(
        self, query: str, params: Sequence[Any] | None = None
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        if params is None:
            params = []

        start_time = time.perf_counter()
        log_sql_query(self._logger, query, list(params))

        try:
            cursor = await self._conn.execute(query, params)
            rows = await cursor.fetchall()

            # Get column names from cursor description
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []

            # Convert rows to a list of dictionaries
            results = []
            for row in rows:
                row_dict = dict(zip(column_names, row, strict=True))
                results.append(row_dict)

            await cursor.close()

            duration = time.perf_counter() - start_time
            log_performance(
                self._logger, f"SQLite query execution (returned {len(results)} rows)", duration
            )

            return results
        except Exception as e:
            self._logger.error("Failed to execute query: %s", str(e))
            raise SchemixConnectionError(f"Failed to execute query: {e}") from e

    async def executemany(self, query: str, params: Sequence[Sequence[Any]]) -> None:
        """Execute a batch query without returning results."""
        start_time = time.perf_counter()
        self._logger.debug("Executing batch query: %s with %d parameter sets", query, len(params))

        try:
            cursor = await self._conn.executemany(query, params)
            await cursor.close()

            duration = time.perf_counter() - start_time
            log_performance(
                self._logger, f"SQLite batch execution ({len(params)} statements)", duration
            )

            return None
        except Exception as e:
            self._logger.error("Failed to execute batch query: %s", str(e))
            raise SchemixConnectionError(f"Failed to execute many: {e}") from e


class PostgreSQLConnection(AsyncConnection):
    """Wrapper for PostgreSQL connections using asyncpg."""

    dialect = Dialect.POSTGRESQL

    def __init__(self, connection: asyncpg.Connection | asyncpg.Pool) -> None:
        assert asyncpg is not None, "asyncpg is not installed"
        self._conn = connection
        self._logger = get_logger("connection.postgresql")
        conn_type = "Pool" if isinstance(connection, asyncpg.Pool) else "Connection"
        log_connection_event(self._logger, "initialized", f"PostgreSQL {conn_type}")

    async def execute(
        self, query: str, params: Sequence[Any] | None = None
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        if params is None:
            params = []

        start_time = time.perf_counter()
        log_sql_query(self._logger, query, list(params))

        try:
            # Handle both Connection and Pool
            if isinstance(self._conn, asyncpg.Pool):
                async with self._conn.acquire() as conn:
                    rows = await conn.fetch(query, *params)
            else:
                rows = await self._conn.fetch(query, *params)

            # asyncpg returns Record objects, convert to dicts
            results = [dict(row) for row in rows]

            duration = time.perf_counter() - start_time
            log_performance(
                self._logger, f"PostgreSQL query execution (returned {len(results)} rows)", duration
            )

            return results
        except Exception as e:
            self._logger.error("Failed to execute query: %s", str(e))
            raise SchemixConnectionError(f"Failed to execute query: {e}") from e

    async def executemany(self, query: str, params: Sequence[Sequence[Any]]) -> None:
        """Execute a batch query without returning results."""
        start_time = time.perf_counter()
        self._logger.debug("Executing batch query: %s with %d parameter sets", query, len(params))

        try:
            # Handle both Connection and Pool
            if isinstance(self._conn, asyncpg.Pool):
                async with self._conn.acquire() as conn:
                    await conn.executemany(query, params)
            else:
                await self._conn.executemany(query, params)

            duration = time.perf_counter() - start_time
            log_performance(
                self._logger, f"PostgreSQL batch execution ({len(params)} statements)", duration
            )

            return None
        except Exception as e:
            self._logger.error("Failed to execute batch query: %s", str(e))
            raise SchemixConnectionError(f"Failed to execute many: {e}") from e
