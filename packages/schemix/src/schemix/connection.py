from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Never

from schemix.dialects import Dialect


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
    async def close(self) -> None:
        """Close the connection."""
        ...

    @abstractmethod
    async def execute(
        self, query: str, params: Sequence[Any] | None = None
    ) -> Sequence[Mapping[str, Any]] | None:
        """Execute a query and return the results."""
        ...

    @abstractmethod
    async def executemany(
        self, query: str, params: Sequence[Sequence[Any]]
    ) -> Sequence[Mapping[str, Any]] | None:
        """Execute a query and return the results."""
        ...

    # @abstractmethod
    # def commit(self) -> None:
    #     """Commit the current transaction."""
    #     ...

    # @abstractmethod
    # def rollback(self) -> None:
    #     """Rollback the current transaction."""
    #     ...


class SQLiteConnection(AsyncConnection):
    """Connection class for SQLite."""

    dialect = Dialect.SQLITE

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

        assert aiosqlite is not None, "aiosqlite is not installed"
        self._conn: aiosqlite.Connection | None = None

    async def __aenter__(self) -> SQLiteConnection:
        self._conn = await aiosqlite.connect(self.database_path)
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: Any
    ) -> None:
        if self._conn is not None:
            await self._conn.close()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def connect(self) -> None:
        if self._conn is None:
            self._conn = await aiosqlite.connect(self.database_path)
            # Enable foreign key constraints
            await self._conn.execute("PRAGMA foreign_keys = ON")
            await self._conn.commit()

    async def execute(
        self, query: str, params: Sequence[Any] | None = None
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        if self._conn is None:
            raise RuntimeError("Connection is not open")

        if params is None:
            params = []

        cursor = await self._conn.execute(query, params)
        rows = await cursor.fetchall()

        # Get column names from cursor description
        column_names = [desc[0] for desc in cursor.description] if cursor.description else []

        # Convert rows to a list of dictionaries
        results = []
        for row in rows:
            row_dict = dict(zip(column_names, row, strict=False))
            results.append(row_dict)

        await cursor.close()
        return results

    async def executemany(
        self, query: str, params: Sequence[Sequence[Any]]
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        if self._conn is None:
            raise RuntimeError("Connection is not open")

        cursor = await self._conn.executemany(query, params)
        rows = await cursor.fetchall()

        # Get column names from cursor description
        column_names = [desc[0] for desc in cursor.description] if cursor.description else []

        # Convert rows to a list of dictionaries
        results = []
        for row in rows:
            row_dict = dict(zip(column_names, row, strict=False))
            results.append(row_dict)

        await cursor.close()
        return results


class PostgreSQLConnection(AsyncConnection):
    """Connection class for PostgreSQL."""

    dialect = Dialect.POSTGRESQL

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

        assert asyncpg is not None, "asyncpg is not installed"
        self._conn: asyncpg.Connection | None = None

    async def __aenter__(self) -> PostgreSQLConnection:
        self._conn = await asyncpg.connect(self.connection_string)
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: Any
    ) -> None:
        if self._conn is not None:
            await self._conn.close()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def connect(self) -> None:
        if self._conn is None:
            self._conn = await asyncpg.connect(self.connection_string)

    async def execute(
        self, query: str, params: Sequence[Any] | None = None
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        if self._conn is None:
            raise RuntimeError("Connection is not open")

        if params is None:
            params = []

        # asyncpg returns Record objects, convert to dicts
        rows = await self._conn.fetch(query, *params)
        results = [dict(row) for row in rows]

        return results

    async def executemany(
        self, query: str, params: Sequence[Sequence[Any]]
    ) -> list[dict[str, Any]] | None:
        """Execute a query and return the results."""
        if self._conn is None:
            raise RuntimeError("Connection is not open")

        await self._conn.executemany(query, params)

        return None
