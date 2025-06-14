"""Schemix ORM - Type-safe ORM for Python."""

from schemix.connection import AsyncConnection, PostgreSQLConnection, SQLiteConnection

# Database and connection
from schemix.database import Database

# Dialects
from schemix.dialects import Dialect

# Schema generation utilities
from schemix.schema import (
    generate_column_sql,
    generate_create_table_sql,
    generate_foreign_key_constraint_sql,
)
from schemix.table import BaseTable

__all__ = [
    # Core classes
    "BaseTable",
    "Database",
    "AsyncConnection",
    "SQLiteConnection",
    "PostgreSQLConnection",
    "Dialect",
    # Schema utilities
    "generate_create_table_sql",
    "generate_column_sql",
    "generate_foreign_key_constraint_sql",
]
