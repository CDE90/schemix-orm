"""Schemix ORM - Type-safe ORM for Python."""

# Core table and column types
from schemix.columns import (
    JSON,
    JSONB,
    BigInt,
    BigSerial,
    Boolean,
    Char,
    ColumnType,
    Date,
    Decimal,
    Integer,
    Numeric,
    Serial,
    SmallInt,
    SmallSerial,
    Text,
    Time,
    Timestamp,
    Varchar,
)
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
    # Column types
    "ColumnType",
    "Integer",
    "SmallInt",
    "BigInt",
    "Serial",
    "SmallSerial",
    "BigSerial",
    "Numeric",
    "Decimal",
    "Varchar",
    "Text",
    "Char",
    "Boolean",
    "Date",
    "Time",
    "Timestamp",
    "JSON",
    "JSONB",
    # Schema utilities
    "generate_create_table_sql",
    "generate_column_sql",
    "generate_foreign_key_constraint_sql",
]


def hello() -> str:
    return "Hello from schemix!"
