from __future__ import annotations

from enum import StrEnum
from typing import Any


class Dialect(StrEnum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class DialectNotSupportedError(Exception):
    def __init__(self, dialect: Dialect, message: str) -> None:
        super().__init__(f"Dialect {dialect} is not supported: {message}")

    @classmethod
    def from_column(cls, dialect: Dialect, column: str):
        return cls(dialect, f"Column type {column} is not supported")


def get_placeholder(dialect: Dialect, index: int) -> str:
    """Returns the appropriate placeholder for the given dialect and index."""
    if dialect == Dialect.SQLITE:
        return "?"
    elif dialect == Dialect.POSTGRESQL:
        return f"${index + 1}"

    raise DialectNotSupportedError(dialect, "Unsupported dialect")


class ParameterCollector:
    """Collects parameters and generates appropriate placeholders for different dialects."""

    def __init__(self, dialect: Dialect) -> None:
        self.dialect = dialect
        self.params: list[Any] = []

    def add(self, param: Any) -> str:
        """Adds a parameter to the parameter list and returns the appropriate placeholder"""
        self.params.append(param)
        return get_placeholder(self.dialect, len(self.params) - 1)

    @property
    def parameters(self) -> list[Any]:
        return self.params.copy()

    def __len__(self) -> int:
        return len(self.params)


# class ConnectionProtocol(Protocol):
#     """Protocol representing a pep249 database connection."""

#     def close(self) -> None: ...

#     def commit(self) -> None: ...

#     def cursor(self, *args: Any, **kwargs: Any) -> CursorProtocol: ...

#     def rollback(self) -> None: ...

#     def __getattr__(self, name: str) -> Any: ...

#     def __setattr__(self, name: str, value: Any) -> None: ...


# class CursorProtocol(Protocol):
#     """Protocol representing a pep249 cursor."""

#     @property
#     def description(self) -> Any: ...

#     @property
#     def rowcount(self) -> int: ...

#     arraysize: int

#     lastrowid: int

#     def close(self) -> None: ...

#     def execute(self, operation: Any, parameters: SingleExecuteParams | None = None) -> Any: ...

#     def executemany(self, operation: Any, parameters: MultipleExecuteParams) -> Any: ...

#     def fetchone(self) -> Any | None: ...

#     def fetchmany(self, size: int = ...) -> Sequence[Any]: ...

#     def fetchall(self) -> Sequence[Any]: ...

#     def setinputsizes(self, sizes: Sequence[Any]) -> None: ...

#     def setoutputsize(self, size: Any, column: Any) -> None: ...

#     def callproc(self, procname: Any, parameters: Sequence[Any]) -> Any: ...

#     def nextset(self) -> bool | None: ...

#     def __getattr__(self, name: str) -> Any: ...


# SingleExecuteParams = Sequence[Any] | Mapping[str, Any]
# MultipleExecuteParams = Sequence[Sequence[Any]] | Sequence[Mapping[str, Any]]
