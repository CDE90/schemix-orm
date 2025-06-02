"""SQLite-specific column types."""

from __future__ import annotations

import datetime
from typing import Any

from schemix.base import (
    ColumnType,
    CountOperatorMixin,
    DateSerializationMixin,
    JSONSerializationMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    OrderedOperatorMixin,
    PassthroughSerializationMixin,
    SQLiteNumericOperatorMixin,
    StringOperatorMixin,
    TimeSerializationMixin,
    TimestampSerializationMixin,
)

__all__ = [
    "Integer",
    "Real",
    "Text",
    "Blob",
    "Numeric",
    "Date",
    "Time",
    "Timestamp",
    "JSON",
]


class Integer(
    PassthroughSerializationMixin,
    SQLiteNumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[int],
):
    def get_sql_type(self) -> str:
        return "INTEGER"


class Real(
    PassthroughSerializationMixin,
    SQLiteNumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[float],
):
    def get_sql_type(self) -> str:
        return "REAL"


class Text(
    PassthroughSerializationMixin,
    StringOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[str],
):
    def get_sql_type(self) -> str:
        return "TEXT"


class Blob(PassthroughSerializationMixin, CountOperatorMixin, ColumnType[bytes]):
    def get_sql_type(self) -> str:
        return "BLOB"


class Numeric(
    PassthroughSerializationMixin,
    SQLiteNumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[float],
):
    def __init__(self, col_name: str, *, precision: int, scale: int = 0) -> None:
        if precision <= 0 or scale < 0 or scale >= precision:
            raise ValueError("Precision must be > 0 and scale must be >= 0 and < precision.")

        super().__init__(col_name, precision=precision, scale=scale)

    def get_sql_type(self) -> str:
        precision = self._type_params["precision"]
        scale = self._type_params["scale"]
        return f"NUMERIC({precision}, {scale})"


class Date(
    DateSerializationMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[datetime.date],
):
    def get_sql_type(self) -> str:
        return "TEXT"  # SQLite stores dates as TEXT


class Time(
    TimeSerializationMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[datetime.time],
):
    def get_sql_type(self) -> str:
        return "TEXT"  # SQLite stores times as TEXT


class Timestamp(
    TimestampSerializationMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[datetime.datetime],
):
    def get_sql_type(self) -> str:
        return "TEXT"  # SQLite stores timestamps as TEXT


class JSON(JSONSerializationMixin, CountOperatorMixin, ColumnType[Any]):
    def get_sql_type(self) -> str:
        return "TEXT"  # SQLite stores JSON as TEXT
