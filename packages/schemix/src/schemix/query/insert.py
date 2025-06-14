from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from schemix.dialects import ParameterCollector
from schemix.exceptions import QueryError
from schemix.logging import get_logger, log_performance, log_sql_query
from schemix.table import BaseTable

if TYPE_CHECKING:
    from schemix.database import Database


@dataclass
class InsertConfig:
    values: dict[str, Any] | list[dict[str, Any]] | None = None


class InsertBuilder:
    """Query builder for INSERT statements.

    Provides methods for building INSERT queries with values.
    Supports method chaining for fluent query construction.
    """

    def __init__(self, table: type[BaseTable], database: Database) -> None:
        self.table = table
        self.database = database
        self._logger = get_logger("query.insert")
        self.config = InsertConfig()

    def values(self, values: dict[str, Any] | list[dict[str, Any]]) -> Self:
        """Set the values to insert.

        Args:
            values: Dictionary mapping column names to values, or list of such dictionaries for bulk insert

        Returns:
            Self for method chaining

        Examples:
            >>> query.values({"title": "New Post", "content": "Post content"})
            >>> query.values([
            ...     {"title": "Post 1", "content": "Content 1"},
            ...     {"title": "Post 2", "content": "Content 2"}
            ... ])
        """
        if isinstance(values, dict):
            self.config.values = dict(values)
        else:
            self.config.values = [dict(row) for row in values]
        return self

    def get_sql(self) -> tuple[str, tuple[Any, ...]]:
        """Get the SQL query and parameters for the current INSERT query."""
        if self.config.values is None:
            raise QueryError("INSERT query requires values. Use .values() method.")

        table_name = self.table.get_table_name()
        dialect = self.database.connection.dialect
        collector = ParameterCollector(dialect)

        # Get table columns to validate input and apply serialization
        table_columns = self.table.get_columns()

        # Handle both single dict and list of dicts
        values_list = (
            self.config.values if isinstance(self.config.values, list) else [self.config.values]
        )

        # Validate that all provided columns exist in the table
        all_columns = set()
        for row_values in values_list:
            for column_name in row_values.keys():
                if column_name not in table_columns:
                    raise QueryError(
                        f"Column '{column_name}' does not exist in table '{table_name}'"
                    )
                all_columns.add(column_name)

        # For bulk insert, ensure all rows have the same columns
        if len(values_list) > 1:
            first_row_columns = set(values_list[0].keys())
            for i, row_values in enumerate(values_list[1:], 1):
                row_columns = set(row_values.keys())
                if row_columns != first_row_columns:
                    raise QueryError(
                        f"Row {i} has different columns than first row. "
                        f"Expected: {sorted(first_row_columns)}, got: {sorted(row_columns)}"
                    )

        # Use columns from first row for consistency
        columns = list(values_list[0].keys())
        column_list = ", ".join(columns)

        # Serialize values using column-level serialization and build placeholders
        value_rows = []
        for row_values in values_list:
            serialized_row_values = []
            for column_name in columns:  # Use consistent column order
                column = table_columns[column_name]
                serialized_value = column.serialize(row_values[column_name])
                serialized_row_values.append(collector.add(serialized_value))
            value_rows.append(f"({', '.join(serialized_row_values)})")

        # Build the INSERT SQL
        values_clause = ", ".join(value_rows)
        sql = f"INSERT INTO {table_name} ({column_list}) VALUES {values_clause}"

        params_tuple = tuple(collector.parameters)
        log_sql_query(self._logger, sql, list(params_tuple))
        return sql, params_tuple

    async def execute(self) -> dict[str, Any]:
        """Execute the INSERT query and return information about the operation."""
        start_time = time.perf_counter()

        try:
            sql, params = self.get_sql()

            # Determine if this is a bulk insert
            is_bulk = isinstance(self.config.values, list)
            row_count = len(self.config.values) if is_bulk else 1  # type: ignore[arg-type]

            self._logger.debug(
                "Executing %s INSERT query on table '%s' (%d rows)",
                "bulk" if is_bulk else "single",
                self.table.get_table_name(),
                row_count,
            )

            result = await self.database.connection.execute(sql, params)

            duration = time.perf_counter() - start_time
            log_performance(
                self._logger,
                f"INSERT query execution (table: {self.table.get_table_name()}, rows: {row_count})",
                duration,
            )

            # Return insert result information
            return {
                "rows_affected": row_count,
                "is_bulk": is_bulk,
                "last_insert_id": getattr(result, "lastrowid", None)
                if hasattr(result, "lastrowid")
                else None,
            }
        except Exception as e:
            self._logger.error("Failed to execute INSERT query: %s", str(e))
            raise QueryError(f"Failed to execute insert query: {e}") from e
