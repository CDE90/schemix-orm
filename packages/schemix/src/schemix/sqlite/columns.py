"""SQLite-specific column types."""

from __future__ import annotations

import datetime
from typing import Any

from schemix.base import (
    ColumnType,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    NumericOperatorMixin,
    OrderedOperatorMixin,
    StringOperatorMixin,
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
    NumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[int],
):
    def get_sql_type(self) -> str:
        return "INTEGER"


class Real(
    NumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[float],
):
    def get_sql_type(self) -> str:
        return "REAL"


class Text(
    StringOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[str],
):
    def get_sql_type(self) -> str:
        return "TEXT"


class Blob(CountOperatorMixin, ColumnType[bytes]):
    def get_sql_type(self) -> str:
        return "BLOB"


class Numeric(
    NumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[float],
):
    def __init__(self, col_name: str, *, precision: int, scale: int = 0) -> None:
        super().__init__(col_name, precision=precision, scale=scale)

    def get_sql_type(self) -> str:
        precision = self._type_params["precision"]
        scale = self._type_params["scale"]
        return f"NUMERIC({precision}, {scale})"


class Date(
    OrderedOperatorMixin, CountOperatorMixin, MinMaxOperatorMixin, ColumnType[datetime.date]
):
    def get_sql_type(self) -> str:
        return "TEXT"  # SQLite stores dates as TEXT


class Time(
    OrderedOperatorMixin, CountOperatorMixin, MinMaxOperatorMixin, ColumnType[datetime.time]
):
    def get_sql_type(self) -> str:
        return "TEXT"  # SQLite stores times as TEXT


class Timestamp(
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[datetime.datetime],
):
    def get_sql_type(self) -> str:
        return "TEXT"  # SQLite stores timestamps as TEXT


class JSON(CountOperatorMixin, ColumnType[dict[str, Any] | list[Any]]):
    def get_sql_type(self) -> str:
        return "TEXT"  # SQLite stores JSON as TEXT
