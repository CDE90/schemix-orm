from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from typing import Any, Self

from schemix.dialects import Dialect, DialectNotSupportedError
from schemix.query import BinaryExpression, FunctionExpression
from schemix.table import BaseTable

__all__ = [
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
]


class ColumnType[T](ABC):
    """An abstract class representing a column type."""

    col_name: str
    _type_params: dict[str, Any]

    is_nullable: bool = True
    is_unique: bool = False
    is_primary_key: bool = False
    default_value: T | None = None

    _table_cls: type[BaseTable] | None = None

    def __init__(self, col_name: str, **kwargs: Any) -> None:
        self.col_name = col_name
        self._type_params = kwargs

    def __repr__(self) -> str:
        if self._table_cls:
            return f"{self.__class__.__name__}({self._table_cls.get_table_name()}.{self.col_name})"
        return f"{self.__class__.__name__}({self.col_name})"

    def _get_qualified_name(self) -> str:
        if self._table_cls:
            return f"{self._table_cls.get_table_name()}.{self.col_name}"
        return self.col_name

    @abstractmethod
    def _get_sql_type(self, dialect: Dialect) -> str: ...

    # Builder Methods
    def not_null(self) -> Self:
        """Marks the column as not nullable."""
        self.is_nullable = False
        return self

    def nullable(self) -> Self:
        """Marks the column as nullable."""
        self.is_nullable = True
        return self

    def unique(self) -> Self:
        """Marks the column as unique."""
        self.is_unique = True
        return self

    def primary_key(self) -> Self:
        """Marks the column as a primary key."""
        self.is_primary_key = True
        return self

    def default(self, value: T) -> Self:
        """Sets the default value for the column."""
        self.default_value = value
        return self

    # Comparison Operators
    def __eq__(self, other: Any):  # type: ignore
        return BinaryExpression(self, "=", other)

    def __ne__(self, other: Any):  # type: ignore
        return BinaryExpression(self, "!=", other)

    # Note: comparison operators and some others are not defined for all column types

    def is_null(self):
        return BinaryExpression(self, "IS", None)

    def is_not_null(self):
        return BinaryExpression(self, "IS NOT", None)


# Operator Mixins
class OrderedOperatorMixin:
    def __lt__(self, other: Any):
        return BinaryExpression(self, "<", other)

    def __le__(self, other: Any):
        return BinaryExpression(self, "<=", other)

    def __gt__(self, other: Any):
        return BinaryExpression(self, ">", other)

    def __ge__(self, other: Any):
        return BinaryExpression(self, ">=", other)


class NumericOperatorMixin:
    def __add__(self, other: Any):
        return BinaryExpression(self, "+", other)

    def __sub__(self, other: Any):
        return BinaryExpression(self, "-", other)

    def __mul__(self, other: Any):
        return BinaryExpression(self, "*", other)

    def __truediv__(self, other: Any):
        return BinaryExpression(self, "/", other)

    def __mod__(self, other: Any):
        return BinaryExpression(self, "%", other)

    def __pow__(self, other: Any):
        return BinaryExpression(self, "^", other)


class StringOperatorMixin:
    def concat(self, other: Any):
        return BinaryExpression(self, "||", other)

    def like(self, other: Any):
        return BinaryExpression(self, "LIKE", other)

    def not_like(self, other: Any):
        return BinaryExpression(self, "NOT LIKE", other)

    def ilike(self, other: Any):
        return BinaryExpression(self, "ILIKE", other)

    def not_ilike(self, other: Any):
        return BinaryExpression(self, "NOT ILIKE", other)


class CountOperatorMixin:
    def count(self):
        return FunctionExpression("COUNT", self)

    def count_distinct(self):
        return FunctionExpression("COUNT DISTINCT", self)


class MinMaxOperatorMixin:
    def max(self):
        return FunctionExpression("MAX", self)

    def min(self):
        return FunctionExpression("MIN", self)


class NumericAggregateOperatorMixin:
    def avg(self):
        return FunctionExpression("AVG", self)

    def sum(self):
        return FunctionExpression("SUM", self)


# Data Types
class Integer(
    NumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[int],
):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "INTEGER"
        elif dialect == Dialect.POSTGRESQL:
            return "INT"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class SmallInt(
    NumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[int],
):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "INT"
        elif dialect == Dialect.POSTGRESQL:
            return "SMALLINT"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class BigInt(
    NumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[int],
):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "INTEGER"
        elif dialect == Dialect.POSTGRESQL:
            return "BIGINT"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class Serial(Integer):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.POSTGRESQL:
            return "SERIAL"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class SmallSerial(SmallInt):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.POSTGRESQL:
            return "SMALLSERIAL"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class BigSerial(BigInt):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.POSTGRESQL:
            return "BIGSERIAL"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class Numeric(
    NumericOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    NumericAggregateOperatorMixin,
    ColumnType[float],
):
    def __init__(
        self, col_name: str, *, precision: int | None = None, scale: int | None = None
    ) -> None:
        self.precision = precision
        self.scale = scale
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "REAL"
        elif dialect == Dialect.POSTGRESQL:
            if self.precision is not None and self.scale is not None:
                return f"NUMERIC({self.precision}, {self.scale})"
            elif self.precision is not None:
                return f"NUMERIC({self.precision})"
            else:
                return "NUMERIC"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class Decimal(Numeric):
    pass


class Varchar(
    StringOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[str],
):
    def __init__(self, col_name: str, *, length: int) -> None:
        self.length = length
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return f"VARCHAR({self.length})"
        elif dialect == Dialect.POSTGRESQL:
            return f"VARCHAR({self.length})"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class Text(
    StringOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[str],
):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "TEXT"
        elif dialect == Dialect.POSTGRESQL:
            return "TEXT"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class Char(
    StringOperatorMixin,
    OrderedOperatorMixin,
    CountOperatorMixin,
    MinMaxOperatorMixin,
    ColumnType[str],
):
    def __init__(self, col_name: str, *, length: int) -> None:
        self.length = length
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "TEXT"
        elif dialect == Dialect.POSTGRESQL:
            return f"CHAR({self.length})"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class Boolean(CountOperatorMixin, ColumnType[bool]):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "BOOLEAN"
        elif dialect == Dialect.POSTGRESQL:
            return "BOOLEAN"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class Date(
    OrderedOperatorMixin, CountOperatorMixin, MinMaxOperatorMixin, ColumnType[datetime.date]
):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "DATE"
        elif dialect == Dialect.POSTGRESQL:
            return "DATE"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class Time(
    OrderedOperatorMixin, CountOperatorMixin, MinMaxOperatorMixin, ColumnType[datetime.time]
):
    def __init__(self, col_name: str, *, precision: int | None = None) -> None:
        self.precision = precision
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "TEXT"
        elif dialect == Dialect.POSTGRESQL:
            if self.precision is not None:
                return f"TIME({self.precision})"
            else:
                return "TIME"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class Timestamp(
    OrderedOperatorMixin, CountOperatorMixin, MinMaxOperatorMixin, ColumnType[datetime.datetime]
):
    def __init__(
        self, col_name: str, *, precision: int | None = None, with_timezone: bool = False
    ) -> None:
        self.precision = precision
        self.with_timezone = with_timezone
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "TEXT"
        elif dialect == Dialect.POSTGRESQL:
            if self.precision is not None:
                if self.with_timezone:
                    return f"TIMESTAMP({self.precision}) WITH TIME ZONE"
                else:
                    return f"TIMESTAMP({self.precision})"
            else:
                if self.with_timezone:
                    return "TIMESTAMP WITH TIME ZONE"
                else:
                    return "TIMESTAMP"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class JSON(CountOperatorMixin, ColumnType[dict[str, Any] | list[Any]]):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "TEXT"
        elif dialect == Dialect.POSTGRESQL:
            return "JSON"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)


class JSONB(JSON):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)

    def _get_sql_type(self, dialect: Dialect) -> str:
        if dialect == Dialect.SQLITE:
            return "TEXT"
        elif dialect == Dialect.POSTGRESQL:
            return "JSONB"

        raise DialectNotSupportedError.from_column(dialect, self.__class__.__name__)
