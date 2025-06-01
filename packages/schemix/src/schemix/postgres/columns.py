"""PostgreSQL-specific column types."""

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
    PassthroughSerializationMixin,
    StringOperatorMixin,
)
from schemix.query import BinaryExpression

__all__ = [
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
]


class PostgreSQLStringOperatorMixin(StringOperatorMixin):
    """PostgreSQL-specific string operators including ILIKE."""

    def ilike(self, other: Any):
        return BinaryExpression(self, "ILIKE", other)

    def not_ilike(self, other: Any):
        return BinaryExpression(self, "NOT ILIKE", other)


class Integer(
    PassthroughSerializationMixin,
    NumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[int],
):
    def get_sql_type(self) -> str:
        return "INTEGER"


class SmallInt(
    PassthroughSerializationMixin,
    NumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[int],
):
    def get_sql_type(self) -> str:
        return "SMALLINT"


class BigInt(
    PassthroughSerializationMixin,
    NumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[int],
):
    def get_sql_type(self) -> str:
        return "BIGINT"


class Serial(Integer):
    def get_sql_type(self) -> str:
        return "SERIAL"


class SmallSerial(SmallInt):
    def get_sql_type(self) -> str:
        return "SMALLSERIAL"


class BigSerial(BigInt):
    def get_sql_type(self) -> str:
        return "BIGSERIAL"


class Numeric(
    PassthroughSerializationMixin,
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


class Decimal(Numeric):
    def get_sql_type(self) -> str:
        precision = self._type_params["precision"]
        scale = self._type_params["scale"]
        return f"DECIMAL({precision}, {scale})"


class Varchar(
    PassthroughSerializationMixin,
    PostgreSQLStringOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[str],
):
    def __init__(self, col_name: str, *, length: int) -> None:
        super().__init__(col_name, length=length)

    def get_sql_type(self) -> str:
        length = self._type_params["length"]
        return f"VARCHAR({length})"


class Text(
    PassthroughSerializationMixin,
    PostgreSQLStringOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[str],
):
    def get_sql_type(self) -> str:
        return "TEXT"


class Char(
    PassthroughSerializationMixin,
    PostgreSQLStringOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[str],
):
    def __init__(self, col_name: str, *, length: int) -> None:
        super().__init__(col_name, length=length)

    def get_sql_type(self) -> str:
        length = self._type_params["length"]
        return f"CHAR({length})"


class Boolean(PassthroughSerializationMixin, CountOperatorMixin, ColumnType[bool]):
    def get_sql_type(self) -> str:
        return "BOOLEAN"


class Date(
    PassthroughSerializationMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[datetime.date],
):
    def get_sql_type(self) -> str:
        return "DATE"


class Time(
    PassthroughSerializationMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[datetime.time],
):
    def __init__(self, col_name: str, *, with_timezone: bool = False) -> None:
        super().__init__(col_name, with_timezone=with_timezone)

    def get_sql_type(self) -> str:
        with_timezone = self._type_params.get("with_timezone", False)
        return "TIME WITH TIME ZONE" if with_timezone else "TIME"


class Timestamp(
    PassthroughSerializationMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[datetime.datetime],
):
    def __init__(self, col_name: str, *, with_timezone: bool = False) -> None:
        super().__init__(col_name, with_timezone=with_timezone)

    def get_sql_type(self) -> str:
        with_timezone = self._type_params.get("with_timezone", False)
        return "TIMESTAMP WITH TIME ZONE" if with_timezone else "TIMESTAMP"


class JSON(
    PassthroughSerializationMixin, CountOperatorMixin, ColumnType[dict[str, Any] | list[Any]]
):
    def get_sql_type(self) -> str:
        return "JSON"


class JSONB(JSON):
    def get_sql_type(self) -> str:
        return "JSONB"
