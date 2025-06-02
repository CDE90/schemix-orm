"""Schema generation utilities for schemix ORM."""

from __future__ import annotations

from typing import TYPE_CHECKING

from schemix.dialects import Dialect
from schemix.logging import get_logger

if TYPE_CHECKING:
    from schemix.base import ColumnType
    from schemix.table import BaseTable


def generate_column_sql(column: ColumnType, dialect: Dialect) -> str:
    """Generate SQL column definition including constraints."""
    parts = [f"{column.col_name} {column.get_sql_type()}"]

    # Add constraints
    if column.is_primary_key:
        parts.append("PRIMARY KEY")

    if not column.is_nullable:
        parts.append("NOT NULL")

    if column.is_unique and not column.is_primary_key:
        parts.append("UNIQUE")

    if column.default_value is not None:
        if isinstance(column.default_value, str):
            parts.append(f"DEFAULT '{column.default_value}'")
        elif isinstance(column.default_value, bool):
            # Handle boolean defaults per dialect
            if dialect == Dialect.SQLITE:
                parts.append(f"DEFAULT {int(column.default_value)}")
            else:
                parts.append(f"DEFAULT {str(column.default_value).upper()}")
        else:
            parts.append(f"DEFAULT {column.default_value}")

    return " ".join(parts)


def generate_foreign_key_constraint_sql(column: ColumnType, dialect: Dialect) -> str:
    """Generate SQL for foreign key constraint."""
    if not column._references:
        raise ValueError("Column does not have a foreign key reference")

    ref_column = column._references
    if not ref_column._table_cls:
        raise ValueError("Referenced column does not have a table class")

    ref_table = ref_column._table_cls.get_table_name()
    ref_col_name = ref_column.col_name

    constraint = f"FOREIGN KEY ({column.col_name}) REFERENCES {ref_table}({ref_col_name})"

    if column._on_delete:
        constraint += f" ON DELETE {column._on_delete}"

    if column._on_update:
        constraint += f" ON UPDATE {column._on_update}"

    return constraint


def generate_create_table_sql(table_cls: type[BaseTable], dialect: Dialect) -> str:
    """Generate CREATE TABLE SQL for a table class."""
    logger = get_logger("schema")
    table_name = table_cls.get_table_name()
    columns = table_cls.get_columns()

    logger.debug(
        "Generating CREATE TABLE SQL for table '%s' with dialect '%s'", table_name, dialect
    )

    # Generate column definitions
    column_definitions = []
    foreign_key_constraints = []

    for column in columns.values():
        column_definitions.append(generate_column_sql(column, dialect))

        # Collect foreign key constraints
        if column._references:
            foreign_key_constraints.append(generate_foreign_key_constraint_sql(column, dialect))

    # Combine all table elements
    table_elements = column_definitions + foreign_key_constraints

    sql = f"CREATE TABLE {table_name} (\n"
    sql += ",\n".join(f"  {element}" for element in table_elements)
    sql += "\n)"

    logger.info(
        "Generated CREATE TABLE SQL for table '%s' (%d columns, %d foreign keys)",
        table_name,
        len(column_definitions),
        len(foreign_key_constraints),
    )
    logger.debug("Generated SQL: %s", sql)

    return sql
