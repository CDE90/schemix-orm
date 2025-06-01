from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from typing import Any

from schemix.dialects import Dialect, ParameterCollector
from schemix.utils import _is_column_type


class SQLExpression(ABC):
    """An abstract class representing an SQL expression."""

    @abstractmethod
    def to_sql(self, dialect: Dialect, collector: ParameterCollector) -> str:
        """Convert the SQL expression to a string."""
        ...

    def __repr__(self) -> str:
        sql_string = self.to_sql(Dialect.SQLITE, ParameterCollector(Dialect.SQLITE))
        return f"{self.__class__.__name__}({sql_string})"

    def __and__(self, other: SQLExpression):
        """Implement the & operator."""
        return BinaryExpression(self, "AND", other)

    def __or__(self, other: SQLExpression):
        """Implement the | operator."""
        return BinaryExpression(self, "OR", other)

    def __invert__(self):
        """Implement the ~ operator."""
        return UnaryExpression("NOT", self)

    def __eq__(self, other: SQLExpression):  # type: ignore
        """Implement the == operator."""
        return BinaryExpression(self, "=", other)

    def __ne__(self, other: SQLExpression):  # type: ignore
        """Implement the != operator."""
        return BinaryExpression(self, "!=", other)

    def _operand_to_sql(self, operand: Any, dialect: Dialect, collector: ParameterCollector) -> str:
        if isinstance(operand, SQLExpression):
            return operand.to_sql(dialect, collector)
        elif _is_column_type(operand):
            return operand._get_qualified_name()
        elif (
            isinstance(
                operand,
                str | int | float | bool | datetime.date | datetime.time | datetime.datetime,
            )
            or operand is None
        ):
            return collector.add(operand)
        else:
            return collector.add(str(operand))


class BinaryExpression(SQLExpression):
    """Represents binary expressions like column = value, expr1 AND expr2, etc."""

    def __init__(self, left: Any, operator: str, right: Any) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def to_sql(self, dialect: Dialect, collector: ParameterCollector) -> str:
        left_sql = self._operand_to_sql(self.left, dialect, collector)
        right_sql = self._operand_to_sql(self.right, dialect, collector)
        
        # Handle dialect-specific operators
        if self.operator == "^" and dialect == Dialect.SQLITE:
            # SQLite uses power(x, y) function instead of ^ operator
            return f"power({left_sql}, {right_sql})"
        
        return f"({left_sql} {self.operator} {right_sql})"


class UnaryExpression(SQLExpression):
    """Represents unary expressions like NOT expr"""

    def __init__(self, operator: str, operand: Any) -> None:
        self.operator = operator
        self.operand = operand

    def to_sql(self, dialect: Dialect, collector: ParameterCollector) -> str:
        operand_sql = self._operand_to_sql(self.operand, dialect, collector)
        return f"({self.operator} {operand_sql})"


class FunctionExpression(SQLExpression):
    """Represents function expressions like COUNT(), MAX(), etc."""

    def __init__(self, function_name: str, *args: Any, modifier: str | None = None) -> None:
        self.function_name = function_name
        self.args = args
        self.modifier = modifier

    def to_sql(self, dialect: Dialect, collector: ParameterCollector) -> str:
        if not self.args:
            return f"{self.function_name}()"

        arg_strings = [self._operand_to_sql(arg, dialect, collector) for arg in self.args]
        if self.modifier:
            return f"{self.function_name}({self.modifier} {', '.join(arg_strings)})"
        return f"{self.function_name}({', '.join(arg_strings)})"
