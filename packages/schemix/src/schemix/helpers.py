"""Helper functions for creating database connections."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from schemix.connection import PostgreSQLConnection, SQLiteConnection

if TYPE_CHECKING:
    pass


async def create_sqlite_connection(database_path: str, **kwargs: Any) -> SQLiteConnection:
    """Create a SQLite connection with proper setup.

    Args:
        database_path: Path to SQLite database file (use ":memory:" for in-memory)
        **kwargs: Additional arguments passed to aiosqlite.connect()

    Returns:
        SQLiteConnection instance ready for use
    """
    try:
        import aiosqlite
    except ImportError as e:
        raise ImportError("aiosqlite is required for SQLite connections") from e

    conn = await aiosqlite.connect(database_path, **kwargs)
    # Enable foreign key constraints by default
    await conn.execute("PRAGMA foreign_keys = ON")
    await conn.commit()

    return SQLiteConnection(conn)


async def create_postgresql_connection(
    connection_string: str, **kwargs: Any
) -> PostgreSQLConnection:
    """Create a PostgreSQL connection.

    Args:
        connection_string: PostgreSQL connection string
        **kwargs: Additional arguments passed to asyncpg.connect()

    Returns:
        PostgreSQLConnection instance ready for use
    """
    try:
        import asyncpg
    except ImportError as e:
        raise ImportError("asyncpg is required for PostgreSQL connections") from e

    conn = await asyncpg.connect(connection_string, **kwargs)
    return PostgreSQLConnection(conn)


async def create_postgresql_pool(
    connection_string: str, min_size: int = 10, max_size: int = 10, **kwargs: Any
) -> PostgreSQLConnection:
    """Create a PostgreSQL connection pool.

    Args:
        connection_string: PostgreSQL connection string
        min_size: Minimum number of connections in pool
        max_size: Maximum number of connections in pool
        **kwargs: Additional arguments passed to asyncpg.create_pool()

    Returns:
        PostgreSQLConnection instance wrapping a connection pool
    """
    try:
        import asyncpg
    except ImportError as e:
        raise ImportError("asyncpg is required for PostgreSQL connections") from e

    pool = await asyncpg.create_pool(
        connection_string, min_size=min_size, max_size=max_size, **kwargs
    )
    return PostgreSQLConnection(pool)
