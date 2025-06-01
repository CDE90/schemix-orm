"""Base classes for column types, shared across all dialects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal, Self

from schemix.query import BinaryExpression, FunctionExpression
from schemix.table import BaseTable

__all__ = [
    "ColumnType",
    "OnDeleteUpdateAction",
    "OrderedOperatorMixin",
    "NumericOperatorMixin",
    "StringOperatorMixin",
    "CountOperatorMixin",
    "MinMaxOperatorMixin",
    "NumericAggregateOperatorMixin",
]


OnDeleteUpdateAction = Literal["cascade", "restrict", "set null", "set default", "no action"]


class ColumnType[T](ABC):
    """An abstract class representing a column type."""

    col_name: str
    _type_params: dict[str, Any]

    is_nullable: bool = True
    is_unique: bool = False
    is_primary_key: bool = False
    default_value: T | None = None

    _table_cls: type[BaseTable] | None = None
    _references: ColumnType | None = None
    _on_delete: str | None = None
    _on_update: str | None = None

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
    def get_sql_type(self) -> str:
        """Get the SQL type string for this column in the specific dialect."""
        ...

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

    def references(
        self,
        column: ColumnType,
        *,
        on_delete: OnDeleteUpdateAction | None = None,
        on_update: OnDeleteUpdateAction | None = None,
    ) -> Self:
        """Sets this column as a foreign key referencing another column.

        Args:
            column: The column this foreign key references
            on_delete: Action to take when referenced row is deleted
            on_update: Action to take when referenced row is updated
        """
        self._references = column
        self._on_delete = on_delete.upper() if on_delete else None
        self._on_update = on_update.upper() if on_update else None
        return self

    # Comparison Operators
    def __eq__(self, other: Any):  # type: ignore
        return BinaryExpression(self, "=", other)

    def __ne__(self, other: Any):  # type: ignore
        return BinaryExpression(self, "!=", other)

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


class CountOperatorMixin:
    def count(self):
        return FunctionExpression("COUNT", self)

    def count_distinct(self):
        return FunctionExpression("COUNT", self, modifier="DISTINCT")


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
