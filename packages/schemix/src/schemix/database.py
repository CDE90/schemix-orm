from __future__ import annotations

from collections.abc import Mapping
from typing import TypeVar

from schemix.base import ColumnType
from schemix.connection import AsyncConnection
from schemix.query import SQLExpression
from schemix.query.insert import InsertBuilder
from schemix.query.select import SelectBuilder
from schemix.table import BaseTable

CType = TypeVar("CType", bound=Mapping[str, ColumnType | SQLExpression])


class Database:
    """Main database interface for schemix.

    Provides query building capabilities and schema management for SQLite and PostgreSQL.
    Supports type-safe queries through mypy plugin integration.

    Args:
        connection: Pre-configured AsyncConnection instance (SQLiteConnection or PostgreSQLConnection)
        tables: List of table classes to include in the database
    """

    def __init__(self, connection: AsyncConnection, tables: list[type[BaseTable]]) -> None:
        self.connection = connection
        self.tables = tables

    def select(self, columns: CType) -> SelectBuilder[CType]:
        """Create a SELECT query builder.

        Args:
            columns: Dictionary mapping alias names to column objects

        Returns:
            SelectBuilder instance for chaining query operations

        Example:
            >>> query = db.select({"user_id": User.id, "name": User.name})
        """
        return SelectBuilder(columns, self)

    def insert(self, table: type[BaseTable]) -> InsertBuilder:
        """Create an INSERT query builder.

        Args:
            table: Table class to insert into

        Returns:
            InsertBuilder instance for chaining query operations

        Example:
            >>> await db.insert(User).values({"name": "John", "email": "john@example.com"}).execute()
        """
        return InsertBuilder(table, self)
