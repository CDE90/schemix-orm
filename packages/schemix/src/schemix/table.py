from __future__ import annotations

from abc import ABCMeta
from typing import TYPE_CHECKING, Any, ClassVar

from schemix.utils import _is_column_type

if TYPE_CHECKING:
    from schemix.columns import ColumnType


class TableMeta(ABCMeta):
    """Metaclass that combines ABCMeta with column collection functionality."""

    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs):
        # Collect all column classes from the class definition
        columns: dict[str, ColumnType] = {}

        for attr_name, attr_value in namespace.items():
            if not _is_column_type(attr_value):
                continue

            columns[attr_name] = attr_value

        # Store column classes in the class definition
        namespace["_columns"] = columns

        # Handle table name - use __tablename__ if it exists, otherwise use the class name
        table_name = namespace.get("__tablename__")
        if table_name is None and name != "BaseTable":
            table_name = "".join(
                [
                    "_" + c.lower() if c.isupper() and i > 0 else c.lower()
                    for i, c in enumerate(name)
                ]
            )
            # Remove 'table' suffix if present
            if table_name.endswith("_table"):
                table_name = table_name[:-6]

        namespace["_table_name"] = table_name

        # Create the class
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Now set the table reference on each column
        if name != "BaseTable":
            for column in columns.values():
                column._table_cls = cls  # type: ignore[assignment]

        return cls


class BaseTable(metaclass=TableMeta):
    """Base class for all table definitions."""

    _columns: ClassVar[dict[str, ColumnType]]
    _table_name: ClassVar[str | None]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name for the current table."""
        if cls._table_name is None:
            raise ValueError(f"Table name is not set for {cls.__name__}")
        return cls._table_name

    @classmethod
    def get_columns(cls) -> dict[str, ColumnType]:
        """Get the columns for the current table."""
        return cls._columns.copy()

    # @classmethod
    # def get_column_names(cls) -> list[str]:
    #     """Get the column names for the current table."""
    #     return list(cls._columns.keys())

    @classmethod
    def get_primary_key_columns(cls) -> list[ColumnType]:
        """Get the primary key columns for the current table."""
        return [
            cls._columns[col_name]
            for col_name in cls._columns
            if cls._columns[col_name].is_primary_key
        ]

    @classmethod
    def get_required_columns(cls) -> list[ColumnType]:
        """Get the required columns for the current table."""
        return [
            cls._columns[col_name]
            for col_name in cls._columns
            if cls._columns[col_name].is_nullable is False
        ]

    @classmethod
    def get_optional_columns(cls) -> list[ColumnType]:
        """Get the optional columns for the current table."""
        return [
            cls._columns[col_name]
            for col_name in cls._columns
            if cls._columns[col_name].is_nullable is True
        ]

    @classmethod
    def get_unique_columns(cls) -> list[ColumnType]:
        """Get the unique columns for the current table."""
        return [
            cls._columns[col_name] for col_name in cls._columns if cls._columns[col_name].is_unique
        ]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(table='{self.get_table_name()}', columns={self._columns.keys()})"
