from typing import TYPE_CHECKING, Any, TypeGuard

if TYPE_CHECKING:
    from schemix.columns import ColumnType


def _is_column_type(obj: Any) -> TypeGuard[ColumnType]:
    return all(
        (
            hasattr(obj, "col_name"),
            hasattr(obj, "is_nullable"),
            hasattr(obj, "is_unique"),
            hasattr(obj, "is_primary_key"),
            hasattr(obj, "default_value"),
            callable(getattr(obj, "not_null", None)),
            callable(getattr(obj, "nullable", None)),
            callable(getattr(obj, "unique", None)),
            callable(getattr(obj, "primary_key", None)),
            callable(getattr(obj, "default", None)),
        )
    )
