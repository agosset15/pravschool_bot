from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import ARRAY, DateTime, Enum, Integer
from sqlalchemy import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, registry

from src.core.enums import ScheduleType, UserRole, WeekDay

mapper_registry = registry(
    type_annotation_map={
        int: Integer,
        dict[str, Any]: JSONB,
        UUID: PG_UUID,
        list[UUID]: ARRAY(PG_UUID),
        datetime: DateTime(timezone=True),
        #
        ScheduleType: Enum(ScheduleType, name="schedule_type"),
        UserRole: Enum(UserRole, name="user_role"),
        WeekDay: Enum(WeekDay, name="week_day"),
    }
)


class BaseSql(DeclarativeBase):
    registry = mapper_registry