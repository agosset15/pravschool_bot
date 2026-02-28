from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any, Optional, Self

from loguru import logger


@dataclass(kw_only=True)
class BaseDto:
    id: Optional[int] = field(default=None)


@dataclass(kw_only=True)
class TimestampMixin:
    created_at: Optional[datetime] = field(default=None)
    updated_at: Optional[datetime] = field(default=None)


@dataclass(kw_only=True)
class TrackableMixin:
    _changed_data: dict[str, Any] = field(default_factory=dict, init=False, repr=False)
    _initialized: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self._initialized = True

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_initialized", False) and not name.startswith("_"):
            old_value = getattr(self, name, None)
            if old_value != value:
                self._changed_data[name] = value
                logger.debug(f"Attribute '{name}' changed from '{old_value}' to '{value}'")

        super().__setattr__(name, value)

    @property
    def changed_data(self) -> dict[str, Any]:
        result = self._changed_data.copy()

        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue

            if isinstance(value, TrackableMixin):
                inner_changes = value.changed_data
                if inner_changes:
                    result[key] = inner_changes

            elif isinstance(value, list):
                list_changes = {
                    i: item.changed_data
                    for i, item in enumerate(value)
                    if isinstance(item, TrackableMixin) and item.changed_data
                }
                if list_changes:
                    result[key] = list_changes

        return result

    def as_fully_changed(self) -> Self:
        cls = self.__class__

        data = {f.name: getattr(self, f.name) for f in fields(self) if not f.name.startswith("_")}

        obj = cls(**data)
        obj._initialized = True

        for key, value in data.items():
            obj._changed_data[key] = value

        return obj