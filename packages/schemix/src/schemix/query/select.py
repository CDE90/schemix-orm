from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, Self, TypeVar

from schemix.columns import ColumnType
from schemix.dialects import ParameterCollector
from schemix.exceptions import QueryError
from schemix.query import SQLExpression
from schemix.table import BaseTable

if TYPE_CHECKING:
    from schemix.database import Database


CType = TypeVar("CType", bound=Mapping[str, ColumnType | SQLExpression])


class SelectBuilder[CType]:
    """Initial query builder for SELECT statements.

    Created by Database.select() and provides the from_() method
    to specify the source table for the query.
    """

    def __init__(self, columns: CType, database: Database) -> None:
        self.columns = columns
        self.database = database

    def from_(self, table: type[BaseTable]) -> SelectBase[CType]:
        """Specify the source table for the query.

        Args:
            table: Table class to query from

        Returns:
            SelectBase instance with full query building capabilities
        """
        return SelectBase(self.columns, table, self.database)


JoinType = Literal["inner", "left", "right", "full", "cross"]


@dataclass
class JoinClause:
    join_type: JoinType
    table: type[BaseTable]
    on: SQLExpression | None = None


@dataclass
class SelectConfig:
    where: SQLExpression | None = None
    having: SQLExpression | None = None
    group_by: list[ColumnType] | None = None
    order_by: tuple[SQLExpression | ColumnType, ...] | None = None
    limit: int | None = None
    offset: int | None = None
    joins: list[JoinClause] | None = None


class SelectBase[CType]:
    """Full-featured query builder for SELECT statements.

    Provides methods for building complex queries with WHERE clauses,
    JOINs, ordering, limiting, and more. Supports method chaining
    for fluent query construction.
    """

    def __init__(
        self,
        columns: CType,
        table: type[BaseTable],
        database: Database,
    ) -> None:
        self.columns = columns
        self.table = table
        self.database = database

        self.config = SelectConfig()

    def _create_join(
        self, join_type: JoinType, table: type[BaseTable], on: SQLExpression | None
    ) -> Self:
        if self.config.joins is None:
            self.config.joins = []

        join_clause = JoinClause(join_type=join_type, table=table, on=on)
        self.config.joins.append(join_clause)
        return self

    def left_join(self, table: type[BaseTable], on: SQLExpression) -> Self:
        return self._create_join("left", table, on)

    def right_join(self, table: type[BaseTable], on: SQLExpression) -> Self:
        return self._create_join("right", table, on)

    def inner_join(self, table: type[BaseTable], on: SQLExpression) -> Self:
        return self._create_join("inner", table, on)

    def full_join(self, table: type[BaseTable], on: SQLExpression) -> Self:
        return self._create_join("full", table, on)

    def cross_join(self, table: type[BaseTable]) -> Self:
        return self._create_join("cross", table, None)

    def where(self, expression: SQLExpression) -> Self:
        """Add WHERE clause to filter results.

        Args:
            expression: SQL expression for filtering rows

        Returns:
            Self for method chaining

        Example:
            >>> query.where(User.age > 18)
        """
        self.config.where = expression
        return self

    def having(self, expression: SQLExpression) -> Self:
        self.config.having = expression
        return self

    def group_by(self, *columns: ColumnType) -> Self:
        self.config.group_by = list(columns)
        return self

    def order_by(self, *args: SQLExpression | ColumnType) -> Self:
        self.config.order_by = args
        return self

    def limit(self, limit: int) -> Self:
        self.config.limit = limit
        return self

    def offset(self, offset: int) -> Self:
        self.config.offset = offset
        return self

    def get_sql(self) -> tuple[str, tuple[Any, ...]]:
        """Get the SQL query and parameters for the current query."""

        table_name = self.table.get_table_name()
        dialect = self.database.connection.dialect
        collector = ParameterCollector(dialect)

        # Build column list with qualified names
        select_columns = []
        for alias, column in self.columns.items():  # type: ignore[attr-defined]
            if isinstance(column, ColumnType):
                select_columns.append(f"{column._get_qualified_name()} AS {alias}")
            else:
                select_columns.append(column.to_sql(dialect, collector) + f" AS {alias}")

        sql = f"SELECT {', '.join(select_columns)} FROM {table_name}"

        # Add JOIN clauses
        if self.config.joins is not None:
            for join in self.config.joins:
                join_table_name = join.table.get_table_name()
                join_type = join.join_type.upper()

                if join_type == "CROSS":
                    sql += f" {join_type} JOIN {join_table_name}"
                else:
                    sql += f" {join_type} JOIN {join_table_name}"
                    if join.on is not None:
                        sql += f" ON {join.on.to_sql(dialect, collector)}"

        # Add WHERE clause
        if self.config.where is not None:
            sql += f" WHERE {self.config.where.to_sql(dialect, collector)}"

        # Add GROUP BY clause
        if self.config.group_by is not None:
            group_by_columns = ", ".join(
                [column._get_qualified_name() for column in self.config.group_by]
            )
            sql += f" GROUP BY {group_by_columns}"

        # Add HAVING clause
        if self.config.having is not None:
            sql += f" HAVING {self.config.having.to_sql(dialect, collector)}"

        # Add ORDER BY clause
        if self.config.order_by is not None:
            order_by_clauses = []
            for expr in self.config.order_by:
                if isinstance(expr, ColumnType):
                    order_by_clauses.append(expr._get_qualified_name())
                else:
                    order_by_clauses.append(expr.to_sql(dialect, collector))
            sql += f" ORDER BY {', '.join(order_by_clauses)}"

        # Add LIMIT clause
        if self.config.limit is not None:
            sql += f" LIMIT {self.config.limit}"

        # Add OFFSET clause
        if self.config.offset is not None:
            sql += f" OFFSET {self.config.offset}"

        return sql, tuple(collector.parameters)

    async def execute(self) -> list[CType]:
        """Execute the query and return the results."""
        try:
            sql, params = self.get_sql()
            results = await self.database.connection.execute(sql, params)
            return results or []  # type: ignore[return-value]
        except Exception as e:
            raise QueryError(f"Failed to execute select query: {e}") from e
