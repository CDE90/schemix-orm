from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from typing import Any

from schemix.dialects import Dialect, ParameterCollector
from schemix.utils import _is_column_type


class SQLExpression(ABC):
    """An abstract class representing an SQL expression."""

    @abstractmethod
    def to_sql(self, collector: ParameterCollector | None = None) -> str:
        """Convert the SQL expression to a string."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_sql()})"

    def __and__(self, other: SQLExpression) -> SQLExpression:
        """Implement the & operator."""
        return BinaryExpression(self, "AND", other)

    def __or__(self, other: SQLExpression) -> SQLExpression:
        """Implement the | operator."""
        return BinaryExpression(self, "OR", other)

    def __invert__(self) -> SQLExpression:
        """Implement the ~ operator."""
        return UnaryExpression("NOT", self)

    def __eq__(self, other: SQLExpression) -> SQLExpression:  # type: ignore
        """Implement the == operator."""
        return BinaryExpression(self, "=", other)

    def __ne__(self, other: SQLExpression) -> SQLExpression:  # type: ignore
        """Implement the != operator."""
        return BinaryExpression(self, "!=", other)

    def _operand_to_sql(self, operand: Any, collector: ParameterCollector) -> str:
        if isinstance(operand, SQLExpression):
            return operand.to_sql(collector)
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

    def to_sql(self, collector: ParameterCollector | None = None) -> str:
        # TODO: ensure that this handles correctly when collector is None (below is temporary)
        if collector is None:
            collector = ParameterCollector(Dialect.SQLITE)

        left_sql = self._operand_to_sql(self.left, collector)
        right_sql = self._operand_to_sql(self.right, collector)
        return f"({left_sql} {self.operator} {right_sql})"


class UnaryExpression(SQLExpression):
    """Represents unary expressions like NOT expr"""

    def __init__(self, operator: str, operand: Any) -> None:
        self.operator = operator
        self.operand = operand

    def to_sql(self, collector: ParameterCollector | None = None) -> str:
        # TODO: ensure that this handles correctly when collector is None (below is temporary)
        if collector is None:
            collector = ParameterCollector(Dialect.SQLITE)

        operand_sql = self._operand_to_sql(self.operand, collector)
        return f"({self.operator} {operand_sql})"


class FunctionExpression(SQLExpression):
    """Represents function expressions like COUNT(), MAX(), etc."""

    def __init__(self, function_name: str, *args: Any) -> None:
        self.function_name = function_name
        self.args = args

    def to_sql(self, collector: ParameterCollector | None = None) -> str:
        # TODO: ensure that this handles correctly when collector is None (below is temporary)
        if collector is None:
            collector = ParameterCollector(Dialect.SQLITE)

        if not self.args:
            return f"{self.function_name}()"

        arg_strings = [self._operand_to_sql(arg, collector) for arg in self.args]
        return f"{self.function_name}({', '.join(arg_strings)})"
